"""
Offline sync logic: Pull/push deltas over Bitchat, merge via CRDT, resolve conflicts, generate new deltas
"""
from .crdt_text import RGA
from .crdt_json import JSONOT
from .offline_queue import OfflineQueue


# Placeholder for Bitchat mesh communication
class BitchatMesh:
    def pull_deltas(self, doc_id):
        # TODO: Implement actual mesh pull
        return []

    def push_deltas(self, doc_id, deltas):
        # TODO: Implement actual mesh push
        pass


class OfflineSync:
    def __init__(self, doc_id, doc_type="text"):
        self.doc_id = doc_id
        self.doc_type = doc_type
        self.queue = OfflineQueue()
        self.mesh = BitchatMesh()
        if doc_type == "text":
            self.crdt = RGA()
        else:
            self.crdt = JSONOT({})

    def pull_and_merge(self):
        remote_deltas = self.mesh.pull_deltas(self.doc_id)
        for delta in remote_deltas:
            self.apply_delta(delta)

    def apply_delta(self, delta):
        if self.doc_type == "text":
            # Assume delta is (op, index/id, char)
            op = delta["op"]
            if op == "insert":
                self.crdt.insert(delta["index"], delta["char"])
            elif op == "delete":
                self.crdt.delete(delta["id"])
        else:
            self.crdt.apply_delta(delta)

    def merge_and_generate(self):
        # Merge local and remote, resolve conflicts
        self.pull_and_merge()
        # Generate new deltas from local queue
        local_deltas = self.queue.get_deltas(self.doc_id)
        for d in local_deltas:
            self.apply_delta(d["delta"])
        # Push new deltas
        self.mesh.push_deltas(self.doc_id, [d["delta"] for d in local_deltas])
        # Remove pushed deltas
        for d in local_deltas:
            self.queue.remove_delta(d["id"])
