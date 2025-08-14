"""Sync Engine for distributed data synchronization
Implements eventual consistency, offline work, and smart merging.
"""

import asyncio
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class SyncState(Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"


@dataclass
class SyncItem:
    """Represents an item to be synchronized."""

    id: str
    type: str
    data: Any
    version: int
    checksum: str
    timestamp: datetime
    source_node: str
    state: SyncState = SyncState.PENDING


@dataclass
class ConflictResolution:
    """Represents a conflict resolution strategy."""

    conflict_id: str
    strategy: str  # "merge", "override", "manual"
    resolution_data: Any
    resolved_by: str
    resolved_at: datetime


class SyncEngine:
    """Manages distributed data synchronization."""

    def __init__(self, node_id: str | None = None) -> None:
        self.node_id = node_id or str(uuid.uuid4())
        self.sync_queue: list[SyncItem] = []
        self.local_data: dict[str, SyncItem] = {}
        self.peer_states: dict[str, dict] = {}
        self.conflicts: dict[str, list[SyncItem]] = {}
        self.is_running = False
        self.sync_callbacks = {}

    async def start(self) -> None:
        """Start sync engine."""
        logger.info("🔄 Starting Sync Engine...")

        self.is_running = True

        # Start background sync tasks
        asyncio.create_task(self._process_sync_queue())
        asyncio.create_task(self._peer_sync_loop())
        asyncio.create_task(self._conflict_resolution_loop())

        logger.info("✅ Sync Engine started")

    async def implement_eventual_consistency(self) -> None:
        """Implement eventual consistency across all nodes."""
        logger.info("⚖️ Implementing eventual consistency")

        # Start consistency checking
        asyncio.create_task(self._consistency_checker())

        # Setup conflict detection
        asyncio.create_task(self._conflict_detector())

        logger.info("✅ Eventual consistency implemented")

    async def add_sync_item(
        self, item_type: str, data: Any, item_id: str | None = None
    ) -> str:
        """Add item to sync queue."""
        item_id = item_id or str(uuid.uuid4())

        # Create checksum
        data_str = json.dumps(data, sort_keys=True, default=str)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()

        sync_item = SyncItem(
            id=item_id,
            type=item_type,
            data=data,
            version=1,
            checksum=checksum,
            timestamp=datetime.now(),
            source_node=self.node_id,
        )

        # Add to local data and sync queue
        self.local_data[item_id] = sync_item
        self.sync_queue.append(sync_item)

        logger.info(f"📝 Added sync item: {item_type} ({item_id})")
        return item_id

    async def update_sync_item(self, item_id: str, data: Any) -> bool:
        """Update existing sync item."""
        if item_id not in self.local_data:
            logger.warning(f"Item not found for update: {item_id}")
            return False

        existing_item = self.local_data[item_id]

        # Create new version
        data_str = json.dumps(data, sort_keys=True, default=str)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()

        updated_item = SyncItem(
            id=item_id,
            type=existing_item.type,
            data=data,
            version=existing_item.version + 1,
            checksum=checksum,
            timestamp=datetime.now(),
            source_node=self.node_id,
        )

        self.local_data[item_id] = updated_item
        self.sync_queue.append(updated_item)

        logger.info(f"✏️ Updated sync item: {item_id} (v{updated_item.version})")
        return True

    async def enable_offline_work(self) -> None:
        """Enable work continuation when disconnected."""
        logger.info("📱 Enabling offline work capabilities")

        # Start offline queue management
        asyncio.create_task(self._manage_offline_queue())

        # Setup connection monitoring
        asyncio.create_task(self._monitor_connectivity())

        logger.info("✅ Offline work enabled")

    async def _manage_offline_queue(self) -> None:
        """Manage offline changes queue."""
        offline_queue = []

        while self.is_running:
            try:
                # Check if we're online
                is_online = await self._check_connectivity()

                if not is_online:
                    # Store changes offline
                    pending_items = [
                        item
                        for item in self.sync_queue
                        if item.state == SyncState.PENDING
                    ]
                    offline_queue.extend(pending_items)

                    # Mark items as offline
                    for item in pending_items:
                        item.state = SyncState.PENDING

                    logger.info(f"📱 Stored {len(pending_items)} items for offline sync")

                # We're back online - sync offline queue
                elif offline_queue:
                    logger.info(f"🔄 Syncing {len(offline_queue)} offline items")

                    for item in offline_queue:
                        await self._sync_single_item(item)

                    offline_queue.clear()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Offline queue management error: {e}")
                await asyncio.sleep(60)

    async def _check_connectivity(self) -> bool:
        """Check if we have network connectivity."""
        try:
            # Simple connectivity check - could be enhanced
            import socket

            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False

    async def _monitor_connectivity(self) -> None:
        """Monitor network connectivity changes."""
        last_state = None

        while self.is_running:
            try:
                current_state = await self._check_connectivity()

                if last_state is not None and current_state != last_state:
                    if current_state:
                        logger.info("🌐 Network connectivity restored")
                        # Trigger sync of offline queue
                        asyncio.create_task(self._sync_offline_changes())
                    else:
                        logger.info(
                            "📱 Network connectivity lost - entering offline mode"
                        )

                last_state = current_state
                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.exception(f"Connectivity monitoring error: {e}")
                await asyncio.sleep(30)

    async def _sync_offline_changes(self) -> None:
        """Sync changes made while offline."""
        offline_items = [
            item for item in self.local_data.values() if item.state == SyncState.PENDING
        ]

        if offline_items:
            logger.info(f"🔄 Syncing {len(offline_items)} offline changes")

            for item in offline_items:
                await self._sync_single_item(item)

    async def setup_smart_merging(self) -> None:
        """Setup intelligent merging of distributed changes."""
        logger.info("🧠 Setting up smart merging")

        # Define merge strategies
        self.merge_strategies = {
            "text": self._merge_text,
            "json": self._merge_json,
            "list": self._merge_list,
            "dict": self._merge_dict,
        }

        logger.info("✅ Smart merging configured")

    async def _merge_text(self, base: str, local: str, remote: str) -> str:
        """Merge text using three-way merge."""
        try:
            # Simple line-based merge
            base_lines = base.split("\n")
            local_lines = local.split("\n")
            remote_lines = remote.split("\n")

            # Find common sections and merge
            merged_lines = []

            # This is a simplified merge - in production would use more sophisticated algorithms
            max_len = max(len(base_lines), len(local_lines), len(remote_lines))

            for i in range(max_len):
                base_line = base_lines[i] if i < len(base_lines) else ""
                local_line = local_lines[i] if i < len(local_lines) else ""
                remote_line = remote_lines[i] if i < len(remote_lines) else ""

                if local_line == remote_line:
                    merged_lines.append(local_line)
                elif local_line == base_line:
                    merged_lines.append(remote_line)
                elif remote_line == base_line:
                    merged_lines.append(local_line)
                else:
                    # Conflict - keep both
                    merged_lines.append("<<<<<<< LOCAL")
                    merged_lines.append(local_line)
                    merged_lines.append("=======")
                    merged_lines.append(remote_line)
                    merged_lines.append(">>>>>>> REMOTE")

            return "\n".join(merged_lines)

        except Exception as e:
            logger.exception(f"Text merge failed: {e}")
            return local  # Fallback to local version

    async def _merge_json(self, base: dict, local: dict, remote: dict) -> dict:
        """Merge JSON objects."""
        try:
            merged = base.copy()

            # Apply local changes
            for key, value in local.items():
                if key not in base or base[key] != value:
                    merged[key] = value

            # Apply remote changes
            for key, value in remote.items():
                if key not in base:
                    # New key from remote
                    merged[key] = value
                elif key in local and local[key] != base[key] and value != base[key]:
                    # Conflict - both changed
                    if isinstance(value, dict) and isinstance(merged[key], dict):
                        # Recursive merge for nested objects
                        merged[key] = await self._merge_json(
                            base.get(key, {}), local.get(key, {}), value
                        )
                    else:
                        # Keep both values with conflict markers
                        merged[key] = {
                            "_conflict": True,
                            "local": local[key],
                            "remote": value,
                            "base": base.get(key),
                        }
                elif value != base[key]:
                    # Only remote changed
                    merged[key] = value

            return merged

        except Exception as e:
            logger.exception(f"JSON merge failed: {e}")
            return local

    async def _merge_list(self, base: list, local: list, remote: list) -> list:
        """Merge lists with conflict detection."""
        try:
            # Simple list merge - append unique items
            merged = local.copy()

            for item in remote:
                if item not in merged:
                    merged.append(item)

            return merged

        except Exception as e:
            logger.exception(f"List merge failed: {e}")
            return local

    async def _merge_dict(self, base: dict, local: dict, remote: dict) -> dict:
        """Merge dictionaries."""
        return await self._merge_json(base, local, remote)

    async def _process_sync_queue(self) -> None:
        """Process items in sync queue."""
        while self.is_running:
            try:
                if self.sync_queue:
                    # Process items in batches
                    batch = self.sync_queue[:5]
                    self.sync_queue = self.sync_queue[5:]

                    for item in batch:
                        await self._sync_single_item(item)

                await asyncio.sleep(1)  # Process every second

            except Exception as e:
                logger.exception(f"Sync queue processing error: {e}")
                await asyncio.sleep(5)

    async def _sync_single_item(self, item: SyncItem) -> None:
        """Sync a single item."""
        try:
            item.state = SyncState.SYNCING

            # Check for conflicts
            has_conflict = await self._check_for_conflicts(item)

            if has_conflict:
                item.state = SyncState.CONFLICT
                logger.warning(f"⚠️ Conflict detected for item: {item.id}")
                return

            # Simulate sync to peers
            success = await self._send_to_peers(item)

            if success:
                item.state = SyncState.SYNCED
                logger.info(f"✅ Synced item: {item.id}")
            else:
                item.state = SyncState.ERROR
                logger.error(f"❌ Failed to sync item: {item.id}")

        except Exception as e:
            item.state = SyncState.ERROR
            logger.exception(f"Sync error for item {item.id}: {e}")

    async def _check_for_conflicts(self, item: SyncItem) -> bool:
        """Check if item conflicts with peer versions."""
        # Check peer states for conflicts
        for peer_state in self.peer_states.values():
            peer_items = peer_state.get("items", {})

            if item.id in peer_items:
                peer_item = peer_items[item.id]

                # Check if there's a version conflict
                if (
                    peer_item["version"] != item.version
                    and peer_item["checksum"] != item.checksum
                ):
                    # Add to conflicts
                    if item.id not in self.conflicts:
                        self.conflicts[item.id] = []
                    self.conflicts[item.id].append(item)

                    return True

        return False

    async def _send_to_peers(self, item: SyncItem) -> bool:
        """Send item to peers."""
        # Simulate sending to peers
        # In real implementation, this would use networking layer
        logger.debug(f"📤 Sending item {item.id} to peers")

        # Simulate success
        await asyncio.sleep(0.1)
        return True

    async def _peer_sync_loop(self) -> None:
        """Periodic sync with peers."""
        while self.is_running:
            try:
                # Get updates from peers
                await self._fetch_peer_updates()

                # Send our updates to peers
                await self._send_our_updates()

                await asyncio.sleep(30)  # Sync every 30 seconds

            except Exception as e:
                logger.exception(f"Peer sync error: {e}")
                await asyncio.sleep(60)

    async def _fetch_peer_updates(self) -> None:
        """Fetch updates from peers."""
        # Simulate fetching updates
        logger.debug("📥 Fetching peer updates")

    async def _send_our_updates(self) -> None:
        """Send our updates to peers."""
        # Simulate sending updates
        logger.debug("📤 Sending updates to peers")

    async def _consistency_checker(self) -> None:
        """Check and ensure data consistency."""
        while self.is_running:
            try:
                # Check consistency across all peers
                inconsistencies = await self._find_inconsistencies()

                if inconsistencies:
                    logger.info(f"🔧 Found {len(inconsistencies)} inconsistencies")
                    await self._resolve_inconsistencies(inconsistencies)

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.exception(f"Consistency check error: {e}")
                await asyncio.sleep(600)

    async def _find_inconsistencies(self) -> list[dict]:
        """Find data inconsistencies."""
        # Simulate finding inconsistencies
        return []

    async def _resolve_inconsistencies(self, inconsistencies: list[dict]) -> None:
        """Resolve data inconsistencies."""
        for inconsistency in inconsistencies:
            logger.info(f"🔧 Resolving inconsistency: {inconsistency.get('id')}")

    async def _conflict_detector(self) -> None:
        """Detect and handle conflicts."""
        while self.is_running:
            try:
                if self.conflicts:
                    logger.info(f"⚠️ Processing {len(self.conflicts)} conflicts")

                    for item_id, conflicting_items in list(self.conflicts.items()):
                        await self._auto_resolve_conflict(item_id, conflicting_items)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.exception(f"Conflict detection error: {e}")
                await asyncio.sleep(120)

    async def _conflict_resolution_loop(self) -> None:
        """Handle conflict resolution."""
        while self.is_running:
            try:
                # Process conflicts that need resolution
                for item_id, conflicting_items in list(self.conflicts.items()):
                    if len(conflicting_items) > 1:
                        await self._auto_resolve_conflict(item_id, conflicting_items)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Conflict resolution error: {e}")
                await asyncio.sleep(60)

    async def _auto_resolve_conflict(
        self, item_id: str, conflicting_items: list[SyncItem]
    ) -> None:
        """Automatically resolve conflict using smart merging."""
        try:
            if len(conflicting_items) < 2:
                # No conflict
                del self.conflicts[item_id]
                return

            logger.info(f"🔧 Auto-resolving conflict for item: {item_id}")

            # Find the merge strategy based on data type
            item_type = conflicting_items[0].type
            merge_strategy = self.merge_strategies.get(item_type, self._merge_json)

            # Perform merge
            base_data = conflicting_items[0].data
            local_data = conflicting_items[0].data
            remote_data = (
                conflicting_items[1].data if len(conflicting_items) > 1 else base_data
            )

            merged_data = await merge_strategy(base_data, local_data, remote_data)

            # Create resolved item
            resolved_item = SyncItem(
                id=item_id,
                type=item_type,
                data=merged_data,
                version=max(item.version for item in conflicting_items) + 1,
                checksum=hashlib.sha256(
                    json.dumps(merged_data, sort_keys=True, default=str).encode()
                ).hexdigest(),
                timestamp=datetime.now(),
                source_node=self.node_id,
                state=SyncState.PENDING,
            )

            # Update local data and add to sync queue
            self.local_data[item_id] = resolved_item
            self.sync_queue.append(resolved_item)

            # Remove from conflicts
            del self.conflicts[item_id]

            logger.info(f"✅ Conflict resolved for item: {item_id}")

        except Exception as e:
            logger.exception(f"Auto-resolve conflict failed for {item_id}: {e}")

    async def get_sync_status(self) -> dict:
        """Get sync engine status."""
        return {
            "active": self.is_running,
            "node_id": self.node_id,
            "queue_size": len(self.sync_queue),
            "local_items": len(self.local_data),
            "conflicts": len(self.conflicts),
            "peer_count": len(self.peer_states),
            "sync_states": {
                "pending": len(
                    [
                        i
                        for i in self.local_data.values()
                        if i.state == SyncState.PENDING
                    ]
                ),
                "syncing": len(
                    [
                        i
                        for i in self.local_data.values()
                        if i.state == SyncState.SYNCING
                    ]
                ),
                "synced": len(
                    [i for i in self.local_data.values() if i.state == SyncState.SYNCED]
                ),
                "conflict": len(
                    [
                        i
                        for i in self.local_data.values()
                        if i.state == SyncState.CONFLICT
                    ]
                ),
                "error": len(
                    [i for i in self.local_data.values() if i.state == SyncState.ERROR]
                ),
            },
        }

    async def stop(self) -> None:
        """Stop sync engine."""
        logger.info("🛑 Stopping Sync Engine")
        self.is_running = False
