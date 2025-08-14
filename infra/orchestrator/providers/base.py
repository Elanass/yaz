"""
Base provider interface for orchestration systems.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class InstanceStatus(Enum):
    """Instance status enum."""

    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    FROZEN = "frozen"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class Instance:
    """Instance representation."""

    name: str
    status: InstanceStatus
    ip_address: Optional[str] = None
    memory_usage: int = 0
    cpu_usage: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseProvider(ABC):
    """Abstract base provider for orchestration."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available on the system."""
        pass

    @abstractmethod
    def ensure_host(self) -> bool:
        """Ensure host system is properly configured."""
        pass

    @abstractmethod
    def create_instance(self, name: str, config: Dict[str, Any]) -> Instance:
        """Create a new instance."""
        pass

    @abstractmethod
    def start_instance(self, name: str) -> bool:
        """Start an instance."""
        pass

    @abstractmethod
    def stop_instance(self, name: str) -> bool:
        """Stop an instance."""
        pass

    @abstractmethod
    def destroy_instance(self, name: str) -> bool:
        """Destroy an instance."""
        pass

    @abstractmethod
    def list_instances(self) -> List[Instance]:
        """List all instances."""
        pass

    @abstractmethod
    def get_instance(self, name: str) -> Optional[Instance]:
        """Get instance details."""
        pass

    @abstractmethod
    def exec_command(self, name: str, command: str) -> str:
        """Execute command in instance."""
        pass

    @abstractmethod
    def push_file(self, name: str, local_path: Path, remote_path: str) -> bool:
        """Push file to instance."""
        pass

    @abstractmethod
    def pull_file(self, name: str, remote_path: str, local_path: Path) -> bool:
        """Pull file from instance."""
        pass

    @abstractmethod
    def snapshot_instance(self, name: str, snapshot_name: str) -> bool:
        """Create instance snapshot."""
        pass

    @abstractmethod
    def export_instance(self, name: str, export_path: Path) -> bool:
        """Export instance to file."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on provider."""
        pass
