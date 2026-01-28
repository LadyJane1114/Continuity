"""Logging configuration."""
import logging
import logging.handlers
import os
from config.settings import LOG_LEVEL, LOG_FILE


def setup_logging() -> None:
    """Configure application logging."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging configured")
