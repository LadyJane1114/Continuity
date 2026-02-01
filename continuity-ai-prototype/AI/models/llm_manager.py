"""Local LLM management using llama-cpp-python and Phi 4."""
import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator
import time

from llama_cpp import Llama

from config.settings import MODEL_PATH, RESPONSE_TIMEOUT

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages interactions with a local Phi 4 GGUF model via llama-cpp-python."""

    def __init__(self, model_path: str = MODEL_PATH):
        """Initialize the LLM manager and load the model."""
        self.model_path = model_path
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Set MODEL_PATH to your GGUF file."
            )

        # Ensure single inference at a time (llama-cpp is not thread-safe)
        self._lock = asyncio.Lock()

        # Load model with llama-cpp-python
        # n_gpu_layers: adjust based on your GPU VRAM; 0 for CPU-only
        # n_ctx: context window size - extremely small for stability
        # Using minimal settings to work around GGML assertion bug
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=256,       # extremely small context (last resort)
            n_threads=4,
            n_gpu_layers=0,  # CPU-only mode
            n_batch=4,       # minimal batch size
            n_ubatch=4,      # minimal micro-batch
            verbose=False,
            use_mlock=False, # Disable memory locking
            use_mmap=True,   # Use memory mapping
        )
        self.model = self.model_path
        logger.info(f"LLMManager initialized with model: {self.model}")

    def reset_context(self):
        """Reset the model's KV cache to clear context."""
        try:
            self.llm.reset()
            logger.debug("Model context reset")
        except Exception as e:
            logger.warning(f"Failed to reset context: {e}")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False,
        reset_context: bool = True,
    ) -> str:
        """Generate a response from the local LLM."""
        loop = asyncio.get_running_loop()

        def _run_inference() -> str:
            # Reset context before each inference to avoid overflow
            if reset_context:
                try:
                    self.llm.reset()
                    logger.debug("Context reset successful")
                except Exception as e:
                    logger.warning(f"Context reset failed: {e}")

            response = self.llm(
                prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=8,   # minimal tokens (just enough for YES/NO or type)
                stop=["</s>", "User:", "\n\n", "\n", ":"],
                echo=False,
            )
            return response["choices"][0]["text"].strip()

        try:
            async with self._lock:
                if stream:
                    tokens = []
                    async for token in self._generate_stream(prompt, temperature, top_p):
                        tokens.append(token)
                    return "".join(tokens)

                return await asyncio.wait_for(
                    loop.run_in_executor(None, _run_inference),
                    timeout=RESPONSE_TIMEOUT,
                )
        except asyncio.TimeoutError:
            logger.error(f"LLM response timeout after {RESPONSE_TIMEOUT}s")
            # Reset context on timeout
            self.reset_context()
            raise
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Reset context on error
            self.reset_context()
            raise

    async def _generate_stream(
        self,
        prompt: str,
        temperature: float,
        top_p: float,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from the LLM."""
        loop = asyncio.get_running_loop()

        def _get_stream():
            return self.llm(
                prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=256,
                stop=["</s>", "User:", "\n\n"],
                stream=True,
            )

        try:
            stream = await loop.run_in_executor(None, _get_stream)
            for chunk in stream:
                token = chunk["choices"][0]["text"]
                if token:
                    yield token
        except Exception as e:
            logger.error(f"Error in stream generation: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        timeout_seconds: int | None = None,
    ) -> str:
        """Generate JSON response from the local LLM with appropriate settings."""
        loop = asyncio.get_running_loop()

        def _run_inference() -> str:
            start = time.time()
            logger.info(
                "LLM JSON start (temp=%.2f, max_tokens=%d, prompt_len=%d)",
                temperature,
                max_tokens,
                len(prompt),
            )
            response = None
            text = ""

            # First attempt: chat completion for chat-optimized models
            try:
                response = self.llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": "You are a precise JSON extractor. Reply only with JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    top_p=0.95,
                    max_tokens=max_tokens,
                    stop=[],
                )
                text = (response["choices"][0]["message"].get("content") or "").strip()
            except Exception as chat_err:
                logger.debug(f"Chat completion not available, falling back: {chat_err}")

            # Fallback: instruction-style completion if chat path produced nothing
            if not text:
                instruction_prompt = (
                    "### Instruction:\n"
                    f"{prompt}\n"
                    "### Response:\n"
                )
                response = self.llm(
                    instruction_prompt,
                    temperature=temperature,
                    top_p=0.95,
                    max_tokens=max_tokens,
                    stop=[],  # No extra stop tokens; let model finish
                    echo=False,
                )
                text = (response["choices"][0].get("text") or "").strip()

            duration = time.time() - start
            logger.info(
                "LLM JSON done in %.2fs; response length=%d",
                duration,
                len(text),
            )

            if not text:
                logger.warning(
                    "LLM returned empty text; raw response keys=%s choices=%s",
                    list(response.keys()) if response else [],
                    response.get("choices") if response else None,
                )
                logger.info(f"Raw response payload: {response}")

            # Remove any thinking tags if they appear
            if "<think>" in text:
                text = text.split("</think>")[-1].strip()
            return text

        try:
            async with self._lock:
                timeout_seconds = timeout_seconds or min(max(RESPONSE_TIMEOUT, 60), 120)
                return await asyncio.wait_for(
                    loop.run_in_executor(None, _run_inference),
                    timeout=timeout_seconds,
                )
        except asyncio.TimeoutError:
            logger.error(
                "LLM JSON response timeout after %.0fs (prompt length=%d)",
                timeout_seconds,
                len(prompt),
            )
            raise
        except Exception as e:
            logger.error(f"Error generating LLM JSON response: {e}")
            raise

    async def health_check(self) -> bool:
        """Quick health check: verify the model file exists and basic call works."""
        if not Path(self.model_path).exists():
            logger.warning(f"Model file missing at {self.model_path}")
            return False

        try:
            loop = asyncio.get_running_loop()

            def _probe() -> bool:
                # Lightweight single-token probe
                _ = self.llm("hi", max_tokens=1)
                return True

            return await asyncio.wait_for(
                loop.run_in_executor(None, _probe),
                timeout=5.0,
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


