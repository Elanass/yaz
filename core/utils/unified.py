"""
Unified utility services for the platform
"""
import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

class NotificationHandler(ABC):
    """Abstract notification handler"""
    
    @abstractmethod
    async def handle(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Handle a notification"""
        pass

class LogNotificationHandler(NotificationHandler):
    """Log-based notification handler"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    async def handle(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Handle notification by logging"""
        if context:
            self.logger.info(f"{message} - Context: {context}")
        else:
            self.logger.info(message)

class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        self.handlers = []
    
    def add_handler(self, handler: NotificationHandler):
        """Add a notification handler"""
        self.handlers.append(handler)
    
    async def notify(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Send a notification to all handlers"""
        for handler in self.handlers:
            await handler.handle(message, context)

class CacheStrategy(ABC):
    """Abstract cache strategy"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        """Delete value from cache"""
        pass

class MemoryCacheStrategy(CacheStrategy):
    """In-memory cache strategy"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in memory cache"""
        self.cache[key] = value
    
    async def delete(self, key: str):
        """Delete value from memory cache"""
        self.cache.pop(key, None)

class CacheService:
    """Cache service with pluggable strategies"""
    
    def __init__(self, strategy: CacheStrategy):
        self.strategy = strategy
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return await self.strategy.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        return await self.strategy.set(key, value, ttl)
    
    async def delete(self, key: str):
        """Delete value from cache"""
        return await self.strategy.delete(key)
