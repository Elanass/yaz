"""
Core Services
Base service classes and common business logic
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from surgify.core.config.settings import get_settings
from surgify.core.models.base import ApiResponse, PaginationMeta, PaginationParams

logger = logging.getLogger(__name__)

T = TypeVar('T')
CreateT = TypeVar('CreateT')
UpdateT = TypeVar('UpdateT')


class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "service": self.__class__.__name__,
            "status": "healthy",
            "version": self.settings.app.version
        }


class CRUDService(BaseService, ABC):
    """Base CRUD service with standard operations"""
    
    @abstractmethod
    async def create(self, data: CreateT) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None
    ) -> ApiResponse[List[T]]:
        """Get all entities with pagination"""
        pass
    
    @abstractmethod
    async def update(self, id: Any, data: UpdateT) -> Optional[T]:
        """Update entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity"""
        pass


class CacheService(BaseService):
    """In-memory cache service for development"""
    
    def __init__(self):
        super().__init__()
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        import time
        
        if key not in self._cache:
            return None
        
        # Check TTL
        if key in self._ttl and time.time() > self._ttl[key]:
            await self.delete(key)
            return None
        
        return self._cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        import time
        
        self._cache[key] = value
        
        if ttl:
            self._ttl[key] = time.time() + ttl
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
        self._ttl.pop(key, None)
    
    async def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._ttl.clear()
    
    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern"""
        if pattern:
            import fnmatch
            return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        return list(self._cache.keys())


class ValidationService(BaseService):
    """Data validation service"""
    
    def validate_clinical_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate clinical data"""
        errors = []
        
        # Age validation
        if "age" in data:
            age = data["age"]
            if not isinstance(age, (int, float)) or age < 0 or age > 150:
                errors.append("Age must be between 0 and 150")
        
        # Performance status validation
        if "performance_status" in data:
            ps = data["performance_status"]
            if not isinstance(ps, int) or ps < 0 or ps > 4:
                errors.append("Performance status must be between 0 and 4")
        
        # TNM staging validation
        if "tumor_stage" in data:
            stage = data["tumor_stage"]
            valid_stages = ["T1a", "T1b", "T2", "T3", "T4a", "T4b", "Tx"]
            if stage not in valid_stages:
                errors.append(f"Invalid tumor stage. Must be one of {valid_stages}")
        
        return errors
    
    def validate_confidence_score(self, score: float) -> List[str]:
        """Validate confidence score"""
        errors = []
        
        if not isinstance(score, (int, float)):
            errors.append("Confidence score must be a number")
        elif score < 0 or score > 1:
            errors.append("Confidence score must be between 0 and 1")
        
        return errors


class AuditService(BaseService):
    """Audit logging service for HIPAA compliance"""
    
    async def log_action(
        self,
        user_id: Optional[str],
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Log an audit event"""
        
        audit_entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address
        }
        
        # In production, this would write to a secure audit log
        self.logger.info(f"AUDIT: {audit_entry}")
    
    async def log_data_access(
        self,
        user_id: str,
        data_type: str,
        record_count: int,
        query_params: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log data access for compliance"""
        
        await self.log_action(
            user_id=user_id,
            action="data_access",
            resource=data_type,
            details={
                "record_count": record_count,
                "query_params": query_params or {}
            }
        )


class NotificationService(BaseService):
    """Notification service for clinical alerts"""
    
    async def send_clinical_alert(
        self,
        user_id: str,
        title: str,
        message: str,
        priority: str = "normal",
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send clinical alert notification"""
        
        try:
            # In production, this would integrate with push notification services
            notification = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "priority": priority,
                "data": data or {},
                "timestamp": asyncio.get_event_loop().time()
            }
            
            self.logger.info(f"Clinical alert sent: {notification}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    async def send_decision_complete(
        self,
        user_id: str,
        decision_id: str,
        confidence_score: float
    ) -> bool:
        """Send notification when decision is complete"""
        
        return await self.send_clinical_alert(
            user_id=user_id,
            title="Decision Analysis Complete",
            message=f"Decision {decision_id} completed with {confidence_score:.1%} confidence",
            priority="high",
            data={"decision_id": decision_id, "confidence": confidence_score}
        )
