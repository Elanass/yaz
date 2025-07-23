"""
Just-in-Time (JIT) Role Elevation Service
Temporary role escalation for clinical procedures with auto-approval logic
"""

import secrets
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import structlog

from ..core.config import settings
from ..core.rbac import RBACMatrix, Role, Resource, Action
from ..db.models import User, RoleElevationRequest, RoleElevationApproval
from ..services.audit_service import AuditService, AuditEvent, AuditEventType, AuditSeverity

logger = structlog.get_logger(__name__)

class ElevationReason(str, Enum):
    """Reasons for role elevation"""
    EMERGENCY_PROCEDURE = "emergency_procedure"
    SURGICAL_ASSISTANCE = "surgical_assistance"
    SPECIALIST_CONSULTATION = "specialist_consultation"
    CLINICAL_TRIAL = "clinical_trial"
    RESEARCH_ACCESS = "research_access"
    ADMINISTRATIVE_TASK = "administrative_task"
    SYSTEM_MAINTENANCE = "system_maintenance"
    AUDIT_REVIEW = "audit_review"
    OTHER = "other"

class ElevationStatus(str, Enum):
    """Status of elevation request"""
    PENDING = "pending"
    AUTO_APPROVED = "auto_approved"
    MANUALLY_APPROVED = "manually_approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"
    COMPLETED = "completed"

