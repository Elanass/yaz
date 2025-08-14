"""Unified utility services for the platform."""

import logging
from abc import ABC, abstractmethod
from typing import Any


class NotificationHandler(ABC):
    """Abstract notification handler."""

    @abstractmethod
    async def handle(self, message: str, context: dict[str, Any] | None = None):
        """Handle a notification."""


class LogNotificationHandler(NotificationHandler):
    """Log-based notification handler."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def handle(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Handle notification by logging."""
        if context:
            self.logger.info(f"{message} - Context: {context}")
        else:
            self.logger.info(message)


class NotificationService:
    """Service for sending notifications."""

    def __init__(self) -> None:
        self.handlers = []

    def add_handler(self, handler: NotificationHandler) -> None:
        """Add a notification handler."""
        self.handlers.append(handler)

    async def notify(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Send a notification to all handlers."""
        for handler in self.handlers:
            await handler.handle(message, context)


class CacheStrategy(ABC):
    """Abstract cache strategy."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None):
        """Set value in cache."""

    @abstractmethod
    async def delete(self, key: str):
        """Delete value from cache."""


class MemoryCacheStrategy(CacheStrategy):
    """In-memory cache strategy."""

    def __init__(self) -> None:
        self.cache: dict[str, Any] = {}

    async def get(self, key: str) -> Any | None:
        """Get value from memory cache."""
        return self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in memory cache."""
        self.cache[key] = value

    async def delete(self, key: str) -> None:
        """Delete value from memory cache."""
        self.cache.pop(key, None)


class CacheService:
    """Cache service with pluggable strategies."""

    def __init__(self, strategy: CacheStrategy) -> None:
        self.strategy = strategy

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        return await self.strategy.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None):
        """Set value in cache."""
        return await self.strategy.set(key, value, ttl)

    async def delete(self, key: str):
        """Delete value from cache."""
        return await self.strategy.delete(key)
