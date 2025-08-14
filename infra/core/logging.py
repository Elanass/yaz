"""Simple logging setup for YAZ platform
"""
import logging
import sys
from pathlib import Path


def setup_logging(name: str = "yaz", level: str = "INFO"):
    """Setup basic logging configuration"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(name)


# Set up root logger
setup_logging()
