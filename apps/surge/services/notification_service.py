"""Notification service for real-time communication and alerts."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import Notification, NotificationType
from ..utils.redis_client import get_redis_client


class NotificationService:
    """Service for managing notifications and real-time communication."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.redis = get_redis_client()

    async def create_notification(
        self,
        user_id: UUID,
        type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> Notification:
        """Create and send a notification."""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data or {},
        )

        self.db.add(notification)
        await self.db.flush()

        # Send real-time notification via Redis
        await self._send_realtime_notification(notification)

        return notification

    async def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Mark notification as read."""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()

        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.db.commit()
            return True

        return False

    async def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(not Notification.is_read)

        query = query.order_by(Notification.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                not Notification.is_read,
            )
        )
        return len(list(result.scalars().all()))

    async def _send_realtime_notification(self, notification: Notification) -> None:
        """Send real-time notification via Redis/WebSocket."""
        if not self.redis:
            return

        try:
            notification_data = {
                "id": str(notification.id),
                "type": notification.type.value,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "created_at": notification.created_at.isoformat(),
            }

            # Publish to Redis channel for real-time delivery
            channel = f"notifications:{notification.user_id}"
            await self.redis.publish(channel, str(notification_data))

        except Exception:
            # Fail silently for real-time notifications
            pass
