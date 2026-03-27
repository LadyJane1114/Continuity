import asyncio
import logging
from pathlib import Path
import sys

from models.ner_extractor import HybridNERExtractor
from interfaces.web_api import create_app
from utils.logger import setup_logging
from config.settings import (
    API_HOST,
    API_PORT,
    EXPORT_JSON_DIR,
    FACT_AUTO_VALIDATE,
    FACT_CONFIDENCE_THRESHOLD,
    FACT_EXTRACTION_MAX_TOKENS,
    FACT_EXTRACTION_TEMPERATURE,
    FACT_MODEL_PATH,
    FACT_RULES_FALLBACK,
    FACT_USE_LLM,
    MAX_FACTS_PER_ENTITY,
    MAX_FACTS_PER_SENTENCE,
    NER_MODEL_NAME,
)
from models.fact_extractor import FactExtractor
from models.llm_manager import LLMManager

setup_logging()
logger = logging.getLogger(__name__)
Path(EXPORT_JSON_DIR).mkdir(parents=True, exist_ok=True)

async def run_web_api(ner_extractor: HybridNERExtractor):
    import uvicorn
    import threading

    llm = LLMManager(model_path=FACT_MODEL_PATH)
    fact_extractor = FactExtractor(
        llm=llm,
        use_llm=FACT_USE_LLM,
        max_facts_per_entity=MAX_FACTS_PER_ENTITY,
        max_facts_per_sentence=MAX_FACTS_PER_SENTENCE,
        rules_fallback=FACT_RULES_FALLBACK,
        temperature=FACT_EXTRACTION_TEMPERATURE,
        max_tokens=FACT_EXTRACTION_MAX_TOKENS,
        fact_confidence_threshold=FACT_CONFIDENCE_THRESHOLD,
        auto_validate_facts=FACT_AUTO_VALIDATE,
    )

    logger.info(
        "Fact extractor config: use_llm=%s, max_facts_per_entity=%s, max_facts_per_sentence=%s, temp=%s, max_tokens=%s, confidence=%s",
        FACT_USE_LLM,
        MAX_FACTS_PER_ENTITY,
        MAX_FACTS_PER_SENTENCE,
        FACT_EXTRACTION_TEMPERATURE,
        FACT_EXTRACTION_MAX_TOKENS,
        FACT_CONFIDENCE_THRESHOLD,
    )

    app = create_app(ner_extractor, fact_extractor=fact_extractor)
    logger.info("Starting Entity Extraction API on %s:%s", API_HOST, API_PORT)

    def run_server():
        uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    logger.info("Server thread started, keeping process alive...")

    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        logger.info("Server interrupted")
        raise

async def main():
    logger.info("Initializing entity extraction system...")
    try:
        logger.info("Loading BERT NER model...")
        ner_extractor = HybridNERExtractor(model_name=NER_MODEL_NAME)
        logger.info("[OK] NER model loaded successfully")
        logger.info("Starting web API server...")
        await run_web_api(ner_extractor)
    except Exception as e:
        logger.error("Fatal error in main: %s: %s", type(e).__name__, e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\n✓ Application terminated")