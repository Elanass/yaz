"""
Service Registry and Dependency Injection Container
Provides a centralized way to manage application dependencies
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class ServiceRegistry:
    """Service registry for dependency injection"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)

    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """Register a singleton instance"""
        key = self._get_key(service_type)
        self._singletons[key] = instance
        self._logger.debug(f"Registered singleton: {key}")

    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function"""
        key = self._get_key(service_type)
        self._factories[key] = factory
        self._logger.debug(f"Registered factory: {key}")

    def register_transient(
        self, service_type: Type[T], implementation: Type[T]
    ) -> None:
        """Register a transient service"""
        key = self._get_key(service_type)
        self._services[key] = implementation
        self._logger.debug(f"Registered transient: {key}")

    def get(self, service_type: Type[T]) -> T:
        """Get a service instance"""
        key = self._get_key(service_type)

        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]

        # Check factories
        if key in self._factories:
            instance = self._factories[key]()
            # Cache as singleton if it's a factory
            self._singletons[key] = instance
            return instance

        # Check transient services
        if key in self._services:
            return self._services[key]()

        raise ValueError(f"Service not registered: {service_type}")

    def get_optional(self, service_type: Type[T]) -> Optional[T]:
        """Get a service instance if registered, otherwise None"""
        try:
            return self.get(service_type)
        except ValueError:
            return None

    def is_registered(self, service_type: Type[T]) -> bool:
        """Check if a service is registered"""
        key = self._get_key(service_type)
        return (
            key in self._singletons or key in self._factories or key in self._services
        )

    def _get_key(self, service_type: Type) -> str:
        """Get a string key for a service type"""
        return f"{service_type.__module__}.{service_type.__qualname__}"


# Global service registry
_registry = ServiceRegistry()


def get_service_registry() -> ServiceRegistry:
    """Get the global service registry"""
    return _registry


def register_singleton(service_type: Type[T], instance: T) -> None:
    """Register a singleton service"""
    _registry.register_singleton(service_type, instance)


def register_factory(service_type: Type[T], factory: Callable[[], T]) -> None:
    """Register a factory function"""
    _registry.register_factory(service_type, factory)


def register_transient(service_type: Type[T], implementation: Type[T]) -> None:
    """Register a transient service"""
    _registry.register_transient(service_type, implementation)


def get_service(service_type: Type[T]) -> T:
    """Get a service instance"""
    return _registry.get(service_type)


def get_optional_service(service_type: Type[T]) -> Optional[T]:
    """Get a service instance if registered"""
    return _registry.get_optional(service_type)


# Service interface base class
class IService(ABC):
    """Base interface for all services"""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources"""
        pass
