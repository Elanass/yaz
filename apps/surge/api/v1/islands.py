"""Islands API - Landing, Indexing, and Interacting Islands
Implements the island architecture pattern for Surgify platform.
"""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/islands", tags=["islands"])


class Island(BaseModel):
    """Base island model."""

    id: str
    name: str
    type: str  # landing, indexing, interacting
    status: str = "active"
    created_at: datetime = datetime.now()
    metadata: dict[str, Any] = {}


class LandingIslandData(BaseModel):
    """Landing island specific data."""

    welcome_message: str
    featured_cases: list[dict[str, Any]] = []
    recent_activity: list[dict[str, Any]] = []
    quick_actions: list[dict[str, str]] = []


class IndexingIslandData(BaseModel):
    """Indexing island specific data."""

    search_query: str | None = None
    filters: dict[str, Any] = {}
    results: list[dict[str, Any]] = []
    pagination: dict[str, int] = {"page": 1, "per_page": 20, "total": 0}


class InteractingIslandData(BaseModel):
    """Interacting island specific data."""

    case_id: str | None = None
    tools: list[str] = []
    active_session: dict[str, Any] = {}
    collaboration: dict[str, Any] = {}


# In-memory island storage (replace with database in production)
islands_store: dict[str, Island] = {}


@router.get("/")
async def list_islands():
    """Get all active islands."""
    return {"islands": list(islands_store.values()), "count": len(islands_store)}


@router.get("/landing")
async def get_landing_island():
    """Get the landing island - main entry point."""
    island_data = LandingIslandData(
        welcome_message="Welcome to Surgify - AI-Powered Surgical Platform",
        featured_cases=[
            {
                "id": "case_001",
                "title": "Gastric Cancer Analysis",
                "type": "Oncology",
                "status": "In Progress",
                "thumbnail": "/static/images/surgery-1.svg",
            },
            {
                "id": "case_002",
                "title": "Laparoscopic Procedure",
                "type": "General Surgery",
                "status": "Completed",
                "thumbnail": "/static/images/surgery-2.svg",
            },
        ],
        recent_activity=[
            {
                "action": "Case Analysis Completed",
                "case": "Gastric ADCI Study",
                "time": "2 minutes ago",
                "user": "Dr. Smith",
            },
            {
                "action": "New Collaboration Started",
                "case": "Multi-center Study",
                "time": "15 minutes ago",
                "user": "Research Team",
            },
        ],
        quick_actions=[
            {"label": "New Analysis", "url": "/surgify", "icon": "fas fa-plus-circle"},
            {"label": "Browse Cases", "url": "/dashboard", "icon": "fas fa-search"},
            {
                "label": "Workstation",
                "url": "/workstation",
                "icon": "fas fa-briefcase-medical",
            },
            {"label": "Get Mobile App", "url": "/get-app", "icon": "fas fa-mobile-alt"},
        ],
    )

    island = Island(
        id="landing_main",
        name="Landing Island",
        type="landing",
        metadata=island_data.dict(),
    )

    islands_store[island.id] = island
    return island


@router.get("/indexing")
async def get_indexing_island(
    query: str | None = None, page: int = 1, per_page: int = 20
):
    """Get the indexing island - search and discovery."""
    # Simulate search results based on query
    mock_results = []
    if query:
        mock_results = [
            {
                "id": f"result_{i}",
                "title": f"Surgical Case {i}: {query} Analysis",
                "type": "Case Study",
                "relevance": 0.95 - (i * 0.1),
                "preview": f"Analysis of {query} related surgical procedures...",
                "metadata": {
                    "procedure_type": "Laparoscopic",
                    "complexity": "Medium",
                    "duration": "2.5 hours",
                },
            }
            for i in range(1, min(per_page + 1, 11))
        ]

    island_data = IndexingIslandData(
        search_query=query,
        filters={"procedure_type": [], "complexity": [], "date_range": {}},
        results=mock_results,
        pagination={
            "page": page,
            "per_page": per_page,
            "total": len(mock_results) if query else 0,
        },
    )

    island = Island(
        id="indexing_search",
        name="Indexing Island",
        type="indexing",
        metadata=island_data.dict(),
    )

    islands_store[island.id] = island
    return island


