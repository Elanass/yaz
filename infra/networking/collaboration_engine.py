"""Collaboration Engine for real-time team collaboration
Implements operational transforms, presence awareness, and conflict resolution.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class OperationType(Enum):
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    UPDATE = "update"


@dataclass
class Operation:
    """Represents an operational transform operation."""

    type: OperationType
    position: int
    content: Any = None
    length: int = 0
    timestamp: datetime = None
    user_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class UserPresence:
    """Represents a user's presence in the collaboration session."""

    user_id: str
    name: str
    cursor_position: int
    selection_start: int
    selection_end: int
    last_seen: datetime
    is_active: bool = True
    current_file: str = None


@dataclass
class CollaborationSession:
    """Represents a collaboration session."""

    session_id: str
    document_id: str
    participants: list[str]
    created_at: datetime
    last_activity: datetime
    is_active: bool = True


class CollaborationEngine:
    """Manages real-time collaboration across the platform."""

    def __init__(self) -> None:
        self.sessions: dict[str, CollaborationSession] = {}
        self.user_presence: dict[str, UserPresence] = {}
        self.operation_queue: list[Operation] = []
        self.document_states: dict[str, Any] = {}
        self.is_running = False
        self.websocket_connections: dict[str, Any] = {}

    async def start(self) -> None:
        """Start collaboration engine."""
        logger.info("🤝 Starting Collaboration Engine...")

        self.is_running = True

        # Start background tasks
        asyncio.create_task(self._process_operations())
        asyncio.create_task(self._manage_presence())
        asyncio.create_task(self._cleanup_sessions())

        logger.info("✅ Collaboration Engine started")

    async def enable_live_editing(self, document_id: str, user_id: str):
        """Enable live editing for a document."""
        logger.info(f"✏️ Enabling live editing for {document_id}")

        # Initialize document state if not exists
        if document_id not in self.document_states:
            self.document_states[document_id] = {
                "content": "",
                "version": 0,
                "operations": [],
                "last_modified": datetime.now(),
            }

        # Create or join collaboration session
        return await self._get_or_create_session(document_id, user_id)

    async def _get_or_create_session(self, document_id: str, user_id: str) -> str:
        """Get existing session or create new one."""
        # Look for existing session
        for session in self.sessions.values():
            if session.document_id == document_id and session.is_active:
                if user_id not in session.participants:
                    session.participants.append(user_id)
                    session.last_activity = datetime.now()
                return session.session_id

        # Create new session
        session_id = str(uuid.uuid4())
        session = CollaborationSession(
            session_id=session_id,
            document_id=document_id,
            participants=[user_id],
            created_at=datetime.now(),
            last_activity=datetime.now(),
        )
        self.sessions[session_id] = session

        logger.info(f"🆕 Created collaboration session: {session_id}")
        return session_id

    async def apply_operation(self, operation: Operation, session_id: str) -> None:
        """Apply operation with operational transform."""
        try:
            session = self.sessions.get(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return

            document_id = session.document_id

            # Transform operation against concurrent operations
            transformed_op = await self._transform_operation(operation, document_id)

            # Apply operation to document
            await self._apply_to_document(transformed_op, document_id)

            # Broadcast to other participants
            await self._broadcast_operation(
                transformed_op, session_id, operation.user_id
            )

            # Update session activity
            session.last_activity = datetime.now()

            logger.debug(
                f"✅ Applied operation: {transformed_op.type.value} at {transformed_op.position}"
            )

        except Exception as e:
            logger.exception(f"Failed to apply operation: {e}")

    async def _transform_operation(
        self, operation: Operation, document_id: str
    ) -> Operation:
        """Transform operation against concurrent operations using OT."""
        document = self.document_states[document_id]
        concurrent_ops = document["operations"]

        # Simple operational transform - adjust position based on concurrent operations
        adjusted_position = operation.position

        for concurrent_op in concurrent_ops:
            if concurrent_op.timestamp > operation.timestamp:
                continue  # Skip newer operations

            if concurrent_op.position <= operation.position:
                if concurrent_op.type == OperationType.INSERT:
                    adjusted_position += len(concurrent_op.content or "")
                elif concurrent_op.type == OperationType.DELETE:
                    adjusted_position -= concurrent_op.length

        # Create transformed operation
        return Operation(
            type=operation.type,
            position=max(0, adjusted_position),
            content=operation.content,
            length=operation.length,
            timestamp=operation.timestamp,
            user_id=operation.user_id,
        )

    async def _apply_to_document(self, operation: Operation, document_id: str) -> None:
        """Apply operation to document state."""
        document = self.document_states[document_id]
        content = document["content"]

        if operation.type == OperationType.INSERT:
            # Insert content at position
            new_content = (
                content[: operation.position]
                + operation.content
                + content[operation.position :]
            )
            document["content"] = new_content

        elif operation.type == OperationType.DELETE:
            # Delete content from position
            end_pos = operation.position + operation.length
            new_content = content[: operation.position] + content[end_pos:]
            document["content"] = new_content

        elif operation.type == OperationType.UPDATE:
            # Update content at position
            end_pos = operation.position + operation.length
            new_content = (
                content[: operation.position] + operation.content + content[end_pos:]
            )
            document["content"] = new_content

        # Update document metadata
        document["version"] += 1
        document["last_modified"] = datetime.now()
        document["operations"].append(operation)

        # Keep only recent operations (for memory management)
        if len(document["operations"]) > 1000:
            document["operations"] = document["operations"][-500:]

    async def _broadcast_operation(
        self, operation: Operation, session_id: str, sender_id: str
    ) -> None:
        """Broadcast operation to other session participants."""
        session = self.sessions.get(session_id)
        if not session:
            return

        operation_data = {
            "type": "operation",
            "operation": {
                "type": operation.type.value,
                "position": operation.position,
                "content": operation.content,
                "length": operation.length,
                "timestamp": operation.timestamp.isoformat(),
                "user_id": operation.user_id,
            },
            "session_id": session_id,
            "sender_id": sender_id,
        }

        # Send to all participants except sender
        for participant_id in session.participants:
            if participant_id != sender_id:
                await self._send_to_user(participant_id, operation_data)

    async def _send_to_user(self, user_id: str, data: dict) -> None:
        """Send data to specific user via WebSocket."""
        if user_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[user_id]
                await websocket.send_text(json.dumps(data))
            except Exception as e:
                logger.exception(f"Failed to send data to user {user_id}: {e}")
                # Remove broken connection
                del self.websocket_connections[user_id]

    async def setup_presence_awareness(self, user_id: str, user_name: str) -> None:
        """Setup presence awareness for user."""
        logger.info(f"👤 Setting up presence for {user_name}")

        presence = UserPresence(
            user_id=user_id,
            name=user_name,
            cursor_position=0,
            selection_start=0,
            selection_end=0,
            last_seen=datetime.now(),
        )

        self.user_presence[user_id] = presence

        # Broadcast presence to other users
        await self._broadcast_presence_update(user_id)

    async def update_user_cursor(
        self,
        user_id: str,
        cursor_position: int,
        selection_start: int = 0,
        selection_end: int = 0,
        current_file: str | None = None,
    ) -> None:
        """Update user cursor position."""
        if user_id in self.user_presence:
            presence = self.user_presence[user_id]
            presence.cursor_position = cursor_position
            presence.selection_start = selection_start
            presence.selection_end = selection_end
            presence.current_file = current_file
            presence.last_seen = datetime.now()

            # Broadcast cursor update
            await self._broadcast_cursor_update(user_id)

    async def _broadcast_presence_update(self, user_id: str) -> None:
        """Broadcast presence update to other users."""
        presence = self.user_presence.get(user_id)
        if not presence:
            return

        presence_data = {
            "type": "presence_update",
            "user_id": user_id,
            "presence": {
                "name": presence.name,
                "is_active": presence.is_active,
                "current_file": presence.current_file,
                "last_seen": presence.last_seen.isoformat(),
            },
        }

        # Send to all other users
        for other_user_id in self.user_presence:
            if other_user_id != user_id:
                await self._send_to_user(other_user_id, presence_data)

    async def _broadcast_cursor_update(self, user_id: str) -> None:
        """Broadcast cursor position update."""
        presence = self.user_presence.get(user_id)
        if not presence:
            return

        cursor_data = {
            "type": "cursor_update",
            "user_id": user_id,
            "cursor": {
                "position": presence.cursor_position,
                "selection_start": presence.selection_start,
                "selection_end": presence.selection_end,
                "current_file": presence.current_file,
                "name": presence.name,
            },
        }

        # Send to all other users
        for other_user_id in self.user_presence:
            if other_user_id != user_id:
                await self._send_to_user(other_user_id, cursor_data)

    async def implement_conflict_resolution(self, conflicts: list[dict]) -> list[dict]:
        """Handle simultaneous edits gracefully."""
        logger.info(f"🔧 Resolving {len(conflicts)} conflicts")

        resolved_operations = []

        for conflict in conflicts:
            try:
                # Simple conflict resolution: last write wins with merge
                operations = conflict.get("operations", [])

                if len(operations) <= 1:
                    resolved_operations.extend(operations)
                    continue

                # Sort by timestamp
                operations.sort(key=lambda op: op.get("timestamp", ""))

                # Apply each operation in sequence with transformation
                conflict.get("base_content", "")

                for op_data in operations:
                    op = Operation(
                        type=OperationType(op_data["type"]),
                        position=op_data["position"],
                        content=op_data.get("content"),
                        length=op_data.get("length", 0),
                        timestamp=datetime.fromisoformat(op_data["timestamp"]),
                        user_id=op_data["user_id"],
                    )

                    # Transform and apply
                    transformed_op = await self._transform_operation(
                        op, conflict["document_id"]
                    )
                    resolved_operations.append(transformed_op)

            except Exception as e:
                logger.exception(f"Conflict resolution failed: {e}")

        logger.info(f"✅ Resolved to {len(resolved_operations)} operations")
        return resolved_operations

    async def _process_operations(self) -> None:
        """Process operation queue."""
        while self.is_running:
            try:
                if self.operation_queue:
                    # Process operations in batches
                    batch = self.operation_queue[:10]
                    self.operation_queue = self.operation_queue[10:]

                    for operation in batch:
                        # Find session for operation
                        session_id = None
                        for sid, session in self.sessions.items():
                            if operation.user_id in session.participants:
                                session_id = sid
                                break

                        if session_id:
                            await self.apply_operation(operation, session_id)

                await asyncio.sleep(0.1)  # Process every 100ms

            except Exception as e:
                logger.exception(f"Operation processing error: {e}")
                await asyncio.sleep(1)

    async def _manage_presence(self) -> None:
        """Manage user presence."""
        while self.is_running:
            try:
                current_time = datetime.now()

                # Check for inactive users
                for user_id, presence in list(self.user_presence.items()):
                    time_since_seen = (
                        current_time - presence.last_seen
                    ).total_seconds()

                    if time_since_seen > 30:  # 30 seconds timeout
                        if presence.is_active:
                            presence.is_active = False
                            await self._broadcast_presence_update(user_id)

                    if time_since_seen > 300:  # 5 minutes - remove presence
                        del self.user_presence[user_id]
                        await self._broadcast_presence_update(user_id)

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.exception(f"Presence management error: {e}")
                await asyncio.sleep(30)

    async def _cleanup_sessions(self) -> None:
        """Cleanup inactive sessions."""
        while self.is_running:
            try:
                current_time = datetime.now()

                # Remove inactive sessions
                for session_id, session in list(self.sessions.items()):
                    time_since_activity = (
                        current_time - session.last_activity
                    ).total_seconds()

                    if time_since_activity > 3600:  # 1 hour timeout
                        session.is_active = False
                        logger.info(f"🗑️ Deactivated session: {session_id}")

                    if time_since_activity > 86400:  # 24 hours - remove session
                        del self.sessions[session_id]
                        logger.info(f"🗑️ Removed session: {session_id}")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.exception(f"Session cleanup error: {e}")
                await asyncio.sleep(600)

    async def add_websocket_connection(self, user_id: str, websocket) -> None:
        """Add WebSocket connection for user."""
        self.websocket_connections[user_id] = websocket
        logger.info(f"🔌 WebSocket connected for user: {user_id}")

    async def remove_websocket_connection(self, user_id: str) -> None:
        """Remove WebSocket connection for user."""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]
            logger.info(f"🔌 WebSocket disconnected for user: {user_id}")

    async def get_collaboration_status(self) -> dict:
        """Get collaboration engine status."""
        return {
            "active": self.is_running,
            "active_sessions": len([s for s in self.sessions.values() if s.is_active]),
            "total_sessions": len(self.sessions),
            "active_users": len(
                [p for p in self.user_presence.values() if p.is_active]
            ),
            "total_users": len(self.user_presence),
            "operation_queue_size": len(self.operation_queue),
            "websocket_connections": len(self.websocket_connections),
            "documents": len(self.document_states),
        }

    async def stop(self) -> None:
        """Stop collaboration engine."""
        logger.info("🛑 Stopping Collaboration Engine")
        self.is_running = False
