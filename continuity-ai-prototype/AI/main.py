"""Main entry point for the AI solution."""
import asyncio
import logging
import sys
from typing import Literal

from database.vector_db import VectorDB
from models.llm_manager import LLMManager
from interfaces.web_api import create_app
from utils.context_manager import ContextManager
from utils.logger import setup_logging
from config.settings import API_HOST, API_PORT

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def run_web_api(vector_db: VectorDB, llm_manager: LLMManager):
    """Run the FastAPI web server."""
    import uvicorn
    import threading

    context_manager = ContextManager()
    app = create_app(vector_db, llm_manager, context_manager)

    config = uvicorn.Config(
        app=app,
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        server_header=False,
    )
    
    logger.info(f"Starting web API on {API_HOST}:{API_PORT}")
    
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
    Main entry point - runs web API server.
    """
    # Initialize components
    logger.info("Initializing components...")
    
    vector_db = None
    llm_manager = None
    
    try:
        vector_db = VectorDB()
        llm_manager = LLMManager()

        # Check health
        logger.info("Checking system health...")
        llm_ok = await llm_manager.health_check()
        if not llm_ok:
            logger.warning("⚠ LLM not available. Ensure the GGUF path is correct and llama-cpp can load it.")
        
        db_info = vector_db.get_collection_info()
        logger.info(f"Vector DB: {db_info['document_count']} documents")
        
        # Auto-load NSCC data if DB is empty
        if db_info['document_count'] == 0:
            logger.info("Knowledge base is empty, auto-loading NSCC data...")
            from load_knowledge_base import load_nscc_data
            load_nscc_data()
            db_info = vector_db.get_collection_info()
            logger.info(f"Vector DB now contains: {db_info['document_count']} documents")

        # Run web API server
        logger.info("Starting web API server...")
        await run_web_api(vector_db, llm_manager)

    except Exception as e:
        logger.error(f"Fatal error in main: {type(e).__name__}: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\n✓ Application terminated")
