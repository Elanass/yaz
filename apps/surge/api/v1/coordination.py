"""
Enhanced HTMX Router with Dash/Interact Coordination
Provides coordinated endpoints for seamless project integration
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("surge.coordination")
router = APIRouter(prefix="/htmx", tags=["htmx-coordination"])

# Coordination state management
coordination_state = {
    "dash": {},
    "interact": {}, 
    "islands": {},
    "templates": {}
}

@router.post("/coordinate/dash")
async def coordinate_dash_action(request: Request, action: str, data: Dict[str, Any] = None):
    """Coordinate action from Dash project"""
    try:
        logger.info(f"Coordinating Dash action: {action}")
        
        # Store action in coordination state
        if "actions" not in coordination_state["dash"]:
            coordination_state["dash"]["actions"] = []
        
        coordination_state["dash"]["actions"].append({
            "action": action,
            "data": data,
            "timestamp": "now"
        })
        
        # Process coordination logic
        coordination_result = await process_dash_coordination(action, data)
        
        return {
            "status": "success",
            "action": action,
            "result": coordination_result,
            "template_updates": get_template_updates_for_dash(action, data)
        }
        
    except Exception as e:
        logger.error(f"Dash coordination error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coordinate/interact")
async def coordinate_interact_action(request: Request, action: str, data: Dict[str, Any] = None):
    """Coordinate action from Interact project"""
    try:
        logger.info(f"Coordinating Interact action: {action}")
        
        # Store action in coordination state
        if "actions" not in coordination_state["interact"]:
            coordination_state["interact"]["actions"] = []
        
        coordination_state["interact"]["actions"].append({
            "action": action,
            "data": data,
            "timestamp": "now"
        })
        
        # Process coordination logic
        coordination_result = await process_interact_coordination(action, data)
        
        return {
            "status": "success",
            "action": action,
            "result": coordination_result,
            "template_updates": get_template_updates_for_interact(action, data)
        }
        
    except Exception as e:
        logger.error(f"Interact coordination error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coordinate/island")
async def coordinate_island_action(request: Request, island_id: str, action: str, data: Dict[str, Any] = None):
    """Coordinate action from React island"""
    try:
        logger.info(f"Coordinating island action: {island_id} -> {action}")
        
        # Store island action
        if island_id not in coordination_state["islands"]:
            coordination_state["islands"][island_id] = {"actions": []}
        
        coordination_state["islands"][island_id]["actions"].append({
            "action": action,
            "data": data,
            "timestamp": "now"
        })
        
        # Process island coordination
        coordination_result = await process_island_coordination(island_id, action, data)
        
        return {
            "status": "success",
            "island_id": island_id,
            "action": action,
            "result": coordination_result,
            "template_updates": get_template_updates_for_island(island_id, action, data)
        }
        
    except Exception as e:
        logger.error(f"Island coordination error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/coordination/state")
async def get_coordination_state():
    """Get current coordination state"""
    return {
        "coordination_state": coordination_state,
        "active_projects": {
            "dash": len(coordination_state["dash"]),
            "interact": len(coordination_state["interact"]),
            "islands": len(coordination_state["islands"])
        }
    }

@router.post("/sync/projects")
async def sync_projects(request: Request, projects: List[str] = ["dash", "interact"]):
    """Synchronize state between projects"""
    try:
        sync_result = {}
        
        for project in projects:
            if project in coordination_state:
                sync_result[project] = await sync_project_state(project)
            else:
                sync_result[project] = {"status": "not_found"}
        
        return {
            "status": "success",
            "sync_result": sync_result,
            "timestamp": "now"
        }
        
    except Exception as e:
        logger.error(f"Project sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Coordination processing functions
async def process_dash_coordination(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process coordination logic for Dash actions"""
    
    if action == "case_selected":
        # Coordinate with Interact for patient details
        return {
            "forward_to": ["interact"],
            "action": "load_patient_details",
            "data": data
        }
    elif action == "schedule_updated":
        # Update calendar island and Interact
        return {
            "forward_to": ["calendar", "interact"],
            "action": "refresh_schedule",
            "data": data
        }
    elif action == "analytics_filter":
        # Update relevant islands
        return {
            "forward_to": ["or-board"],
            "action": "apply_filter",
            "data": data
        }
    
    return {"status": "processed", "action": action}

