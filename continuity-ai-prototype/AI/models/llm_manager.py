"""Local LLM management using llama-cpp-python and Phi 4."""
import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator

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

        # Load model with llama-cpp-python
        # n_gpu_layers: adjust based on your GPU VRAM; 0 for CPU-only
        # n_ctx: context window size
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,  # CPU-only mode
            verbose=False,
        )
        self.model = self.model_path
        logger.info(f"LLMManager initialized with model: {self.model}")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False,
    ) -> str:
        """Generate a response from the local LLM."""
        loop = asyncio.get_running_loop()

        def _run_inference() -> str:
            response = self.llm(
                prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=256,
                stop=["</s>", "User:", "\n\n"],
                echo=False,
            )
            return response["choices"][0]["text"].strip()

        try:
            if stream:
                # Collect streamed tokens into a single string for API compatibility
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
            raise
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
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


