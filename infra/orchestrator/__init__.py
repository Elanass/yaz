"""
YAZ Orchestration System

A lean, scriptable orchestration system with Incus primary and Multipass fallback
for multi-VM and multi-container environments.
"""
from .health import get_provider, health_check, switch_provider
from .providers.base import BaseProvider, Instance, InstanceStatus
from .providers.incus import IncusProvider
from .providers.multipass import MultipassProvider
from .utils import (InstanceNotFoundError, ProviderError,
                    ProviderUnavailableError)

__version__ = "1.0.0"
__all__ = [
    "get_provider",
    "health_check",
    "switch_provider",
    "BaseProvider",
    "Instance",
    "InstanceStatus",
    "IncusProvider",
    "MultipassProvider",
    "ProviderError",
    "InstanceNotFoundError",
    "ProviderUnavailableError",
]
