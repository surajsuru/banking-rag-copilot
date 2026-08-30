"""
logger.py
Shared logging configuration for the entire project.
Import get_logger() in any module instead of using print().
"""

import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Usage in any other file:
        from src.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Processing file...")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    # Set the log level from config (INFO, DEBUG, WARNING, etc.)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # Handler: sends log output to the terminal (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # Formatter: defines how each log line looks
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
