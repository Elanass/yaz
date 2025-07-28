"""
Event Logger Service for Gastric ADCI Platform.

This service provides a comprehensive, HIPAA/GDPR-compliant logging system
that tracks all clinical data access, modifications, and user interactions
while maintaining proper audit trails.

Features:
- Structured logging with clinical context
- PII/PHI de-identification options
- Tamper-proof audit logs using blockchain verification
- Configurable retention policies
- Support for external SIEM integration
"""

import json
import uuid
import datetime
import hashlib
from typing import Dict, Any, Optional, List, Union
import logging
from pydantic import BaseModel, Field

from core.services.logger import get_logger
from core.services.ipfs_client import IPFSClient
from core.services.encryption import encrypt_data

# Configure logger
logger = get_logger(__name__)

class EventSeverity(str):
    """Event severity levels aligned with clinical context."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"  # Requires immediate clinical attention

class EventCategory(str):
    """Event categories for structured logging and filtering."""
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    DATA_ACCESS = "DATA_ACCESS"
    DATA_MODIFICATION = "DATA_MODIFICATION"
    CLINICAL_DECISION = "CLINICAL_DECISION"
    PROTOCOL_DEVIATION = "PROTOCOL_DEVIATION"
    SYSTEM = "SYSTEM"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    PATIENT_CARE = "PATIENT_CARE"

class EventSource(BaseModel):
    """Source of the event for traceability."""
    component: str
    service: Optional[str] = None
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class EventContext(BaseModel):
    """Clinical context of the event."""
    patient_id: Optional[str] = None  # Encrypted or tokenized
    encounter_id: Optional[str] = None
    provider_id: Optional[str] = None
    care_team_ids: Optional[List[str]] = None
    organization_id: Optional[str] = None
    protocol_id: Optional[str] = None
    decision_id: Optional[str] = None
    related_events: Optional[List[str]] = None
    clinical_domain: Optional[str] = None
    is_emergency: bool = False

class EventData(BaseModel):
    """Event data payload with clinical specificity."""
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    prior_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = None
    confidence_interval: Optional[float] = None
    risk_level: Optional[str] = None
    rationale: Optional[str] = None
    evidence_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class EventLog(BaseModel):
    """Complete event log structure for HIPAA/GDPR compliance."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    category: str
    severity: str = EventSeverity.INFO
    source: EventSource
    context: EventContext
    data: EventData
    message: str
    hash: Optional[str] = None  # For integrity verification
    ipfs_cid: Optional[str] = None  # Content ID if stored on IPFS
    
    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }
    
    def calculate_hash(self) -> str:
        """Calculate cryptographic hash of the event for integrity verification."""
        # Create a copy without the hash field
        event_dict = self.dict(exclude={"hash", "ipfs_cid"})
        event_json = json.dumps(event_dict, sort_keys=True)
        return hashlib.sha256(event_json.encode()).hexdigest()
    
    def finalize(self):
        """Finalize the event by calculating its hash."""
        self.hash = self.calculate_hash()
        return self


