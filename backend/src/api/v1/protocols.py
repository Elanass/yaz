"""
Protocol management API endpoints.
Handles clinical protocols, guidelines, and decision trees.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.security import get_current_user, require_permissions
from ...core.logging import get_logger
from ...db.database import get_db
from ...db.models import User, Protocol
from ...services.protocol_service import ProtocolService
from ...schemas.protocol import (
    ProtocolCreate, ProtocolUpdate, ProtocolResponse, ProtocolList,
    ProtocolDetailResponse, ProtocolVersionResponse
)

router = APIRouter(prefix="/protocols", tags=["protocols"])
logger = get_logger(__name__)
security = HTTPBearer()

@router.get("/", response_model=ProtocolList)
async def list_protocols(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List protocols with filtering and pagination."""
    try:
        service = ProtocolService(db)
        protocols, total = await service.list_protocols(
            skip=skip,
            limit=limit,
            category=category,
            status=status,
            search=search,
            stage=stage
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocols.list",
            resource_type="protocol",
            details={
                "filters": {
                    "category": category,
                    "status": status,
                    "search": search,
                    "stage": stage
                }
            }
        )
        
        return ProtocolList(
            protocols=[ProtocolResponse.from_orm(protocol) for protocol in protocols],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing protocols: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocols"
        )

@router.get("/categories")
async def get_protocol_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all available protocol categories."""
    try:
        service = ProtocolService(db)
        categories = await service.get_categories()
        
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting protocol categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )

@router.get("/stages")
async def get_protocol_stages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all available protocol stages."""
    try:
        service = ProtocolService(db)
        stages = await service.get_stages()
        
        return {"stages": stages}
    except Exception as e:
        logger.error(f"Error getting protocol stages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stages"
        )

@router.get("/{protocol_id}", response_model=ProtocolDetailResponse)
async def get_protocol(
    protocol_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get protocol by ID with full details."""
    try:
        service = ProtocolService(db)
        protocol = await service.get_protocol_by_id(protocol_id)
        
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.read",
            resource_type="protocol",
            resource_id=protocol_id
        )
        
        return ProtocolDetailResponse.from_orm(protocol)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting protocol {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocol"
        )

@router.post("/", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_protocol(
    protocol_data: ProtocolCreate,
    current_user: User = Depends(require_permissions(["protocols:create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new protocol."""
    try:
        service = ProtocolService(db)
        
        # Check if protocol with same name exists
        existing_protocol = await service.get_protocol_by_name(protocol_data.name)
        if existing_protocol:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Protocol with this name already exists"
            )
        
        new_protocol = await service.create_protocol(
            protocol_data=protocol_data.dict(),
            created_by=current_user.id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.create",
            resource_type="protocol",
            resource_id=str(new_protocol.id),
            details={"name": protocol_data.name, "category": protocol_data.category}
        )
        
        return ProtocolResponse.from_orm(new_protocol)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating protocol: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create protocol"
        )

@router.put("/{protocol_id}", response_model=ProtocolResponse)
async def update_protocol(
    protocol_id: str,
    protocol_update: ProtocolUpdate,
    current_user: User = Depends(require_permissions(["protocols:update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update protocol by ID."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        updated_protocol = await service.update_protocol(
            protocol_id=protocol_id,
            update_data=protocol_update.dict(exclude_unset=True),
            updated_by=current_user.id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.update",
            resource_type="protocol",
            resource_id=protocol_id,
            details={"updated_fields": list(protocol_update.dict(exclude_unset=True).keys())}
        )
        
        return ProtocolResponse.from_orm(updated_protocol)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating protocol {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update protocol"
        )

@router.put("/{protocol_id}/status")
async def update_protocol_status(
    protocol_id: str,
    status_update: dict,
    current_user: User = Depends(require_permissions(["protocols:update_status"])),
    db: AsyncSession = Depends(get_db)
):
    """Update protocol status (draft/active/deprecated)."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        new_status = status_update.get("status")
        if new_status not in ["draft", "active", "deprecated"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'draft', 'active', or 'deprecated'"
            )
        
        updated_protocol = await service.update_protocol_status(
            protocol_id=protocol_id,
            new_status=new_status,
            reason=status_update.get("reason"),
            updated_by=current_user.id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.status_update",
            resource_type="protocol",
            resource_id=protocol_id,
            details={
                "old_status": protocol.status,
                "new_status": new_status,
                "reason": status_update.get("reason")
            }
        )
        
        return ProtocolResponse.from_orm(updated_protocol)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating protocol status {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update protocol status"
        )

@router.get("/{protocol_id}/versions", response_model=List[ProtocolVersionResponse])
async def get_protocol_versions(
    protocol_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all versions of a protocol."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        versions = await service.get_protocol_versions(protocol_id)
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.versions_read",
            resource_type="protocol",
            resource_id=protocol_id
        )
        
        return [ProtocolVersionResponse.from_orm(version) for version in versions]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting protocol versions {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocol versions"
        )

@router.post("/{protocol_id}/versions", response_model=ProtocolVersionResponse)
async def create_protocol_version(
    protocol_id: str,
    version_data: dict,
    current_user: User = Depends(require_permissions(["protocols:version"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new version of a protocol."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        new_version = await service.create_protocol_version(
            protocol_id=protocol_id,
            version_data=version_data,
            created_by=current_user.id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.version_create",
            resource_type="protocol",
            resource_id=protocol_id,
            details={"version": new_version.version, "changes": version_data.get("changes")}
        )
        
        return ProtocolVersionResponse.from_orm(new_version)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating protocol version {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create protocol version"
        )

@router.get("/{protocol_id}/decision-tree")
async def get_protocol_decision_tree(
    protocol_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the decision tree for a protocol."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        decision_tree = await service.get_protocol_decision_tree(protocol_id)
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.decision_tree_read",
            resource_type="protocol",
            resource_id=protocol_id
        )
        
        return {"decision_tree": decision_tree}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting decision tree for protocol {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve decision tree"
        )

@router.put("/{protocol_id}/decision-tree")
async def update_protocol_decision_tree(
    protocol_id: str,
    decision_tree: dict,
    current_user: User = Depends(require_permissions(["protocols:update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update the decision tree for a protocol."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        updated_protocol = await service.update_protocol_decision_tree(
            protocol_id=protocol_id,
            decision_tree=decision_tree,
            updated_by=current_user.id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.decision_tree_update",
            resource_type="protocol",
            resource_id=protocol_id,
            details={"tree_nodes": len(decision_tree.get("nodes", []))}
        )
        
        return {"message": "Decision tree updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating decision tree for protocol {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update decision tree"
        )

@router.delete("/{protocol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_protocol(
    protocol_id: str,
    current_user: User = Depends(require_permissions(["protocols:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete protocol by ID."""
    try:
        service = ProtocolService(db)
        
        protocol = await service.get_protocol_by_id(protocol_id)
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Protocol not found"
            )
        
        await service.soft_delete_protocol(protocol_id)
        
        await service.log_audit(
            user_id=current_user.id,
            action="protocol.delete",
            resource_type="protocol",
            resource_id=protocol_id,
            details={"name": protocol.name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting protocol {protocol_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete protocol"
        )
