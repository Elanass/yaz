"""
Core Utilities
Shared utility functions and helpers
"""

import hashlib
import json
import logging
import re
import uuid
import csv
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import structlog

logger = structlog.get_logger(__name__)


class DateUtils:
    """Date and time utilities"""
    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime"""
        return datetime.utcnow()
    
    @staticmethod
    def format_iso(dt: datetime) -> str:
        """Format datetime as ISO string"""
        return dt.isoformat() + "Z"
    
    @staticmethod
    def parse_iso(iso_string: str) -> datetime:
        """Parse ISO datetime string"""
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    
    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """Add hours to datetime"""
        return dt + timedelta(hours=hours)
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Add days to datetime"""
        return dt + timedelta(days=days)


class StringUtils:
    """String manipulation utilities"""
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', '-', text).strip('-')
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def mask_sensitive(text: str, visible_chars: int = 4) -> str:
        """Mask sensitive information"""
        if len(text) <= visible_chars:
            return "*" * len(text)
        return text[:visible_chars] + "*" * (len(text) - visible_chars)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text"""
        return re.sub(r'\s+', ' ', text.strip())


class ValidationUtils:
    """Data validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Validate UUID string"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_clinical_value(
        value: Any, 
        value_type: str, 
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> List[str]:
        """Validate clinical values"""
        errors = []
        
        if value_type == "age":
            if not isinstance(value, (int, float)) or value < 0 or value > 150:
                errors.append("Age must be between 0 and 150")
        
        elif value_type == "bmi":
            if not isinstance(value, (int, float)) or value < 10 or value > 60:
                errors.append("BMI must be between 10 and 60")
        
        elif value_type == "performance_status":
            if not isinstance(value, int) or value < 0 or value > 4:
                errors.append("Performance status must be between 0 and 4")
        
        elif value_type == "confidence":
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                errors.append("Confidence must be between 0 and 1")
        
        elif value_type == "percentage":
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                errors.append("Percentage must be between 0 and 100")
        
        # Custom range validation
        if min_val is not None and isinstance(value, (int, float)) and value < min_val:
            errors.append(f"Value must be at least {min_val}")
        
        if max_val is not None and isinstance(value, (int, float)) and value > max_val:
            errors.append(f"Value must be at most {max_val}")
        
        return errors


class HashUtils:
    """Hashing and encryption utilities"""
    
    @staticmethod
    def md5_hash(text: str) -> str:
        """Generate MD5 hash"""
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def sha256_hash(text: str) -> str:
        """Generate SHA256 hash"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def generate_cache_key(*args: Any) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session ID"""
        return str(uuid.uuid4()).replace('-', '')


class DataUtils:
    """Data manipulation utilities"""
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        result = {}
        for key, value in d.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(DataUtils.flatten_dict(value, new_key))
            else:
                result[new_key] = value
        return result
    
    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    @staticmethod
    def remove_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from dictionary"""
        return {k: v for k, v in d.items() if v is not None}
    
    @staticmethod
    def safe_get(d: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Safely get nested dictionary value"""
        keys = path.split('.')
        value = d
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default


class ClinicalUtils:
    """Clinical domain utilities"""
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """Calculate BMI from weight and height"""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    @staticmethod
    def categorize_bmi(bmi: float) -> str:
        """Categorize BMI value"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"
    
    @staticmethod
    def calculate_age(birth_date: datetime) -> int:
        """Calculate age from birth date"""
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    @staticmethod
    def format_tnm_stage(t: str, n: str, m: str) -> str:
        """Format TNM staging"""
        return f"{t.upper()}{n.upper()}{m.upper()}"
    
    @staticmethod
    def confidence_to_level(score: float) -> str:
        """Convert confidence score to descriptive level"""
        if score < 0.3:
            return "Very Low"
        elif score < 0.5:
            return "Low"
        elif score < 0.7:
            return "Moderate"
        elif score < 0.9:
            return "High"
        else:
            return "Very High"


class LoggingUtils:
    """Logging utilities"""
    
    @staticmethod
    def setup_structured_logging(level: str = "INFO") -> None:
        """Setup structured logging with structlog"""
        
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
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logging.basicConfig(
            format="%(message)s",
            level=getattr(logging, level.upper()),
        )
    
    @staticmethod
    def create_audit_logger(name: str) -> logging.Logger:
        """Create dedicated audit logger"""
        logger = logging.getLogger(f"audit.{name}")
        handler = logging.FileHandler("logs/audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger


def load_csv(file_path: str) -> List[Dict[str, str]]:
    """Load CSV file into a list of dictionaries"""
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        logger.error(f"Failed to load CSV file: {file_path}. Error: {e}")
        raise


def log_action(user_id: str, action: str, details: Dict[str, str]):
    """Log user actions for audit trails"""
    logger.info(f"User {user_id} performed action: {action} with details: {details}")


def handle_error(error: Exception):
    """Handle errors gracefully"""
    logger.error(f"Error occurred: {error}")
    return {"success": False, "error": str(error)}
