"""
Protocol service for managing clinical protocols.
Handles protocol CRUD, versioning, and decision trees.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, delete
from sqlalchemy.orm import selectinload
import uuid

from ..db.models import Protocol, AuditLog
from ..core.logging import get_logger

logger = get_logger(__name__)

class ProtocolService:
    """Service class for protocol operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_protocol(self, protocol_data: Dict[str, Any], created_by: str) -> Protocol:
        """Create a new protocol."""
        try:
            # Generate protocol ID
            protocol_data["id"] = uuid.uuid4()
            protocol_data["created_by"] = created_by
            
            # Set default values
            protocol_data.setdefault("status", "draft")
            protocol_data.setdefault("applicable_stages", [])
            protocol_data.setdefault("inclusion_criteria", [])
            protocol_data.setdefault("exclusion_criteria", [])
            protocol_data.setdefault("parameters", {})
            protocol_data.setdefault("decision_tree", {})
            protocol_data.setdefault("references", [])
            
            protocol = Protocol(**protocol_data)
            self.db.add(protocol)
            await self.db.commit()
            await self.db.refresh(protocol)
            
            logger.info(f"Created protocol: {protocol.name}")
            return protocol
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating protocol: {str(e)}")
            raise
    
    async def get_protocol_by_id(self, protocol_id: str) -> Optional[Protocol]:
        """Get protocol by ID."""
        try:
            result = await self.db.execute(
                select(Protocol).where(
                    and_(Protocol.id == protocol_id, Protocol.deleted_at.is_(None))
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting protocol by ID {protocol_id}: {str(e)}")
            raise
    
    async def get_protocol_by_name(self, name: str) -> Optional[Protocol]:
        """Get protocol by name."""
        try:
            result = await self.db.execute(
                select(Protocol).where(
                    and_(Protocol.name == name, Protocol.deleted_at.is_(None))
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting protocol by name {name}: {str(e)}")
            raise
    
    async def list_protocols(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        stage: Optional[str] = None
    ) -> Tuple[List[Protocol], int]:
        """List protocols with filtering and pagination."""
        try:
            query = select(Protocol).where(Protocol.deleted_at.is_(None))
            
            # Apply filters
            if category:
                query = query.where(Protocol.category == category)
            
            if status:
                query = query.where(Protocol.status == status)
            
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Protocol.name.ilike(search_term),
                        Protocol.description.ilike(search_term)
                    )
                )
            
            if stage:
                # Check if stage is in applicable_stages JSON array
                query = query.where(
                    Protocol.applicable_stages.contains([stage])
                )
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = count_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            query = query.order_by(Protocol.created_at.desc())
            
            result = await self.db.execute(query)
            protocols = result.scalars().all()
            
            return list(protocols), total
        except Exception as e:
            logger.error(f"Error listing protocols: {str(e)}")
            raise
    
    async def update_protocol(
        self, 
        protocol_id: str, 
        update_data: Dict[str, Any], 
        updated_by: str
    ) -> Protocol:
        """Update protocol information."""
        try:
            update_data["updated_at"] = datetime.utcnow()
            update_data["updated_by"] = updated_by
            
            await self.db.execute(
                update(Protocol)
                .where(and_(Protocol.id == protocol_id, Protocol.deleted_at.is_(None)))
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_protocol_by_id(protocol_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating protocol {protocol_id}: {str(e)}")
            raise
    
    async def update_protocol_status(
        self,
        protocol_id: str,
        new_status: str,
        reason: Optional[str] = None,
        updated_by: str = None
    ) -> Protocol:
        """Update protocol status with reason."""
        try:
            protocol = await self.get_protocol_by_id(protocol_id)
            if not protocol:
                raise ValueError("Protocol not found")
            
            update_data = {
                "status": new_status,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by
            }
            
            # Store status change history in metadata
            metadata = protocol.metadata or {}
            metadata.setdefault("status_history", [])
            metadata["status_history"].append({
                "old_status": protocol.status,
                "new_status": new_status,
                "reason": reason,
                "updated_by": updated_by,
                "timestamp": datetime.utcnow().isoformat()
            })
            update_data["metadata"] = metadata
            
            await self.db.execute(
                update(Protocol)
                .where(and_(Protocol.id == protocol_id, Protocol.deleted_at.is_(None)))
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_protocol_by_id(protocol_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating protocol status {protocol_id}: {str(e)}")
            raise
    
    async def get_protocol_versions(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a protocol."""
        try:
            # Mock implementation - in reality, you'd have a protocol_versions table
            protocol = await self.get_protocol_by_id(protocol_id)
            if not protocol:
                return []
            
            # Return current version for now
            versions = [{
                "id": str(uuid.uuid4()),
                "protocol_id": protocol_id,
                "version": protocol.version,
                "changes": "Current version",
                "change_reason": "Active protocol",
                "created_by": protocol.created_by,
                "created_at": protocol.created_at,
                "is_current": True
            }]
            
            return versions
        except Exception as e:
            logger.error(f"Error getting protocol versions {protocol_id}: {str(e)}")
            raise
    
    async def create_protocol_version(
        self,
        protocol_id: str,
        version_data: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """Create a new version of a protocol."""
        try:
            protocol = await self.get_protocol_by_id(protocol_id)
            if not protocol:
                raise ValueError("Protocol not found")
            
            # Create new version record
            version = {
                "id": str(uuid.uuid4()),
                "protocol_id": protocol_id,
                "version": version_data.get("version", "1.0"),
                "changes": version_data.get("changes", ""),
                "change_reason": version_data.get("change_reason", ""),
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "is_current": False
            }
            
            # In a full implementation, save to protocol_versions table
            logger.info(f"Created protocol version for {protocol_id}: {version['version']}")
            return version
        except Exception as e:
            logger.error(f"Error creating protocol version {protocol_id}: {str(e)}")
            raise
    
    async def get_protocol_decision_tree(self, protocol_id: str) -> Dict[str, Any]:
        """Get the decision tree for a protocol."""
        try:
            protocol = await self.get_protocol_by_id(protocol_id)
            if not protocol:
                raise ValueError("Protocol not found")
            
            return protocol.decision_tree or {}
        except Exception as e:
            logger.error(f"Error getting decision tree for protocol {protocol_id}: {str(e)}")
            raise
    
    async def update_protocol_decision_tree(
        self,
        protocol_id: str,
        decision_tree: Dict[str, Any],
        updated_by: str
    ) -> Protocol:
        """Update the decision tree for a protocol."""
        try:
            return await self.update_protocol(
                protocol_id=protocol_id,
                update_data={"decision_tree": decision_tree},
                updated_by=updated_by
            )
        except Exception as e:
            logger.error(f"Error updating decision tree for protocol {protocol_id}: {str(e)}")
            raise
    
    async def get_categories(self) -> List[str]:
        """Get all available protocol categories."""
        try:
            result = await self.db.execute(
                select(Protocol.category)
                .where(Protocol.deleted_at.is_(None))
                .distinct()
            )
            categories = [row[0] for row in result.fetchall()]
            return sorted(categories)
        except Exception as e:
            logger.error(f"Error getting protocol categories: {str(e)}")
            raise
    
    async def get_stages(self) -> List[str]:
        """Get all available protocol stages."""
        try:
            # Mock implementation - return standard cancer stages
            stages = ["0", "I", "II", "III", "IV"]
            return stages
        except Exception as e:
            logger.error(f"Error getting protocol stages: {str(e)}")
            raise
    
    async def soft_delete_protocol(self, protocol_id: str) -> None:
        """Soft delete protocol."""
        try:
            await self.db.execute(
                update(Protocol)
                .where(and_(Protocol.id == protocol_id, Protocol.deleted_at.is_(None)))
                .values(
                    deleted_at=datetime.utcnow(),
                    status="archived"
                )
            )
            await self.db.commit()
            
            logger.info(f"Soft deleted protocol: {protocol_id}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error soft deleting protocol {protocol_id}: {str(e)}")
            raise
    
    async def log_audit(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log audit event."""
        try:
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            # Don't raise - audit logging should not break the main flow