class ElevationUrgency(str, Enum):
    """Urgency levels for elevation requests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ElevationRequest:
    """JIT role elevation request"""
    requester_id: int
    target_role: Role
    reason: ElevationReason
    justification: str
    urgency: ElevationUrgency
    duration_hours: int
    context: Dict[str, Any]
    auto_approve: bool = False
    
    def __post_init__(self):
        # Validate duration
        if self.duration_hours < 1 or self.duration_hours > 168:  # Max 1 week
            raise ValueError("Duration must be between 1 and 168 hours")

class JITElevationRules:
    """Rules engine for automatic approval of role elevations"""
    
    def __init__(self):
        self.rbac = RBACMatrix()
        
        # Define auto-approval rules
        self.auto_approval_rules = {
            # Nurse -> Surgeon Assistant (for specific procedures)
            (Role.NURSE, Role.SURGEON): {
                "max_duration_hours": 8,
                "allowed_reasons": [ElevationReason.SURGICAL_ASSISTANCE],
                "required_context": ["procedure_id", "supervising_surgeon"],
                "approval_conditions": self._validate_surgical_assistance
            },
            
            # Physician -> Oncologist (for consultation)
            (Role.PHYSICIAN, Role.ONCOLOGIST): {
                "max_duration_hours": 24,
                "allowed_reasons": [ElevationReason.SPECIALIST_CONSULTATION],
                "required_context": ["patient_id", "consultation_type"],
                "approval_conditions": self._validate_oncology_consultation
            },
            
            # Researcher -> Physician (for clinical trials)
            (Role.RESEARCHER, Role.PHYSICIAN): {
                "max_duration_hours": 48,
                "allowed_reasons": [ElevationReason.CLINICAL_TRIAL],
                "required_context": ["trial_id", "patient_id"],
                "approval_conditions": self._validate_clinical_trial_access
            },
            
            # Any -> Administrator (emergency only)
            ("ANY", Role.ADMINISTRATOR): {
                "max_duration_hours": 2,
                "allowed_reasons": [ElevationReason.EMERGENCY_PROCEDURE, ElevationReason.SYSTEM_MAINTENANCE],
                "required_context": ["emergency_code", "incident_id"],
                "approval_conditions": self._validate_emergency_admin
            }
        }
    
    def can_auto_approve(
        self, 
        request: ElevationRequest, 
        requester: User,
        context: Dict[str, Any] = None
    ) -> bool:
        """Check if elevation request can be auto-approved"""
        
        try:
            # Get rule for this role transition
            rule = self._get_matching_rule(requester.role, request.target_role)
            if not rule:
                return False
            
            # Check duration
            if request.duration_hours > rule["max_duration_hours"]:
                return False
            
            # Check reason
            if request.reason not in rule["allowed_reasons"]:
                return False
            
            # Check required context
            for required_field in rule["required_context"]:
                if required_field not in request.context:
                    return False
            
            # Run custom approval conditions
            approval_func = rule.get("approval_conditions")
            if approval_func:
                return approval_func(request, requester, context or {})
            
            return True
            
        except Exception as e:
            logger.error("Auto-approval check failed", error=str(e))
            return False
    
    def _get_matching_rule(self, current_role: Role, target_role: Role) -> Optional[Dict]:
        """Get matching auto-approval rule"""
        
        # Check exact match
        rule_key = (current_role, target_role)
        if rule_key in self.auto_approval_rules:
            return self.auto_approval_rules[rule_key]
        
        # Check wildcard rules
        wildcard_key = ("ANY", target_role)
        if wildcard_key in self.auto_approval_rules:
            return self.auto_approval_rules[wildcard_key]
        
        return None
    
    def _validate_surgical_assistance(
        self, 
        request: ElevationRequest, 
        requester: User, 
        context: Dict[str, Any]
    ) -> bool:
        """Validate surgical assistance elevation"""
        
        # Check if supervising surgeon exists and is active
        supervising_surgeon_id = request.context.get("supervising_surgeon")
        if not supervising_surgeon_id:
            return False
        
        # In a real implementation, you would check:
        # - Surgeon is authorized for this procedure
        # - Procedure is scheduled and active
        # - Nurse is assigned to this procedure
        # - No conflicts with other assignments
        
        return True
    
    def _validate_oncology_consultation(
        self, 
        request: ElevationRequest, 
        requester: User, 
        context: Dict[str, Any]
    ) -> bool:
        """Validate oncology consultation elevation"""
        
        # Check if patient exists and consultation is valid
        patient_id = request.context.get("patient_id")
        consultation_type = request.context.get("consultation_type")
        
        if not patient_id or not consultation_type:
            return False
        
        # Validate consultation type
        valid_types = [
            "initial_consultation",
            "follow_up",
            "treatment_planning",
            "second_opinion"
        ]
        
        return consultation_type in valid_types
    
    def _validate_clinical_trial_access(
        self, 
        request: ElevationRequest, 
        requester: User, 
        context: Dict[str, Any]
    ) -> bool:
        """Validate clinical trial access elevation"""
        
        trial_id = request.context.get("trial_id")
        patient_id = request.context.get("patient_id")
        
        if not trial_id or not patient_id:
            return False
        
        # In a real implementation, check:
        # - Researcher is authorized for this trial
        # - Patient is enrolled in the trial
        # - Trial is active and recruiting
        # - Required approvals are in place
        
        return True
    
    def _validate_emergency_admin(
        self, 
        request: ElevationRequest, 
        requester: User, 
        context: Dict[str, Any]
    ) -> bool:
        """Validate emergency administrator access"""
        
        emergency_code = request.context.get("emergency_code")
        incident_id = request.context.get("incident_id")
        
        if not emergency_code or not incident_id:
            return False
        
        # In a real implementation, verify:
        # - Emergency code is valid and active
        # - Incident is logged and requires admin access
        # - User has emergency response training
        # - Escalation protocols are followed
        
        return emergency_code.startswith("EMG_") and len(incident_id) > 5

class JITRoleElevationService:
    """Main service for just-in-time role elevation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.rules_engine = JITElevationRules()
        
        # Active elevations cache (in production, use Redis)
        self._active_elevations: Dict[int, Dict[str, Any]] = {}
    
    async def request_elevation(
        self,
        request: ElevationRequest,
        requester: User,
        approver_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Submit role elevation request"""
        
        try:
            # Generate unique request ID
            request_id = secrets.token_urlsafe(16)
            
            # Check if auto-approval is possible
            can_auto_approve = self.rules_engine.can_auto_approve(request, requester)
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(hours=request.duration_hours)
            
            # Create elevation request record
            elevation_request = RoleElevationRequest(
                request_id=request_id,
                requester_id=request.requester_id,
                current_role=requester.role.value,
                target_role=request.target_role.value,
                reason=request.reason.value,
                justification=request.justification,
                urgency=request.urgency.value,
                duration_hours=request.duration_hours,
                expires_at=expires_at,
                context=request.context,
                status=ElevationStatus.AUTO_APPROVED.value if can_auto_approve else ElevationStatus.PENDING.value,
                auto_approved=can_auto_approve
            )
            
            self.db.add(elevation_request)
            self.db.flush()  # Get the ID
            
            # If auto-approved, activate immediately
            if can_auto_approve:
                await self._activate_elevation(elevation_request, requester)
            else:
                # Create approval requests for specified approvers
                if approver_ids:
                    await self._create_approval_requests(elevation_request, approver_ids)
                else:
                    # Auto-assign approvers based on target role
                    auto_approvers = await self._get_auto_approvers(request.target_role)
                    await self._create_approval_requests(elevation_request, auto_approvers)
            
            self.db.commit()
            
            # Log elevation request
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.PERMISSION_CHANGE,
                    user_id=requester.id,
                    resource_type="role_elevation",
                    resource_id=request_id,
                    action="request_elevation",
                    details={
                        "current_role": requester.role.value,
                        "target_role": request.target_role.value,
                        "reason": request.reason.value,
                        "duration_hours": request.duration_hours,
                        "auto_approved": can_auto_approve,
                        "urgency": request.urgency.value
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.HIGH
                )
            )
            
            return {
                "request_id": request_id,
                "status": elevation_request.status,
                "auto_approved": can_auto_approve,
                "expires_at": expires_at.isoformat(),
                "active": can_auto_approve,
                "message": "Role elevation activated" if can_auto_approve else "Role elevation request submitted for approval"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create elevation request", error=str(e))
            raise
    
    async def approve_elevation(
        self,
        request_id: str,
        approver: User,
        approved: bool,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve or deny elevation request"""
        
        try:
            # Get elevation request
            elevation_request = self.db.query(RoleElevationRequest).filter(
                RoleElevationRequest.request_id == request_id,
                RoleElevationRequest.status == ElevationStatus.PENDING.value
            ).first()
            
            if not elevation_request:
                raise ValueError("Elevation request not found or not pending")
            
            # Check if approver has authority
            if not await self._can_approve_elevation(approver, elevation_request):
                raise ValueError("Insufficient authority to approve this elevation")
            
            # Create approval record
            approval = RoleElevationApproval(
                request_id=elevation_request.id,
                approver_id=approver.id,
                approved=approved,
                comments=comments or "",
                approved_at=datetime.utcnow()
            )
            
            self.db.add(approval)
            
            if approved:
                # Update request status
                elevation_request.status = ElevationStatus.MANUALLY_APPROVED.value
                elevation_request.approved_by = approver.id
                elevation_request.approved_at = datetime.utcnow()
                
                # Activate elevation
                requester = self.db.query(User).filter(User.id == elevation_request.requester_id).first()
                await self._activate_elevation(elevation_request, requester)
                
                message = "Role elevation approved and activated"
            else:
                # Deny request
                elevation_request.status = ElevationStatus.DENIED.value
                message = "Role elevation denied"
            
            self.db.commit()
            
            # Log approval/denial
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.PERMISSION_CHANGE,
                    user_id=approver.id,
                    resource_type="role_elevation",
                    resource_id=request_id,
                    action="approve_elevation" if approved else "deny_elevation",
                    details={
                        "requester_id": elevation_request.requester_id,
                        "target_role": elevation_request.target_role,
                        "approved": approved,
                        "comments": comments
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.HIGH
                )
            )
            
            return {
                "request_id": request_id,
                "approved": approved,
                "message": message,
                "active": approved
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to approve elevation", error=str(e))
            raise
    
    async def revoke_elevation(
        self,
        request_id: str,
        revoker: User,
        reason: str = "manual_revocation"
    ) -> bool:
        """Revoke active role elevation"""
        
        try:
            # Check if elevation is active
            if request_id not in self._active_elevations:
                return False
            
            elevation_data = self._active_elevations[request_id]
            
            # Check authority to revoke
            if not await self._can_revoke_elevation(revoker, elevation_data):
                raise ValueError("Insufficient authority to revoke this elevation")
            
            # Update database record
            elevation_request = self.db.query(RoleElevationRequest).filter(
                RoleElevationRequest.request_id == request_id
            ).first()
            
            if elevation_request:
                elevation_request.status = ElevationStatus.REVOKED.value
                elevation_request.revoked_by = revoker.id
                elevation_request.revoked_at = datetime.utcnow()
                elevation_request.revocation_reason = reason
            
            # Remove from active elevations
            del self._active_elevations[request_id]
            
            self.db.commit()
            
            # Log revocation
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.PERMISSION_CHANGE,
                    user_id=revoker.id,
                    resource_type="role_elevation",
                    resource_id=request_id,
                    action="revoke_elevation",
                    details={
                        "requester_id": elevation_data["requester_id"],
                        "target_role": elevation_data["target_role"],
                        "reason": reason
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.HIGH
                )
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to revoke elevation", error=str(e))
            raise
    
    async def get_user_elevations(
        self,
        user_id: int,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's role elevations"""
        
        query = self.db.query(RoleElevationRequest).filter(
            RoleElevationRequest.requester_id == user_id
        )
        
        if active_only:
            active_statuses = [
                ElevationStatus.AUTO_APPROVED.value,
                ElevationStatus.MANUALLY_APPROVED.value
            ]
            query = query.filter(
                RoleElevationRequest.status.in_(active_statuses),
                RoleElevationRequest.expires_at > datetime.utcnow()
            )
        
        elevations = query.order_by(RoleElevationRequest.created_at.desc()).all()
        
        return [
            {
                "request_id": elev.request_id,
                "current_role": elev.current_role,
                "target_role": elev.target_role,
                "reason": elev.reason,
                "justification": elev.justification,
                "urgency": elev.urgency,
                "duration_hours": elev.duration_hours,
                "status": elev.status,
                "created_at": elev.created_at.isoformat(),
                "expires_at": elev.expires_at.isoformat(),
                "auto_approved": elev.auto_approved,
                "context": elev.context,
                "active": elev.request_id in self._active_elevations
            }
            for elev in elevations
        ]
    
    async def get_pending_approvals(self, approver_id: int) -> List[Dict[str, Any]]:
        """Get pending elevation requests for approver"""
        
        # This would need a more sophisticated query based on approval workflows
        # For now, return pending requests that the user can approve
        
        pending_requests = self.db.query(RoleElevationRequest).filter(
            RoleElevationRequest.status == ElevationStatus.PENDING.value
        ).all()
        
        # Filter by approval authority
        approved_requests = []
        for request in pending_requests:
            requester = self.db.query(User).filter(User.id == request.requester_id).first()
            if await self._can_approve_elevation_by_role(approver_id, request):
                approved_requests.append({
                    "request_id": request.request_id,
                    "requester": {
                        "id": requester.id,
                        "username": requester.username,
                        "first_name": requester.first_name,
                        "last_name": requester.last_name
                    },
                    "current_role": request.current_role,
                    "target_role": request.target_role,
                    "reason": request.reason,
                    "justification": request.justification,
                    "urgency": request.urgency,
                    "duration_hours": request.duration_hours,
                    "created_at": request.created_at.isoformat(),
                    "expires_at": request.expires_at.isoformat(),
                    "context": request.context
                })
        
        return approved_requests
    
    async def _activate_elevation(self, elevation_request: RoleElevationRequest, requester: User):
        """Activate role elevation"""
        
        self._active_elevations[elevation_request.request_id] = {
            "requester_id": requester.id,
            "current_role": elevation_request.current_role,
            "target_role": elevation_request.target_role,
            "activated_at": datetime.utcnow(),
            "expires_at": elevation_request.expires_at,
            "context": elevation_request.context
        }
        
        logger.info(
            "Role elevation activated",
            user_id=requester.id,
            request_id=elevation_request.request_id,
            target_role=elevation_request.target_role
        )
    
    async def _create_approval_requests(self, elevation_request: RoleElevationRequest, approver_ids: List[int]):
        """Create approval requests for specified approvers"""
        
        for approver_id in approver_ids:
            approval = RoleElevationApproval(
                request_id=elevation_request.id,
                approver_id=approver_id,
                approved=None,  # Pending
                comments="",
                approved_at=None
            )
            self.db.add(approval)
    
    async def _get_auto_approvers(self, target_role: Role) -> List[int]:
        """Get list of users who can approve elevation to target role"""
        
        # Define approval hierarchy
        approval_roles = {
            Role.SURGEON: [Role.SURGEON, Role.ADMINISTRATOR],
            Role.ONCOLOGIST: [Role.ONCOLOGIST, Role.ADMINISTRATOR],
            Role.PHYSICIAN: [Role.PHYSICIAN, Role.SURGEON, Role.ONCOLOGIST, Role.ADMINISTRATOR],
            Role.NURSE: [Role.PHYSICIAN, Role.SURGEON, Role.ONCOLOGIST, Role.ADMINISTRATOR],
            Role.ADMINISTRATOR: [Role.SUPER_ADMIN],
            Role.SUPER_ADMIN: []  # Cannot be elevated to
        }
        
        authorized_roles = approval_roles.get(target_role, [Role.ADMINISTRATOR])
        
        approvers = self.db.query(User).filter(
            User.role.in_([role.value for role in authorized_roles]),
            User.is_active == True
        ).all()
        
        return [approver.id for approver in approvers]
    
    async def _can_approve_elevation(self, approver: User, elevation_request: RoleElevationRequest) -> bool:
        """Check if user can approve this elevation request"""
        
        target_role = Role(elevation_request.target_role)
        auto_approvers = await self._get_auto_approvers(target_role)
        
        return approver.id in auto_approvers
    
    async def _can_approve_elevation_by_role(self, approver_id: int, elevation_request: RoleElevationRequest) -> bool:
        """Check if user can approve elevation by role"""
        
        approver = self.db.query(User).filter(User.id == approver_id).first()
        if not approver:
            return False
        
        return await self._can_approve_elevation(approver, elevation_request)
    
    async def _can_revoke_elevation(self, revoker: User, elevation_data: Dict[str, Any]) -> bool:
        """Check if user can revoke this elevation"""
        
        # Super admins can revoke any elevation
        if revoker.role == Role.SUPER_ADMIN:
            return True
        
        # Admins can revoke non-admin elevations
        if revoker.role == Role.ADMINISTRATOR and elevation_data["target_role"] != Role.ADMINISTRATOR.value:
            return True
        
        # Users can revoke their own elevations
        if revoker.id == elevation_data["requester_id"]:
            return True
        
        return False
    
    async def cleanup_expired_elevations(self):
        """Clean up expired elevations (should be run periodically)"""
        
        current_time = datetime.utcnow()
        expired_request_ids = []
        
        # Check active elevations for expiration
        for request_id, elevation_data in self._active_elevations.items():
            if elevation_data["expires_at"] < current_time:
                expired_request_ids.append(request_id)
        
        # Remove expired elevations
        for request_id in expired_request_ids:
            del self._active_elevations[request_id]
            
            # Update database
            elevation_request = self.db.query(RoleElevationRequest).filter(
                RoleElevationRequest.request_id == request_id
            ).first()
            
            if elevation_request:
                elevation_request.status = ElevationStatus.EXPIRED.value
        
        if expired_request_ids:
            self.db.commit()
            logger.info("Cleaned up expired elevations", count=len(expired_request_ids))
    
    def has_elevated_role(self, user_id: int, target_role: Role) -> bool:
        """Check if user currently has elevated role"""
        
        for elevation_data in self._active_elevations.values():
            if (elevation_data["requester_id"] == user_id and 
                elevation_data["target_role"] == target_role.value and
                elevation_data["expires_at"] > datetime.utcnow()):
                return True
        
        return False
    
    def get_effective_role(self, user: User) -> Role:
        """Get user's effective role (considering elevations)"""
        
        # Check for active elevations
        highest_role = user.role
        
        for elevation_data in self._active_elevations.values():
            if (elevation_data["requester_id"] == user.id and
                elevation_data["expires_at"] > datetime.utcnow()):
                
                elevated_role = Role(elevation_data["target_role"])
                # This is a simplified role hierarchy comparison
                # In practice, you'd want a more sophisticated comparison
                if self._role_hierarchy_level(elevated_role) > self._role_hierarchy_level(highest_role):
                    highest_role = elevated_role
        
        return highest_role
    
    def _role_hierarchy_level(self, role: Role) -> int:
        """Get role hierarchy level (higher number = more privileges)"""
        
        hierarchy = {
            Role.PATIENT: 0,
            Role.NURSE: 1,
            Role.PHYSICIAN: 2,
            Role.SURGEON: 3,
            Role.ONCOLOGIST: 3,
            Role.RESEARCHER: 2,
            Role.ADMINISTRATOR: 4,
            Role.SUPER_ADMIN: 5,
            Role.AUDITOR: 2
        }
        
        return hierarchy.get(role, 0)
