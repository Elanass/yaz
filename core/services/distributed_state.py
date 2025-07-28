"""
Distributed State Service for Real-time Synchronization

This service provides a Python interface to Gun.js for real-time distributed
state management, enabling offline-first data synchronization with conflict resolution.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable, Awaitable

import websockets
from fastapi import WebSocket

from core.config.settings import get_feature_config
from core.services.base import BaseService


class DistributedState(BaseService):
    """
    Distributed state management service using Gun.js
    
    This service provides a Python interface to Gun.js, allowing real-time
    data synchronization across clients with conflict resolution.
    """
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("sync")
        self.relay_url = self.config.get("gun_relay_url", "ws://localhost:8765")
        self.connection = None
        self.connected = False
        self.handlers = {}
        self.subscription_ids = {}
        
        # Initialize background task for processing messages
        self.message_queue = asyncio.Queue()
        self.background_task = None
    
    async def connect(self):
        """Connect to the Gun.js relay server"""
        if self.connected:
            return
            
        try:
            self.connection = await websockets.connect(self.relay_url)
            self.connected = True
            self.logger.info(f"Connected to Gun.js relay at {self.relay_url}")
            
            # Start background processing
            self.background_task = asyncio.create_task(self._process_messages())
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Gun.js relay: {str(e)}")
            self.connected = False
            raise ConnectionError(f"Could not connect to Gun.js relay: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from the Gun.js relay server"""
        if not self.connected:
            return
            
        # Cancel background task
        if self.background_task:
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
            
        # Close connection
        if self.connection:
            await self.connection.close()
            self.connection = None
            
        self.connected = False
        self.logger.info("Disconnected from Gun.js relay")
    
    async def _process_messages(self):
        """Background task to process incoming messages"""
        while True:
            try:
                # Receive message
                message = await self.connection.recv()
                data = json.loads(message)
                
                # Process message
                await self._handle_message(data)
                
            except websockets.ConnectionClosed:
                self.logger.warning("Connection to Gun.js relay closed")
                self.connected = False
                break
                
            except Exception as e:
                self.logger.error(f"Error processing Gun.js message: {str(e)}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle an incoming message from Gun.js"""
        msg_type = data.get("type")
        path = data.get("path")
        subscription_id = data.get("subscription_id")
        
        # Call appropriate handler
        if subscription_id in self.handlers:
            handler = self.handlers[subscription_id]
            await handler(data.get("data"), path)
    
    async def put(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Put data at a specific path
        
        Args:
            path: The path in the distributed graph
            data: The data to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            await self.connect()
            
        message = {
            "type": "put",
            "path": path,
            "data": data
        }
        
        try:
            await self.connection.send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Failed to put data: {str(e)}")
            return False
    
    async def get(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get data from a specific path
        
        Args:
            path: The path in the distributed graph
            
        Returns:
            The data at the path, or None if not found
        """
        if not self.connected:
            await self.connect()
            
        message = {
            "type": "get",
            "path": path
        }
        
        try:
            await self.connection.send(json.dumps(message))
            
            # Wait for response
            response = await self.connection.recv()
            data = json.loads(response)
            
            if data.get("type") == "get_response" and data.get("path") == path:
                return data.get("data")
                
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get data: {str(e)}")
            return None
    
    async def subscribe(
        self,
        path: str,
        handler: Callable[[Dict[str, Any], str], Awaitable[None]]
    ) -> str:
        """
        Subscribe to changes at a specific path
        
        Args:
            path: The path in the distributed graph
            handler: The callback function to handle changes
            
        Returns:
            Subscription ID
        """
        if not self.connected:
            await self.connect()
            
        # Generate subscription ID
        import uuid
        subscription_id = str(uuid.uuid4())
        
        # Register handler
        self.handlers[subscription_id] = handler
        
        # Send subscription request
        message = {
            "type": "subscribe",
            "path": path,
            "subscription_id": subscription_id
        }
        
        try:
            await self.connection.send(json.dumps(message))
            self.subscription_ids[path] = subscription_id
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe: {str(e)}")
            del self.handlers[subscription_id]
            raise
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from changes
        
        Args:
            subscription_id: The subscription ID to unsubscribe
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            return False
            
        # Send unsubscribe request
        message = {
            "type": "unsubscribe",
            "subscription_id": subscription_id
        }
        
        try:
            await self.connection.send(json.dumps(message))
            
            # Remove handler
            if subscription_id in self.handlers:
                del self.handlers[subscription_id]
                
            # Remove from subscription_ids
            for path, sub_id in list(self.subscription_ids.items()):
                if sub_id == subscription_id:
                    del self.subscription_ids[path]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe: {str(e)}")
            return False
