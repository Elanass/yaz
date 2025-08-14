"""Enhanced Real-Time Notifications API
Server-Sent Events, Web Push, Background Sync, and Badging API.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


@dataclass
class Notification:
    """Enhanced notification model with PWA features."""

    id: str
    user_id: str
    title: str
    message: str
    type: str  # info, success, warning, error, system, case_update, sync_complete
    data: dict[str, Any] | None = None
    created_at: datetime = datetime.now()
    read: bool = False
    persistent: bool = False
    action_url: str | None = None
    action_text: str | None = None
    expires_at: datetime | None = None
    badge_count: int = 1
    icon: str | None = None
    image: str | None = None
    vibrate: list[int] | None = None
    silent: bool = False


class PushSubscription(BaseModel):
    """Web Push subscription model."""

    endpoint: str
    keys: dict[str, str]


class NotificationRequest(BaseModel):
    """Request model for creating notifications."""

    title: str
    message: str
    type: str = "info"
    action_url: str | None = None
    action_text: str | None = None
    persistent: bool = False


# Enhanced notification management
class NotificationManager:
    """Advanced notification manager with PWA features."""

    def __init__(self) -> None:
        self.notifications: dict[str, list[Notification]] = {}
        self.push_subscriptions: dict[str, PushSubscription] = {}
        self.active_connections: dict[str, asyncio.Queue] = {}
        self.badge_counts: dict[str, int] = {}

    async def add_connection(self, user_id: str, queue: asyncio.Queue) -> None:
        """Add SSE connection for user."""
        self.active_connections[user_id] = queue
        logger.info(f"[SSE] Connection added for user: {user_id}")

        # Send initial badge count
        await self.send_badge_update(user_id)

    async def remove_connection(self, user_id: str) -> None:
        """Remove SSE connection for user."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"[SSE] Connection removed for user: {user_id}")

    async def send_notification(self, notification: Notification) -> None:
        """Send notification via SSE and/or Push with badge update."""
        # Store notification
        if notification.user_id not in self.notifications:
            self.notifications[notification.user_id] = []

        self.notifications[notification.user_id].append(notification)

        # Update badge count
        self.update_badge_count(notification.user_id, notification.badge_count)

        # Send via SSE if user is connected
        if notification.user_id in self.active_connections:
            queue = self.active_connections[notification.user_id]
            try:
                await queue.put({"event": "notification", "data": asdict(notification)})

                # Send badge update
                await self.send_badge_update(notification.user_id)

            except Exception as e:
                logger.exception(f"[SSE] Failed to send notification: {e}")

        # Send via Web Push if user is offline
        else:
            await self.send_push_notification(notification)

    async def send_push_notification(self, notification: Notification) -> None:
        """Send Web Push notification with badge."""
        if notification.user_id in self.push_subscriptions:
            # In production, use py-vapid or similar library
            # Build data dict safely
            data_dict = {
                "url": notification.action_url or "/surgify",
                "notification_id": notification.id,
            }
            if notification.data:
                data_dict.update(notification.data)

            logger.info(
                f"[Push] Would send to {notification.user_id}: {notification.title}"
            )
            # await webpush.send(subscription, json.dumps(push_payload))

    def update_badge_count(self, user_id: str, increment: int = 1) -> None:
        """Update badge count for user."""
        if user_id not in self.badge_counts:
            self.badge_counts[user_id] = 0

        self.badge_counts[user_id] += increment

    async def send_badge_update(self, user_id: str) -> None:
        """Send badge count update via SSE."""
        if user_id in self.active_connections:
            queue = self.active_connections[user_id]
            try:
                await queue.put(
                    {
                        "event": "badge-update",
                        "data": {"count": self.badge_counts.get(user_id, 0)},
                    }
                )
            except Exception as e:
                logger.exception(f"[Badge] Failed to send update: {e}")

    async def clear_badge(self, user_id: str) -> None:
        """Clear badge count for user."""
        self.badge_counts[user_id] = 0
        await self.send_badge_update(user_id)

    async def send_case_update(self, user_id: str, case_id: str, status: str) -> None:
        """Send case update notification."""
        notification = Notification(
            id=f"case_update_{datetime.now().timestamp()}",
            user_id=user_id,
            title="Case Update",
            message=f"Case {case_id} status changed to {status}",
            type="case_update",
            data={"case_id": case_id, "status": status},
            action_url=f"/surgify/cases/{case_id}",
            action_text="View Case",
            icon="/static/icons/case-update.png",
        )

        await self.send_notification(notification)

    async def send_sync_complete(self, user_id: str, resource: str) -> None:
        """Send background sync completion notification."""
        notification = Notification(
            id=f"sync_{resource}_{datetime.now().timestamp()}",
            user_id=user_id,
            title="Sync Complete",
            message=f"{resource.title()} data synchronized successfully",
            type="sync_complete",
            data={"resource": resource},
            silent=True,
            badge_count=0,  # Don't increment badge for sync notifications
        )

        await self.send_notification(notification)


