"""Custom exceptions for the Surgify platform."""

from typing import Any


class SurgeException(Exception):
    """Base exception for Surgify platform."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ValidationError(SurgeException):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
    ) -> None:
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class NotFoundError(SurgeException):
    """Raised when a resource is not found."""

    def __init__(self, message: str, resource_type: str | None = None) -> None:
        super().__init__(message, "NOT_FOUND")
        self.resource_type = resource_type


class PermissionError(SurgeException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str, required_permission: str | None = None) -> None:
        super().__init__(message, "PERMISSION_DENIED")
        self.required_permission = required_permission


class ConfigurationError(SurgeException):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str, setting: str | None = None) -> None:
        super().__init__(message, "CONFIGURATION_ERROR")
        self.setting = setting


class ExternalServiceError(SurgeException):
    """Raised when an external service fails."""

    def __init__(
        self,
        message: str,
        service_name: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name
        self.status_code = status_code


class RateLimitError(SurgeException):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class DataIntegrityError(SurgeException):
    """Raised when data integrity constraints are violated."""

    def __init__(self, message: str, constraint: str | None = None) -> None:
        super().__init__(message, "DATA_INTEGRITY_ERROR")
        self.constraint = constraint
