"""Alerting Service for Protocol Compliance.

This service tracks compliance with clinical protocols and generates alerts
when deviations are detected, ensuring proper adherence to medical guidelines.
"""

import asyncio
import contextlib
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from shared.config import get_shared_config
from apps.surge.core.services.base import BaseService
from apps.surge.core.services.logger import get_logger


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(str, Enum):
    """Alert status states."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class Alert:
    """Alert model for protocol compliance monitoring."""

    def __init__(
        self,
        alert_id: str,
        title: str,
        message: str,
        severity: AlertSeverity,
        category: str,
        resource_type: str,
        resource_id: str | None = None,
        patient_id: str | None = None,
        protocol_id: str | None = None,
        expires_at: datetime | None = None,
        actions: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.alert_id = alert_id
        self.title = title
        self.message = message
        self.severity = severity
        self.category = category
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.patient_id = patient_id
        self.protocol_id = protocol_id
        self.status = AlertStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at
        self.acknowledged_at = None
        self.resolved_at = None
        self.acknowledged_by = None
        self.resolved_by = None
        self.actions = actions or []
        self.metadata = metadata or {}

    def acknowledge(self, user_id: str) -> bool:
        """Acknowledge the alert.

        Args:
            user_id: ID of the user acknowledging the alert

        Returns:
            True if successful, False if already acknowledged
        """
        if self.status != AlertStatus.ACTIVE:
            return False

        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
        return True

    def resolve(self, user_id: str, resolution_note: str | None = None) -> bool:
        """Resolve the alert.

        Args:
            user_id: ID of the user resolving the alert
            resolution_note: Optional note on how the alert was resolved

        Returns:
            True if successful, False if already resolved
        """
        if self.status == AlertStatus.RESOLVED:
            return False

        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id

        if resolution_note:
            self.metadata["resolution_note"] = resolution_note

        return True

    def is_expired(self) -> bool:
        """Check if the alert is expired."""
        if not self.expires_at:
            return False

        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "alert_id": self.alert_id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "category": self.category,
            "status": self.status,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "patient_id": self.patient_id,
            "protocol_id": self.protocol_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat()
            if self.acknowledged_at
            else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_by": self.resolved_by,
            "actions": self.actions,
            "metadata": self.metadata,
        }


class AlertingService(BaseService):
    """Service for monitoring protocol compliance and generating alerts."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_shared_config()
        self.config = {
            "enabled": True,
            "max_alerts_per_hour": 10,
            "email_enabled": False,
            "severity_threshold": "INFO",
        }
        self.logger = get_logger(__name__)
        self.active_alerts: dict[str, Alert] = {}
        self.alert_listeners: list[Callable[[Alert], Awaitable[None]]] = []
        self.expiration_task = None

    async def start(self) -> None:
        """Start the alerting service."""
        # Start expiration checking task
        self.expiration_task = asyncio.create_task(self._check_expirations())
        self.logger.info("Alerting service started")

    async def stop(self) -> None:
        """Stop the alerting service."""
        if self.expiration_task:
            self.expiration_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.expiration_task
        self.logger.info("Alerting service stopped")

    async def _check_expirations(self) -> None:
        """Background task to check for expired alerts."""
        while True:
            try:
                # Check all active alerts
                datetime.utcnow()
                expired_ids = []

                for alert_id, alert in self.active_alerts.items():
                    if alert.status == AlertStatus.ACTIVE and alert.is_expired():
                        alert.status = AlertStatus.EXPIRED
                        expired_ids.append(alert_id)

                        # Notify listeners
                        await self._notify_listeners(alert)

                # Log expired alerts
                if expired_ids:
                    self.logger.info(
                        f"Expired {len(expired_ids)} alerts", alert_ids=expired_ids
                    )

                # Sleep for the configured interval
                check_interval = self.config.get(
                    "expiration_check_interval_seconds", 60
                )
                await asyncio.sleep(check_interval)

            except asyncio.CancelledError:
                break

            except Exception as e:
                self.logger.exception("Error checking alert expirations", exc_info=e)
                await asyncio.sleep(5)  # Short delay before retry

    async def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        category: str,
        resource_type: str,
        resource_id: str | None = None,
        patient_id: str | None = None,
        protocol_id: str | None = None,
        expires_in: int | None = None,  # Seconds
        actions: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        """Create a new alert.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            category: Alert category (e.g., "protocol_deviation", "system")
            resource_type: Type of resource this alert is about
            resource_id: ID of the specific resource (optional)
            patient_id: ID of the related patient (optional)
            protocol_id: ID of the related protocol (optional)
            expires_in: Seconds until this alert expires (optional)
            actions: List of possible actions that can be taken
            metadata: Additional context about the alert

        Returns:
            The created alert
        """
        import uuid

        # Generate alert ID
        alert_id = str(uuid.uuid4())

        # Calculate expiration time if provided
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Create alert
        alert = Alert(
            alert_id=alert_id,
            title=title,
            message=message,
            severity=severity,
            category=category,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            protocol_id=protocol_id,
            expires_at=expires_at,
            actions=actions,
            metadata=metadata,
        )

        # Store alert
        self.active_alerts[alert_id] = alert

        # Log alert creation
        self.logger.info(
            f"Created {severity.value} alert: {title}",
            alert_id=alert_id,
            severity=severity.value,
            category=category,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            protocol_id=protocol_id,
        )

        # Notify listeners
        await self._notify_listeners(alert)

        return alert

    async def get_alert(self, alert_id: str) -> Alert | None:
        """Get an alert by ID.

        Args:
            alert_id: The alert ID

        Returns:
            The alert, or None if not found
        """
        return self.active_alerts.get(alert_id)

    async def list_active_alerts(
        self,
        patient_id: str | None = None,
        protocol_id: str | None = None,
        category: str | None = None,
        min_severity: AlertSeverity | None = None,
    ) -> list[Alert]:
        """List active alerts with optional filters.

        Args:
            patient_id: Filter by patient ID
            protocol_id: Filter by protocol ID
            category: Filter by category
            min_severity: Filter by minimum severity

        Returns:
            List of matching alerts
        """
        alerts = []

        for alert in self.active_alerts.values():
            # Skip non-active alerts
            if alert.status != AlertStatus.ACTIVE:
                continue

            # Apply filters
            if patient_id and alert.patient_id != patient_id:
                continue

            if protocol_id and alert.protocol_id != protocol_id:
                continue

            if category and alert.category != category:
                continue

            if min_severity:
                # Get severity index
                severity_order = [s.value for s in AlertSeverity]
                min_idx = severity_order.index(min_severity.value)
                alert_idx = severity_order.index(alert.severity.value)

                if alert_idx < min_idx:
                    continue

            alerts.append(alert)

        return alerts

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert.

        Args:
            alert_id: The alert ID
            user_id: ID of the user acknowledging the alert

        Returns:
            True if successful, False otherwise
        """
        alert = await self.get_alert(alert_id)
        if not alert:
            return False

        result = alert.acknowledge(user_id)

        if result:
            self.logger.info(
                f"Alert {alert_id} acknowledged by user {user_id}",
                alert_id=alert_id,
                user_id=user_id,
            )

            # Notify listeners
            await self._notify_listeners(alert)

        return result

    async def resolve_alert(
        self, alert_id: str, user_id: str, resolution_note: str | None = None
    ) -> bool:
        """Resolve an alert.

        Args:
            alert_id: The alert ID
            user_id: ID of the user resolving the alert
            resolution_note: Optional note on how the alert was resolved

        Returns:
            True if successful, False otherwise
        """
        alert = await self.get_alert(alert_id)
        if not alert:
            return False

        result = alert.resolve(user_id, resolution_note)

        if result:
            self.logger.info(
                f"Alert {alert_id} resolved by user {user_id}",
                alert_id=alert_id,
                user_id=user_id,
                resolution_note=resolution_note,
            )

            # Notify listeners
            await self._notify_listeners(alert)

        return result

    async def add_listener(self, listener: Callable[[Alert], Awaitable[None]]) -> None:
        """Add a listener for alert events.

        Args:
            listener: Async callback function that receives alerts
        """
        self.alert_listeners.append(listener)

    async def remove_listener(
        self, listener: Callable[[Alert], Awaitable[None]]
    ) -> None:
        """Remove a listener.

        Args:
            listener: The listener to remove
        """
        if listener in self.alert_listeners:
            self.alert_listeners.remove(listener)

    async def _notify_listeners(self, alert: Alert) -> None:
        """Notify all listeners of an alert event."""
        for listener in self.alert_listeners:
            try:
                await listener(alert)
            except Exception as e:
                self.logger.exception(
                    "Error in alert listener", exc_info=e, alert_id=alert.alert_id
                )
