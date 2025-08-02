"""
Security Operations Operator
Handles security monitoring, access control, and threat detection
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
from core.services.logger import get_logger

logger = get_logger(__name__)


class SecurityOperationsOperator:
    """Security operations manager for access control and threat detection"""
    
    def __init__(self):
        """Initialize security operations operator"""
        self.security_events = {}
        self.access_logs = {}
        self.failed_attempts = {}
        self.security_policies = {}
        logger.info("Security operations operator initialized")
    
    def log_security_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log security-related events"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        event_id = core_ops.generate_operation_id("SECEVT")
        
        security_event = {
            "event_id": event_id,
            "event_type": event_data["event_type"],  # login, logout, access_denied, etc.
            "severity": event_data.get("severity", "info"),  # info, warning, critical
            "user_id": event_data.get("user_id"),
            "ip_address": event_data.get("ip_address"),
            "user_agent": event_data.get("user_agent"),
            "resource_accessed": event_data.get("resource"),
            "action_attempted": event_data.get("action"),
            "success": event_data.get("success", True),
            "details": event_data.get("details", {}),
            "timestamp": datetime.now().isoformat(),
            "session_id": event_data.get("session_id")
        }
        
        self.security_events[event_id] = security_event
        
        # Log failed attempts separately for monitoring
        if not security_event["success"]:
            self._track_failed_attempt(security_event)
        
        # Log the operation
        core_ops.log_operation("security_event", {
            "data": {
                "event_id": event_id,
                "event_type": event_data["event_type"],
                "success": security_event["success"]
            }
        })
        
        logger.info(f"Security event logged: {event_id} - {event_data['event_type']}")
        return security_event
    
    def _track_failed_attempt(self, security_event: Dict[str, Any]) -> None:
        """Track failed attempts for brute force detection"""
        key = f"{security_event.get('user_id', 'unknown')}:{security_event.get('ip_address', 'unknown')}"
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        self.failed_attempts[key].append({
            "timestamp": security_event["timestamp"],
            "event_type": security_event["event_type"],
            "event_id": security_event["event_id"]
        })
        
        # Check for brute force patterns
        self._check_brute_force_pattern(key, security_event)
    
    def _check_brute_force_pattern(self, key: str, latest_event: Dict[str, Any]) -> None:
        """Check for brute force attack patterns"""
        attempts = self.failed_attempts[key]
        
        # Check last 15 minutes
        fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.fromisoformat(attempt["timestamp"]) >= fifteen_minutes_ago
        ]
        
        # Alert if more than 5 failed attempts in 15 minutes
        if len(recent_attempts) >= 5:
            self._create_security_alert({
                "title": "Potential Brute Force Attack",
                "description": f"Multiple failed login attempts detected for {key}",
                "severity": "critical",
                "user_id": latest_event.get("user_id"),
                "ip_address": latest_event.get("ip_address"),
                "failed_attempts_count": len(recent_attempts),
                "time_window_minutes": 15
            })
    
    def _create_security_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create security alert"""
        from .infrastructure_operations import InfrastructureOperationsOperator
        infra_ops = InfrastructureOperationsOperator()
        
        alert_data["source"] = "security_monitor"
        return infra_ops.create_alert(alert_data)
    
    def validate_access_attempt(self, access_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate access attempt and log accordingly"""
        user_id = access_data.get("user_id")
        resource = access_data.get("resource")
        action = access_data.get("action")
        ip_address = access_data.get("ip_address")
        
        # Check if user is temporarily locked out
        if self._is_user_locked_out(user_id, ip_address):
            access_result = {
                "access_granted": False,
                "reason": "account_temporarily_locked",
                "lockout_expires": self._get_lockout_expiry(user_id, ip_address)
            }
        else:
            # Perform actual access validation (simplified)
            access_result = self._perform_access_check(user_id, resource, action)
        
        # Log the access attempt
        self.log_security_event({
            "event_type": "access_attempt",
            "user_id": user_id,
            "ip_address": ip_address,
            "resource": resource,
            "action": action,
            "success": access_result["access_granted"],
            "details": access_result
        })
        
        return access_result
    
    def _is_user_locked_out(self, user_id: str, ip_address: str) -> bool:
        """Check if user is currently locked out"""
        key = f"{user_id}:{ip_address}"
        attempts = self.failed_attempts.get(key, [])
        
        # Check last 30 minutes for lockout
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.fromisoformat(attempt["timestamp"]) >= thirty_minutes_ago
        ]
        
        # Lock out if 10 or more failed attempts in 30 minutes
        return len(recent_attempts) >= 10
    
    def _get_lockout_expiry(self, user_id: str, ip_address: str) -> str:
        """Get when lockout expires"""
        key = f"{user_id}:{ip_address}"
        attempts = self.failed_attempts.get(key, [])
        
        if attempts:
            latest_attempt = max(attempts, key=lambda x: x["timestamp"])
            expiry = datetime.fromisoformat(latest_attempt["timestamp"]) + timedelta(minutes=30)
            return expiry.isoformat()
        
        return datetime.now().isoformat()
    
    def _perform_access_check(self, user_id: str, resource: str, action: str) -> Dict[str, Any]:
        """Perform actual access control check (simplified implementation)"""
        # In a real implementation, this would check user roles, permissions, etc.
        return {
            "access_granted": True,
            "reason": "authorized",
            "permissions": ["read", "write"],  # Example permissions
            "policy_applied": "default_policy"
        }
    
    def generate_secure_token(self, token_type: str = "session", length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hash sensitive data with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use SHA-256 with salt
        hash_object = hashlib.sha256((data + salt).encode())
        hashed_data = hash_object.hexdigest()
        
        return {
            "hash": hashed_data,
            "salt": salt,
            "algorithm": "sha256"
        }
    
    def verify_hash(self, data: str, stored_hash: str, salt: str) -> bool:
        """Verify data against stored hash"""
        computed_hash = self.hash_sensitive_data(data, salt)["hash"]
        return computed_hash == stored_hash
    
    def get_security_summary(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get security summary for a time period"""
        if time_period is None:
            time_period = timedelta(days=7)
        
        cutoff_date = datetime.now() - time_period
        
        # Get events within time period
        period_events = [
            event for event in self.security_events.values()
            if datetime.fromisoformat(event["timestamp"]) >= cutoff_date
        ]
        
        # Count by event type
        events_by_type = {}
        failed_events = []
        
        for event in period_events:
            event_type = event["event_type"]
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            if not event["success"]:
                failed_events.append(event)
        
        # Get unique IP addresses with failed attempts
        suspicious_ips = set()
        for event in failed_events:
            if event.get("ip_address"):
                suspicious_ips.add(event["ip_address"])
        
        # Count locked out users
        locked_out_users = 0
        for key in self.failed_attempts.keys():
            user_id, ip_address = key.split(":", 1)
            if self._is_user_locked_out(user_id, ip_address):
                locked_out_users += 1
        
        return {
            "period_days": time_period.days,
            "total_security_events": len(period_events),
            "failed_events": len(failed_events),
            "events_by_type": events_by_type,
            "suspicious_ip_count": len(suspicious_ips),
            "locked_out_users": locked_out_users,
            "success_rate_percent": round(
                ((len(period_events) - len(failed_events)) / len(period_events) * 100)
                if period_events else 100, 2
            ),
            "generated_at": datetime.now().isoformat()
        }
