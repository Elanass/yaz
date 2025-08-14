"""WebSocket Manager for Surge Platform
Handles real-time connections and messaging.
"""

import json
import logging
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time communication."""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self.connection_groups: dict[str, set[str]] = {}
        self.user_connections: dict[str, str] = {}  # user_id -> connection_id

    async def connect(
        self, websocket: WebSocket, connection_id: str, user_id: str | None = None
    ) -> bool:
        """Accept a WebSocket connection."""
        try:
            await websocket.accept()
            self.active_connections[connection_id] = websocket

            if user_id:
                self.user_connections[user_id] = connection_id

            logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")

            # Send welcome message
            await self.send_personal_message(
                connection_id,
                {
                    "type": "connection_established",
                    "connection_id": connection_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to connect WebSocket {connection_id}: {e}")
            return False

    def disconnect(self, connection_id: str) -> None:
        """Disconnect a WebSocket."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from user mapping
        user_id = None
        for uid, cid in self.user_connections.items():
            if cid == connection_id:
                user_id = uid
                break

        if user_id:
            del self.user_connections[user_id]

        # Remove from groups
        for connections in self.connection_groups.values():
            connections.discard(connection_id)

        logger.info(f"WebSocket disconnected: {connection_id} (user: {user_id})")

    async def send_personal_message(self, connection_id: str, message: Any) -> None:
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                if isinstance(message, dict):
                    await websocket.send_text(json.dumps(message))
                else:
                    await websocket.send_text(str(message))
            except Exception as e:
                logger.exception(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def send_to_user(self, user_id: str, message: Any) -> None:
        """Send a message to a specific user."""
        if user_id in self.user_connections:
            connection_id = self.user_connections[user_id]
            await self.send_personal_message(connection_id, message)
        else:
            logger.warning(f"User {user_id} not connected")

    async def broadcast(self, message: Any, exclude: set[str] | None = None) -> None:
        """Broadcast a message to all connected clients."""
        exclude = exclude or set()

        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            if connection_id in exclude:
                continue

            try:
                if isinstance(message, dict):
                    await websocket.send_text(json.dumps(message))
                else:
                    await websocket.send_text(str(message))
            except Exception as e:
                logger.exception(f"Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)

    def join_group(self, connection_id: str, group_id: str) -> None:
        """Add a connection to a group."""
        if group_id not in self.connection_groups:
            self.connection_groups[group_id] = set()

        self.connection_groups[group_id].add(connection_id)
        logger.info(f"Connection {connection_id} joined group {group_id}")

    def leave_group(self, connection_id: str, group_id: str) -> None:
        """Remove a connection from a group."""
        if group_id in self.connection_groups:
            self.connection_groups[group_id].discard(connection_id)

            # Remove empty groups
            if not self.connection_groups[group_id]:
                del self.connection_groups[group_id]

        logger.info(f"Connection {connection_id} left group {group_id}")

    async def broadcast_to_group(
        self, group_id: str, message: Any, exclude: set[str] | None = None
    ) -> None:
        """Broadcast a message to all connections in a group."""
        if group_id not in self.connection_groups:
            return

        exclude = exclude or set()
        group_connections = self.connection_groups[group_id] - exclude

        disconnected = []
        for connection_id in group_connections:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    if isinstance(message, dict):
                        await websocket.send_text(json.dumps(message))
                    else:
                        await websocket.send_text(str(message))
                except Exception as e:
                    logger.exception(
                        f"Failed to send to group {group_id}, connection {connection_id}: {e}"
                    )
                    disconnected.append(connection_id)

        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

    def get_group_count(self, group_id: str) -> int:
        """Get the number of connections in a group."""
        return len(self.connection_groups.get(group_id, set()))

    def get_active_users(self) -> list[str]:
        """Get list of active user IDs."""
        return list(self.user_connections.keys())

    def get_stats(self) -> dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": self.get_connection_count(),
            "active_users": len(self.user_connections),
            "groups": {
                group_id: len(connections)
                for group_id, connections in self.connection_groups.items()
            },
            "timestamp": datetime.now().isoformat(),
        }


# Global connection manager instance
connection_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, connection_id: str) -> None:
    """Generic WebSocket endpoint handler."""
    await connection_manager.connect(websocket, connection_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(connection_id, message)
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    connection_id, {"type": "error", "message": "Invalid JSON format"}
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.exception(f"WebSocket error for {connection_id}: {e}")
        connection_manager.disconnect(connection_id)


async def handle_websocket_message(connection_id: str, message: dict[str, Any]) -> None:
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")

    if message_type == "ping":
        await connection_manager.send_personal_message(
            connection_id, {"type": "pong", "timestamp": datetime.now().isoformat()}
        )

    elif message_type == "join_group":
        group_id = message.get("group_id")
        if group_id:
            connection_manager.join_group(connection_id, group_id)
            await connection_manager.send_personal_message(
                connection_id, {"type": "joined_group", "group_id": group_id}
            )

    elif message_type == "leave_group":
        group_id = message.get("group_id")
        if group_id:
            connection_manager.leave_group(connection_id, group_id)
            await connection_manager.send_personal_message(
                connection_id, {"type": "left_group", "group_id": group_id}
            )

    elif message_type == "broadcast":
        if message.get("data"):
            await connection_manager.broadcast(
                {
                    "type": "broadcast_message",
                    "data": message["data"],
                    "from": connection_id,
                    "timestamp": datetime.now().isoformat(),
                },
                exclude={connection_id},
            )

    else:
        await connection_manager.send_personal_message(
            connection_id,
            {"type": "error", "message": f"Unknown message type: {message_type}"},
        )
