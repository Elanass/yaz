"""
PWA Schemas - Pydantic models for Progressive Web App functionality.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class PushSubscriptionKeys(BaseModel):
    """Push subscription keys for VAPID authentication."""
    
    p256dh: str = Field(..., description="P-256 public key")
    auth: str = Field(..., description="Authentication secret")


class PushSubscription(BaseModel):
    """Push subscription data from browser."""
    
    endpoint: str = Field(..., description="Push service endpoint URL")
    keys: PushSubscriptionKeys = Field(..., description="Encryption keys")
    
    @validator("endpoint")
    def validate_endpoint(cls, v):
        if not v.startswith(("https://", "http://")):
            raise ValueError("Endpoint must be a valid URL")
        return v


class NotificationAction(BaseModel):
    """Notification action button."""
    
    action: str = Field(..., description="Action identifier")
    title: str = Field(..., description="Action button text")
    icon: Optional[str] = Field(None, description="Action icon URL")


class NotificationPayload(BaseModel):
    """Push notification payload."""
    
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body text")
    icon: Optional[str] = Field(None, description="Notification icon URL")
    badge: Optional[str] = Field(None, description="Notification badge URL")
    tag: Optional[str] = Field(None, description="Notification tag for grouping")
    data: Optional[Dict[str, Any]] = Field(None, description="Custom notification data")
    require_interaction: bool = Field(False, description="Require user interaction")
    actions: Optional[List[NotificationAction]] = Field(None, description="Action buttons")
    
    @validator("title")
    def validate_title(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        if len(v) > 100:
            raise ValueError("Title must be 100 characters or less")
        return v.strip()
    
    @validator("body")
    def validate_body(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Body cannot be empty")
        if len(v) > 300:
            raise ValueError("Body must be 300 characters or less")
        return v.strip()


class BackgroundSyncJobCreate(BaseModel):
    """Create background sync job request."""
    
    job_type: str = Field(..., description="Type of background sync job")
    data: Optional[Dict[str, Any]] = Field(None, description="Job data payload")
    priority: int = Field(5, ge=1, le=10, description="Job priority (1-10)")
    max_retries: Optional[int] = Field(3, ge=0, le=10, description="Maximum retry attempts")
    scheduled_at: Optional[datetime] = Field(None, description="When to execute the job")
    
    @validator("job_type")
    def validate_job_type(cls, v):
        allowed_types = [
            "patient_data_sync",
            "decision_cache_update", 
            "audit_log_sync",
            "clinical_protocol_update",
            "evidence_backup",
            "guideline_update"
        ]
        if v not in allowed_types:
            raise ValueError(f"Job type must be one of: {', '.join(allowed_types)}")
        return v


class BackgroundSyncJobResponse(BaseModel):
    """Background sync job response."""
    
    id: UUID
    job_type: str
    priority: int
    status: str
    retry_count: int
    max_retries: int
    created_at: datetime
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    last_error: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PWASubscriptionResponse(BaseModel):
    """PWA subscription response."""
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PWAIcon(BaseModel):
    """PWA manifest icon."""
    
    src: str = Field(..., description="Icon image URL")
    sizes: str = Field(..., description="Icon sizes (e.g., '192x192')")
    type: str = Field("image/png", description="Icon MIME type")
    purpose: str = Field("any maskable", description="Icon purpose")


class PWAShortcut(BaseModel):
    """PWA manifest shortcut."""
    
    name: str = Field(..., description="Shortcut name")
    short_name: str = Field(..., description="Short name")
    description: str = Field(..., description="Shortcut description")
    url: str = Field(..., description="Shortcut target URL")
    icons: List[PWAIcon] = Field(..., description="Shortcut icons")


class PWAManifest(BaseModel):
    """PWA manifest for installable app."""
    
    name: str = Field(..., description="App full name")
    short_name: str = Field(..., description="App short name")
    description: str = Field(..., description="App description")
    start_url: str = Field("/", description="App start URL")
    display: str = Field("standalone", description="Display mode")
    background_color: str = Field("#ffffff", description="Background color")
    theme_color: str = Field("#1976d2", description="Theme color")
    orientation: str = Field("portrait-primary", description="Preferred orientation")
    scope: str = Field("/", description="App scope")
    lang: str = Field("en", description="App language")
    categories: List[str] = Field(..., description="App categories")
    icons: List[PWAIcon] = Field(..., description="App icons")
    shortcuts: List[PWAShortcut] = Field(..., description="App shortcuts")
    related_applications: List[Dict[str, Any]] = Field([], description="Related applications")
    prefer_related_applications: bool = Field(False, description="Prefer related applications")


class PWAStats(BaseModel):
    """PWA usage statistics."""
    
    total_subscriptions: int = Field(..., description="Total active subscriptions")
    notifications_sent_24h: int = Field(..., description="Notifications sent in last 24 hours")
    background_jobs_pending: int = Field(..., description="Pending background sync jobs")
    background_jobs_completed_24h: int = Field(..., description="Background jobs completed in last 24 hours")
    offline_sessions_24h: int = Field(..., description="Offline sessions in last 24 hours")
    cache_hit_rate: float = Field(..., ge=0, le=1, description="Cache hit rate (0-1)")


class InstallPromptEvent(BaseModel):
    """PWA install prompt event data."""
    
    user_id: UUID = Field(..., description="User ID")
    event_type: str = Field(..., description="Event type (prompted, accepted, dismissed)")
    platform: str = Field(..., description="User platform")
    user_agent: str = Field(..., description="User agent string")
    timestamp: datetime = Field(..., description="Event timestamp")
    
    @validator("event_type")
    def validate_event_type(cls, v):
        allowed_types = ["prompted", "accepted", "dismissed", "installed"]
        if v not in allowed_types:
            raise ValueError(f"Event type must be one of: {', '.join(allowed_types)}")
        return v


class OfflineCapabilityCheck(BaseModel):
    """Check offline capability requirements."""
    
    feature: str = Field(..., description="Feature to check")
    required_data: List[str] = Field(..., description="Required data for offline operation")
    cache_size_estimate: int = Field(..., description="Estimated cache size in bytes")
    
    @validator("feature")
    def validate_feature(cls, v):
        allowed_features = [
            "patient_cases",
            "clinical_guidelines",
            "decision_support",
            "audit_logging",
            "user_preferences"
        ]
        if v not in allowed_features:
            raise ValueError(f"Feature must be one of: {', '.join(allowed_features)}")
        return v


class PWAPerformanceMetrics(BaseModel):
    """PWA performance metrics."""
    
    load_time_ms: int = Field(..., description="App load time in milliseconds")
    cache_hit_ratio: float = Field(..., ge=0, le=1, description="Cache hit ratio")
    offline_time_seconds: int = Field(..., description="Time spent offline in seconds")
    sync_success_rate: float = Field(..., ge=0, le=1, description="Background sync success rate")
    notification_click_rate: float = Field(..., ge=0, le=1, description="Notification click-through rate")
    install_conversion_rate: float = Field(..., ge=0, le=1, description="Install prompt conversion rate")


class ServiceWorkerUpdate(BaseModel):
    """Service worker update notification."""
    
    version: str = Field(..., description="New service worker version")
    update_type: str = Field(..., description="Update type (critical, feature, bug_fix)")
    changes: List[str] = Field(..., description="List of changes")
    requires_restart: bool = Field(False, description="Whether app restart is required")
    
    @validator("update_type")
    def validate_update_type(cls, v):
        allowed_types = ["critical", "feature", "bug_fix", "security"]
        if v not in allowed_types:
            raise ValueError(f"Update type must be one of: {', '.join(allowed_types)}")
        return v


class ClinicalNotificationTemplate(BaseModel):
    """Template for clinical notifications."""
    
    template_id: str = Field(..., description="Template identifier")
    title_template: str = Field(..., description="Title template with placeholders")
    body_template: str = Field(..., description="Body template with placeholders")
    urgency_level: int = Field(..., ge=1, le=5, description="Clinical urgency level (1-5)")
    require_interaction: bool = Field(False, description="Require user interaction")
    vibration_pattern: List[int] = Field([100], description="Vibration pattern in milliseconds")
    icon_type: str = Field("default", description="Icon type for notification")
    
    @validator("template_id")
    def validate_template_id(cls, v):
        allowed_templates = [
            "case_assignment",
            "urgent_review",
            "protocol_update",
            "decision_ready",
            "sync_failure",
            "security_alert",
            "guideline_update"
        ]
        if v not in allowed_templates:
            raise ValueError(f"Template ID must be one of: {', '.join(allowed_templates)}")
        return v
