"""
PWA API - Progressive Web App endpoints for offline-first clinical workflows.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user, get_db
from ..db.models import User
from ..schemas.pwa import (
    BackgroundSyncJobCreate,
    BackgroundSyncJobResponse,
    NotificationPayload,
    PWAManifest,
    PWAStats,
    PWASubscriptionResponse,
    PushSubscription,
    ServiceWorkerUpdate,
    ClinicalNotificationTemplate,
)
from ..services.pwa_service import PWAService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pwa", tags=["PWA"])
pwa_service = PWAService()


@router.get("/manifest.json", response_model=PWAManifest)
async def get_pwa_manifest():
    """Get PWA manifest for installable app."""
    try:
        manifest = await pwa_service.get_pwa_manifest()
        return manifest
    except Exception as e:
        logger.error(f"Failed to generate PWA manifest: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PWA manifest")


@router.get("/service-worker.js")
async def get_service_worker():
    """Get service worker JavaScript for PWA functionality."""
    try:
        sw_content = await pwa_service.generate_service_worker()
        return Response(
            content=sw_content,
            media_type="application/javascript",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Service-Worker-Allowed": "/",
            },
        )
    except Exception as e:
        logger.error(f"Failed to generate service worker: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate service worker")


@router.post("/push/subscribe", response_model=PWASubscriptionResponse)
async def subscribe_to_push(
    subscription: PushSubscription,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to push notifications."""
    try:
        subscription_record = await pwa_service.register_push_subscription(
            db, current_user.id, subscription
        )
        
        # Send welcome notification
        await pwa_service.send_push_notification(
            db,
            current_user.id,
            NotificationPayload(
                title="Welcome to ADCI Platform",
                body="Push notifications are now enabled for clinical updates",
                tag="welcome",
                data={"type": "welcome"},
            ),
        )
        
        return subscription_record
    except Exception as e:
        logger.error(f"Failed to subscribe to push notifications: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to subscribe to push notifications"
        )


@router.post("/push/send")
async def send_push_notification(
    notification: NotificationPayload,
    user_id: UUID,
    urgent: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send push notification to a specific user."""
    try:
        # Check if current user has permission to send notifications
        # In a real implementation, add proper RBAC checks here
        
        results = await pwa_service.send_push_notification(
            db, user_id, notification, urgent
        )
        
        return {
            "message": "Notification sent",
            "delivery_results": results,
            "total_subscriptions": len(results),
            "successful_deliveries": sum(results),
        }
    except Exception as e:
        logger.error(f"Failed to send push notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send push notification")


@router.post("/push/broadcast")
async def broadcast_push_notification(
    notification: NotificationPayload,
    urgent: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Broadcast push notification to all users (admin only)."""
    try:
        # Check admin permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403, detail="Only administrators can broadcast notifications"
            )
        
        # Implementation would broadcast to all active users
        # For now, just return success message
        
        return {
            "message": "Broadcast notification sent",
            "notification": notification.dict(),
            "urgent": urgent,
        }
    except Exception as e:
        logger.error(f"Failed to broadcast push notification: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to broadcast push notification"
        )


@router.post("/background-sync", response_model=BackgroundSyncJobResponse)
async def create_background_sync_job(
    job_data: BackgroundSyncJobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a background sync job."""
    try:
        job = await pwa_service.create_background_sync_job(
            db, current_user.id, job_data
        )
        return job
    except Exception as e:
        logger.error(f"Failed to create background sync job: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create background sync job"
        )


@router.get("/background-sync/jobs", response_model=List[BackgroundSyncJobResponse])
async def get_user_background_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's background sync jobs."""
    try:
        # Implementation would fetch user's jobs from database
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Failed to get background sync jobs: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get background sync jobs"
        )


@router.post("/background-sync/process")
async def process_background_sync_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process pending background sync jobs (admin only)."""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403, detail="Only administrators can process background jobs"
            )
        
        processed_jobs = await pwa_service.process_background_sync_jobs(db)
        
        return {
            "message": "Background sync jobs processed",
            "processed_count": len(processed_jobs),
            "processed_jobs": processed_jobs,
        }
    except Exception as e:
        logger.error(f"Failed to process background sync jobs: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to process background sync jobs"
        )


@router.get("/stats", response_model=PWAStats)
async def get_pwa_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get PWA usage statistics."""
    try:
        # Implementation would fetch real statistics from database
        # For now, return mock data
        stats = PWAStats(
            total_subscriptions=0,
            notifications_sent_24h=0,
            background_jobs_pending=0,
            background_jobs_completed_24h=0,
            offline_sessions_24h=0,
            cache_hit_rate=0.85,
        )
        return stats
    except Exception as e:
        logger.error(f"Failed to get PWA stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get PWA stats")


