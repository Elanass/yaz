"""
Shared Logging Configuration
Minimal logging setup for all apps
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_shared_config


def setup_logging(app_name: Optional[str] = None) -> None:
    """Setup logging configuration"""
    config = get_shared_config()
    
    # Create logs directory
    log_dir = Path(config.log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "yaz.log")
        ]
    )
    
    if app_name:
        # App-specific log file
        app_handler = logging.FileHandler(log_dir / f"{app_name}.log")
        app_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        
        app_logger = logging.getLogger(app_name)
        app_logger.addHandler(app_handler)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
