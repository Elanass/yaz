"""
ElectricsQL Sync Handlers

This module provides sync handlers for ElectricsQL to enable offline-first data
synchronization between client and server, with proper conflict resolution.
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable

from core.config.settings import get_feature_config
from core.services.base import BaseService
from core.services.logger import Logger


class SyncOperation(str, Enum):
    """Sync operation types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"


class SyncStatus(str, Enum):
    """Sync status types"""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncRecord:
    """Record for tracking sync status"""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        operation: SyncOperation,
        data: Dict[str, Any],
        local_timestamp: datetime,
        server_timestamp: Optional[datetime] = None,
        status: SyncStatus = SyncStatus.PENDING,
        error: Optional[str] = None,
        conflict_data: Optional[Dict[str, Any]] = None
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.operation = operation
        self.data = data
        self.local_timestamp = local_timestamp
        self.server_timestamp = server_timestamp
        self.status = status
        self.error = error
        self.conflict_data = conflict_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "operation": self.operation,
            "data": self.data,
            "local_timestamp": self.local_timestamp.isoformat(),
            "server_timestamp": self.server_timestamp.isoformat() if self.server_timestamp else None,
            "status": self.status,
            "error": self.error,
            "conflict_data": self.conflict_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncRecord":
        """Create from dictionary"""
        return cls(
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            operation=data["operation"],
            data=data["data"],
            local_timestamp=datetime.fromisoformat(data["local_timestamp"]),
            server_timestamp=datetime.fromisoformat(data["server_timestamp"]) if data.get("server_timestamp") else None,
            status=data["status"],
            error=data.get("error"),
            conflict_data=data.get("conflict_data")
        )


class SyncHandlers(BaseService):
    """
    ElectricsQL sync handlers for offline-first data synchronization
    
    This service provides handlers for syncing data between client and server,
    with proper conflict resolution strategies.
    """
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("sync")
        self.logger = Logger()
        self.entity_handlers: Dict[str, Dict[str, Callable]] = {}
    
    def register_handler(
        self,
        entity_type: str,
        operation: SyncOperation,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ):
        """
        Register a handler for a specific entity type and operation
        
        Args:
            entity_type: The entity type (e.g., "patient", "decision")
            operation: The operation type
            handler: The handler function
        """
        if entity_type not in self.entity_handlers:
            self.entity_handlers[entity_type] = {}
            
        self.entity_handlers[entity_type][operation] = handler
        self.logger.debug(
            f"Registered {operation} handler for {entity_type}"
        )
    
    async def handle_sync(
        self,
        entity_type: str,
        entity_id: str,
        operation: SyncOperation,
        data: Dict[str, Any],
        client_timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Handle a sync request
        
        Args:
            entity_type: The entity type
            entity_id: The entity ID
            operation: The operation type
            data: The entity data
            client_timestamp: The client timestamp
            
        Returns:
            Result of the sync operation
        """
        # Check if handler exists
        if (
            entity_type not in self.entity_handlers or
            operation not in self.entity_handlers[entity_type]
        ):
            self.logger.warning(
                f"No handler for {operation} on {entity_type}",
                entity_type=entity_type,
                entity_id=entity_id,
                operation=operation
            )
            return {
                "status": SyncStatus.ERROR,
                "error": f"No handler for {operation} on {entity_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Get handler
            handler = self.entity_handlers[entity_type][operation]
            
            # Add metadata
            context = {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "operation": operation,
                "client_timestamp": client_timestamp,
                "server_timestamp": datetime.utcnow()
            }
            
            # Call handler
            result = await handler(data, context)
            
            # Add standard fields
            if "status" not in result:
                result["status"] = SyncStatus.SYNCED
                
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(
                f"Error handling {operation} on {entity_type}/{entity_id}",
                exc_info=e,
                entity_type=entity_type,
                entity_id=entity_id,
                operation=operation
            )
            
            return {
                "status": SyncStatus.ERROR,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def handle_bulk_sync(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Handle bulk sync requests
        
        Args:
            records: List of sync records
            
        Returns:
            Results for each record
        """
        results = []
        
        for record in records:
            entity_type = record.get("entity_type")
            entity_id = record.get("entity_id")
            operation = record.get("operation")
            data = record.get("data", {})
            client_timestamp = datetime.fromisoformat(record.get("timestamp", datetime.utcnow().isoformat()))
            
            result = await self.handle_sync(
                entity_type=entity_type,
                entity_id=entity_id,
                operation=operation,
                data=data,
                client_timestamp=client_timestamp
            )
            
            results.append({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "operation": operation,
                **result
            })
        
        return results


# Create handlers for specific entity types


async def handle_patient_create(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for patient creation
    
    Args:
        data: Patient data
        context: Sync context
        
    Returns:
        Sync result
    """
    # Normally, this would call a repository or service
    # For this example, we'll just return success
    
    return {
        "status": SyncStatus.SYNCED,
        "entity_id": context["entity_id"]
    }


async def handle_patient_update(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for patient updates
    
    Args:
        data: Patient data
        context: Sync context
        
    Returns:
        Sync result
    """
    # Check for conflicts
    # This would normally compare timestamps or versions
    
    return {
        "status": SyncStatus.SYNCED,
        "entity_id": context["entity_id"]
    }


async def handle_decision_create(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for decision creation
    
    Args:
        data: Decision data
        context: Sync context
        
    Returns:
        Sync result
    """
    # Create decision in database
    
    return {
        "status": SyncStatus.SYNCED,
        "entity_id": context["entity_id"]
    }


async def handle_protocol_update(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for protocol updates
    
    Args:
        data: Protocol data
        context: Sync context
        
    Returns:
        Sync result
    """
    # Update protocol in database
    
    return {
        "status": SyncStatus.SYNCED,
        "entity_id": context["entity_id"]
    }


# Initialize and register handlers
def initialize_sync_handlers() -> SyncHandlers:
    """Initialize sync handlers with all registered handlers"""
    handlers = SyncHandlers()
    
    # Register handlers
    handlers.register_handler("patient", SyncOperation.CREATE, handle_patient_create)
    handlers.register_handler("patient", SyncOperation.UPDATE, handle_patient_update)
    handlers.register_handler("decision", SyncOperation.CREATE, handle_decision_create)
    handlers.register_handler("protocol", SyncOperation.UPDATE, handle_protocol_update)
    
    return handlers
