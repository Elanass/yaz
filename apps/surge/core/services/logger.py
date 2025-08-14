"""Centralized logging configuration for Surge Platform."""

import logging
import logging.config
import logging.handlers
import sys
from pathlib import Path

import structlog

from shared.config import get_shared_config


# Load logging configuration from logging.ini if it exists
_config_path = Path(__file__).parents[4] / "logging.ini"
if _config_path.exists():
    logging.config.fileConfig(_config_path, disable_existing_loggers=False)


def setup_logging(
    level: str | None = None, log_to_file: bool = True, log_to_console: bool = True
) -> None:
    """Setup comprehensive logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    settings = get_shared_config()

    # Determine log level
    if level is None:
        level = settings.log_level

    log_level = getattr(logging, level.upper(), logging.INFO)

    # Ensure logs directory exists
    logs_dir = settings.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if settings.is_production:
            console_handler.setFormatter(detailed_formatter)
        else:
            console_handler.setFormatter(simple_formatter)

        root_logger.addHandler(console_handler)

    # File handlers
    if log_to_file:
        # Application log (rotating)
        app_log_file = logs_dir / "surge.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,  # 10MB
        )
        app_handler.setLevel(log_level)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)

        # Error log (for warnings and above)
        error_log_file = logs_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,  # 10MB
        )
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

    # Set specific logger levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"🔧 Logging configured - Level: {level}, Environment: {settings.environment}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request(
    request_id: str, method: str, path: str, user_id: str | None = None
) -> None:
    """Log an API request.

    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        user_id: Optional user identifier
    """
    logger = get_logger("api.requests")
    logger.info(
        f"Request: {method} {path}",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "user_id": user_id,
        },
    )


def log_error(error: Exception, context: dict | None = None) -> None:
    """Log an error with context.

    Args:
        error: Exception to log
        context: Additional context information
    """
    logger = get_logger("errors")
    logger.error(f"Error: {error!s}", extra=context or {})


def audit_log(action: str, user_id: str | None = None, **kwargs) -> None:
    """Enhanced audit logging function."""
    logger = get_logger("audit")
    logger.info(f"AUDIT: {action}", extra={"user_id": user_id, **kwargs})
