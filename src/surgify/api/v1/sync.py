"""
Sync API - Surgify Platform
Handles data synchronization, messaging, and inter-service communication
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from surgify.core.database import get_db
from surgify.core.services.sync_service import (
    SyncService,
    SyncRequest,
    MessageRequest,
    SyncResponse,
    MessageResponse,
    SyncStatus,
    MessageType
)
from surgify.core.services.auth_service import get_current_user
from surgify.core.models.user import User
from surgify.core.cache import cache_list_endpoint, cache_detail_endpoint, invalidate_cache

router = APIRouter(tags=["Sync"])

def get_sync_service(db: Session = Depends(get_db)) -> SyncService:
    """Dependency to get sync service instance"""
    return SyncService(db)

# Sync Job Endpoints

@router.post("/jobs", response_model=SyncResponse, status_code=status.HTTP_201_CREATED)
async def create_sync_job(
    request: SyncRequest,
    sync_service: SyncService = Depends(get_sync_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new data synchronization job.
    
    This endpoint is **stateless** - it doesn't maintain any in-process state.
    Each request creates a new sync job that runs independently.
    
    **Sync Types:**
    - full: Complete data synchronization
    - incremental: Sync only changes since last sync
    - delta: Sync specific changes based on timestamps
    
    **Resource Types:**
    - cases: Surgical case data
    - users: User information
    - protocols: Surgical protocols
    - reports: Generated reports
    
    **Priority Levels:**
    - low: Background synchronization
    - medium: Standard priority (default)
    - high: Expedited processing
    - urgent: Immediate processing
    
    **Response:**
    Returns the created sync job with unique ID and initial status.
    The job will be processed asynchronously.
    """
    try:
        job = await sync_service.create_sync_job(request, current_user.username)
        
        # Invalidate related caches
        await invalidate_cache("sync_jobs")
        
        return job
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sync job: {str(e)}"
        )

@router.get("/jobs", response_model=List[SyncResponse])
@cache_list_endpoint("sync_jobs", ttl=30)  # Cache for 30 seconds
async def list_sync_jobs(
    status: Optional[SyncStatus] = Query(None, description="Filter by job status"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    target_system: Optional[str] = Query(None, description="Filter by target system"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sync_service: SyncService = Depends(get_sync_service)
):
    """
    List synchronization jobs with filtering and pagination.
    
    This endpoint is **stateless** and **idempotent** - multiple calls with the same
    parameters will return the same results. Results are cached for performance.
    
    **Filtering Options:**
    - status: Filter by job status (pending, in_progress, completed, failed, cancelled)
    - resource_type: Filter by resource type being synchronized
    - target_system: Filter by destination system
    
    **Job Statuses:**
    - pending: Job created but not yet started
    - in_progress: Job currently running
    - completed: Job finished successfully
    - failed: Job encountered an error
    - cancelled: Job was manually cancelled
    
    **Response:**
    Returns paginated list of sync jobs with current status and progress information.
    """
    try:
        jobs = await sync_service.list_sync_jobs(
            status=status,
            resource_type=resource_type,
            target_system=target_system,
            page=page,
            limit=limit
        )
        
        return jobs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sync jobs: {str(e)}"
        )

@router.get("/jobs/{job_id}", response_model=SyncResponse)
@cache_detail_endpoint("sync_jobs", ttl=10)  # Cache for 10 seconds
async def get_sync_job(
    job_id: str,
    sync_service: SyncService = Depends(get_sync_service)
):
    """
    Get details of a specific synchronization job.
    
    This endpoint is **stateless** and **idempotent** - multiple calls will
    return the same result for the current job state.
    
    **Response:**
    Returns complete job details including:
    - Current status and progress (0-100%)
    - Start and completion timestamps
    - Error messages (if any)
    - Metadata and configuration
    """
    try:
        job = await sync_service.get_sync_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sync job with ID {job_id} not found"
            )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sync job: {str(e)}"
        )