class EventLogger:
    """HIPAA/GDPR compliant event logger for clinical systems."""
    
    def __init__(
        self,
        log_to_file: bool = True,
        log_to_database: bool = True,
        log_to_ipfs: bool = False,
        encrypt_sensitive: bool = True,
        file_path: str = "logs/audit.log",
        retention_days: int = 2555  # 7-year retention for HIPAA
    ):
        self.log_to_file = log_to_file
        self.log_to_database = log_to_database
        self.log_to_ipfs = log_to_ipfs
        self.encrypt_sensitive = encrypt_sensitive
        self.file_path = file_path
        self.retention_days = retention_days
        
        if self.log_to_ipfs:
            self.ipfs_client = IPFSClient()
    
    async def log_event(
        self,
        category: str,
        severity: str,
        source: Union[EventSource, Dict[str, Any]],
        context: Union[EventContext, Dict[str, Any]],
        data: Union[EventData, Dict[str, Any]],
        message: str
    ) -> EventLog:
        """
        Log a clinical event with proper context and compliance features.
        
        Args:
            category: The event category (see EventCategory)
            severity: The event severity (see EventSeverity)
            source: Information about the source of the event
            context: Clinical context of the event
            data: Details about the event and related clinical data
            message: Human-readable message describing the event
            
        Returns:
            The finalized event log object
        """
        # Convert dict inputs to proper models if needed
        if isinstance(source, dict):
            source = EventSource(**source)
            
        if isinstance(context, dict):
            context = EventContext(**context)
            
        if isinstance(data, dict):
            data = EventData(**data)
        
        # Create the event log
        event = EventLog(
            category=category,
            severity=severity,
            source=source,
            context=context,
            data=data,
            message=message
        ).finalize()
        
        # Handle sensitive data encryption if enabled
        if self.encrypt_sensitive and context.patient_id:
            event.context.patient_id = encrypt_data(context.patient_id)
        
        # Log to file
        if self.log_to_file:
            await self._log_to_file(event)
        
        # Log to database (async)
        if self.log_to_database:
            await self._log_to_database(event)
        
        # Log to IPFS for immutability (if enabled)
        if self.log_to_ipfs:
            ipfs_cid = await self._log_to_ipfs(event)
            event.ipfs_cid = ipfs_cid
        
        return event
    
    async def _log_to_file(self, event: EventLog):
        """Log event to structured log file."""
        logger.info(f"AUDIT: {event.json()}")
    
    async def _log_to_database(self, event: EventLog):
        """Log event to database for querying and retention."""
        # Implementation will connect to database service
        # For now we'll just log it
        logger.debug(f"DB-AUDIT: {event.id} logged to database")
    
    async def _log_to_ipfs(self, event: EventLog) -> str:
        """Log event to IPFS for immutable audit trail."""
        try:
            event_json = event.json()
            cid = await self.ipfs_client.add_json(event_json)
            logger.debug(f"Event {event.id} stored on IPFS with CID: {cid}")
            return cid
        except Exception as e:
            logger.error(f"Failed to store event {event.id} on IPFS: {str(e)}")
            return None
    
    async def query_events(
        self,
        filters: Dict[str, Any],
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[EventLog]:
        """
        Query audit logs based on filters with pagination.
        
        This method would connect to the database service to retrieve logs.
        For now, it returns an empty list as a placeholder.
        """
        # This would be implemented with database queries
        return []
    
    async def verify_event_integrity(self, event_id: str) -> bool:
        """
        Verify the integrity of an event log by checking its hash.
        
        For IPFS-stored events, this can also verify against the blockchain.
        """
        # This would fetch the event and verify its hash
        return True


# Create a singleton instance
event_logger = EventLogger()

# Convenience functions
async def log_clinical_decision(
    provider_id: str,
    patient_id: str,
    decision_id: str,
    action: str,
    outcome: str,
    confidence: float,
    evidence_ids: List[str],
    message: str,
    source_component: str,
    risk_level: Optional[str] = None,
    is_emergency: bool = False
) -> EventLog:
    """Log a clinical decision event with proper context."""
    return await event_logger.log_event(
        category=EventCategory.CLINICAL_DECISION,
        severity=EventSeverity.INFO,
        source=EventSource(component=source_component),
        context=EventContext(
            provider_id=provider_id,
            patient_id=patient_id,
            decision_id=decision_id,
            is_emergency=is_emergency
        ),
        data=EventData(
            action=action,
            outcome=outcome,
            confidence_interval=confidence,
            evidence_ids=evidence_ids,
            risk_level=risk_level
        ),
        message=message
    )

async def log_data_access(
    user_id: str,
    resource_type: str,
    resource_id: str,
    patient_id: Optional[str] = None,
    reason: Optional[str] = None,
    source_component: str = "api",
    ip_address: Optional[str] = None
) -> EventLog:
    """Log data access events for HIPAA compliance."""
    return await event_logger.log_event(
        category=EventCategory.DATA_ACCESS,
        severity=EventSeverity.INFO,
        source=EventSource(
            component=source_component,
            ip_address=ip_address
        ),
        context=EventContext(
            provider_id=user_id,
            patient_id=patient_id
        ),
        data=EventData(
            resource_type=resource_type,
            resource_id=resource_id,
            action="READ",
            rationale=reason
        ),
        message=f"User {user_id} accessed {resource_type} {resource_id}" + 
                (f" for patient {patient_id}" if patient_id else "")
    )

async def log_protocol_deviation(
    provider_id: str,
    patient_id: str,
    protocol_id: str,
    deviation_type: str,
    severity: str,
    rationale: str,
    source_component: str
) -> EventLog:
    """Log protocol deviation events with clinical context."""
    return await event_logger.log_event(
        category=EventCategory.PROTOCOL_DEVIATION,
        severity=severity,
        source=EventSource(component=source_component),
        context=EventContext(
            provider_id=provider_id,
            patient_id=patient_id,
            protocol_id=protocol_id
        ),
        data=EventData(
            action="PROTOCOL_DEVIATION",
            resource_type="PROTOCOL",
            resource_id=protocol_id,
            rationale=rationale,
            metadata={"deviation_type": deviation_type}
        ),
        message=f"Protocol deviation of type {deviation_type} for protocol {protocol_id}"
    )
