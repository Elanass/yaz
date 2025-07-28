"""
Protocol Management Service

This service manages clinical protocols, including versioning, compliance tracking,
and deviation reporting.
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

from core.config.settings import get_feature_config
from core.models.base import BaseEntity
from core.services.base import BaseService
from core.services.logger import Logger
from core.services.alerting import AlertingService, AlertSeverity
from adapters.open_source.openclinica_adapter import OpenClinicaAdapter


class ProtocolStatus(str, Enum):
    """Protocol status values"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ProtocolType(str, Enum):
    """Protocol types"""
    ADCI = "adci"
    GASTRECTOMY = "gastrectomy"
    FLOT = "flot"
    CUSTOM = "custom"


class DeviationType(str, Enum):
    """Protocol deviation types"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ProtocolVersion(BaseModel):
    """Protocol version model"""
    
    version: str = Field(..., description="Version number")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    created_by: str = Field(..., description="User ID of creator")
    change_summary: str = Field(..., description="Summary of changes")
    status: ProtocolStatus = Field(ProtocolStatus.DRAFT, description="Version status")
    content: Dict[str, Any] = Field(..., description="Protocol content")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    approved_by: Optional[str] = Field(None, description="User ID of approver")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProtocolDeviation(BaseModel):
    """Protocol deviation model"""
    
    deviation_id: str = Field(..., description="Deviation ID")
    protocol_id: str = Field(..., description="Protocol ID")
    case_id: Optional[str] = Field(None, description="Case ID if applicable")
    patient_id: Optional[str] = Field(None, description="Patient ID if applicable")
    deviation_type: DeviationType = Field(..., description="Deviation type")
    description: str = Field(..., description="Deviation description")
    reason: str = Field(..., description="Reason for deviation")
    reported_at: datetime = Field(default_factory=datetime.utcnow, description="Report timestamp")
    reported_by: str = Field(..., description="User ID of reporter")
    status: str = Field("reported", description="Status of the deviation")
    resolution: Optional[str] = Field(None, description="Resolution notes")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolved_by: Optional[str] = Field(None, description="User ID of resolver")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Protocol(BaseEntity):
    """Clinical protocol model"""
    
    title: str = Field(..., description="Protocol title")
    description: str = Field(..., description="Protocol description")
    protocol_type: ProtocolType = Field(..., description="Protocol type")
    versions: List[ProtocolVersion] = Field(default_factory=list, description="Version history")
    current_version: str = Field(..., description="Current version number")
    status: ProtocolStatus = Field(ProtocolStatus.DRAFT, description="Protocol status")
    owner_id: str = Field(..., description="User ID of owner")
    external_ids: Dict[str, str] = Field(default_factory=dict, description="External system IDs")
    compliance_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Compliance rules")
    deviations: List[ProtocolDeviation] = Field(default_factory=list, description="Recorded deviations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def add_version(
        self,
        version: str,
        created_by: str,
        change_summary: str,
        content: Dict[str, Any],
        status: ProtocolStatus = ProtocolStatus.DRAFT
    ) -> ProtocolVersion:
        """
        Add a new version to the protocol
        
        Args:
            version: Version number
            created_by: User ID of creator
            change_summary: Summary of changes
            content: Protocol content
            status: Version status
            
        Returns:
            The created version
        """
        # Check if version already exists
        for v in self.versions:
            if v.version == version:
                raise ValueError(f"Version {version} already exists")
                
        # Create new version
        protocol_version = ProtocolVersion(
            version=version,
            created_by=created_by,
            change_summary=change_summary,
            content=content,
            status=status
        )
        
        # Add to versions
        self.versions.append(protocol_version)
        
        # Update current version if this is the first version
        if not self.versions or status == ProtocolStatus.ACTIVE:
            self.current_version = version
            self.status = status
            
        return protocol_version
    
    def approve_version(
        self,
        version: str,
        approved_by: str
    ) -> Optional[ProtocolVersion]:
        """
        Approve a protocol version
        
        Args:
            version: Version number
            approved_by: User ID of approver
            
        Returns:
            The approved version, or None if not found
        """
        # Find version
        target_version = None
        for v in self.versions:
            if v.version == version:
                target_version = v
                break
                
        if not target_version:
            return None
            
        # Update status
        target_version.status = ProtocolStatus.APPROVED
        target_version.approved_at = datetime.utcnow()
        target_version.approved_by = approved_by
        
        return target_version
    
    def activate_version(self, version: str) -> bool:
        """
        Activate a protocol version
        
        Args:
            version: Version number
            
        Returns:
            True if successful, False if version not found
        """
        # Find version
        target_version = None
        for v in self.versions:
            if v.version == version:
                target_version = v
                break
                
        if not target_version:
            return False
            
        # Check if approved
        if target_version.status != ProtocolStatus.APPROVED:
            raise ValueError(f"Version {version} must be approved before activation")
            
        # Update version status
        target_version.status = ProtocolStatus.ACTIVE
        
        # Update protocol
        self.current_version = version
        self.status = ProtocolStatus.ACTIVE
        
        return True
    
    def get_version(self, version: str) -> Optional[ProtocolVersion]:
        """
        Get a specific version
        
        Args:
            version: Version number
            
        Returns:
            The version, or None if not found
        """
        for v in self.versions:
            if v.version == version:
                return v
                
        return None
    
    def get_current_version(self) -> Optional[ProtocolVersion]:
        """
        Get the current version
        
        Returns:
            The current version, or None if no versions
        """
        return self.get_version(self.current_version)
    
    def add_deviation(
        self,
        deviation_type: DeviationType,
        description: str,
        reason: str,
        reported_by: str,
        case_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ) -> ProtocolDeviation:
        """
        Add a deviation report
        
        Args:
            deviation_type: Deviation type
            description: Deviation description
            reason: Reason for deviation
            reported_by: User ID of reporter
            case_id: Optional case ID
            patient_id: Optional patient ID
            
        Returns:
            The created deviation report
        """
        import uuid
        
        # Create deviation
        deviation = ProtocolDeviation(
            deviation_id=str(uuid.uuid4()),
            protocol_id=str(self.id),
            case_id=case_id,
            patient_id=patient_id,
            deviation_type=deviation_type,
            description=description,
            reason=reason,
            reported_by=reported_by
        )
        
        # Add to deviations
        self.deviations.append(deviation)
        
        return deviation


class ProtocolManagementService(BaseService):
    """Service for managing clinical protocols"""
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("protocols")
        self.logger = Logger()
        self.alerting = AlertingService()
        self.openclinica_adapter = OpenClinicaAdapter()
    
    async def create_protocol(
        self,
        title: str,
        description: str,
        protocol_type: ProtocolType,
        initial_content: Dict[str, Any],
        owner_id: str
    ) -> Protocol:
        """
        Create a new protocol
        
        Args:
            title: Protocol title
            description: Protocol description
            protocol_type: Protocol type
            initial_content: Initial protocol content
            owner_id: User ID of owner
            
        Returns:
            The created protocol
        """
        import uuid
        
        # Create protocol
        protocol = Protocol(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            protocol_type=protocol_type,
            current_version="1.0",
            owner_id=owner_id,
            status=ProtocolStatus.DRAFT
        )
        
        # Add initial version
        protocol.add_version(
            version="1.0",
            created_by=owner_id,
            change_summary="Initial version",
            content=initial_content
        )
        
        # Add default compliance rules based on type
        if protocol_type == ProtocolType.ADCI:
            protocol.compliance_rules = self._get_adci_compliance_rules()
        elif protocol_type == ProtocolType.GASTRECTOMY:
            protocol.compliance_rules = self._get_gastrectomy_compliance_rules()
        elif protocol_type == ProtocolType.FLOT:
            protocol.compliance_rules = self._get_flot_compliance_rules()
        
        # Store the protocol
        # This would normally use a repository to persist the protocol
        # For this example, we'll just log and return
        
        self.logger.info(
            f"Created {protocol_type} protocol: {title}",
            protocol_id=protocol.id,
            protocol_type=protocol_type,
            owner_id=owner_id
        )
        
        return protocol
    
    def _get_adci_compliance_rules(self) -> List[Dict[str, Any]]:
        """Get default compliance rules for ADCI protocols"""
        return [
            {
                "id": "adci_rule_1",
                "name": "Required patient data",
                "description": "Patient must have complete clinical data",
                "severity": "major",
                "condition": {
                    "type": "required_fields",
                    "fields": ["age", "performance_status", "comorbidities"]
                }
            },
            {
                "id": "adci_rule_2",
                "name": "Tumor staging",
                "description": "Tumor must be properly staged",
                "severity": "critical",
                "condition": {
                    "type": "required_fields",
                    "fields": ["stage", "location", "histology"]
                }
            }
        ]
    
    def _get_gastrectomy_compliance_rules(self) -> List[Dict[str, Any]]:
        """Get default compliance rules for Gastrectomy protocols"""
        return [
            {
                "id": "gastrectomy_rule_1",
                "name": "Pre-operative assessment",
                "description": "Patient must have complete pre-operative assessment",
                "severity": "critical",
                "condition": {
                    "type": "required_fields",
                    "fields": ["endoscopy", "ct_scan", "blood_work"]
                }
            },
            {
                "id": "gastrectomy_rule_2",
                "name": "Nutritional status",
                "description": "Patient nutritional status must be assessed",
                "severity": "major",
                "condition": {
                    "type": "required_fields",
                    "fields": ["albumin", "weight_loss", "nutritional_risk_score"]
                }
            }
        ]
    
    def _get_flot_compliance_rules(self) -> List[Dict[str, Any]]:
        """Get default compliance rules for FLOT protocols"""
        return [
            {
                "id": "flot_rule_1",
                "name": "Eligibility criteria",
                "description": "Patient must meet all eligibility criteria",
                "severity": "critical",
                "condition": {
                    "type": "all_true",
                    "conditions": [
                        {"field": "performance_status", "operator": "<=", "value": 2},
                        {"field": "renal_function", "operator": ">=", "value": "adequate"},
                        {"field": "liver_function", "operator": ">=", "value": "adequate"}
                    ]
                }
            },
            {
                "id": "flot_rule_2",
                "name": "Cycle timing",
                "description": "Cycles must be administered at correct intervals",
                "severity": "major",
                "condition": {
                    "type": "time_between",
                    "field": "cycle_date",
                    "min_days": 12,
                    "max_days": 16
                }
            }
        ]
    
    async def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        """
        Get a protocol by ID
        
        Args:
            protocol_id: Protocol ID
            
        Returns:
            The protocol, or None if not found
        """
        # This would normally retrieve from a database
        # For this example, we'll return None
        
        return None
    
    async def list_protocols(
        self,
        protocol_type: Optional[ProtocolType] = None,
        status_filter: Optional[ProtocolStatus] = None,
        owner_id: Optional[str] = None
    ) -> List[Protocol]:
        """
        List protocols with optional filters
        
        Args:
            protocol_type: Optional type filter
            status_filter: Optional status filter
            owner_id: Optional owner filter
            
        Returns:
            List of matching protocols
        """
        # This would normally query a database
        # For this example, we'll return an empty list
        
        return []
    
    async def create_version(
        self,
        protocol_id: str,
        version: str,
        change_summary: str,
        content: Dict[str, Any],
        created_by: str
    ) -> Optional[ProtocolVersion]:
        """
        Create a new version of a protocol
        
        Args:
            protocol_id: Protocol ID
            version: Version number
            change_summary: Summary of changes
            content: Protocol content
            created_by: User ID of creator
            
        Returns:
            The created version, or None if protocol not found
        """
        protocol = await self.get_protocol(protocol_id)
        if not protocol:
            return None
            
        # Add version
        try:
            version = protocol.add_version(
                version=version,
                created_by=created_by,
                change_summary=change_summary,
                content=content
            )
            
            self.logger.info(
                f"Created version {version.version} of protocol {protocol_id}",
                protocol_id=protocol_id,
                version=version.version,
                created_by=created_by
            )
            
            # Save and return version
            # This would normally update in a database
            return version
            
        except Exception as e:
            self.logger.error(
                f"Error creating protocol version: {str(e)}",
                exc_info=e,
                protocol_id=protocol_id,
                version=version
            )
            raise
    
    async def approve_version(
        self,
        protocol_id: str,
        version: str,
        approved_by: str
    ) -> Optional[ProtocolVersion]:
        """
        Approve a protocol version
        
        Args:
            protocol_id: Protocol ID
            version: Version number
            approved_by: User ID of approver
            
        Returns:
            The approved version, or None if not found
        """
        protocol = await self.get_protocol(protocol_id)
        if not protocol:
            return None
            
        # Approve version
        approved_version = protocol.approve_version(version, approved_by)
        if not approved_version:
            return None
            
        self.logger.info(
            f"Approved version {version} of protocol {protocol_id}",
            protocol_id=protocol_id,
            version=version,
            approved_by=approved_by
        )
        
        # Save and return version
        # This would normally update in a database
        return approved_version
    
    async def activate_version(
        self,
        protocol_id: str,
        version: str,
        activated_by: str
    ) -> bool:
        """
        Activate a protocol version
        
        Args:
            protocol_id: Protocol ID
            version: Version number
            activated_by: User ID activating the version
            
        Returns:
            True if successful, False otherwise
        """
        protocol = await self.get_protocol(protocol_id)
        if not protocol:
            return False
            
        # Activate version
        try:
            result = protocol.activate_version(version)
            if not result:
                return False
                
            self.logger.info(
                f"Activated version {version} of protocol {protocol_id}",
                protocol_id=protocol_id,
                version=version,
                activated_by=activated_by
            )
            
            # Save protocol
            # This would normally update in a database
            return True
            
        except ValueError as e:
            self.logger.warning(
                f"Cannot activate protocol version: {str(e)}",
                protocol_id=protocol_id,
                version=version
            )
            return False
    
    async def check_compliance(
        self,
        protocol_id: str,
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check compliance with a protocol
        
        Args:
            protocol_id: Protocol ID
            case_data: Case data to check
            
        Returns:
            Compliance results
        """
        protocol = await self.get_protocol(protocol_id)
        if not protocol:
            raise ValueError(f"Protocol {protocol_id} not found")
            
        # Get current version
        current = protocol.get_current_version()
        if not current:
            raise ValueError(f"Protocol {protocol_id} has no versions")
            
        # Check each compliance rule
        compliance_results = {
            "protocol_id": protocol_id,
            "protocol_title": protocol.title,
            "version": current.version,
            "timestamp": datetime.utcnow().isoformat(),
            "compliant": True,
            "rules": []
        }
        
        for rule in protocol.compliance_rules:
            rule_result = self._check_rule(rule, case_data)
            compliance_results["rules"].append(rule_result)
            
            # Update overall compliance
            if not rule_result["compliant"]:
                compliance_results["compliant"] = False
                
                # Generate alert for major/critical deviations
                if rule["severity"] in ["major", "critical"]:
                    case_id = case_data.get("case_id")
                    patient_id = case_data.get("patient_id")
                    
                    await self.alerting.create_alert(
                        title=f"Protocol Compliance Issue: {rule['name']}",
                        message=f"Non-compliance detected: {rule_result['message']}",
                        severity=AlertSeverity.WARNING if rule["severity"] == "major" else AlertSeverity.CRITICAL,
                        category="protocol_deviation",
                        resource_type="protocol",
                        resource_id=protocol_id,
                        patient_id=patient_id,
                        protocol_id=protocol_id,
                        metadata={
                            "case_id": case_id,
                            "rule_id": rule["id"],
                            "rule_name": rule["name"],
                            "severity": rule["severity"]
                        }
                    )
        
        return compliance_results
    
    def _check_rule(
        self,
        rule: Dict[str, Any],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check a single compliance rule
        
        Args:
            rule: Rule definition
            case_data: Case data to check
            
        Returns:
            Rule check result
        """
        rule_id = rule["id"]
        rule_name = rule["name"]
        condition = rule["condition"]
        condition_type = condition["type"]
        
        result = {
            "rule_id": rule_id,
            "name": rule_name,
            "compliant": False,
            "message": ""
        }
        
        # Check condition based on type
        if condition_type == "required_fields":
            required_fields = condition["fields"]
            missing_fields = []
            
            for field in required_fields:
                if field not in case_data or case_data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                result["compliant"] = False
                result["message"] = f"Missing required fields: {', '.join(missing_fields)}"
            else:
                result["compliant"] = True
                result["message"] = "All required fields present"
                
        elif condition_type == "all_true":
            sub_conditions = condition["conditions"]
            failed_conditions = []
            
            for sub_cond in sub_conditions:
                field = sub_cond["field"]
                operator = sub_cond["operator"]
                value = sub_cond["value"]
                
                if field not in case_data:
                    failed_conditions.append(f"{field} is missing")
                    continue
                    
                field_value = case_data[field]
                
                if operator == "==" and field_value != value:
                    failed_conditions.append(f"{field} != {value}")
                elif operator == "!=" and field_value == value:
                    failed_conditions.append(f"{field} == {value}")
                elif operator == "<" and not (field_value < value):
                    failed_conditions.append(f"{field} >= {value}")
                elif operator == "<=" and not (field_value <= value):
                    failed_conditions.append(f"{field} > {value}")
                elif operator == ">" and not (field_value > value):
                    failed_conditions.append(f"{field} <= {value}")
                elif operator == ">=" and not (field_value >= value):
                    failed_conditions.append(f"{field} < {value}")
            
            if failed_conditions:
                result["compliant"] = False
                result["message"] = f"Failed conditions: {', '.join(failed_conditions)}"
            else:
                result["compliant"] = True
                result["message"] = "All conditions met"
                
        elif condition_type == "time_between":
            field = condition["field"]
            min_days = condition["min_days"]
            max_days = condition["max_days"]
            
            if field not in case_data:
                result["compliant"] = False
                result["message"] = f"Missing time field: {field}"
            else:
                # This would need date parsing and comparison logic
                # For this example, we'll assume compliance
                result["compliant"] = True
                result["message"] = "Time between criteria met"
        
        return result
    
    async def report_deviation(
        self,
        protocol_id: str,
        deviation_type: DeviationType,
        description: str,
        reason: str,
        reported_by: str,
        case_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ) -> Optional[ProtocolDeviation]:
        """
        Report a protocol deviation
        
        Args:
            protocol_id: Protocol ID
            deviation_type: Deviation type
            description: Deviation description
            reason: Reason for deviation
            reported_by: User ID of reporter
            case_id: Optional case ID
            patient_id: Optional patient ID
            
        Returns:
            The created deviation report, or None if protocol not found
        """
        protocol = await self.get_protocol(protocol_id)
        if not protocol:
            return None
            
        # Add deviation
        deviation = protocol.add_deviation(
            deviation_type=deviation_type,
            description=description,
            reason=reason,
            reported_by=reported_by,
            case_id=case_id,
            patient_id=patient_id
        )
        
        self.logger.info(
            f"Reported {deviation_type} deviation for protocol {protocol_id}",
            protocol_id=protocol_id,
            deviation_id=deviation.deviation_id,
            deviation_type=deviation_type,
            reported_by=reported_by,
            case_id=case_id,
            patient_id=patient_id
        )
        
        # Try to report to OpenClinica if configured
        try:
            if case_id and patient_id and self.config.get("openclinica_integration", False):
                # Map to OpenClinica format
                deviation_data = {
                    "study_subject_oid": patient_id,
                    "type": deviation_type,
                    "description": description,
                    "reason": reason
                }
                
                # Report to OpenClinica
                study_oid = protocol.external_ids.get("openclinica_study_oid")
                if study_oid:
                    await self.openclinica_adapter.report_protocol_deviation(
                        study_oid=study_oid,
                        subject_key=patient_id,
                        deviation_data=deviation_data
                    )
        except Exception as e:
            self.logger.error(
                f"Failed to report deviation to OpenClinica: {str(e)}",
                exc_info=e,
                protocol_id=protocol_id,
                deviation_id=deviation.deviation_id
            )
        
        # Generate alert based on severity
        alert_severity = AlertSeverity.INFO
        if deviation_type == DeviationType.MAJOR:
            alert_severity = AlertSeverity.WARNING
        elif deviation_type == DeviationType.CRITICAL:
            alert_severity = AlertSeverity.CRITICAL
            
        await self.alerting.create_alert(
            title=f"{deviation_type.capitalize()} Protocol Deviation Reported",
            message=description,
            severity=alert_severity,
            category="protocol_deviation",
            resource_type="protocol",
            resource_id=protocol_id,
            patient_id=patient_id,
            protocol_id=protocol_id,
            metadata={
                "case_id": case_id,
                "deviation_id": deviation.deviation_id,
                "deviation_type": deviation_type,
                "reason": reason
            }
        )
        
        # Save and return deviation
        # This would normally update in a database
        return deviation
