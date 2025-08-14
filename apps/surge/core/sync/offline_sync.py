"""Offline sync logic: Pull/push deltas over Bitchat, merge via CRDT, resolve conflicts."""

from typing import Any

from .crdt_json import JSONOT
from .crdt_text import RGA
from .offline_queue import OfflineQueue


class BitchatMesh:
    """Bitchat mesh communication interface."""

    def pull_deltas(self, doc_id: str) -> list[dict]:
        """Pull deltas from mesh network."""
        # Implementation will be added when Bitchat integration is ready
        return []

    def push_deltas(self, doc_id: str, deltas: list[dict]) -> None:
        """Push deltas to mesh network."""
        # Implementation will be added when Bitchat integration is ready


class OfflineSync:
    """Offline synchronization manager using CRDTs."""

    def __init__(self, doc_id: str, doc_type: str = "text") -> None:
        self.doc_id = doc_id
        self.doc_type = doc_type
        self.queue = OfflineQueue()
        self.mesh = BitchatMesh()

        if doc_type == "text":
            self.crdt = RGA()
        else:
            self.crdt = JSONOT({})

    def pull_and_merge(self) -> None:
        """Pull remote deltas and merge with local state."""
        remote_deltas = self.mesh.pull_deltas(self.doc_id)
        for delta in remote_deltas:
            self.apply_delta(delta)

    def apply_delta(self, delta: dict) -> None:
        """Apply a delta to the CRDT."""
        if self.doc_type == "text":
            op = delta.get("op")
            if op == "insert":
                self.crdt.insert(delta["index"], delta["char"])
            elif op == "delete":
                self.crdt.delete(delta["id"])
        else:
            self.crdt.apply_delta(delta)

    def merge_and_generate(self) -> None:
        """Merge local and remote changes, then push new deltas."""
        # Merge local and remote changes
        self.pull_and_merge()

        # Generate new deltas from local queue
        local_deltas = self.queue.get_deltas(self.doc_id)
        for d in local_deltas:
            self.apply_delta(d["delta"])

        # Push new deltas to mesh
        self.mesh.push_deltas(self.doc_id, [d["delta"] for d in local_deltas])

        # Remove pushed deltas from queue
        for d in local_deltas:
            self.queue.remove_delta(d["id"])

    def get_document_state(self) -> Any:
        """Get current document state."""
        if self.doc_type == "text":
            return self.crdt.to_string()
        return self.crdt.get_document()
