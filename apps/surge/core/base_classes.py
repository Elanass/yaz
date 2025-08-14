"""Base Classes for DRY Refactoring
Common patterns extracted from the surgify codebase.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


# Get logger
logger = logging.getLogger(__name__)


class BaseAPIRouter(ABC):
    """Base router with common functionality."""

    def __init__(self, prefix: str = "", tags: list[str] | None = None) -> None:
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self._setup_routes()

    @abstractmethod
    def _setup_routes(self):
        """Setup routes specific to this router."""

    def get_router(self) -> APIRouter:
        """Get the FastAPI router instance."""
        return self.router


class BaseService(ABC):
    """Base service with standard CRUD operations."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.version = "2.0.0"
        self._initialize()

    @abstractmethod
    def _initialize(self):
        """Initialize service-specific components."""

    def get_health_status(self) -> dict[str, Any]:
        """Common health check implementation."""
        return {
            "status": "healthy",
            "service": self.__class__.__name__,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
        }


class BaseModel(BaseModel):
    """Base model with common fields and methods."""

    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    version: str = "2.0.0"

    class Config:
        validate_assignment = True
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class BaseAnalyticsEngine(BaseService):
    """Base analytics engine with common analytics methods."""

    def _initialize(self) -> None:
        """Initialize analytics components."""
        self.metrics = {}
        self.insights = []

    def calculate_metrics(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate common metrics."""
        total_records = len(data)
        return {
            "total_records": total_records,
            "processed_at": datetime.now().isoformat(),
            "success_rate": 1.0 if total_records > 0 else 0.0,
        }

    @abstractmethod
    def generate_insights(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate domain-specific insights."""


class BaseUIComponent:
    """Base JavaScript UI Component pattern (for documentation)."""

    def __init__(
        self, container_id: str, options: dict[str, Any] | None = None
    ) -> None:
        """Common initialization pattern for UI components.

        Args:
            container_id: DOM element ID
            options: Component configuration
        """
        self.container_id = container_id
        self.options = options or {}
        self.data = {}
        self.initialized = False

    def render(self) -> str:
        """Render component HTML."""

    def attach_event_listeners(self) -> None:
        """Attach event listeners."""

    def destroy(self) -> None:
        """Cleanup component."""


class StandardErrorHandler:
    """Standard error handling patterns."""

    @staticmethod
    def handle_api_error(error: Exception) -> HTTPException:
        """Convert various exceptions to HTTP exceptions."""
        if isinstance(error, ValueError):
            return HTTPException(status_code=400, detail=str(error))
        if isinstance(error, FileNotFoundError):
            return HTTPException(status_code=404, detail="Resource not found")
        logger.error(f"Unexpected error: {error}")
        return HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
        """Standard error logging."""
        context = context or {}
        logger.error(
            f"Error in {context.get('function', 'unknown')}: {error}", extra=context
        )


class ConfigurationManager:
    """Centralized configuration management."""

    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    def load_from_dict(self, config: dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        self._config.update(config)


class CacheManager:
    """Base caching functionality."""

    def __init__(self, default_ttl: int = 300) -> None:
        self.default_ttl = default_ttl
        self._cache = {}

    def get(self, key: str) -> Any | None:
        """Get cached value."""
        if key in self._cache:
            item = self._cache[key]
            if datetime.now() < item["expires"]:
                return item["value"]
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set cached value."""
        expires = datetime.now().timestamp() + (ttl or self.default_ttl)
        self._cache[key] = {"value": value, "expires": datetime.fromtimestamp(expires)}

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()


# Common response schemas
class StandardResponse(BaseModel):
    """Standard API response format."""

    success: bool = True
    message: str = "Operation completed successfully"
    data: dict[str, Any] | None = None
    timestamp: datetime = datetime.now()


class PaginatedResponse(BaseModel):
    """Standard paginated response format."""

    items: list[dict[str, Any]]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def create(cls, items: list[dict[str, Any]], total: int, page: int, per_page: int):
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=(total + per_page - 1) // per_page,
        )


class HealthCheckResponse(BaseModel):
    """Standard health check response."""

    status: str
    service: str
    version: str
    timestamp: datetime
    details: dict[str, Any] | None = None
