"""
Collaboration Service

This service manages secure collaboration between healthcare providers,
including messaging, care plan editing, and scheduling.
"""

import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set

from pydantic import BaseModel, Field

from core.config.settings import get_feature_config
from core.models.base import BaseEntity
from core.services.base import BaseService
from core.services.logger import Logger
from core.services.encryption import EncryptionService
from core.services.distributed_state import DistributedState


class MessageType(str, Enum):
    """Message types"""
    TEXT = "text"
    ACTION = "action"
    SYSTEM = "system"
    FILE = "file"


class MessageStatus(str, Enum):
    """Message status values"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class UserStatus(str, Enum):
    """User status values"""
    AVAILABLE = "available"
    BUSY = "busy"
    AWAY = "away"
    OFFLINE = "offline"


class Participant(BaseModel):
    """Conversation participant"""
    
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="Display name")
    role: str = Field(..., description="Role")
    joined_at: datetime = Field(default_factory=datetime.utcnow, description="When joined")


class Message(BaseModel):
    """Secure message model"""
    
    message_id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    sender_id: str = Field(..., description="Sender user ID")
    message_type: MessageType = Field(MessageType.TEXT, description="Message type")
    content: str = Field(..., description="Message content")
    encrypted: bool = Field(False, description="Whether content is encrypted")
    sent_at: datetime = Field(default_factory=datetime.utcnow, description="Sent timestamp")
    status: MessageStatus = Field(MessageStatus.SENT, description="Message status")
    read_by: List[str] = Field(default_factory=list, description="IDs of users who read")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Attached files")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Conversation(BaseEntity):
    """Secure conversation model"""
    
    title: str = Field(..., description="Conversation title")
    description: Optional[str] = Field(None, description="Conversation description")
    participants: List[Participant] = Field(default_factory=list, description="Participants")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    case_id: Optional[str] = Field(None, description="Related case ID")
    patient_id: Optional[str] = Field(None, description="Related patient ID")
    messages: List[Message] = Field(default_factory=list, description="Messages")
    encryption_enabled: bool = Field(False, description="Whether end-to-end encryption is enabled")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def add_message(
        self,
        sender_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        attachments: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Message:
        """
        Add a message to the conversation
        
        Args:
            sender_id: Sender user ID
            content: Message content
            message_type: Message type
            attachments: Attached files
            metadata: Additional metadata
            
        Returns:
            The created message
        """
        import uuid
        
        # Create message
        message = Message(
            message_id=str(uuid.uuid4()),
            conversation_id=str(self.id),
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            encrypted=self.encryption_enabled,
            attachments=attachments or [],
            metadata=metadata or {}
        )
        
        # Add to messages
        self.messages.append(message)
        
        return message
    
    def add_participant(
        self,
        user_id: str,
        name: str,
        role: str
    ) -> Participant:
        """
        Add a participant to the conversation
        
        Args:
            user_id: User ID
            name: Display name
            role: Role
            
        Returns:
            The added participant
        """
        # Check if already a participant
        for participant in self.participants:
            if participant.user_id == user_id:
                return participant
                
        # Create participant
        participant = Participant(
            user_id=user_id,
            name=name,
            role=role
        )
        
        # Add to participants
        self.participants.append(participant)
        
        # Add system message
        self.add_message(
            sender_id="system",
            content=f"{name} joined the conversation",
            message_type=MessageType.SYSTEM
        )
        
        return participant
    
    def mark_as_read(self, user_id: str, message_id: Optional[str] = None) -> int:
        """
        Mark messages as read by a user
        
        Args:
            user_id: User ID
            message_id: Optional specific message ID
            
        Returns:
            Number of messages marked as read
        """
        count = 0
        
        for message in self.messages:
            if message_id and message.message_id != message_id:
                continue
                
            if user_id not in message.read_by:
                message.read_by.append(user_id)
                count += 1
                
                # Update status if all participants have read
                participant_ids = {p.user_id for p in self.participants}
                if set(message.read_by).issuperset(participant_ids):
                    message.status = MessageStatus.READ
                elif message.status == MessageStatus.SENT:
                    message.status = MessageStatus.DELIVERED
        
        return count


class CarePlanSection(BaseModel):
    """Care plan section model"""
    
    section_id: str = Field(..., description="Section ID")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    order: int = Field(0, description="Display order")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_by: Optional[str] = Field(None, description="Last editor user ID")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    revision: int = Field(1, description="Revision number")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CarePlan(BaseEntity):
    """Care plan model with CRDT-based collaborative editing"""
    
    title: str = Field(..., description="Care plan title")
    patient_id: str = Field(..., description="Patient ID")
    case_id: Optional[str] = Field(None, description="Related case ID")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    status: str = Field("draft", description="Status")
    sections: List[CarePlanSection] = Field(default_factory=list, description="Plan sections")
    contributors: List[str] = Field(default_factory=list, description="Contributor user IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def add_section(
        self,
        title: str,
        content: str,
        created_by: str,
        order: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ) -> CarePlanSection:
        """
        Add a section to the care plan
        
        Args:
            title: Section title
            content: Section content
            created_by: Creator user ID
            order: Display order
            metadata: Additional metadata
            
        Returns:
            The created section
        """
        import uuid
        
        # Determine order if not specified
        if order is None:
            order = len(self.sections)
            
        # Create section
        section = CarePlanSection(
            section_id=str(uuid.uuid4()),
            title=title,
            content=content,
            order=order,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        # Add to sections
        self.sections.append(section)
        
        # Update care plan
        self.updated_at = datetime.utcnow()
        
        # Add contributor if not already added
        if created_by not in self.contributors:
            self.contributors.append(created_by)
            
        return section
    
    def update_section(
        self,
        section_id: str,
        updated_by: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        order: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[CarePlanSection]:
        """
        Update a section
        
        Args:
            section_id: Section ID
            updated_by: Editor user ID
            title: New title
            content: New content
            order: New display order
            metadata: New metadata
            
        Returns:
            The updated section, or None if not found
        """
        # Find section
        section = None
        for s in self.sections:
            if s.section_id == section_id:
                section = s
                break
                
        if not section:
            return None
            
        # Update fields
        if title is not None:
            section.title = title
            
        if content is not None:
            section.content = content
            
        if order is not None:
            section.order = order
            
        if metadata is not None:
            section.metadata.update(metadata)
            
        # Update metadata
        section.updated_by = updated_by
        section.updated_at = datetime.utcnow()
        section.revision += 1
        
        # Update care plan
        self.updated_at = datetime.utcnow()
        
        # Add contributor if not already added
        if updated_by not in self.contributors:
            self.contributors.append(updated_by)
            
        return section
    
    def remove_section(self, section_id: str, removed_by: str) -> bool:
        """
        Remove a section
        
        Args:
            section_id: Section ID
            removed_by: User ID removing the section
            
        Returns:
            True if removed, False if not found
        """
        # Find section index
        section_idx = None
        for i, section in enumerate(self.sections):
            if section.section_id == section_id:
                section_idx = i
                break
                
        if section_idx is None:
            return False
            
        # Remove section
        self.sections.pop(section_idx)
        
        # Update care plan
        self.updated_at = datetime.utcnow()
        
        # Add contributor if not already added
        if removed_by not in self.contributors:
            self.contributors.append(removed_by)
            
        return True


class AvailabilitySlot(BaseModel):
    """Provider availability slot"""
    
    slot_id: str = Field(..., description="Slot ID")
    provider_id: str = Field(..., description="Provider user ID")
    start_time: datetime = Field(..., description="Start time")
    end_time: datetime = Field(..., description="End time")
    status: str = Field("available", description="Status")
    booking_id: Optional[str] = Field(None, description="Booking ID if booked")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CollaborationService(BaseService):
    """Service for secure provider collaboration"""
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("collaboration")
        self.logger = Logger()
        self.encryption = EncryptionService()
        self.distributed_state = DistributedState()
        self.user_status: Dict[str, UserStatus] = {}
    
    async def create_conversation(
        self,
        title: str,
        created_by: str,
        creator_name: str,
        creator_role: str,
        description: Optional[str] = None,
        case_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        encryption_enabled: bool = False,
        initial_participants: List[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Create a new conversation
        
        Args:
            title: Conversation title
            created_by: Creator user ID
            creator_name: Creator name
            creator_role: Creator role
            description: Conversation description
            case_id: Related case ID
            patient_id: Related patient ID
            encryption_enabled: Whether to enable end-to-end encryption
            initial_participants: Initial participants besides creator
            
        Returns:
            The created conversation
        """
        import uuid
        
        # Create conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            created_by=created_by,
            case_id=case_id,
            patient_id=patient_id,
            encryption_enabled=encryption_enabled
        )
        
        # Add creator as participant
        conversation.add_participant(
            user_id=created_by,
            name=creator_name,
            role=creator_role
        )
        
        # Add initial participants
        if initial_participants:
            for participant in initial_participants:
                conversation.add_participant(
                    user_id=participant["user_id"],
                    name=participant["name"],
                    role=participant["role"]
                )
        
        # Add welcome message
        conversation.add_message(
            sender_id="system",
            content=f"Conversation created by {creator_name}",
            message_type=MessageType.SYSTEM
        )
        
        # Store the conversation
        # This would normally use a repository to persist the conversation
        # For this example, we'll just log and return
        
        self.logger.info(
            f"Created conversation: {title}",
            conversation_id=conversation.id,
            created_by=created_by,
            case_id=case_id,
            patient_id=patient_id,
            encryption_enabled=encryption_enabled
        )
        
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            The conversation, or None if not found
        """
        # This would normally retrieve from a database
        # For this example, we'll return None
        
        return None
    
    async def list_conversations(
        self,
        user_id: str,
        case_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ) -> List[Conversation]:
        """
        List conversations for a user
        
        Args:
            user_id: User ID
            case_id: Optional case filter
            patient_id: Optional patient filter
            
        Returns:
            List of matching conversations
        """
        # This would normally query a database
        # For this example, we'll return an empty list
        
        return []
    
    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        attachments: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[Message]:
        """
        Send a message in a conversation
        
        Args:
            conversation_id: Conversation ID
            sender_id: Sender user ID
            content: Message content
            message_type: Message type
            attachments: Attached files
            metadata: Additional metadata
            
        Returns:
            The sent message, or None if conversation not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
            
        # Check if sender is a participant
        is_participant = False
        for participant in conversation.participants:
            if participant.user_id == sender_id:
                is_participant = True
                break
                
        if not is_participant:
            raise ValueError(f"User {sender_id} is not a participant in conversation {conversation_id}")
            
        # Encrypt content if needed
        encrypted_content = content
        if conversation.encryption_enabled:
            encrypted_content = self.encryption.encrypt_data(content)
            
        # Add message
        message = conversation.add_message(
            sender_id=sender_id,
            content=encrypted_content,
            message_type=message_type,
            attachments=attachments,
            metadata=metadata
        )
        
        self.logger.info(
            f"Message sent in conversation {conversation_id}",
            conversation_id=conversation_id,
            message_id=message.message_id,
            sender_id=sender_id,
            message_type=message_type
        )
        
        # Save and return message
        # This would normally update in a database
        return message
    
    async def create_care_plan(
        self,
        title: str,
        patient_id: str,
        created_by: str,
        case_id: Optional[str] = None,
        initial_sections: List[Dict[str, Any]] = None
    ) -> CarePlan:
        """
        Create a new care plan
        
        Args:
            title: Care plan title
            patient_id: Patient ID
            created_by: Creator user ID
            case_id: Related case ID
            initial_sections: Initial sections
            
        Returns:
            The created care plan
        """
        import uuid
        
        # Create care plan
        care_plan = CarePlan(
            id=str(uuid.uuid4()),
            title=title,
            patient_id=patient_id,
            case_id=case_id,
            created_by=created_by,
            contributors=[created_by]
        )
        
        # Add initial sections
        if initial_sections:
            for i, section in enumerate(initial_sections):
                care_plan.add_section(
                    title=section["title"],
                    content=section["content"],
                    created_by=created_by,
                    order=i,
                    metadata=section.get("metadata")
                )
        
        # Store the care plan
        # This would normally use a repository to persist the care plan
        # For this example, we'll just log and return
        
        self.logger.info(
            f"Created care plan: {title}",
            care_plan_id=care_plan.id,
            patient_id=patient_id,
            created_by=created_by,
            case_id=case_id
        )
        
        return care_plan
    
    async def get_care_plan(self, care_plan_id: str) -> Optional[CarePlan]:
        """
        Get a care plan by ID
        
        Args:
            care_plan_id: Care plan ID
            
        Returns:
            The care plan, or None if not found
        """
        # This would normally retrieve from a database
        # For this example, we'll return None
        
        return None
    
    async def update_care_plan_section(
        self,
        care_plan_id: str,
        section_id: str,
        updated_by: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        order: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[CarePlanSection]:
        """
        Update a care plan section
        
        Args:
            care_plan_id: Care plan ID
            section_id: Section ID
            updated_by: Editor user ID
            title: New title
            content: New content
            order: New display order
            metadata: New metadata
            
        Returns:
            The updated section, or None if not found
        """
        care_plan = await self.get_care_plan(care_plan_id)
        if not care_plan:
            return None
            
        # Update section
        section = care_plan.update_section(
            section_id=section_id,
            updated_by=updated_by,
            title=title,
            content=content,
            order=order,
            metadata=metadata
        )
        
        if section:
            self.logger.info(
                f"Updated care plan section {section_id}",
                care_plan_id=care_plan_id,
                section_id=section_id,
                updated_by=updated_by
            )
            
            # Save and return section
            # This would normally update in a database
            return section
            
        return None
    
    async def add_availability_slots(
        self,
        provider_id: str,
        slots: List[Dict[str, Any]]
    ) -> List[AvailabilitySlot]:
        """
        Add availability slots for a provider
        
        Args:
            provider_id: Provider user ID
            slots: List of slots with start_time, end_time, and metadata
            
        Returns:
            List of created slots
        """
        import uuid
        
        created_slots = []
        
        for slot_data in slots:
            # Create slot
            slot = AvailabilitySlot(
                slot_id=str(uuid.uuid4()),
                provider_id=provider_id,
                start_time=slot_data["start_time"],
                end_time=slot_data["end_time"],
                metadata=slot_data.get("metadata", {})
            )
            
            # Store the slot
            # This would normally use a repository to persist the slot
            
            created_slots.append(slot)
            
        self.logger.info(
            f"Added {len(created_slots)} availability slots for provider {provider_id}",
            provider_id=provider_id
        )
        
        return created_slots
    
    async def find_available_slots(
        self,
        provider_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        duration_minutes: Optional[int] = None
    ) -> List[AvailabilitySlot]:
        """
        Find available slots
        
        Args:
            provider_ids: Optional list of provider IDs
            start_date: Optional start date
            end_date: Optional end date
            duration_minutes: Optional minimum duration in minutes
            
        Returns:
            List of matching slots
        """
        # This would normally query a database
        # For this example, we'll return an empty list
        
        return []
    
    async def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """
        Update a user's status
        
        Args:
            user_id: User ID
            status: New status
            
        Returns:
            True if successful
        """
        self.user_status[user_id] = status
        
        self.logger.debug(
            f"Updated user {user_id} status to {status}",
            user_id=user_id,
            status=status
        )
        
        return True
    
    async def get_user_status(self, user_id: str) -> UserStatus:
        """
        Get a user's status
        
        Args:
            user_id: User ID
            
        Returns:
            The user's status
        """
        return self.user_status.get(user_id, UserStatus.OFFLINE)
