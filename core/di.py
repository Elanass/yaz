"""
Simple dependency injection container for the platform
"""
from typing import Any, Dict, Callable, TypeVar, Type
import inspect

T = TypeVar('T')

class DIScope:
    """Dependency injection scopes"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"

class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[Type, Dict[str, Any]] = {}
    
    def register_singleton(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a singleton service"""
        self._services[service_type] = {
            'factory': factory,
            'scope': DIScope.SINGLETON,
            'instance': None
        }
    
    def register_transient(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a transient service"""
        self._services[service_type] = {
            'factory': factory,
            'scope': DIScope.TRANSIENT,
            'instance': None
        }
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance"""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")
        
        service_info = self._services[service_type]
        
        if service_info['scope'] == DIScope.SINGLETON:
            if service_info['instance'] is None:
                service_info['instance'] = service_info['factory']()
            return service_info['instance']
        else:
            return service_info['factory']()

# Global container instance
container = DIContainer()