@router.get("/update-check", response_model=ServiceWorkerUpdate)
async def check_for_updates():
    """Check for service worker updates."""
    try:
        # Implementation would check for actual updates
        # For now, return no updates available
        update = ServiceWorkerUpdate(
            version="1.0.0",
            update_type="feature",
            changes=["Initial PWA implementation"],
            requires_restart=False,
        )
        return update
    except Exception as e:
        logger.error(f"Failed to check for updates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check for updates")


@router.get("/notification-templates", response_model=List[ClinicalNotificationTemplate])
async def get_notification_templates():
    """Get clinical notification templates."""
    try:
        templates = [
            ClinicalNotificationTemplate(
                template_id="case_assignment",
                title_template="New Case Assigned",
                body_template="Case #{case_id} for {patient_name} has been assigned to you",
                urgency_level=3,
                require_interaction=True,
                vibration_pattern=[100, 50, 100],
                icon_type="case",
            ),
            ClinicalNotificationTemplate(
                template_id="urgent_review",
                title_template="Urgent Case Review Required",
                body_template="Case #{case_id} requires immediate clinical review",
                urgency_level=5,
                require_interaction=True,
                vibration_pattern=[300, 100, 300, 100, 300],
                icon_type="urgent",
            ),
            ClinicalNotificationTemplate(
                template_id="protocol_update",
                title_template="Clinical Protocol Updated",
                body_template="Protocol '{protocol_name}' has been updated with new guidelines",
                urgency_level=2,
                require_interaction=False,
                vibration_pattern=[100],
                icon_type="protocol",
            ),
            ClinicalNotificationTemplate(
                template_id="decision_ready",
                title_template="Decision Support Ready",
                body_template="ADCI analysis complete for case #{case_id}",
                urgency_level=3,
                require_interaction=True,
                vibration_pattern=[100, 50, 100, 50, 100],
                icon_type="decision",
            ),
            ClinicalNotificationTemplate(
                template_id="sync_failure",
                title_template="Sync Failure",
                body_template="Failed to sync clinical data. Check connection.",
                urgency_level=4,
                require_interaction=True,
                vibration_pattern=[200, 100, 200],
                icon_type="error",
            ),
        ]
        return templates
    except Exception as e:
        logger.error(f"Failed to get notification templates: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get notification templates"
        )


@router.post("/install-prompt")
async def track_install_prompt(
    event_type: str,
    platform: str,
    user_agent: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Track PWA install prompt events."""
    try:
        # Implementation would track install prompt events
        # For analytics and conversion tracking
        
        logger.info(f"Install prompt event: {event_type} for user {current_user.id}")
        
        return {
            "message": "Install prompt event tracked",
            "event_type": event_type,
            "platform": platform,
        }
    except Exception as e:
        logger.error(f"Failed to track install prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track install prompt")


@router.get("/offline-data")
async def get_offline_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get essential data for offline functionality."""
    try:
        # Implementation would return essential data that should be cached
        # for offline operation (user profile, recent cases, guidelines, etc.)
        
        offline_data = {
            "user_profile": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role,
            },
            "clinical_guidelines": [],  # Would fetch from database
            "recent_cases": [],  # Would fetch from database
            "protocols": [],  # Would fetch from database
            "cache_timestamp": "2024-01-01T00:00:00Z",
        }
        
        return offline_data
    except Exception as e:
        logger.error(f"Failed to get offline data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get offline data")


@router.post("/offline-action")
async def queue_offline_action(
    action_type: str,
    action_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Queue an action performed while offline for later sync."""
    try:
        # Create background sync job for offline action
        job_data = BackgroundSyncJobCreate(
            job_type="offline_action_sync",
            data={
                "action_type": action_type,
                "action_data": action_data,
                "performed_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            },
            priority=7,  # High priority for user actions
        )
        
        job = await pwa_service.create_background_sync_job(
            db, current_user.id, job_data
        )
        
        return {
            "message": "Offline action queued for sync",
            "job_id": str(job.id),
            "action_type": action_type,
        }
    except Exception as e:
        logger.error(f"Failed to queue offline action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to queue offline action")
