"""
Advanced Role-Based Access Control (RBAC) Matrix
Fine-grained permissions for clinical workflows
"""

from typing import Dict, List, Set, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

class Resource(str, Enum):
    """System resources that can be protected"""
    PATIENT = "patient"
    PROTOCOL = "protocol"
    DECISION = "decision"
    EVIDENCE = "evidence"
    AUDIT_LOG = "audit_log"
    USER_MANAGEMENT = "user_management"
    CLINICAL_DATA = "clinical_data"
    RESEARCH_DATA = "research_data"
    SYSTEM_CONFIG = "system_config"

class Action(str, Enum):
    """Actions that can be performed on resources"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"
    SHARE = "share"
    AUDIT = "audit"
    COMMENT = "comment"
    FORK = "fork"

class Role(str, Enum):
    """System roles with hierarchical permissions"""
    PATIENT = "patient"
    NURSE = "nurse"
    PHYSICIAN = "physician"
    SURGEON = "surgeon"
    ONCOLOGIST = "oncologist"
    RESEARCHER = "researcher"
    ADMINISTRATOR = "administrator"
    SUPER_ADMIN = "super_admin"
    AUDITOR = "auditor"

@dataclass
class Permission:
    """Individual permission definition"""
    resource: Resource
    action: Action
    conditions: Optional[Dict] = None  # Additional conditions (e.g., own_data_only)
    data_sensitivity: str = "normal"  # normal, sensitive, highly_sensitive
    
class PatientGroup(str, Enum):
    """Patient groupings for data access control"""
    OWN_PATIENTS = "own_patients"
    DEPARTMENT_PATIENTS = "department_patients"
    ALL_PATIENTS = "all_patients"
    RESEARCH_COHORT = "research_cohort"

class ProtocolType(str, Enum):
    """Protocol classifications"""
    STANDARD = "standard"
    EXPERIMENTAL = "experimental"
    RESEARCH = "research"
    EMERGENCY = "emergency"

class RBACMatrix:
    """Advanced RBAC matrix with fine-grained controls"""
    
    def __init__(self):
        self._role_permissions = self._initialize_permissions()
        self._context_rules = self._initialize_context_rules()
    
    def _initialize_permissions(self) -> Dict[Role, Set[Permission]]:
        """Initialize the permission matrix"""
        matrix = {
            Role.PATIENT: {
                Permission(Resource.PATIENT, Action.READ, {"scope": "own_data"}),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"scope": "own_data"}),
                Permission(Resource.DECISION, Action.READ, {"scope": "own_data"}),
                Permission(Resource.EVIDENCE, Action.READ, {"data_sensitivity": "normal"}),
                Permission(Resource.PROTOCOL, Action.READ, {"approved_only": True}),
            },
            
            Role.NURSE: {
                Permission(Resource.PATIENT, Action.READ, {"scope": "assigned_patients"}),
                Permission(Resource.PATIENT, Action.UPDATE, {"fields": ["vital_signs", "notes"]}),
                Permission(Resource.CLINICAL_DATA, Action.CREATE, {"data_type": "vital_signs"}),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"scope": "assigned_patients"}),
                Permission(Resource.PROTOCOL, Action.READ, {"approved_only": True}),
                Permission(Resource.DECISION, Action.READ, {"scope": "assigned_patients"}),
            },
            
            Role.PHYSICIAN: {
                Permission(Resource.PATIENT, Action.CREATE),
                Permission(Resource.PATIENT, Action.READ, {"scope": "department_patients"}),
                Permission(Resource.PATIENT, Action.UPDATE, {"scope": "assigned_patients"}),
                Permission(Resource.CLINICAL_DATA, Action.CREATE),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"scope": "department_patients"}),
                Permission(Resource.CLINICAL_DATA, Action.UPDATE, {"scope": "assigned_patients"}),
                Permission(Resource.DECISION, Action.CREATE),
                Permission(Resource.DECISION, Action.READ, {"scope": "department_patients"}),
                Permission(Resource.PROTOCOL, Action.READ),
                Permission(Resource.PROTOCOL, Action.COMMENT),
                Permission(Resource.EVIDENCE, Action.READ),
                Permission(Resource.EVIDENCE, Action.COMMENT),
            },
            
            Role.SURGEON: {
                Permission(Resource.PATIENT, Action.CREATE),
                Permission(Resource.PATIENT, Action.READ, {"scope": "surgical_patients"}),
                Permission(Resource.PATIENT, Action.UPDATE, {"scope": "surgical_patients"}),
                Permission(Resource.CLINICAL_DATA, Action.CREATE),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"scope": "surgical_patients"}),
                Permission(Resource.CLINICAL_DATA, Action.UPDATE, {"scope": "surgical_patients"}),
                Permission(Resource.DECISION, Action.CREATE),
                Permission(Resource.DECISION, Action.READ, {"scope": "surgical_patients"}),
                Permission(Resource.DECISION, Action.APPROVE, {"protocol_type": "surgical"}),
                Permission(Resource.PROTOCOL, Action.READ),
                Permission(Resource.PROTOCOL, Action.COMMENT),
                Permission(Resource.PROTOCOL, Action.FORK, {"protocol_type": "surgical"}),
                Permission(Resource.EVIDENCE, Action.READ),
                Permission(Resource.EVIDENCE, Action.CREATE, {"evidence_type": "surgical_outcome"}),
            },
            
            Role.ONCOLOGIST: {
                Permission(Resource.PATIENT, Action.CREATE),
                Permission(Resource.PATIENT, Action.READ, {"scope": "oncology_patients"}),
                Permission(Resource.PATIENT, Action.UPDATE, {"scope": "oncology_patients"}),
                Permission(Resource.CLINICAL_DATA, Action.CREATE),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"scope": "oncology_patients"}),
                Permission(Resource.CLINICAL_DATA, Action.UPDATE, {"scope": "oncology_patients"}),
                Permission(Resource.DECISION, Action.CREATE),
                Permission(Resource.DECISION, Action.READ, {"scope": "oncology_patients"}),
                Permission(Resource.DECISION, Action.APPROVE, {"protocol_type": "oncology"}),
                Permission(Resource.PROTOCOL, Action.READ),
                Permission(Resource.PROTOCOL, Action.CREATE, {"protocol_type": "oncology"}),
                Permission(Resource.PROTOCOL, Action.UPDATE, {"protocol_type": "oncology"}),
                Permission(Resource.PROTOCOL, Action.COMMENT),
                Permission(Resource.PROTOCOL, Action.FORK),
                Permission(Resource.EVIDENCE, Action.READ),
                Permission(Resource.EVIDENCE, Action.CREATE),
                Permission(Resource.EVIDENCE, Action.UPDATE, {"scope": "own_evidence"}),
            },
            
            Role.RESEARCHER: {
                Permission(Resource.PATIENT, Action.READ, {"scope": "research_cohort", "anonymized": True}),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"scope": "research_cohort", "anonymized": True}),
                Permission(Resource.RESEARCH_DATA, Action.CREATE),
                Permission(Resource.RESEARCH_DATA, Action.READ),
                Permission(Resource.RESEARCH_DATA, Action.UPDATE, {"scope": "own_research"}),
                Permission(Resource.DECISION, Action.READ, {"scope": "research_cohort", "anonymized": True}),
                Permission(Resource.PROTOCOL, Action.READ),
                Permission(Resource.PROTOCOL, Action.CREATE, {"protocol_type": "research"}),
                Permission(Resource.PROTOCOL, Action.FORK),
                Permission(Resource.EVIDENCE, Action.READ),
                Permission(Resource.EVIDENCE, Action.CREATE, {"evidence_type": "research"}),
                Permission(Resource.EVIDENCE, Action.EXPORT, {"format": "anonymized"}),
            },
            
            Role.ADMINISTRATOR: {
                Permission(Resource.USER_MANAGEMENT, Action.CREATE),
                Permission(Resource.USER_MANAGEMENT, Action.READ),
                Permission(Resource.USER_MANAGEMENT, Action.UPDATE),
                Permission(Resource.USER_MANAGEMENT, Action.DELETE),
                Permission(Resource.SYSTEM_CONFIG, Action.READ),
                Permission(Resource.SYSTEM_CONFIG, Action.UPDATE),
                Permission(Resource.AUDIT_LOG, Action.READ),
                Permission(Resource.PROTOCOL, Action.APPROVE),
                Permission(Resource.PROTOCOL, Action.READ),
                Permission(Resource.PROTOCOL, Action.UPDATE, {"status": "administrative"}),
            },
            
            Role.AUDITOR: {
                Permission(Resource.AUDIT_LOG, Action.READ),
                Permission(Resource.AUDIT_LOG, Action.EXPORT),
                Permission(Resource.PATIENT, Action.READ, {"audit_purpose": True, "anonymized": True}),
                Permission(Resource.CLINICAL_DATA, Action.READ, {"audit_purpose": True, "anonymized": True}),
                Permission(Resource.DECISION, Action.READ, {"audit_purpose": True, "anonymized": True}),
                Permission(Resource.EVIDENCE, Action.READ, {"audit_purpose": True}),
                Permission(Resource.PROTOCOL, Action.READ, {"audit_purpose": True}),
            }
        }
        return matrix
    
    def _initialize_context_rules(self) -> Dict[str, callable]:
        """Initialize context-based rules"""
        return {
            "time_based": self._check_time_restrictions,
            "location_based": self._check_location_restrictions,
            "emergency_override": self._check_emergency_conditions,
            "data_sensitivity": self._check_data_sensitivity,
            "patient_consent": self._check_patient_consent,
        }
    
    def check_permission(
        self,
        user_role: Role,
        resource: Resource,
        action: Action,
        context: Optional[Dict] = None
    ) -> bool:
        """Check if a role has permission for a specific action on a resource"""
        if context is None:
            context = {}
        
        role_permissions = self._role_permissions.get(user_role, set())
        
        # Check direct permissions
        for permission in role_permissions:
            if permission.resource == resource and permission.action == action:
                # Check conditions
                if self._check_conditions(permission.conditions, context):
                    # Apply context rules
                    if self._apply_context_rules(permission, context):
                        return True
        
        # Check hierarchical permissions (e.g., SUPER_ADMIN has all permissions)
        if user_role == Role.SUPER_ADMIN:
            return True
        
        return False
    
    def _check_conditions(self, conditions: Optional[Dict], context: Dict) -> bool:
        """Check if permission conditions are met"""
        if not conditions:
            return True
        
        for condition_key, condition_value in conditions.items():
            context_value = context.get(condition_key)
            
            if condition_key == "scope":
                if not self._check_scope_access(condition_value, context):
                    return False
            elif condition_key == "approved_only":
                if condition_value and not context.get("is_approved", False):
                    return False
            elif condition_key == "anonymized":
                if condition_value and not context.get("is_anonymized", False):
                    return False
            elif context_value != condition_value:
                return False
        
        return True
    
    def _check_scope_access(self, required_scope: str, context: Dict) -> bool:
        """Check scope-based access"""
        user_id = context.get("user_id")
        resource_owner = context.get("resource_owner")
        department = context.get("department")
        
        if required_scope == "own_data":
            return user_id == resource_owner
        elif required_scope == "assigned_patients":
            return context.get("is_assigned_provider", False)
        elif required_scope == "department_patients":
            return context.get("same_department", False)
        elif required_scope == "research_cohort":
            return context.get("in_research_cohort", False)
        
        return False
    
    def _apply_context_rules(self, permission: Permission, context: Dict) -> bool:
        """Apply context-based rules"""
        for rule_name, rule_func in self._context_rules.items():
            if not rule_func(permission, context):
                return False
        return True
    
    def _check_time_restrictions(self, permission: Permission, context: Dict) -> bool:
        """Check time-based access restrictions"""
        time_restrictions = context.get("time_restrictions")
        if not time_restrictions:
            return True
        
        current_time = datetime.now()
        start_time = time_restrictions.get("start_time")
        end_time = time_restrictions.get("end_time")
        
        if start_time and current_time < start_time:
            return False
        if end_time and current_time > end_time:
            return False
        
        return True
    
    def _check_location_restrictions(self, permission: Permission, context: Dict) -> bool:
        """Check location-based access restrictions"""
        allowed_locations = context.get("allowed_locations")
        current_location = context.get("current_location")
        
        if allowed_locations and current_location:
            return current_location in allowed_locations
        
        return True
    
    def _check_emergency_conditions(self, permission: Permission, context: Dict) -> bool:
        """Check emergency override conditions"""
        is_emergency = context.get("is_emergency", False)
        emergency_override = context.get("emergency_override", False)
        
        # In emergency situations, allow broader access
        if is_emergency and emergency_override:
            return True
        
        return True
    
    def _check_data_sensitivity(self, permission: Permission, context: Dict) -> bool:
        """Check data sensitivity level access"""
        required_clearance = permission.data_sensitivity
        user_clearance = context.get("security_clearance", "normal")
        
        clearance_levels = {
            "normal": 1,
            "sensitive": 2,
            "highly_sensitive": 3
        }
        
        return clearance_levels.get(user_clearance, 1) >= clearance_levels.get(required_clearance, 1)
    
    def _check_patient_consent(self, permission: Permission, context: Dict) -> bool:
        """Check patient consent for data access"""
        requires_consent = context.get("requires_consent", False)
        has_consent = context.get("has_patient_consent", True)
        
        if requires_consent:
            return has_consent
        
        return True
    
    def get_user_permissions(self, user_role: Role) -> List[Dict]:
        """Get all permissions for a user role"""
        role_permissions = self._role_permissions.get(user_role, set())
        
        permissions = []
        for permission in role_permissions:
            permissions.append({
                "resource": permission.resource.value,
                "action": permission.action.value,
                "conditions": permission.conditions,
                "data_sensitivity": permission.data_sensitivity
            })
        
        return permissions
    
    def export_permission_matrix(self) -> str:
        """Export the complete permission matrix as JSON"""
        matrix = {}
        
        for role, permissions in self._role_permissions.items():
            matrix[role.value] = []
            for permission in permissions:
                matrix[role.value].append({
                    "resource": permission.resource.value,
                    "action": permission.action.value,
                    "conditions": permission.conditions,
                    "data_sensitivity": permission.data_sensitivity
                })
        
        return json.dumps(matrix, indent=2)

# Global RBAC instance
rbac = RBACMatrix()

def check_permission(user_role: str, resource: str, action: str, context: Dict = None) -> bool:
    """Convenience function to check permissions"""
    try:
        role_enum = Role(user_role)
        resource_enum = Resource(resource)
        action_enum = Action(action)
        return rbac.check_permission(role_enum, resource_enum, action_enum, context or {})
    except ValueError:
        return False

def get_user_permissions(user_role: str) -> List[Dict]:
    """Convenience function to get user permissions"""
    try:
        role_enum = Role(user_role)
        return rbac.get_user_permissions(role_enum)
    except ValueError:
        return []
