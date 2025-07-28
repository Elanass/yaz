"""
Case Coordination Service

This service manages the coordination of clinical cases across providers,
ensuring proper assignment, tracking, and workflow management.
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
from adapters.open_source.openmrs_adapter import OpenMRSAdapter


class CaseStatus(str, Enum):
    """Case status values"""
    PENDING = "pending"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CaseAction(str, Enum):
    """Case action types"""
    ASSIGNED = "assigned"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    COMMENT_ADDED = "comment_added"
    PROTOCOL_APPLIED = "protocol_applied"
    DOCUMENT_ADDED = "document_added"


class Role(str, Enum):
    """Role types for case assignments"""
    PATIENT = "patient"
    PRIMARY_PROVIDER = "primary_provider"
    SPECIALIST = "specialist"
    CONSULTANT = "consultant"
    RESEARCHER = "researcher"
    ADMINISTRATOR = "administrator"


class CaseParticipant(BaseModel):
    """Participant in a case"""
    
    user_id: str = Field(..., description="User ID")
    role: Role = Field(..., description="Role in the case")
    name: str = Field(..., description="Display name")
    added_at: datetime = Field(default_factory=datetime.utcnow, description="When added")
    added_by: Optional[str] = Field(None, description="Who added this participant")
    permissions: List[str] = Field(default_factory=list, description="Specific permissions")


class CaseComment(BaseModel):
    """Comment on a case"""
    
    comment_id: str = Field(..., description="Comment ID")
    content: str = Field(..., description="Comment content")
    author_id: str = Field(..., description="Author user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    parent_id: Optional[str] = Field(None, description="Parent comment ID if a reply")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Attached files")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CaseTimeline(BaseModel):
    """Timeline entry for a case"""
    
    entry_id: str = Field(..., description="Entry ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Entry timestamp")
    action: CaseAction = Field(..., description="Action type")
    actor_id: str = Field(..., description="User who performed the action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Action details")
    visible_to_patient: bool = Field(False, description="Whether visible to patient")


class Case(BaseEntity):
    """Clinical case model"""
    
    title: str = Field(..., description="Case title")
    patient_id: str = Field(..., description="Patient ID")
    description: str = Field(..., description="Case description")
    status: CaseStatus = Field(default=CaseStatus.PENDING, description="Current status")
    participants: List[CaseParticipant] = Field(default_factory=list, description="Case participants")
    protocols: List[str] = Field(default_factory=list, description="Applied protocol IDs")
    external_ids: Dict[str, str] = Field(default_factory=dict, description="External system IDs")
    timeline: List[CaseTimeline] = Field(default_factory=list, description="Case timeline")
    comments: List[CaseComment] = Field(default_factory=list, description="Case comments")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def add_participant(
        self,
        user_id: str,
        role: Role,
        name: str,
        added_by: Optional[str] = None,
        permissions: List[str] = None
    ) -> CaseParticipant:
        """
        Add a participant to the case
        
        Args:
            user_id: User ID
            role: Role in the case
            name: Display name
            added_by: Who added this participant
            permissions: Specific permissions
            
        Returns:
            The added participant
        """
        participant = CaseParticipant(
            user_id=user_id,
            role=role,
            name=name,
            added_at=datetime.utcnow(),
            added_by=added_by,
            permissions=permissions or []
        )
        
        self.participants.append(participant)
        
        # Add to timeline
        self.add_timeline_entry(
            action=CaseAction.ASSIGNED,
            actor_id=added_by or user_id,
            details={
                "user_id": user_id,
                "role": role,
                "name": name
            }
        )
        
        return participant
    
    def update_status(self, status: CaseStatus, actor_id: str) -> None:
        """
        Update the case status
        
        Args:
            status: New status
            actor_id: User making the change
        """
        old_status = self.status
        self.status = status
        
        # Add to timeline
        self.add_timeline_entry(
            action=CaseAction.STATUS_CHANGED,
            actor_id=actor_id,
            details={
                "old_status": old_status,
                "new_status": status
            }
        )
    
    def add_comment(
        self,
        content: str,
        author_id: str,
        parent_id: Optional[str] = None,
        attachments: List[Dict[str, Any]] = None
    ) -> CaseComment:
        """
        Add a comment to the case
        
        Args:
            content: Comment content
            author_id: Author user ID
            parent_id: Parent comment ID if a reply
            attachments: Attached files
            
        Returns:
            The added comment
        """
        import uuid
        
        comment = CaseComment(
            comment_id=str(uuid.uuid4()),
            content=content,
            author_id=author_id,
            created_at=datetime.utcnow(),
            parent_id=parent_id,
            attachments=attachments or []
        )
        
        self.comments.append(comment)
        
        # Add to timeline
        self.add_timeline_entry(
            action=CaseAction.COMMENT_ADDED,
            actor_id=author_id,
            details={
                "comment_id": comment.comment_id,
                "content_preview": content[:100] + ("..." if len(content) > 100 else ""),
                "has_attachments": bool(attachments)
            },
            visible_to_patient=True
        )
        
        return comment
    
    def add_timeline_entry(
        self,
        action: CaseAction,
        actor_id: str,
        details: Dict[str, Any],
        visible_to_patient: bool = False
    ) -> CaseTimeline:
        """
        Add an entry to the case timeline
        
        Args:
            action: Action type
            actor_id: User who performed the action
            details: Action details
            visible_to_patient: Whether visible to patient
            
        Returns:
            The added timeline entry
        """
        import uuid
        
        entry = CaseTimeline(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            actor_id=actor_id,
            details=details,
            visible_to_patient=visible_to_patient
        )
        
        self.timeline.append(entry)
        return entry
    
    def apply_protocol(self, protocol_id: str, actor_id: str) -> None:
        """
        Apply a protocol to the case
        
        Args:
            protocol_id: Protocol ID
            actor_id: User applying the protocol
        """
        if protocol_id not in self.protocols:
            self.protocols.append(protocol_id)
            
            # Add to timeline
            self.add_timeline_entry(
                action=CaseAction.PROTOCOL_APPLIED,
                actor_id=actor_id,
                details={
                    "protocol_id": protocol_id
                }
            )


class CaseCoordinationService(BaseService):
    """Service for managing case coordination"""
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("case_coordination")
        self.logger = Logger()
        self.openmrs_adapter = OpenMRSAdapter()
    
    async def create_case(
        self,
        title: str,
        patient_id: str,
        description: str,
        created_by: str,
        creator_name: str,
        initial_status: CaseStatus = CaseStatus.PENDING
    ) -> Case:
        """
        Create a new case
        
        Args:
            title: Case title
            patient_id: Patient ID
            description: Case description
            created_by: User ID of creator
            creator_name: Name of creator
            initial_status: Initial case status
            
        Returns:
            The created case
        """
        import uuid
        
        # Create case
        case = Case(
            id=str(uuid.uuid4()),
            title=title,
            patient_id=patient_id,
            description=description,
            status=initial_status
        )
        
        # Add creator as participant
        case.add_participant(
            user_id=created_by,
            role=Role.PRIMARY_PROVIDER,
            name=creator_name
        )
        
        # Add patient data if available
        try:
            patient = await self.openmrs_adapter.get_patient(patient_id)
            if patient:
                case.metadata["patient_name"] = patient.name
                case.metadata["patient_identifier"] = patient.identifier
                
                # Add patient as participant
                case.add_participant(
                    user_id=patient_id,
                    role=Role.PATIENT,
                    name=patient.name,
                    added_by=created_by
                )
        except Exception as e:
            self.logger.warning(
                f"Could not retrieve patient data: {str(e)}",
                exc_info=e,
                patient_id=patient_id
            )
        
        # Store the case
        # This would normally use a repository to persist the case
        # For this example, we'll just log and return
        
        self.logger.info(
            f"Created case {case.id} for patient {patient_id}",
            case_id=case.id,
            patient_id=patient_id,
            created_by=created_by
        )
        
        return case
    
    async def get_case(self, case_id: str) -> Optional[Case]:
        """
        Get a case by ID
        
        Args:
            case_id: Case ID
            
        Returns:
            The case, or None if not found
        """
        # This would normally retrieve from a database
        # For this example, we'll return None
        
        return None
    
    async def assign_provider(
        self,
        case_id: str,
        provider_id: str,
        provider_name: str,
        role: Role,
        assigned_by: str
    ) -> Optional[Case]:
        """
        Assign a provider to a case
        
        Args:
            case_id: Case ID
            provider_id: Provider user ID
            provider_name: Provider name
            role: Provider role
            assigned_by: User ID making the assignment
            
        Returns:
            The updated case, or None if not found
        """
        case = await self.get_case(case_id)
        if not case:
            return None
            
        # Check if already assigned
        for participant in case.participants:
            if participant.user_id == provider_id and participant.role == role:
                self.logger.info(
                    f"Provider {provider_id} already assigned to case {case_id} as {role}",
                    case_id=case_id,
                    provider_id=provider_id,
                    role=role
                )
                return case
        
        # Add participant
        case.add_participant(
            user_id=provider_id,
            role=role,
            name=provider_name,
            added_by=assigned_by
        )
        
        self.logger.info(
            f"Assigned provider {provider_id} to case {case_id} as {role}",
            case_id=case_id,
            provider_id=provider_id,
            role=role,
            assigned_by=assigned_by
        )
        
        # Save and return updated case
        # This would normally update in a database
        return case
    
    async def list_cases(
        self,
        user_id: str,
        status_filter: Optional[CaseStatus] = None,
        role_filter: Optional[Role] = None
    ) -> List[Case]:
        """
        List cases for a user
        
        Args:
            user_id: User ID
            status_filter: Optional status filter
            role_filter: Optional role filter
            
        Returns:
            List of matching cases
        """
        # This would normally query a database
        # For this example, we'll return an empty list
        
        return []
    
    async def add_case_comment(
        self,
        case_id: str,
        content: str,
        author_id: str,
        parent_id: Optional[str] = None,
        attachments: List[Dict[str, Any]] = None
    ) -> Optional[CaseComment]:
        """
        Add a comment to a case
        
        Args:
            case_id: Case ID
            content: Comment content
            author_id: Author user ID
            parent_id: Parent comment ID if a reply
            attachments: Attached files
            
        Returns:
            The added comment, or None if case not found
        """
        case = await self.get_case(case_id)
        if not case:
            return None
            
        # Add comment
        comment = case.add_comment(
            content=content,
            author_id=author_id,
            parent_id=parent_id,
            attachments=attachments
        )
        
        self.logger.info(
            f"Added comment to case {case_id}",
            case_id=case_id,
            comment_id=comment.comment_id,
            author_id=author_id
        )
        
        # Save and return comment
        # This would normally update in a database
        return comment
    
    async def update_case_status(
        self,
        case_id: str,
        status: CaseStatus,
        actor_id: str
    ) -> Optional[Case]:
        """
        Update case status
        
        Args:
            case_id: Case ID
            status: New status
            actor_id: User making the change
            
        Returns:
            The updated case, or None if not found
        """
        case = await self.get_case(case_id)
        if not case:
            return None
            
        # Update status
        case.update_status(status, actor_id)
        
        self.logger.info(
            f"Updated case {case_id} status to {status}",
            case_id=case_id,
            status=status,
            actor_id=actor_id
        )
        
        # Save and return updated case
        # This would normally update in a database
        return case
    
    async def apply_protocol(
        self,
        case_id: str,
        protocol_id: str,
        actor_id: str
    ) -> Optional[Case]:
        """
        Apply a protocol to a case
        
        Args:
            case_id: Case ID
            protocol_id: Protocol ID
            actor_id: User applying the protocol
            
        Returns:
            The updated case, or None if not found
        """
        case = await self.get_case(case_id)
        if not case:
            return None
            
        # Apply protocol
        case.apply_protocol(protocol_id, actor_id)
        
        self.logger.info(
            f"Applied protocol {protocol_id} to case {case_id}",
            case_id=case_id,
            protocol_id=protocol_id,
            actor_id=actor_id
        )
        
        # Save and return updated case
        # This would normally update in a database
        return case
