"""
Core logging setup for the Decision Precision Engine
"""
import logging
import sys
from pathlib import Path
import structlog


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger"""
    return logging.getLogger(name)


def setup_logging():
    """Setup centralized logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "application.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure structured logging for audit trails
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("decision_engine").setLevel(logging.INFO)


def audit_log(action: str, user_id: str = None, **kwargs):
    """Simple audit logging function"""
    logger = get_logger("audit")
    logger.info(f"AUDIT: {action}", extra={"user_id": user_id, **kwargs})
