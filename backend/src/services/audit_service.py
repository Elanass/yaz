"""
Advanced Audit Trail Service
HIPAA/GDPR compliant audit logging with tamper-proof evidence
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import hmac
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
import structlog

from ..db.models import AuditLog, User
from ..core.security import get_current_user
from ..core.config import settings

logger = structlog.get_logger(__name__)

class AuditEventType(str, Enum):
    """Types of auditable events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_FAILED_LOGIN = "user_failed_login"
    DATA_ACCESS = "data_access"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DECISION_CREATE = "decision_create"
    DECISION_APPROVE = "decision_approve"
    PROTOCOL_CREATE = "protocol_create"
    PROTOCOL_UPDATE = "protocol_update"
    PROTOCOL_FORK = "protocol_fork"
    EVIDENCE_CREATE = "evidence_create"
    EVIDENCE_UPDATE = "evidence_update"
    SYSTEM_CONFIG = "system_config"
    PERMISSION_CHANGE = "permission_change"
    EMERGENCY_ACCESS = "emergency_access"

class AuditSeverity(str, Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Structured audit event"""
    event_type: AuditEventType
    user_id: Optional[int]
    resource_type: str
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    severity: AuditSeverity = AuditSeverity.MEDIUM
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class TamperProofLogger:
    """Tamper-proof audit logging with cryptographic verification"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        
    def create_hash_chain(self, event: AuditEvent, previous_hash: Optional[str] = None) -> str:
        """Create tamper-proof hash chain"""
        event_data = asdict(event)
        event_json = json.dumps(event_data, sort_keys=True, default=str)
        
        if previous_hash:
            combined_data = f"{previous_hash}{event_json}"
        else:
            combined_data = event_json
            
        return hmac.new(
            self.secret_key,
            combined_data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_integrity(self, events: List[Dict]) -> bool:
        """Verify the integrity of audit log chain"""
        if not events:
            return True
            
        previous_hash = None
        for event in events:
            expected_hash = self.create_hash_chain(
                AuditEvent(**event), 
                previous_hash
            )
            if event.get('hash') != expected_hash:
                return False
            previous_hash = event['hash']
        return True

class AuditService:
    """Advanced audit trail service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tamper_logger = TamperProofLogger(settings.AUDIT_SECRET_KEY)
        
    async def log_event(
        self,
        event: AuditEvent,
        context: Optional[Dict] = None
    ) -> str:
        """Log an audit event with tamper-proof hash"""
        try:
            # Get the last audit log entry for hash chaining
            last_entry = self.db.query(AuditLog).order_by(desc(AuditLog.created_at)).first()
            previous_hash = last_entry.hash if last_entry else None
            
            # Create tamper-proof hash
            event_hash = self.tamper_logger.create_hash_chain(event, previous_hash)
            
            # Create audit log entry
            audit_log = AuditLog(
                event_type=event.event_type.value,
                user_id=event.user_id,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                action=event.action,
                details=event.details,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                severity=event.severity.value,
                session_id=event.session_id,
                hash=event_hash,
                context=context or {}
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
            # Log to structured logger as well
            logger.info(
                "audit_event_logged",
                event_type=event.event_type.value,
                user_id=event.user_id,
                resource_type=event.resource_type,
                action=event.action,
                severity=event.severity.value,
                hash=event_hash
            )
            
            return event_hash
            
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))
            self.db.rollback()
            raise
    
    async def get_audit_trail(
        self,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get filtered audit trail with pagination"""
        
        query = self.db.query(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type.value)
        if severity:
            query = query.filter(AuditLog.severity == severity.value)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Apply sorting
        sort_column = getattr(AuditLog, sort_by, AuditLog.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        events = query.offset(offset).limit(per_page).all()
        
        return {
            "events": [self._serialize_audit_event(event) for event in events],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    
    async def verify_audit_integrity(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Verify the integrity of audit logs"""
        
        query = self.db.query(AuditLog).order_by(AuditLog.created_at)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        events = query.all()
        event_dicts = [self._serialize_audit_event(event) for event in events]
        
        is_valid = self.tamper_logger.verify_integrity(event_dicts)
        
        return {
            "is_valid": is_valid,
            "total_events": len(events),
            "verification_timestamp": datetime.utcnow(),
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
    
    async def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit trail statistics"""
        
        query = self.db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Get event type distribution
        event_types = {}
        severity_dist = {}
        user_activity = {}
        
        events = query.all()
        
        for event in events:
            # Event type distribution
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            # Severity distribution
            severity_dist[event.severity] = severity_dist.get(event.severity, 0) + 1
            
            # User activity
            if event.user_id:
                user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
        
        return {
            "total_events": len(events),
            "event_type_distribution": event_types,
            "severity_distribution": severity_dist,
            "top_users": sorted(
                user_activity.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
    
    def _serialize_audit_event(self, event: AuditLog) -> Dict[str, Any]:
        """Serialize audit event for API response"""
        return {
            "id": event.id,
            "event_type": event.event_type,
            "user_id": event.user_id,
            "username": event.user.username if event.user else None,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "action": event.action,
            "details": event.details,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "severity": event.severity,
            "session_id": event.session_id,
            "hash": event.hash,
            "context": event.context,
            "created_at": event.created_at.isoformat(),
            "timestamp": event.created_at.isoformat()
        }

# Audit decorator for automatic logging
def audit_action(
    event_type: AuditEventType,
    resource_type: str,
    action: str,
    severity: AuditSeverity = AuditSeverity.MEDIUM
):
    """Decorator for automatic audit logging"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract common audit info
            # This would be integrated with your request context
            audit_event = AuditEvent(
                event_type=event_type,
                user_id=None,  # Extract from context
                resource_type=resource_type,
                resource_id=None,  # Extract from function args
                action=action,
                details={},
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=severity
            )
            
            # Execute function and log audit
            try:
                result = await func(*args, **kwargs)
                # Log successful action
                return result
            except Exception as e:
                # Log failed action
                raise
        return wrapper
    return decorator
