# orchestrator/tests/test_orchestrator.py
"""
Smoke tests for the orchestrator module.
"""

import pytest
from core.orchestrator.main import run

def test_run_smoke(monkeypatch):
    """Smoke test for orchestrator.run."""
    # Monkeypatch any external dependencies
    monkeypatch.setattr("orchestrator.main.api_router", None)
    # Ensure run does not raise exceptions
    run()