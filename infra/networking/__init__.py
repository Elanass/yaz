"""Advanced Networking Module for Yaz Healthcare Platform
Supports local, P2P, BLE mesh, and multi-VM collaboration.
"""

from .ble_mesh import BLEMeshManager
from .collaboration_engine import CollaborationEngine
from .fallback_manager import NetworkFallbackManager
from .local_network import LocalNetworkManager
from .multi_vm import MultiVMManager
from .network_monitor import NetworkMonitor
from .p2p_network import P2PNetworkManager
from .security_manager import SecurityManager
from .sync_engine import SyncEngine


__all__ = [
    "BLEMeshManager",
    "CollaborationEngine",
    "LocalNetworkManager",
    "MultiVMManager",
    "NetworkFallbackManager",
    "NetworkMonitor",
    "P2PNetworkManager",
    "SecurityManager",
    "SyncEngine",
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "YAZ Healthcare Platform Team"
__description__ = (
    "Advanced networking capabilities for distributed healthcare collaboration"
)