# Global notification manager
notification_manager = NotificationManager()


def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from request headers or JWT."""
    # Try to get from Authorization header
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        # In production, decode JWT to get user_id
        # For now, use a simple fallback
        return request.headers.get("x-user-id", "demo-user")

    return request.headers.get("x-user-id", "anonymous")


@router.get("/stream")
async def notification_stream(request: Request):
    """Enhanced Server-Sent Events endpoint with badge support."""
    user_id = get_user_id_from_request(request)

    async def event_generator():
        queue = asyncio.Queue()
        await notification_manager.add_connection(user_id, queue)

        try:
            # Send connection confirmation
            yield {
                "event": "connected",
                "data": json.dumps(
                    {
                        "message": "Connected to Surgify notifications",
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat(),
                        "features": [
                            "notifications",
                            "badge",
                            "push",
                            "background-sync",
                        ],
                    }
                ),
            }

            # Send existing unread notifications
            unread_notifications = notification_manager.get_user_notifications(
                user_id, unread_only=True
            )

            for notification in unread_notifications:
                yield {
                    "event": "notification",
                    "data": json.dumps(asdict(notification), default=str),
                }

            # Listen for new events
            while True:
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)

                    yield {
                        "event": event_data["event"],
                        "data": json.dumps(event_data["data"], default=str),
                    }

                except asyncio.TimeoutError:
                    # Send heartbeat with server status
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps(
                            {
                                "timestamp": datetime.now().isoformat(),
                                "server_time": datetime.now().isoformat(),
                                "active_connections": len(
                                    notification_manager.active_connections
                                ),
                            }
                        ),
                    }

        except asyncio.CancelledError:
            logger.info(f"[SSE] Connection cancelled for user: {user_id}")
        except Exception as e:
            logger.exception(f"[SSE] Error for user {user_id}: {e}")
        finally:
            await notification_manager.remove_connection(user_id)

    return EventSourceResponse(event_generator())


@router.get("/")
async def get_notifications(
    request: Request, unread_only: bool = False, limit: int = 50
):
    """Get user notifications with pagination."""
    user_id = get_user_id_from_request(request)
    notifications = notification_manager.get_user_notifications(user_id, unread_only)

    # Apply limit
    notifications = (
        notifications[-limit:] if len(notifications) > limit else notifications
    )

    return {
        "notifications": [asdict(n) for n in notifications],
        "total": len(notifications),
        "unread": len([n for n in notifications if not n.read]),
        "badge_count": notification_manager.badge_counts.get(user_id, 0),
    }


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(request: Request, notification_id: str):
    """Mark notification as read and update badge."""
    user_id = get_user_id_from_request(request)

    success = notification_manager.mark_as_read(user_id, notification_id)

    if success:
        # Decrease badge count
        if user_id in notification_manager.badge_counts:
            notification_manager.badge_counts[user_id] = max(
                0, notification_manager.badge_counts[user_id] - 1
            )

        await notification_manager.send_badge_update(user_id)
        return {"message": "Notification marked as read"}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/mark-all-read")
async def mark_all_notifications_read(request: Request):
    """Mark all notifications as read and clear badge."""
    user_id = get_user_id_from_request(request)

    user_notifications = notification_manager.notifications.get(user_id, [])
    for notification in user_notifications:
        notification.read = True

    await notification_manager.clear_badge(user_id)

    return {
        "message": "All notifications marked as read",
        "count": len(user_notifications),
    }


@router.post("/subscribe-push")
async def subscribe_push_notifications(
    request: Request, subscription: PushSubscription
):
    """Subscribe to Web Push notifications."""
    user_id = get_user_id_from_request(request)

    notification_manager.push_subscriptions[user_id] = subscription

    # Send welcome push notification
    welcome_notification = Notification(
        id=f"welcome_push_{datetime.now().timestamp()}",
        user_id=user_id,
        title="Push Notifications Enabled",
        message="You'll now receive important Surgify updates even when the app is closed",
        type="success",
        badge_count=0,
        silent=True,
    )

    await notification_manager.send_push_notification(welcome_notification)

    return {"message": "Push notification subscription saved"}


@router.post("/send")
async def send_notification(
    request: Request, notification_request: NotificationRequest
):
    """Send notification to current user (for testing/admin)."""
    user_id = get_user_id_from_request(request)

    notification = Notification(
        id=f"manual_{datetime.now().timestamp()}",
        user_id=user_id,
        title=notification_request.title,
        message=notification_request.message,
        type=notification_request.type,
        action_url=notification_request.action_url,
        action_text=notification_request.action_text,
        persistent=notification_request.persistent,
    )

    await notification_manager.send_notification(notification)

    return {"message": "Notification sent", "id": notification.id}


@router.post("/case-update/{case_id}")
async def send_case_update(request: Request, case_id: str, status: str):
    """Send case update notification."""
    user_id = get_user_id_from_request(request)

    await notification_manager.send_case_update(user_id, case_id, status)

    return {"message": f"Case update notification sent for {case_id}"}


@router.post("/sync-complete/{resource}")
async def notify_sync_complete(request: Request, resource: str):
    """Notify that background sync completed."""
    user_id = get_user_id_from_request(request)

    await notification_manager.send_sync_complete(user_id, resource)

    return {"message": f"Sync completion notification sent for {resource}"}


@router.get("/badge")
async def get_badge_count(request: Request):
    """Get current badge count for user."""
    user_id = get_user_id_from_request(request)

    return {
        "count": notification_manager.badge_counts.get(user_id, 0),
        "user_id": user_id,
    }


@router.post("/clear-badge")
async def clear_badge_count(request: Request):
    """Clear badge count for user."""
    user_id = get_user_id_from_request(request)

    await notification_manager.clear_badge(user_id)

    return {"message": "Badge cleared", "count": 0}


@router.get("/test")
async def test_notifications(request: Request):
    """Send test notifications of different types."""
    user_id = get_user_id_from_request(request)

    test_notifications = [
        Notification(
            id=f"test_info_{datetime.now().timestamp()}",
            user_id=user_id,
            title="Information",
            message="This is an info notification",
            type="info",
            action_url="/surgify/dashboard",
        ),
        Notification(
            id=f"test_success_{datetime.now().timestamp()}",
            user_id=user_id,
            title="Success!",
            message="Operation completed successfully",
            type="success",
        ),
        Notification(
            id=f"test_warning_{datetime.now().timestamp()}",
            user_id=user_id,
            title="Warning",
            message="Please review your case data",
            type="warning",
            action_url="/surgify/cases",
            action_text="Review Cases",
        ),
        Notification(
            id=f"test_error_{datetime.now().timestamp()}",
            user_id=user_id,
            title="Error",
            message="Something went wrong",
            type="error",
            persistent=True,
        ),
    ]

    for notification in test_notifications:
        await notification_manager.send_notification(notification)
        await asyncio.sleep(0.5)  # Small delay between notifications

    return {"message": "Test notifications sent", "count": len(test_notifications)}


# Enhanced notification management methods
notification_manager.get_user_notifications = lambda user_id, unread_only=False: [
    n
    for n in notification_manager.notifications.get(user_id, [])
    if not unread_only or not n.read
]

notification_manager.mark_as_read = lambda user_id, notification_id: any(
    setattr(n, "read", True) or True
    for n in notification_manager.notifications.get(user_id, [])
    if n.id == notification_id
)

# Global notification queues and connections for SSE
import queue


notification_queues = {}
active_connections = {}


def start_notification_event_stream(user_id):
    if user_id not in notification_queues:
        notification_queues[user_id] = queue.Queue()
    active_connections[user_id] = True

    def event_generator():
        try:
            while active_connections.get(user_id, False):
                try:
                    notification = notification_queues[user_id].get_nowait()
                    event_data = {
                        "id": notification.id,
                        "title": notification.title,
                        "message": notification.message,
                        "type": notification.type,
                        "created_at": notification.created_at.isoformat(),
                        "data": notification.data,
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                except queue.Empty:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
        except Exception:
            pass
        finally:
            active_connections[user_id] = False

    return event_generator


@router.post("/send")
async def send_notification(
    notification: Notification, user_id: str | None = None, broadcast: bool = False
):
    """Send notification to specific user or broadcast to all."""
    if broadcast:
        # Send to all active users
        for uid in list(active_connections.keys()):
            if active_connections.get(uid, False):
                add_notification(uid, notification)
        return {
            "message": f"Notification broadcasted to {len(active_connections)} users"
        }

    if user_id:
        add_notification(user_id, notification)
        return {"message": f"Notification sent to user {user_id}"}

    # Send to demo user if no specific user
    add_notification("anonymous", notification)
    return {"message": "Notification sent to anonymous user"}


@router.post("/case-update/{case_id}")
async def notify_case_update(
    case_id: str, update_type: str, details: dict[str, Any] | None = None
):
    """Send case-specific update notification."""
    if details is None:
        details = {}
    notification = Notification(
        id=f"case_{case_id}_{datetime.now().timestamp()}",
        type="info",
        title=f"Case {case_id} Update",
        message=f"Case update: {update_type}",
        data={"case_id": case_id, "update_type": update_type, "details": details},
    )

    # In production, determine which users should receive this notification
    # For demo, broadcast to all
    for user_id in list(active_connections.keys()):
        if active_connections.get(user_id, False):
            add_notification(user_id, notification)

    return {"message": f"Case update notification sent for {case_id}"}


@router.post("/ai-analysis-complete/{case_id}")
async def notify_ai_analysis_complete(
    case_id: str, results: dict[str, Any] | None = None
):
    """Notify when AI analysis is complete."""
    if results is None:
        results = {}
    notification = Notification(
        id=f"ai_complete_{case_id}_{datetime.now().timestamp()}",
        type="success",
        title="AI Analysis Complete",
        message=f"Analysis for case {case_id} is ready for review",
        data={
            "case_id": case_id,
            "analysis_results": results,
            "action_url": f"/cases/{case_id}/results",
        },
    )

    # Send to all active users (in production, filter by case access)
    for user_id in list(active_connections.keys()):
        if active_connections.get(user_id, False):
            add_notification(user_id, notification)

    return {"message": f"AI analysis completion notification sent for {case_id}"}


@router.post("/collaboration-invite")
async def notify_collaboration_invite(
    case_id: str, invited_by: str, invited_user: str, message: str = ""
):
    """Send collaboration invitation notification."""
    notification = Notification(
        id=f"collab_invite_{case_id}_{datetime.now().timestamp()}",
        type="info",
        title="Collaboration Invitation",
        message=f"{invited_by} invited you to collaborate on case {case_id}",
        data={
            "case_id": case_id,
            "invited_by": invited_by,
            "invitation_message": message,
            "action_url": f"/cases/{case_id}/collaborate",
            "actions": [
                {"label": "Accept", "action": "accept_collaboration"},
                {"label": "Decline", "action": "decline_collaboration"},
            ],
        },
    )

    add_notification(invited_user, notification)
    return {"message": f"Collaboration invitation sent to {invited_user}"}


@router.get("/history/{user_id}")
async def get_notification_history(user_id: str, limit: int = 50):
    """Get notification history for a user."""
    # In production, fetch from database
    # For demo, return mock data

    mock_notifications = [
        {
            "id": f"notif_{i}",
            "type": "info" if i % 2 == 0 else "success",
            "title": f"Notification {i}",
            "message": f"This is notification message {i}",
            "timestamp": datetime.now().isoformat(),
            "read": i > 5,
        }
        for i in range(1, limit + 1)
    ]

    return {
        "notifications": mock_notifications,
        "total": len(mock_notifications),
        "unread_count": len([n for n in mock_notifications if not n["read"]]),
    }


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str, user_id: str):
    """Mark notification as read."""
    # In production, update database
    return {
        "message": f"Notification {notification_id} marked as read for user {user_id}"
    }


@router.delete("/clear/{user_id}")
async def clear_notifications(user_id: str):
    """Clear all notifications for a user."""
    if user_id in notification_queues:
        # Clear the queue
        while not notification_queues[user_id].empty():
            try:
                notification_queues[user_id].get_nowait()
            except queue.Empty:
                break

    return {"message": f"All notifications cleared for user {user_id}"}


@router.get("/status")
async def notification_status():
    """Get notification system status."""
    return {
        "active_connections": len(
            [uid for uid, active in active_connections.items() if active]
        ),
        "total_queues": len(notification_queues),
        "queue_sizes": {uid: q.qsize() for uid, q in notification_queues.items()},
        "timestamp": datetime.now().isoformat(),
    }


# Demo endpoints for testing
@router.post("/demo/success")
async def demo_success_notification():
    """Demo success notification."""
    notification = Notification(
        id=f"demo_success_{datetime.now().timestamp()}",
        type="success",
        title="Operation Successful",
        message="Your surgical analysis has been completed successfully!",
    )

    for user_id in list(active_connections.keys()):
        if active_connections.get(user_id, False):
            add_notification(user_id, notification)

    return {"message": "Demo success notification sent"}


@router.post("/demo/error")
async def demo_error_notification():
    """Demo error notification."""
    notification = Notification(
        id=f"demo_error_{datetime.now().timestamp()}",
        type="error",
        title="Processing Error",
        message="There was an error processing your request. Please try again.",
    )

    for user_id in list(active_connections.keys()):
        if active_connections.get(user_id, False):
            add_notification(user_id, notification)

    return {"message": "Demo error notification sent"}


@router.post("/demo/warning")
async def demo_warning_notification():
    """Demo warning notification."""
    notification = Notification(
        id=f"demo_warning_{datetime.now().timestamp()}",
        type="warning",
        title="Review Required",
        message="Your case analysis requires additional review before finalizing.",
    )

    for user_id in list(active_connections.keys()):
        if active_connections.get(user_id, False):
            add_notification(user_id, notification)

    return {"message": "Demo warning notification sent"}
