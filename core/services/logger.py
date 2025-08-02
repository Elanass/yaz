"""
Simplified logging service
"""
import logging
import structlog


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger"""
    return logging.getLogger(name)


def setup_logging():
    """Setup structured logging"""
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


def audit_log(action: str, user_id: str = None, **kwargs):
    """Simple audit logging function"""
    logger = get_logger("audit")
    logger.info(f"AUDIT: {action}", extra={"user_id": user_id, **kwargs})
