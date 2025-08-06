"""
Common Utility Functions
Extracted from duplicate code patterns across the codebase
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def format_date(date_input: Union[str, datetime, None]) -> str:
    """Standardize date formatting across the application"""
    if not date_input:
        return ""

    if isinstance(date_input, str):
        try:
            date_input = datetime.fromisoformat(date_input.replace("Z", "+00:00"))
        except ValueError:
            return date_input

    return date_input.strftime("%Y-%m-%d %H:%M:%S")


def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
    """Format percentage values consistently"""
    if value is None:
        return "0.0%"
    return f"{float(value):.{decimals}f}%"


def format_currency(amount: Union[int, float], currency: str = "$") -> str:
    """Format currency values consistently"""
    if amount is None:
        return f"{currency}0.00"
    return f"{currency}{amount:,.2f}"


def format_duration(minutes: Union[int, float]) -> str:
    """Format duration in minutes to human-readable format"""
    if not minutes:
        return "0 min"

    hours = int(minutes // 60)
    mins = int(minutes % 60)

    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins} min"


def safe_get(dictionary: Dict[str, Any], *keys, default=None) -> Any:
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default
    return dictionary


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate consistent IDs across the application"""
    timestamp = str(int(datetime.now().timestamp() * 1000))
    hash_obj = hashlib.md5(timestamp.encode())
    hash_id = hash_obj.hexdigest()[:length]
    return f"{prefix}_{hash_id}" if prefix else hash_id


def validate_api_response(response_data: Dict[str, Any]) -> bool:
    """Validate API response structure"""
    required_fields = ["success", "message", "timestamp"]
    return all(field in response_data for field in required_fields)


def paginate_results(
    items: List[Dict[str, Any]], page: int = 1, per_page: int = 20
) -> Dict[str, Any]:
    """Paginate results with consistent structure"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "items": items[start:end],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
            "has_next": end < total,
            "has_prev": page > 1,
        },
    }


def calculate_statistics(data: List[Union[int, float]]) -> Dict[str, float]:
    """Calculate common statistics"""
    if not data:
        return {"count": 0, "mean": 0, "min": 0, "max": 0}

    return {
        "count": len(data),
        "mean": sum(data) / len(data),
        "min": min(data),
        "max": max(data),
        "sum": sum(data),
    }


def get_auth_token(request=None, headers: Dict[str, str] = None) -> Optional[str]:
    """Extract auth token from request or headers"""
    auth_header = None

    if request and hasattr(request, "headers"):
        auth_header = request.headers.get("Authorization")
    elif headers:
        auth_header = headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


def create_api_response(
    success: bool = True,
    message: str = "Operation completed successfully",
    data: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> Dict[str, Any]:
    """Create standardized API responses"""
    return {
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "status_code": status_code,
    }


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2**attempt))
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        import time

                        time.sleep(delay * (2**attempt))
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )
            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def log_performance(func):
    """Decorator to log function performance"""

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations"""
    import re

    # Remove or replace unsafe characters
    safe_filename = re.sub(r"[^\w\-_.]", "_", filename)
    return safe_filename[:255]  # Limit length


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def filter_dict_by_keys(
    data: Dict[str, Any], allowed_keys: List[str]
) -> Dict[str, Any]:
    """Filter dictionary to only include allowed keys"""
    return {key: value for key, value in data.items() if key in allowed_keys}


def batch_process(items: List[Any], batch_size: int = 100):
    """Process items in batches"""
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]
