"""
Integration test: Simulate two clients editing the same case and reconciling via CRDT
"""
import pytest
from src.surgify.core.sync.crdt_text import RGA
from src.surgify.core.sync.crdt_json import JSONOT


@pytest.mark.asyncio
def test_rga_text_merge():
    # Client A
    a = RGA()
    a.insert(0, "H")
    a.insert(1, "i")
    # Client B
    b = RGA()
    b.insert(0, "H")
    b.insert(1, "o")
    # Simulate concurrent edits
    a.merge(b)
    b.merge(a)
    assert set(a.value()) == set("Hio")
    assert set(b.value()) == set("Hio")


@pytest.mark.asyncio
def test_json_ot_merge():
    # Client A
    a = JSONOT({"x": 1})
    a.apply_delta({"y": 2})
    # Client B
    b = JSONOT({"x": 1})
    b.apply_delta({"z": 3})
    # Simulate concurrent edits
    a.merge(b)
    b.merge(a)
    assert a.value() == {"x": 1, "y": 2, "z": 3}
    assert b.value() == {"x": 1, "y": 2, "z": 3}
