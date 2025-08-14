"""Centralized in-memory store for processing results and deliverables.
This unifies access across API modules (pipeline, deliverables, ingestion).

Note: Replace with persistent DB or object storage in production.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..models.processing_models import Deliverable, ProcessingResult


@dataclass
class ShareToken:
    token: str
    deliverable_id: str
    expires_at: datetime


class ProcessingStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._processing_results: dict[str, ProcessingResult] = {}
        self._deliverables: dict[str, Deliverable] = {}
        self._share_tokens: dict[str, ShareToken] = {}

    # Processing Results
    def save_processing_result(self, result_id: str, result: ProcessingResult) -> None:
        with self._lock:
            self._processing_results[result_id] = result

    def get_processing_result(self, result_id: str) -> ProcessingResult | None:
        with self._lock:
            return self._processing_results.get(result_id)

    def has_processing_result(self, result_id: str) -> bool:
        with self._lock:
            return result_id in self._processing_results

    # Deliverables
    def save_deliverable(self, deliverable_id: str, deliverable: Deliverable) -> None:
        with self._lock:
            self._deliverables[deliverable_id] = deliverable

    def get_deliverable(self, deliverable_id: str) -> Deliverable | None:
        with self._lock:
            return self._deliverables.get(deliverable_id)

    def delete_deliverable(self, deliverable_id: str) -> None:
        with self._lock:
            self._deliverables.pop(deliverable_id, None)

    def list_deliverables(self) -> dict[str, Deliverable]:
        with self._lock:
            return dict(self._deliverables)

    # Simple sharing tokens
    def create_share_token(self, deliverable_id: str, ttl_minutes: int = 60) -> str:
        import secrets

        token = secrets.token_urlsafe(24)
        with self._lock:
            self._share_tokens[token] = ShareToken(
                token=token,
                deliverable_id=deliverable_id,
                expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
            )
        return token

    def resolve_share_token(self, token: str) -> str | None:
        with self._lock:
            st = self._share_tokens.get(token)
            if not st:
                return None
            if st.expires_at < datetime.utcnow():
                # Expired
                self._share_tokens.pop(token, None)
                return None
            return st.deliverable_id


# Singleton instance
store = ProcessingStore()