@router.get("/interacting/{case_id}")
async def get_interacting_island(case_id: str):
    """Get the interacting island - active work environment."""
    island_data = InteractingIslandData(
        case_id=case_id,
        tools=[
            "AI Analysis Engine",
            "Medical Image Viewer",
            "Collaboration Chat",
            "Decision Support System",
            "Report Generator",
        ],
        active_session={
            "session_id": f"session_{case_id}",
            "started_at": datetime.now().isoformat(),
            "participants": ["Dr. Smith", "AI Assistant"],
            "status": "active",
        },
        collaboration={
            "team_members": [
                {"name": "Dr. Smith", "role": "Lead Surgeon", "online": True},
                {"name": "Dr. Johnson", "role": "Radiologist", "online": False},
                {"name": "AI Assistant", "role": "Decision Support", "online": True},
            ],
            "shared_notes": f"Analysis in progress for case {case_id}",
            "real_time_updates": True,
        },
    )

    island = Island(
        id=f"interacting_{case_id}",
        name=f"Interacting Island - {case_id}",
        type="interacting",
        metadata=island_data.dict(),
    )

    islands_store[island.id] = island
    return island


@router.post("/landing/update")
async def update_landing_island(data: LandingIslandData):
    """Update landing island data."""
    island_id = "landing_main"
    if island_id in islands_store:
        islands_store[island_id].metadata = data.dict()
        return {"message": "Landing island updated", "island": islands_store[island_id]}
    raise HTTPException(status_code=404, detail="Landing island not found")


@router.post("/indexing/search")
async def perform_search(query: str, filters: dict[str, Any] | None = None):
    """Perform search operation in indexing island."""
    # Simulate async search
    if filters is None:
        filters = {}
    await asyncio.sleep(0.1)

    results = [
        {
            "id": f"search_result_{i}",
            "title": f"Surgical Case: {query} - Result {i}",
            "type": "Medical Case",
            "score": 0.9 - (i * 0.1),
            "highlight": f"...{query} related findings...",
            "url": f"/cases/result_{i}",
        }
        for i in range(1, 6)
    ]

    return {
        "query": query,
        "filters": filters,
        "results": results,
        "total": len(results),
        "search_time": "0.1s",
    }


@router.post("/interacting/{case_id}/action")
async def perform_case_action(
    case_id: str, action: str, payload: dict[str, Any] | None = None
):
    """Perform action in interacting island."""
    # Simulate different actions
    if payload is None:
        payload = {}
    if action == "analyze":
        return {
            "case_id": case_id,
            "action": "analyze",
            "result": "AI analysis initiated",
            "progress": 0,
            "estimated_time": "5 minutes",
        }
    if action == "collaborate":
        return {
            "case_id": case_id,
            "action": "collaborate",
            "result": "Collaboration session started",
            "participants": payload.get("participants", []),
        }
    if action == "export":
        return {
            "case_id": case_id,
            "action": "export",
            "result": "Export prepared",
            "download_url": f"/api/v1/cases/{case_id}/export",
        }
    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


@router.websocket("/interacting/{case_id}/ws")
async def websocket_endpoint(websocket, case_id: str) -> None:
    """WebSocket endpoint for real-time collaboration in interacting island."""
    await websocket.accept()

    try:
        while True:
            # Listen for incoming messages
            data = await websocket.receive_text()

            # Echo back with case context
            response = {
                "case_id": case_id,
                "message": data,
                "timestamp": datetime.now().isoformat(),
                "type": "collaboration_update",
            }

            await websocket.send_json(response)

    except Exception:
        pass
    finally:
        await websocket.close()


@router.get("/health")
async def islands_health():
    """Health check for islands system."""
    return {
        "status": "healthy",
        "islands_count": len(islands_store),
        "active_islands": [
            {"id": island.id, "type": island.type, "status": island.status}
            for island in islands_store.values()
        ],
        "timestamp": datetime.now().isoformat(),
    }
