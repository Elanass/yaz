"""FastAPI router exposing lightweight HTTP mesh endpoints for peer discovery and
simple deliverable visibility/sync. Works with MeshManager.

Endpoints (mounted at /api/mesh):
- GET    /status           -> node info + last sync
- GET    /peers            -> list known peers
- POST   /announce         -> accept peer announcement and merge
- GET    /deliverables     -> list local deliverables metadata
- GET    /file?rel=path    -> download a file by relative path under deliverables root

This API is intentionally minimal and dependency-light.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse


logger = logging.getLogger(__name__)

router = APIRouter()


def _get_manager(request: Request):
    mgr = getattr(request.app.state, "mesh_manager", None)
    if mgr is None:
        raise HTTPException(status_code=503, detail="Mesh manager not initialized")
    return mgr


@router.get("/status")
async def mesh_status(request: Request) -> dict[str, Any]:
    mgr = _get_manager(request)
    return mgr.to_dict()


@router.get("/peers")
async def mesh_peers(request: Request) -> dict[str, Any]:
    mgr = _get_manager(request)
    return {
        "node_id": mgr.node_id,
        "base_url": mgr.base_url,
        "peers": sorted(mgr.peers),
    }


@router.post("/announce")
async def mesh_announce(request: Request, payload: dict[str, Any]):
    """Accept peer announcement and merge peer list.
    Expected payload: { node_id: str, base_url: str, peers?: List[str] }.
    """
    mgr = _get_manager(request)

    base_url = (payload or {}).get("base_url")
    peers: list[str] = (payload or {}).get("peers", []) or []

    if not base_url:
        raise HTTPException(status_code=400, detail="base_url is required")

    added = mgr.add_peer(base_url)
    merged = 0
    for p in peers:
        if mgr.add_peer(p):
            merged += 1

    logger.info(f"📣 Mesh announce from {base_url} added={added} merged={merged}")
    return mgr.to_dict()


@router.get("/deliverables")
async def mesh_deliverables(request: Request) -> dict[str, Any]:
    mgr = _get_manager(request)
    metas = [asdict(m) for m in mgr.list_deliverables()]
    return {"count": len(metas), "items": metas}


@router.get("/file")
async def mesh_file(request: Request, rel: str):
    _get_manager(request)
    # Search for the file under known roots
    for root in [Path("uploads/deliverables"), Path("data/uploads/deliverables")]:
        candidate = (root / rel).resolve()
        try:
            # Prevent path traversal by ensuring candidate is within root
            if not str(candidate).startswith(str(root.resolve())):
                continue
            if candidate.exists() and candidate.is_file():
                return FileResponse(str(candidate))
        except Exception:
            continue
    raise HTTPException(status_code=404, detail="File not found")


@router.post("/sync")
async def mesh_sync(request: Request) -> dict[str, Any]:
    mgr = _get_manager(request)
    await mgr.sync_once()
    return {"ok": True, "last_sync": mgr.last_sync, "peers": sorted(mgr.peers)}
