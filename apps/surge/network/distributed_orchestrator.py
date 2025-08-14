"""Distributed Orchestrator for multi-VM dataset processing and deliverable generation.

- Uses lightweight HTTP to submit pipeline jobs to peers
- Polls job status until completion
- Downloads generated deliverables back to the coordinator

Peers are HTTP base URLs (e.g., http://10.0.0.5:8000). Each must run the Surgify app.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

# NEW: Read unified settings for mesh configuration
from shared.config import get_shared_config


if TYPE_CHECKING:
    from collections.abc import Iterable


DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


@dataclass
class PeerJob:
    peer: str
    job_id: str


class DistributedOrchestrator:
    def __init__(
        self,
        base_url: str | None = None,
        peers: Iterable[str] | None = None,
        downloads_root: Path | None = None,
    ) -> None:
        # Prefer explicit arg, then env, then settings
        settings = get_shared_config()
        cfg_base = getattr(settings, "mesh_base_url", None)
        self.base_url = (
            base_url or os.getenv("SURGIFY_BASE_URL") or (cfg_base or "")
        ).rstrip("/")

        # Seed peers from env and settings, then explicit arg
        env_peers = os.getenv("SURGIFY_PEERS", "")
        initial_peers = [
            p.strip().rstrip("/") for p in env_peers.split(",") if p.strip()
        ]
        cfg_peers = getattr(settings, "mesh_peers", None) or ""
        if cfg_peers:
            initial_peers.extend(
                [p.strip().rstrip("/") for p in cfg_peers.split(",") if p.strip()]
            )
        if peers:
            initial_peers.extend([p.rstrip("/") for p in peers])
        # De-duplicate and drop empty/self
        self.peers = [
            p for p in dict.fromkeys(initial_peers) if p and p != self.base_url
        ]

        self.downloads_root = downloads_root or Path("uploads/deliverables/distributed")
        self.downloads_root.mkdir(parents=True, exist_ok=True)

    async def _submit_pipeline(
        self,
        client: httpx.AsyncClient,
        peer: str,
        file_path: Path,
        config: dict[str, Any],
    ) -> str | None:
        url = f"{peer}/api/v1/pipeline/process-csv"
        data = {"pipeline_config": json.dumps(config)}
        files = {"file": (file_path.name, file_path.read_bytes(), "text/csv")}
        try:
            r = await client.post(url, data=data, files=files)
            r.raise_for_status()
            body = r.json()
            return body.get("job_id")
        except Exception:
            return None

    async def _poll_status(
        self,
        client: httpx.AsyncClient,
        peer: str,
        job_id: str,
        timeout_s: int = 600,
        interval_s: float = 2.5,
    ) -> tuple[bool, dict[str, Any]]:
        deadline = datetime.utcnow() + timedelta(seconds=timeout_s)
        status_url = f"{peer}/api/v1/pipeline/status/{job_id}"
        results_url = f"{peer}/api/v1/pipeline/results/{job_id}"
        last_status: dict[str, Any] = {}
        while datetime.utcnow() < deadline:
            try:
                rs = await client.get(status_url)
                if rs.status_code == 404:
                    await asyncio.sleep(interval_s)
                    continue
                rs.raise_for_status()
                last_status = rs.json()
                if last_status.get("status") == "completed":
                    rr = await client.get(results_url)
                    if rr.is_success:
                        return True, rr.json()
                    return True, last_status
                if last_status.get("status") == "failed":
                    return False, last_status
            except Exception:
                # Ignore transient errors
                pass
            await asyncio.sleep(interval_s)
        return False, last_status

    async def _download_deliverable(
        self, client: httpx.AsyncClient, peer: str, deliverable_id: str, subdir: str
    ) -> Path | None:
        url = f"{peer}/api/v1/deliverables/download/{deliverable_id}"
        try:
            r = await client.get(url)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            content_type = (
                r.headers.get("content-type", "application/octet-stream")
                .split(";")[0]
                .strip()
            )
            disposition = r.headers.get("content-disposition", "")
            # Choose extension
            ext = ".bin"
            if "application/pdf" in content_type:
                ext = ".pdf"
            elif "text/html" in content_type:
                ext = ".html"
            elif "application/json" in content_type:
                ext = ".json"
            # File name
            fname = deliverable_id + ext
            if "filename=" in disposition:
                with contextlib.suppress(Exception):
                    fname = disposition.split("filename=")[-1].strip().strip('"')
            safe_subdir = (
                subdir.replace("://", "_")
                .replace("/", "_")
                .replace(" ", "_")
                .replace(".", "_")
            )
            out_dir = self.downloads_root / safe_subdir
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / fname
            out_path.write_bytes(r.content)
            return out_path
        except Exception:
            return None

    async def _discover_peers_from_mesh(self) -> list[str]:
        """Attempt to fetch peers from local mesh API if base_url is available and running.
        This is best-effort and safe to ignore on failure.
        """
        if not self.base_url:
            return []
        url = f"{self.base_url}/api/mesh/peers"
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0, connect=2.0)
            ) as client:
                r = await client.get(url)
                if not r.is_success:
                    return []
                data = r.json()
                peers = [
                    p.rstrip("/") for p in data.get("peers", []) if isinstance(p, str)
                ]
                # Filter self
                return [p for p in peers if p and p != self.base_url]
        except Exception:
            return []

    async def run_distributed_pipeline(
        self,
        dataset_path: str,
        target_audiences: list[str],
        deliverable_formats: list[str],
        domain: str | None = None,
        include_interactive: bool = False,
        timeout_s: int = 900,
    ) -> dict[str, Any]:
        """Submit a pipeline job to each peer and collect deliverables locally.

        target_audiences: values from AudienceType (e.g., ["executive", "clinical"])
        deliverable_formats: values from DeliverableFormat (e.g., ["pdf", "interactive"]).
        """
        file_path = Path(dataset_path)
        if not file_path.exists():
            msg = f"Dataset not found: {file_path}"
            raise FileNotFoundError(msg)

        # Bootstrap peers if empty
        if not self.peers:
            mesh_peers = await self._discover_peers_from_mesh()
            # De-duplicate preserve order
            seen = set()
            merged: list[str] = []
            for p in mesh_peers:
                if p not in seen:
                    merged.append(p)
                    seen.add(p)
            self.peers = merged

        config = {
            "domain": domain,
            "generate_insights": True,
            "deliverable_formats": deliverable_formats,
            "target_audiences": target_audiences,
            "include_interactive": include_interactive,
        }

        summary: dict[str, Any] = {
            "submitted": [],
            "completed": [],
            "failed": [],
            "downloads": [],
        }

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            # Submit jobs
            jobs: list[PeerJob] = []
            for peer in self.peers:
                job_id = await self._submit_pipeline(client, peer, file_path, config)
                if job_id:
                    jobs.append(PeerJob(peer=peer, job_id=job_id))
                    summary["submitted"].append({"peer": peer, "job_id": job_id})
                else:
                    summary["failed"].append({"peer": peer, "error": "submit_failed"})

            # Poll and collect
            for pj in jobs:
                ok, info = await self._poll_status(
                    client, pj.peer, pj.job_id, timeout_s=timeout_s
                )
                if not ok:
                    summary["failed"].append(
                        {"peer": pj.peer, "job_id": pj.job_id, "info": info}
                    )
                    continue
                summary["completed"].append({"peer": pj.peer, "job_id": pj.job_id})
                # Download any deliverables
                deliverable_ids = []
                try:
                    deliverables_ready = info.get("deliverables_ready") or []
                    if isinstance(deliverables_ready, list):
                        deliverable_ids = deliverables_ready
                except Exception:
                    deliverable_ids = []
                # Subdir for this peer
                subdir = pj.peer
                for did in deliverable_ids:
                    out = await self._download_deliverable(
                        client, pj.peer, did, subdir=subdir
                    )
                    if out:
                        summary["downloads"].append(
                            {"peer": pj.peer, "deliverable_id": did, "path": str(out)}
                        )
        return summary
