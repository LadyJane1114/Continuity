"""Main entry point for entity extraction API."""
import asyncio
import logging
import sys

from models.ner_extractor import HybridNERExtractor
from interfaces.web_api import create_app
from utils.logger import setup_logging
from config.settings import API_HOST, API_PORT

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def run_web_api(ner_extractor: HybridNERExtractor):
    """Run the FastAPI web server."""
    import uvicorn # type: ignore
    import threading # type: ignore

    app = create_app(ner_extractor)

    logger.info(f"Starting Entity Extraction API on {API_HOST}:{API_PORT}")

    # Run uvicorn in a blocking manner with Python's asyncio
    # Use a thread to run the sync uvicorn.run()
    def run_server():
        uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")

    # Run server in thread so it blocks properly
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # Keep the async function running
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
    # Initialize components
    logger.info("Initializing entity extraction system...")

    try:
        # Initialize NER extractor with BERT model
        logger.info("Loading BERT NER model...")
        ner_extractor = HybridNERExtractor(model_name="dslim/bert-base-NER")
        logger.info("[OK] NER model loaded successfully")

        # Run web API server
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