async def process_interact_coordination(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process coordination logic for Interact actions"""
    
    if action == "patient_updated":
        # Forward to Dash for case management
        return {
            "forward_to": ["dash"],
            "action": "refresh_patient_data",
            "data": data
        }
    elif action == "form_submitted":
        # Update relevant islands and Dash
        return {
            "forward_to": ["dash", "calendar"],
            "action": "process_form_data",
            "data": data
        }
    elif action == "communication_sent":
        # Update notification systems
        return {
            "forward_to": ["dash"],
            "action": "update_notifications",
            "data": data
        }
    
    return {"status": "processed", "action": action}

async def process_island_coordination(island_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process coordination logic for island actions"""
    
    if action == "navigate":
        # Coordinate navigation across projects
        return {
            "forward_to": ["dash", "interact"],
            "action": "sync_navigation",
            "data": {"path": data.get("path"), "source": island_id}
        }
    elif action == "state_change":
        # Synchronize state across related components
        return {
            "forward_to": get_related_components(island_id),
            "action": "sync_state",
            "data": data
        }
    
    return {"status": "processed", "island_id": island_id}

async def sync_project_state(project: str) -> Dict[str, Any]:
    """Synchronize state for a specific project"""
    
    if project == "dash":
        return {
            "status": "synced",
            "actions_count": len(coordination_state["dash"].get("actions", [])),
            "last_sync": "now"
        }
    elif project == "interact":
        return {
            "status": "synced", 
            "actions_count": len(coordination_state["interact"].get("actions", [])),
            "last_sync": "now"
        }
    
    return {"status": "unknown_project"}

# Template update helpers
def get_template_updates_for_dash(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Get template updates for Dash actions"""
    return {
        "partial_updates": {
            "cases-list": f"/htmx/partials/cases?action={action}",
            "dashboard-stats": f"/htmx/partials/stats?action={action}"
        }
    }

def get_template_updates_for_interact(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Get template updates for Interact actions"""
    return {
        "partial_updates": {
            "patient-panel": f"/htmx/partials/patient?action={action}",
            "forms-section": f"/htmx/partials/forms?action={action}"
        }
    }

def get_template_updates_for_island(island_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Get template updates for island actions"""
    return {
        "partial_updates": {
            f"{island_id}-status": f"/htmx/partials/island/{island_id}?action={action}"
        }
    }

def get_related_components(island_id: str) -> List[str]:
    """Get components related to an island for coordination"""
    
    relations = {
        "calendar": ["dash", "interact"],
        "or-board": ["dash"],
        "cases-list": ["dash", "interact"],
        "patient-panel": ["interact"],
        "dashboard": ["dash"]
    }
    
    return relations.get(island_id, [])

# Enhanced partial endpoints with coordination
@router.get("/partials/coordinated-cases")
async def coordinated_cases_partial(request: Request, project: str = None, action: str = None):
    """Enhanced cases partial with project coordination"""
    
    # Get coordination context
    coordination_context = {
        "project": project,
        "action": action,
        "dash_state": coordination_state.get("dash", {}),
        "interact_state": coordination_state.get("interact", {})
    }
    
    # Mock coordinated cases data
    cases = [
        {
            "id": "C001",
            "patient": "John Doe",
            "procedure": "Laparoscopic Cholecystectomy", 
            "status": "scheduled",
            "or_room": "OR-1",
            "dash_data": {"priority": "high", "team_assigned": True},
            "interact_data": {"consent_status": "completed", "forms_ready": True}
        },
        {
            "id": "C002", 
            "patient": "Jane Smith",
            "procedure": "Appendectomy",
            "status": "in_progress",
            "or_room": "OR-2",
            "dash_data": {"priority": "urgent", "team_assigned": True},
            "interact_data": {"consent_status": "pending", "forms_ready": False}
        }
    ]
    
    return {
        "cases": cases,
        "coordination_context": coordination_context,
        "template": "partials/coordinated_cases.html"
    }

@router.get("/partials/project-status")
async def project_status_partial(request: Request):
    """Get coordinated project status"""
    
    return {
        "dash_status": {
            "active": True,
            "components": ["OperationalSurgePlatform", "CaseManagement"],
            "last_action": coordination_state.get("dash", {}).get("actions", [])[-1:] 
        },
        "interact_status": {
            "active": True,
            "components": ["InteractApp", "PatientForms"],
            "last_action": coordination_state.get("interact", {}).get("actions", [])[-1:]
        },
        "islands_status": {
            "active_count": len(coordination_state.get("islands", {})),
            "islands": list(coordination_state.get("islands", {}).keys())
        }
    }
