"""
API endpoints for the event logger service.

These endpoints provide access to the event logger functionality for
retrieving and querying audit logs.
"""

from typing import Dict, Any, List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel

from core.models.base import UserIdentity
from core.services.logger import get_logger
from services.event_logger.service import (
    event_logger,
    EventLog,
    EventSeverity,
    EventCategory
)
from api.v1.auth import get_current_active_user

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)

class EventQuery(BaseModel):
    """Query parameters for event filtering."""
    category: Optional[str] = None
    severity: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    limit: int = 100
    offset: int = 0

@router.get("/", response_model=List[EventLog])
async def get_events(
    query: EventQuery = Depends(),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get events based on filter criteria.
    
    This endpoint requires administrative privileges for accessing
    events that don't belong to the current user.
    """
    # Check if user has permission to view these events
    if (query.provider_id and query.provider_id != current_user.id and 
        not current_user.has_role("admin")):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view events for other providers"
        )
    
    # Convert query to filters
    filters = {
        k: v for k, v in query.dict().items() 
        if v is not None and k not in ['limit', 'offset']
    }
    
    # Query events
    events = await event_logger.query_events(
        filters=filters,
        start_time=query.start_time,
        end_time=query.end_time,
        limit=query.limit,
        offset=query.offset
    )
    
    return events

@router.get("/categories", response_model=List[str])
async def get_event_categories(
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """Get the list of available event categories."""
    # This returns all event categories from the EventCategory enum
    categories = [
        EventCategory.AUTHENTICATION,
        EventCategory.AUTHORIZATION,
        EventCategory.DATA_ACCESS,
        EventCategory.DATA_MODIFICATION,
        EventCategory.CLINICAL_DECISION,
        EventCategory.PROTOCOL_DEVIATION,
        EventCategory.SYSTEM,
        EventCategory.SECURITY,
        EventCategory.COMPLIANCE,
        EventCategory.PATIENT_CARE
    ]
    return categories

@router.get("/severities", response_model=List[str])
async def get_event_severities(
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """Get the list of available event severities."""
    # This returns all event severities from the EventSeverity enum
    severities = [
        EventSeverity.DEBUG,
        EventSeverity.INFO,
        EventSeverity.WARNING,
        EventSeverity.ERROR,
        EventSeverity.CRITICAL,
        EventSeverity.ALERT
    ]
    return severities

@router.get("/{event_id}", response_model=EventLog)
async def get_event(
    event_id: str = Path(..., description="The ID of the event to retrieve"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get a specific event by ID.
    
    This endpoint requires administrative privileges for accessing
    events that don't belong to the current user.
    """
    # Query the event
    events = await event_logger.query_events(
        filters={"id": event_id},
        limit=1
    )
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found"
        )
    
    event = events[0]
    
    # Check if user has permission to view this event
    if (event.context.provider_id and 
        event.context.provider_id != current_user.id and 
        not current_user.has_role("admin")):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this event"
        )
    
    return event

@router.get("/{event_id}/verify", response_model=Dict[str, Any])
async def verify_event_integrity(
    event_id: str = Path(..., description="The ID of the event to verify"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Verify the integrity of an event.
    
    This endpoint checks the cryptographic hash of the event to ensure
    it hasn't been tampered with. For IPFS-stored events, it also
    verifies against the blockchain.
    """
    # First get the event
    events = await event_logger.query_events(
        filters={"id": event_id},
        limit=1
    )
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found"
        )
    
    event = events[0]
    
    # Check if user has permission to view this event
    if (event.context.provider_id and 
        event.context.provider_id != current_user.id and 
        not current_user.has_role("admin")):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to verify this event"
        )
    
    # Verify integrity
    is_valid = await event_logger.verify_event_integrity(event_id)
    
    return {
        "event_id": event_id,
        "integrity_valid": is_valid,
        "ipfs_verified": event.ipfs_cid is not None,
        "verification_time": datetime.datetime.utcnow().isoformat()
    }

# Add more endpoints for specific event logging needs
