"""
CRDT for JSON objects (simple JSON-OT style)
"""

from typing import Any, Dict
import copy


class JSONOT:
    def __init__(self, base: Dict[str, Any]):
        self.base = copy.deepcopy(base)
        self.deltas = []

    def apply_delta(self, delta: Dict[str, Any]):
        self.base.update(delta)
        self.deltas.append(delta)

    def merge(self, remote: "JSONOT"):
        # Merge all deltas, last-write-wins
        for delta in remote.deltas:
            self.apply_delta(delta)

    def value(self) -> Dict[str, Any]:
        return self.base
