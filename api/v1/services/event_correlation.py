"""
API endpoints for the event correlation service.

These endpoints provide access to the event correlation engine for
viewing correlated events, rules, and alerts.
"""

from typing import Dict, Any, List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel

from core.models.base import UserIdentity
from core.services.logger import get_logger
from services.event_correlation.service import (
    correlation_engine,
    CorrelationRule,
    CorrelatedEvent
)
from api.v1.auth import get_current_active_user

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/correlations",
    tags=["correlations"],
    responses={404: {"description": "Not found"}},
)

class CorrelationQuery(BaseModel):
    """Query parameters for correlation filtering."""
    severity: Optional[str] = None
    requires_action: Optional[bool] = None
    status: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    limit: int = 100
    offset: int = 0

class UpdateStatusRequest(BaseModel):
    """Request for updating correlated event status."""
    status: str
    assigned_to: Optional[str] = None


@router.get("/", response_model=List[CorrelatedEvent])
async def get_correlated_events(
    query: CorrelationQuery = Depends(),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get correlated events based on filter criteria.
    """
    events = await correlation_engine.get_correlated_events(
        severity=query.severity,
        requires_action=query.requires_action,
        status=query.status,
        start_time=query.start_time,
        end_time=query.end_time,
        limit=query.limit,
        offset=query.offset
    )
    return events

@router.get("/rules", response_model=List[CorrelationRule])
async def get_correlation_rules(
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get all correlation rules.
    """
    # Check if user has admin privileges
    if not current_user.has_role("admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view correlation rules"
        )
    
    return correlation_engine.rules

@router.post("/rules", response_model=CorrelationRule)
async def add_correlation_rule(
    rule: CorrelationRule,
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Add a new correlation rule.
    """
    # Check if user has admin privileges
    if not current_user.has_role("admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add correlation rules"
        )
    
    correlation_engine.add_rule(rule)
    return rule

@router.delete("/rules/{rule_id}", response_model=Dict[str, Any])
async def remove_correlation_rule(
    rule_id: str = Path(..., description="The ID of the rule to remove"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Remove a correlation rule.
    """
    # Check if user has admin privileges
    if not current_user.has_role("admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to remove correlation rules"
        )
    
    # Check if the rule exists
    rule = next((r for r in correlation_engine.rules if r.id == rule_id), None)
    if not rule:
        raise HTTPException(
            status_code=404,
            detail=f"Rule {rule_id} not found"
        )
    
    correlation_engine.remove_rule(rule_id)
    
    return {
        "status": "success",
        "message": f"Rule {rule_id} removed successfully"
    }

@router.get("/{correlation_id}", response_model=CorrelatedEvent)
async def get_correlated_event(
    correlation_id: str = Path(..., description="The ID of the correlated event to retrieve"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get a specific correlated event by ID.
    """
    events = await correlation_engine.get_correlated_events()
    event = next((e for e in events if e.correlation_id == correlation_id), None)
    
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Correlated event {correlation_id} not found"
        )
    
    return event

@router.put("/{correlation_id}/status", response_model=CorrelatedEvent)
async def update_correlation_status(
    correlation_id: str = Path(..., description="The ID of the correlated event to update"),
    request: UpdateStatusRequest = Body(..., description="The status update"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Update the status of a correlated event.
    """
    # If assigned_to is not specified, assign to current user
    assigned_to = request.assigned_to or current_user.id
    
    updated_event = await correlation_engine.update_correlated_event_status(
        correlation_id=correlation_id,
        status=request.status,
        assigned_to=assigned_to
    )
    
    if not updated_event:
        raise HTTPException(
            status_code=404,
            detail=f"Correlated event {correlation_id} not found"
        )
    
    return updated_event

@router.get("/{correlation_id}/events", response_model=List[Dict[str, Any]])
async def get_correlation_events(
    correlation_id: str = Path(..., description="The ID of the correlated event"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get the individual events that make up a correlation.
    """
    # First get the correlated event
    events = await correlation_engine.get_correlated_events()
    correlated_event = next((e for e in events if e.correlation_id == correlation_id), None)
    
    if not correlated_event:
        raise HTTPException(
            status_code=404,
            detail=f"Correlated event {correlation_id} not found"
        )
    
    # This would normally fetch the individual events from the event logger
    # For now, we'll return a placeholder
    
    return [
        {"event_id": event_id, "summary": f"Event {event_id}", "timestamp": datetime.datetime.utcnow().isoformat()}
        for event_id in correlated_event.events
    ]
