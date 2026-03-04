import asyncio
import logging
import time
from pathlib import Path
from typing import AsyncGenerator

from llama_cpp import Llama
from config.settings import MODEL_PATH, RESPONSE_TIMEOUT

logger = logging.getLogger(__name__)


class LLMManager:
    """Local LLM manager (llama-cpp)."""

    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        self._lock = asyncio.Lock()
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=256,
            n_threads=4,
            n_gpu_layers=0,
            n_batch=4,
            n_ubatch=4,
            verbose=False,
            use_mlock=False,
            use_mmap=True,
        )
        logger.info("LLMManager initialized with model: %s", self.model_path)

    def reset_context(self):
        try:
            self.llm.reset()
            logger.debug("KV cache reset")
        except Exception as e:
            logger.warning("KV cache reset failed: %s", e)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False,
        reset_context: bool = True,
    ) -> str:
        loop = asyncio.get_running_loop()

        def _run() -> str:
            if reset_context:
                try:
                    self.llm.reset()
                except Exception as e:
                    logger.warning("Context reset failed: %s", e)
            resp = self.llm(
                prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=8,
                stop=["</s>", "User:", "\n\n", "\n", ":"],
                echo=False,
            )
            return (resp["choices"][0]["text"] or "").strip()

        try:
            async with self._lock:
                if stream:
                    tokens = []
                    async for t in self._generate_stream(prompt, temperature, top_p):
                        tokens.append(t)
                    return "".join(tokens)
                return await asyncio.wait_for(
                    loop.run_in_executor(None, _run), timeout=RESPONSE_TIMEOUT
                )
        except asyncio.TimeoutError:
            logger.error("LLM response timeout after %ss", RESPONSE_TIMEOUT)
            self.reset_context()
            raise
        except Exception as e:
            logger.error("LLM generate error: %s", e)
            self.reset_context()
            raise

    async def _generate_stream(
        self, prompt: str, temperature: float, top_p: float
    ) -> AsyncGenerator[str, None]:
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
            logger.error("LLM stream error: %s", e)
            raise

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        timeout_seconds: int | None = None,
    ) -> str:
        loop = asyncio.get_running_loop()

        def _run() -> str:
            start = time.time()
            logger.info(
                "LLM JSON start (temp=%.2f, max_tokens=%d, prompt_len=%d)",
                temperature,
                max_tokens,
                len(prompt),
            )
            text = ""
            resp = None

            # Try chat completion first
            try:
                resp = self.llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": "You are a precise JSON extractor. Reply only with JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    top_p=0.95,
                    max_tokens=max_tokens,
                    stop=[],
                )
                text = (resp["choices"][0]["message"].get("content") or "").strip()
            except Exception as chat_err:
                logger.debug("Chat completion not available: %s", chat_err)

            # Fallback to instruction completion
            if not text:
                instr = f"### Instruction:\n{prompt}\n### Response:\n"
                resp = self.llm(
                    instr,
                    temperature=temperature,
                    top_p=0.95,
                    max_tokens=max_tokens,
                    stop=[],
                    echo=False,
                )
                text = (resp["choices"][0].get("text") or "").strip()

            dur = time.time() - start
            logger.info("LLM JSON done in %.2fs; len=%d", dur, len(text))

            if not text:
                logger.warning(
                    "LLM returned empty text; keys=%s choices=%s",
                    list(resp.keys()) if resp else [],
                    (resp.get("choices") if resp else None),
                )

            # Trim any think tags if present (HTML-escaped style handled upstream as needed)
            if "<think>" in text and "</think>" in text:
                text = text.split("</think>")[-1].strip()
            if "&lt;think&gt;" in text and "&lt;/think&gt;" in text:
                text = text.split("&lt;/think&gt;")[-1].strip()
            return text

        try:
            async with self._lock:
                to = timeout_seconds or min(max(RESPONSE_TIMEOUT, 60), 120)
                return await asyncio.wait_for(loop.run_in_executor(None, _run), timeout=to)
        except asyncio.TimeoutError:
            logger.error("LLM JSON timeout after %.0fs (prompt len=%d)", to, len(prompt))
            raise
        except Exception as e:
            logger.error("LLM generate_json error: %s", e)
            raise

    async def health_check(self) -> bool:
        if not Path(self.model_path).exists():
            logger.warning("Model file missing: %s", self.model_path)
            return False
        loop = asyncio.get_running_loop()

        def _probe() -> bool:
            _ = self.llm("hi", max_tokens=1)
            return True

        try:
            return await asyncio.wait_for(loop.run_in_executor(None, _probe), timeout=5.0)
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False