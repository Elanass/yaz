"""Simple HTTP-based mesh manager for multi-VM peer discovery and deliverable sync.
Designed as a pragmatic fallback until full libp2p is integrated.

- Discovers and tracks peers from an environment variable or API announcements
- Periodically exchanges peer lists and deliverable metadata over HTTP
- Exposes lightweight APIs via mesh_api.py

This module intentionally avoids extra runtime deps and uses urllib from stdlib.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)


@dataclass
class DeliverableMeta:
    name: str
    path: str
    size_bytes: int
    modified_at: str
    content_type: str | None = None
    rel_path: str | None = None


def _http_get_json(url: str, timeout: float = 3.0) -> dict | None:
    try:
        req = Request(url, headers={"User-Agent": "surgify-mesh/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError, TimeoutError, ValueError) as e:
        logger.debug(f"mesh GET failed {url}: {e}")
        return None


def _http_get_bytes(url: str, timeout: float = 10.0) -> bytes | None:
    try:
        req = Request(url, headers={"User-Agent": "surgify-mesh/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return resp.read()
    except (URLError, HTTPError, TimeoutError) as e:
        logger.debug(f"mesh GET(bytes) failed {url}: {e}")
        return None


def _http_post_json(url: str, data: dict, timeout: float = 3.0) -> dict | None:
    try:
        body = json.dumps(data).encode("utf-8")
        req = Request(
            url,
            data=body,
            headers={
                "User-Agent": "surgify-mesh/1.0",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(req, timeout=timeout) as resp:
            if resp.status not in (200, 201):
                return None
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except (URLError, HTTPError, TimeoutError, ValueError) as e:
        logger.debug(f"mesh POST failed {url}: {e}")
        return None


class MeshManager:
    def __init__(
        self,
        base_url: str,
        node_id: str | None = None,
        peers: list[str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.node_id = node_id or os.getenv("SURGIFY_NODE_ID") or socket.gethostname()
        env_peers = os.getenv("SURGIFY_PEERS", "")
        initial_peers = {
            p.strip().rstrip("/") for p in env_peers.split(",") if p.strip()
        }
        if peers:
            initial_peers.update(p.rstrip("/") for p in peers)
        self.peers: set[str] = {p for p in initial_peers if p != self.base_url}
        self._task: asyncio.Task | None = None
        self._stop: asyncio.Event = asyncio.Event()
        self.last_sync: str | None = None
        self.sync_files: bool = os.getenv(
            "SURGIFY_MESH_SYNC_FILES", "false"
        ).lower() in {"1", "true", "yes"}
        self.interval_seconds: int = int(os.getenv("MESH_INTERVAL", "30"))
        # Directories to scan and sync deliverables
        self._deliverable_roots: list[Path] = [
            Path("uploads/deliverables"),
            Path("data/uploads/deliverables"),
        ]
        logger.info(
            f"🌐 MeshManager initialized node_id={self.node_id} base={self.base_url} peers={list(self.peers)} sync_files={self.sync_files}"
        )

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "base_url": self.base_url,
            "peers": sorted(self.peers),
            "last_sync": self.last_sync,
        }

    def add_peer(self, url: str) -> bool:
        url = url.rstrip("/")
        if url and url != self.base_url and url not in self.peers:
            self.peers.add(url)
            logger.info(f"🤝 Added peer: {url}")
            return True
        return False

    def _roots(self) -> list[Path]:
        return [p for p in self._deliverable_roots if p.exists()]

    def list_deliverables(self, root: Path | None = None) -> list[DeliverableMeta]:
        items: list[DeliverableMeta] = []
        roots = [root] if root else self._roots()
        if not roots:
            return items
        for r in roots:
            for path in r.rglob("*"):
                if path.is_file():
                    try:
                        stat = path.stat()
                        content_type = None
                        if path.suffix.lower() in {".pdf"}:
                            content_type = "application/pdf"
                        elif path.suffix.lower() in {".html", ".htm"}:
                            content_type = "text/html"
                        elif path.suffix.lower() in {".json"}:
                            content_type = "application/json"
                        rel = path.relative_to(r)
                        items.append(
                            DeliverableMeta(
                                name=path.name,
                                path=str(path),
                                size_bytes=stat.st_size,
                                modified_at=datetime.utcfromtimestamp(
                                    stat.st_mtime
                                ).isoformat()
                                + "Z",
                                content_type=content_type,
                                rel_path=str(rel).replace("\\", "/"),
                            )
                        )
                    except OSError:
                        continue
        return items

    async def _announce_to_peer(self, peer: str) -> None:
        _http_post_json(urljoin(peer + "/", "api/mesh/announce"), self.to_dict())

    async def _pull_from_peer(self, peer: str) -> None:
        # Merge peers
        data = _http_get_json(urljoin(peer + "/", "api/mesh/peers"))
        if data and isinstance(data.get("peers", []), list):
            for p in data["peers"]:
                self.add_peer(p)
        # Fetch deliverables list
        d = _http_get_json(urljoin(peer + "/", "api/mesh/deliverables"))
        if self.sync_files and d and isinstance(d.get("items", []), list):
            await self._sync_deliverables_from_peer(peer, d["items"])  # type: ignore

    async def _sync_deliverables_from_peer(self, peer: str, items: list[dict]) -> None:
        # Build local index by rel_path
        {m.rel_path or m.path: m for m in self.list_deliverables()}
        for it in items:
            rel = it.get("rel_path") or it.get("path")
            if not rel:
                continue
            # Determine destination under the first existing root or default
            roots = self._roots() or [self._deliverable_roots[0]]
            dest = roots[0] / rel
            need = False
            if not dest.exists():
                need = True
            else:
                try:
                    remote_mtime = datetime.fromisoformat(
                        it.get("modified_at", "").rstrip("Z")
                    )
                    local_mtime = datetime.utcfromtimestamp(dest.stat().st_mtime)
                    if remote_mtime > local_mtime:
                        need = True
                except Exception:
                    need = False
            if need:
                dest.parent.mkdir(parents=True, exist_ok=True)
                q = urlencode({"rel": rel})
                url = urljoin(peer + "/", f"api/mesh/file?{q}")
                content = _http_get_bytes(url)
                if content is not None:
                    try:
                        dest.write_bytes(content)
                        logger.info(f"⬇️  Synced deliverable from {peer}: {rel}")
                    except OSError as e:
                        logger.warning(f"⚠️ Failed to write deliverable {dest}: {e}")

    async def sync_once(self) -> None:
        # Announce self and pull info
        for peer in list(self.peers):
            try:
                await self._announce_to_peer(peer)
                await self._pull_from_peer(peer)
            except Exception as e:
                logger.debug(f"mesh sync error peer={peer}: {e}")
        self.last_sync = datetime.utcnow().isoformat() + "Z"

    async def run_background(self, interval_seconds: int | None = None) -> None:
        interval = interval_seconds or self.interval_seconds
        logger.info("🔄 MeshManager background sync loop starting")
        while not self._stop.is_set():
            try:
                await self.sync_once()
            except Exception as e:
                logger.debug(f"mesh loop error: {e}")
            await asyncio.wait([self._stop.wait()], timeout=interval)
        logger.info("🛑 MeshManager background sync loop stopped")

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stop.clear()
            self._task = asyncio.create_task(self.run_background())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5)
            except asyncio.TimeoutError:
                logger.warning("mesh background task did not stop in time")