@router.put("/jobs/{job_id}/cancel", response_model=dict)
async def cancel_sync_job(
    job_id: str,
    sync_service: SyncService = Depends(get_sync_service),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running or pending synchronization job.
    
    This endpoint is **idempotent** - multiple cancel requests for the same
    job will have the same effect.
    
    **Cancellation Rules:**
    - Only pending or in_progress jobs can be cancelled
    - Completed or failed jobs cannot be cancelled
    - Already cancelled jobs remain cancelled
    
    **Response:**
    Returns success status and updated job information.
    """
    try:
        cancelled = await sync_service.cancel_sync_job(job_id)
        
        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel sync job {job_id} - job not found or not cancellable"
            )
        
        # Invalidate related caches
        await invalidate_cache("sync_jobs")
        await invalidate_cache("sync_jobs", id=job_id)
        
        return {"success": True, "message": f"Sync job {job_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling sync job: {str(e)}"
        )

# Message Endpoints

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    request: MessageRequest,
    sync_service: SyncService = Depends(get_sync_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new message for system communication.
    
    This endpoint is **stateless** - each request creates a new message
    independently without maintaining any in-process state.
    
    **Message Types:**
    - case_update: Case-related notifications
    - user_action: User action notifications
    - system_alert: System alerts and warnings
    - sync_request: Synchronization requests
    - notification: General notifications
    
    **Priority Levels:**
    - low: Informational messages
    - medium: Standard notifications (default)
    - high: Important messages
    - urgent: Critical alerts requiring immediate attention
    
    **Response:**
    Returns the created message with unique ID and metadata.
    """
    try:
        message = await sync_service.create_message(request, current_user.username)
        
        # Invalidate related caches
        await invalidate_cache("messages")
        
        return message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/messages", response_model=List[MessageResponse])
@cache_list_endpoint("messages", ttl=30)  # Cache for 30 seconds
async def list_messages(
    recipient_id: Optional[str] = Query(None, description="Filter by recipient ID"),
    type: Optional[MessageType] = Query(None, description="Filter by message type"),
    status: Optional[str] = Query(None, description="Filter by message status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sync_service: SyncService = Depends(get_sync_service)
):
    """
    List messages with filtering and pagination.
    
    This endpoint is **stateless** and **idempotent** - multiple calls with the same
    parameters will return the same results. Results are cached for performance.
    
    **Filtering Options:**
    - recipient_id: Filter messages for specific recipient
    - type: Filter by message type
    - status: Filter by read/unread status
    
    **Message Status:**
    - unread: Message not yet read
    - read: Message has been read
    
    **Automatic Cleanup:**
    Expired messages are automatically filtered out from results.
    
    **Response:**
    Returns paginated list of messages sorted by creation time (newest first).
    """
    try:
        messages = await sync_service.list_messages(
            recipient_id=recipient_id,
            type=type,
            status=status,
            page=page,
            limit=limit
        )
        
        return messages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )

@router.get("/messages/{message_id}", response_model=MessageResponse)
@cache_detail_endpoint("messages", ttl=60)  # Cache for 1 minute
async def get_message(
    message_id: str,
    sync_service: SyncService = Depends(get_sync_service)
):
    """
    Get details of a specific message.
    
    This endpoint is **stateless** and **idempotent** - multiple calls will
    return the same message content.
    
    **Expiration Handling:**
    Returns 404 if the message has expired based on its expires_at timestamp.
    
    **Response:**
    Returns complete message details including content, metadata, and timestamps.
    """
    try:
        message = await sync_service.get_message(message_id)
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID {message_id} not found or expired"
            )
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving message: {str(e)}"
        )

@router.put("/messages/{message_id}/read", response_model=dict)
async def mark_message_read(
    message_id: str,
    sync_service: SyncService = Depends(get_sync_service),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a message as read.
    
    This endpoint is **idempotent** - multiple requests to mark the same
    message as read will have the same effect.
    
    **Status Changes:**
    - Changes message status from "unread" to "read"
    - Sets read_at timestamp to current time
    - If already read, no changes are made
    
    **Response:**
    Returns success status and confirmation message.
    """
    try:
        marked = await sync_service.mark_message_read(message_id, current_user.username)
        
        if not marked:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID {message_id} not found or already read"
            )
        
        # Invalidate related caches
        await invalidate_cache("messages")
        await invalidate_cache("messages", id=message_id)
        
        return {"success": True, "message": f"Message {message_id} marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking message as read: {str(e)}"
        )

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str,
    sync_service: SyncService = Depends(get_sync_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a message.
    
    This endpoint is **idempotent** - multiple delete requests for the same
    message will have the same effect.
    
    **Warning:**
    This operation permanently removes the message and cannot be undone.
    
    **Response:**
    Returns 204 No Content on successful deletion.
    Returns 404 Not Found if the message doesn't exist.
    """
    try:
        deleted = await sync_service.delete_message(message_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID {message_id} not found"
            )
        
        # Invalidate related caches
        await invalidate_cache("messages")
        await invalidate_cache("messages", id=message_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        )

# Status Endpoints

@router.get("/status/{resource_type}", response_model=dict)
async def get_sync_status(
    resource_type: str,
    resource_id: Optional[str] = Query(None, description="Specific resource ID"),
    sync_service: SyncService = Depends(get_sync_service)
):
    """
    Get synchronization status for a resource type.
    
    This endpoint is **stateless** and **idempotent** - it provides current
    sync status information without modifying any state.
    
    **Resource Types:**
    - cases: Surgical case synchronization status
    - users: User data synchronization status
    - protocols: Protocol synchronization status
    - reports: Report synchronization status
    
    **Response:**
    Returns sync status information including:
    - Current sync status
    - Last successful sync timestamp
    - Progress information
    - Error details (if any)
    """
    try:
        status_info = await sync_service.get_sync_status(resource_type, resource_id)
        
        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            **status_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sync status: {str(e)}"
        )

@router.get("/health", response_model=dict)
async def get_sync_health(
    sync_service: SyncService = Depends(get_sync_service)
):
    """
    Get sync service health status.
    
    This endpoint is **stateless** and **idempotent** - it provides current
    service health information for monitoring and diagnostics.
    
    **Response:**
    Returns service health metrics including:
    - Service status
    - Active sync job count
    - Message queue statistics
    - Performance metrics
    """
    try:
        health_info = await sync_service.health_check()
        return health_info
        
    except Exception as e:
        return {
            "service": "SyncService",
            "status": "error",
            "error": str(e)
        }
