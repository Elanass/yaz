"""
Structured Logging Service

Provides a centralized, structured logging service for the entire application,
with support for different log levels, contexts, and HIPAA/GDPR compliant audit logging.
"""

import logging
import os
import json
import traceback
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog
from structlog.types import Processor

from core.config.settings import get_logging_config


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogType(str, Enum):
    """Log types"""
    APPLICATION = "application"
    AUDIT = "audit"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ERROR = "error"


class Logger:
    """Structured logging service with HIPAA/GDPR compliance"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the logger"""
        if self._initialized:
            return
            
        self.config = get_logging_config()
        self._setup_logging()
        self._initialized = True
    
    def _setup_logging(self):
        """Set up structlog with processors and configuration"""
        # Configure structlog
        processors: List[Processor] = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        
        # Add JSON renderer for production
        if os.getenv("ENVIRONMENT") == "production":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(
                structlog.dev.ConsoleRenderer(colors=True)
            )
        
        structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Set up Python's logging module
        logging.basicConfig(
            format="%(message)s",
            level=self._get_log_level(),
            handlers=self._get_handlers()
        )
        
        # Create loggers for different types
        self.app_logger = structlog.get_logger("application")
        self.audit_logger = structlog.get_logger("audit")
        self.security_logger = structlog.get_logger("security")
        self.perf_logger = structlog.get_logger("performance")
        self.error_logger = structlog.get_logger("error")
    
    def _get_log_level(self) -> int:
        """Get the configured log level"""
        level = self.config.get("log_level", "INFO").upper()
        return getattr(logging, level, logging.INFO)
    
    def _get_handlers(self) -> List[logging.Handler]:
        """Configure log handlers based on settings"""
        handlers = []
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(self._get_log_level())
        handlers.append(console)
        
        # File handlers if enabled
        if self.config.get("log_to_file", False):
            log_dir = self.config.get("log_dir", "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Application log
            app_handler = logging.FileHandler(f"{log_dir}/application.log")
            app_handler.setLevel(self._get_log_level())
            handlers.append(app_handler)
            
            # Audit log (always INFO or higher)
            audit_handler = logging.FileHandler(f"{log_dir}/audit.log")
            audit_handler.setLevel(logging.INFO)
            handlers.append(audit_handler)
            
            # Security log
            security_handler = logging.FileHandler(f"{log_dir}/security.log")
            security_handler.setLevel(logging.INFO)
            handlers.append(security_handler)
            
            # Performance log
            perf_handler = logging.FileHandler(f"{log_dir}/performance.log")
            perf_handler.setLevel(logging.INFO)
            handlers.append(perf_handler)
            
            # Error log
            error_handler = logging.FileHandler(f"{log_dir}/errors.log")
            error_handler.setLevel(logging.ERROR)
            handlers.append(error_handler)
        
        return handlers
    
    def log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        log_type: LogType = LogType.APPLICATION,
        context: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
        **kwargs
    ):
        """
        Log a message with structured context
        
        Args:
            message: The log message
            level: The log level
            log_type: The type of log
            context: Additional structured context
            exc_info: Exception information if any
            **kwargs: Additional key-value pairs for structured context
        """
        # Get the appropriate logger based on type
        logger = getattr(self, f"{log_type.value}_logger", self.app_logger)
        
        # Combine context and kwargs
        log_context = {**(context or {}), **kwargs}
        
        # Generate unique event ID
        log_context["event_id"] = str(uuid.uuid4())
        
        # Add timestamp
        log_context["timestamp"] = datetime.utcnow().isoformat()
        
        # Log with appropriate level
        log_method = getattr(logger, level.value)
        if exc_info:
            log_context["exception"] = str(exc_info)
            log_context["traceback"] = traceback.format_exc()
            log_method(message, **log_context)
        else:
            log_method(message, **log_context)
    
    def debug(self, message: str, **kwargs):
        """Log a debug message"""
        self.log(message, level=LogLevel.DEBUG, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log an info message"""
        self.log(message, level=LogLevel.INFO, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log a warning message"""
        self.log(message, level=LogLevel.WARNING, **kwargs)
    
    def error(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """Log an error message"""
        self.log(
            message,
            level=LogLevel.ERROR,
            log_type=LogType.ERROR,
            exc_info=exc_info,
            **kwargs
        )
    
    def critical(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """Log a critical message"""
        self.log(
            message,
            level=LogLevel.CRITICAL,
            log_type=LogType.ERROR,
            exc_info=exc_info,
            **kwargs
        )
    
    def audit(
        self,
        action: str,
        actor_id: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        outcome: str = "success",
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log an audit event
        
        Args:
            action: The action performed (e.g., "create", "read", "update", "delete")
            actor_id: ID of the user or system performing the action
            resource_type: Type of resource being accessed (e.g., "patient", "decision")
            resource_id: ID of the specific resource (optional)
            outcome: Outcome of the action ("success" or "failure")
            details: Additional details about the action
            **kwargs: Additional context
        """
        self.log(
            f"AUDIT: {action} on {resource_type}" + 
            (f" {resource_id}" if resource_id else ""),
            level=LogLevel.INFO,
            log_type=LogType.AUDIT,
            context={
                "audit": {
                    "action": action,
                    "actor_id": actor_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "outcome": outcome,
                    "details": details or {}
                }
            },
            **kwargs
        )
    
    def security(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log a security event
        
        Args:
            event_type: Type of security event (e.g., "login", "access_denied")
            severity: Severity of the event ("low", "medium", "high", "critical")
            user_id: ID of the user involved (optional)
            ip_address: IP address involved (optional)
            details: Additional details about the event
            **kwargs: Additional context
        """
        self.log(
            f"SECURITY: {event_type} [{severity}]" +
            (f" by user {user_id}" if user_id else ""),
            level=LogLevel.INFO,
            log_type=LogType.SECURITY,
            context={
                "security": {
                    "event_type": event_type,
                    "severity": severity,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "details": details or {}
                }
            },
            **kwargs
        )
    
    def performance(
        self,
        operation: str,
        duration_ms: float,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log a performance metric
        
        Args:
            operation: The operation being measured
            duration_ms: Duration in milliseconds
            resource_type: Type of resource being accessed (optional)
            resource_id: ID of the specific resource (optional)
            details: Additional details about the operation
            **kwargs: Additional context
        """
        self.log(
            f"PERF: {operation} took {duration_ms:.2f}ms",
            level=LogLevel.INFO,
            log_type=LogType.PERFORMANCE,
            context={
                "performance": {
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": details or {}
                }
            },
            **kwargs
        )
