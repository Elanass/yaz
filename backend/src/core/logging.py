"""
Logging configuration for clinical audit trails and system monitoring
"""

import sys
import logging
from pathlib import Path
from loguru import logger
from datetime import datetime
import json

from .config import get_settings


class AuditFormatter:
    """Custom formatter for audit logs (HIPAA compliance)"""
    
    def format(self, record):
        """Format audit log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add extra fields if present
        if "extra" in record:
            log_entry.update(record["extra"])
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging():
    """Setup structured logging for clinical environment"""
    settings = get_settings()
    
    # Remove default logger
    logger.remove()
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Console logging (for development)
    if settings.debug:
        logger.add(
            sys.stderr,
            level=settings.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True
        )
    
    # File logging for audit trails
    logger.add(
        "logs/application.log",
        level="INFO",
        rotation="1 day",
        retention=f"{settings.audit_log_retention_days} days",
        compression="gzip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True  # Thread-safe logging
    )
    
    # Separate audit log for HIPAA compliance
    logger.add(
        "logs/audit.log",
        level="INFO",
        rotation="1 day",
        retention=f"{settings.audit_log_retention_days} days",
        compression="gzip",
        format=AuditFormatter().format,
        filter=lambda record: record["extra"].get("audit", False),
        enqueue=True
    )
    
    # Error logs
    logger.add(
        "logs/errors.log",
        level="ERROR",
        rotation="1 week",
        retention="1 year",
        compression="gzip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
        enqueue=True
    )
    
    # Performance logs
    logger.add(
        "logs/performance.log",
        level="INFO",
        rotation="1 day",
        retention="30 days",
        compression="gzip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: record["extra"].get("performance", False),
        enqueue=True
    )
    
    # Security logs
    logger.add(
        "logs/security.log",
        level="WARNING",
        rotation="1 day",
        retention=f"{settings.audit_log_retention_days} days",
        compression="gzip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message} | {extra}",
        filter=lambda record: record["extra"].get("security", False),
        enqueue=True
    )


# Logging utilities for different contexts
class ClinicalLogger:
    """Specialized logger for clinical operations"""
    
    @staticmethod
    def log_patient_access(user_id: str, patient_id: str, operation: str, details: dict = None):
        """Log patient data access for audit trail"""
        logger.bind(
            audit=True,
            user_id=user_id,
            patient_id=patient_id,
            operation=operation,
            details=details or {}
        ).info(f"Patient data access: {operation}")
    
    @staticmethod
    def log_decision_engine_use(user_id: str, engine: str, patient_id: str, result: dict):
        """Log decision engine usage"""
        logger.bind(
            audit=True,
            user_id=user_id,
            patient_id=patient_id,
            engine=engine,
            result=result
        ).info(f"Decision engine used: {engine}")
    
    @staticmethod
    def log_clinical_protocol_change(user_id: str, protocol_id: str, changes: dict):
        """Log clinical protocol modifications"""
        logger.bind(
            audit=True,
            user_id=user_id,
            protocol_id=protocol_id,
            changes=changes
        ).info(f"Clinical protocol modified: {protocol_id}")


class SecurityLogger:
    """Specialized logger for security events"""
    
    @staticmethod
    def log_authentication_attempt(user_id: str, success: bool, ip_address: str):
        """Log authentication attempts"""
        logger.bind(
            security=True,
            user_id=user_id,
            success=success,
            ip_address=ip_address
        ).warning(f"Authentication attempt: {'success' if success else 'failed'}")
    
    @staticmethod
    def log_authorization_failure(user_id: str, resource: str, action: str):
        """Log authorization failures"""
        logger.bind(
            security=True,
            user_id=user_id,
            resource=resource,
            action=action
        ).warning(f"Authorization failed: {action} on {resource}")
    
    @staticmethod
    def log_suspicious_activity(user_id: str, activity: str, details: dict):
        """Log suspicious security activity"""
        logger.bind(
            security=True,
            user_id=user_id,
            activity=activity,
            details=details
        ).error(f"Suspicious activity detected: {activity}")


class PerformanceLogger:
    """Specialized logger for performance monitoring"""
    
    @staticmethod
    def log_api_performance(endpoint: str, method: str, duration: float, status_code: int):
        """Log API performance metrics"""
        logger.bind(
            performance=True,
            endpoint=endpoint,
            method=method,
            duration=duration,
            status_code=status_code
        ).info(f"API call: {method} {endpoint} - {duration:.3f}s - {status_code}")
    
    @staticmethod
    def log_database_performance(query_type: str, duration: float, affected_rows: int = None):
        """Log database performance"""
        logger.bind(
            performance=True,
            query_type=query_type,
            duration=duration,
            affected_rows=affected_rows
        ).info(f"DB query: {query_type} - {duration:.3f}s")
    
    @staticmethod
    def log_decision_engine_performance(engine: str, duration: float, complexity: str):
        """Log decision engine performance"""
        logger.bind(
            performance=True,
            engine=engine,
            duration=duration,
            complexity=complexity
        ).info(f"Decision engine: {engine} - {duration:.3f}s - {complexity}")


# Export logger instances
clinical_logger = ClinicalLogger()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()
