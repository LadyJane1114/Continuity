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
from config.settings import API_HOST, API_PORT, DISCORD_TOKEN

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


async def run_discord_bot(vector_db: VectorDB, llm_manager: LLMManager):
    """Run the Discord bot."""
    # Import discord_bot only when needed
    from interfaces.discord_bot import create_bot
    
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN not set in environment")

    context_manager = ContextManager()
    bot = create_bot(vector_db, llm_manager, context_manager)

    logger.info("Starting Discord bot")
    await bot.start(DISCORD_TOKEN)


async def main(mode: Literal["web", "discord", "both"] = "both"):
    """
    Main entry point.

    Args:
        mode: Which interface to run ('web', 'discord', or 'both')
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

        # Run specified interface(s)
        if mode == "web":
            logger.info("Running in WEB mode")
            logger.info("About to call run_web_api...")
            await run_web_api(vector_db, llm_manager)
            logger.info("run_web_api returned!")
        elif mode == "discord":
            await run_discord_bot(vector_db, llm_manager)
        elif mode == "both":
            # Run both concurrently
            await asyncio.gather(
                run_web_api(vector_db, llm_manager),
                run_discord_bot(vector_db, llm_manager),
            )

    except Exception as e:
        logger.error(f"Fatal error in main: {type(e).__name__}: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Assistant with RAG powered by Phi 4"
    )
    parser.add_argument(
        "--mode",
        choices=["web", "discord", "both"],
        default="both",
        help="Which interface to run",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(mode=args.mode))
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\n✓ Application terminated")
