"""Shared Exception Classes
Common exceptions that can be used across all apps.
"""

from typing import Any


class YazException(Exception):
    """Base exception for all Yaz platform apps."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class ValidationError(YazException):
    """Raised when data validation fails."""

    def __init__(self, message: str, field: str | None = None, **kwargs) -> None:
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class NotFoundError(YazException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str, **kwargs) -> None:
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, code="NOT_FOUND", **kwargs)
        self.details.update({"resource": resource, "identifier": identifier})


class PermissionError(YazException):
    """Raised when user lacks required permissions."""

    def __init__(self, action: str, resource: str | None = None, **kwargs) -> None:
        message = f"Permission denied for action '{action}'"
        if resource:
            message += f" on resource '{resource}'"
        super().__init__(message, code="PERMISSION_DENIED", **kwargs)
        self.details.update({"action": action, "resource": resource})


class ConfigurationError(YazException):
    """Raised when there's a configuration issue."""

    def __init__(self, setting: str, **kwargs) -> None:
        message = f"Configuration error with setting '{setting}'"
        super().__init__(message, code="CONFIGURATION_ERROR", **kwargs)
        self.details["setting"] = setting


class ExternalServiceError(YazException):
    """Raised when an external service fails."""

    def __init__(self, service: str, operation: str, **kwargs) -> None:
        message = f"External service '{service}' failed during '{operation}'"
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", **kwargs)
        self.details.update({"service": service, "operation": operation})


class RateLimitError(YazException):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit: int, window: str, **kwargs) -> None:
        message = f"Rate limit exceeded: {limit} requests per {window}"
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", **kwargs)
        self.details.update({"limit": limit, "window": window})


class MaintenanceError(YazException):
    """Raised when system is in maintenance mode."""

    def __init__(self, **kwargs) -> None:
        message = "System is currently under maintenance"
        super().__init__(message, code="MAINTENANCE_MODE", **kwargs)
