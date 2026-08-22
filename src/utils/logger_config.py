import logging
import os


def setup_logger(name: str, level: int | None = None) -> logging.Logger:
    """Create a logger without exposing verbose request details in production."""
    configured_level = level
    if configured_level is None:
        level_name = os.getenv("LOG_LEVEL", "WARNING").upper()
        configured_level = getattr(logging, level_name, logging.WARNING)

    logger = logging.getLogger(name)
    logger.setLevel(configured_level)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
