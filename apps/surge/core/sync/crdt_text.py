"""CRDT for collaborative text editing (RGA - Replicated Growable Array)."""

import uuid


class RGAElement:
    def __init__(self, char: str, id: str | None = None, visible: bool = True) -> None:
        self.char = char
        self.id = id or str(uuid.uuid4())
        self.visible = visible


class RGA:
    def __init__(self) -> None:
        self.elements: list[RGAElement] = []

    def insert(self, index: int, char: str) -> str:
        elem = RGAElement(char)
        self.elements.insert(index, elem)
        return elem.id

    def delete(self, elem_id: str) -> None:
        for elem in self.elements:
            if elem.id == elem_id:
                elem.visible = False
                break

    def value(self) -> str:
        return "".join(e.char for e in self.elements if e.visible)

    def merge(self, remote: "RGA") -> None:
        # Simple merge: union by id, favor visible
        local_ids = {e.id for e in self.elements}
        for re in remote.elements:
            if re.id not in local_ids:
                self.elements.append(re)
            else:
                for le in self.elements:
                    if le.id == re.id:
                        le.visible = le.visible or re.visible
        self.elements.sort(key=lambda e: e.id)
