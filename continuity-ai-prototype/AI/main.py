"""Main entry point for entity extraction API with facts."""
import asyncio
import logging
import sys

from models.ner_extractor import HybridNERExtractor
from interfaces.web_api import create_app
from utils.logger import setup_logging
from config.settings import API_HOST, API_PORT, FACT_MODEL_PATH
from models.fact_extractor import FactExtractor
from models.llm_manager import LLMManager  # NEW: Phi-4 mini manager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def run_web_api(ner_extractor: HybridNERExtractor):
    """Run the FastAPI web server."""
    import uvicorn  # type: ignore
    import threading  # type: ignore

    # NEW: LLM-first facts using local Phi-4 mini
    
    llm = LLMManager(model_path=FACT_MODEL_PATH)  # ← use Qwen 2.5 3B Instruct Q6_K
    fact_extractor = FactExtractor(
        llm=llm,
        use_llm=True,
        max_facts_per_entity=3,
        rules_fallback=False,   # set True temporarily if you want regex backup
        temperature=0.2,
        max_tokens=120,         # 96–160 is a good range for concise JSON
    )


    app = create_app(ner_extractor, fact_extractor=fact_extractor)
    logger.info(f"Starting Entity Extraction API on {API_HOST}:{API_PORT}")

    def run_server():
        uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")

    # Run server in a daemon thread so our async loop stays alive
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
    """
    Main entry point - runs entity extraction API server.
    """
    logger.info("Initializing entity extraction system...")
    try:
        # Initialize NER extractor with BERT model (entities only)
        logger.info("Loading BERT NER model...")
        ner_extractor = HybridNERExtractor(model_name="dslim/bert-base-NER")
        logger.info("[OK] NER model loaded successfully")
        logger.info("Starting web API server...")
        await run_web_api(ner_extractor)
    except Exception as e:
        logger.error(f"Fatal error in main: {type(e).__name__}: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\n✓ Application terminated")