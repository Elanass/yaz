"""CRDT for JSON objects (simple JSON-OT style)."""

import copy
from typing import Any


class JSONOT:
    def __init__(self, base: dict[str, Any]) -> None:
        self.base = copy.deepcopy(base)
        self.deltas = []

    def apply_delta(self, delta: dict[str, Any]) -> None:
        self.base.update(delta)
        self.deltas.append(delta)

    def merge(self, remote: "JSONOT") -> None:
        # Merge all deltas, last-write-wins
        for delta in remote.deltas:
            self.apply_delta(delta)

    def value(self) -> dict[str, Any]:
        return self.base
