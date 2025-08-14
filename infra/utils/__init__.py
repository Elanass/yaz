"""Utility modules for the Surge platform."""

from src.shared.core.cache import cache_response

from .exceptions import (
                         ConfigurationError,
                         DataIntegrityError,
                         ExternalServiceError,
                         NotFoundError,
                         PermissionError,
                         RateLimitError,
                         SurgeException,
                         ValidationError,
)
from .pagination import Page, PageParams
from .redis_client import close_redis_client, get_redis_client


__all__ = [
    "ConfigurationError",
    "DataIntegrityError",
    "ExternalServiceError",
    "NotFoundError",
    "Page",
    "PageParams",
    "PermissionError",
    "RateLimitError",
    "SurgeException",
    "ValidationError",
    "cache_response",
    "close_redis_client",
    "get_redis_client",
]
