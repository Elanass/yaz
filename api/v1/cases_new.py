"""
Cases API
Endpoints for managing retrospective and prospective case data with ElectricSQL
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.dependencies import DatabaseSession, CurrentUser, EncryptionService
from core.models.base import ApiResponse
from data.models import Case, CaseCreate, CaseUpdate, CaseResponse


router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("", response_model=ApiResponse[List[CaseResponse]])
async def get_cases(
    session: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(100, description="Maximum number of cases to return"),
    offset: int = Query(0, description="Number of cases to skip"),
    center_id: Optional[str] = Query(None, description="Filter by center ID"),
    stage: Optional[str] = Query(None, description="Filter by tumor stage")
):
    """
    Get cases from the database with filtering and pagination
    """
    try:
        # Build query
        query = select(Case)
        
        # Apply filters
        if center_id:
            query = query.where(Case.center_id == center_id)
        if stage:
            query = query.where(Case.tumor_stage == stage)
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await session.execute(query)
        cases = result.scalars().all()
        
        # Convert to response models
        case_responses = [
            CaseResponse(
                id=str(case.id),
                patient_id=str(case.patient_id),
                center_id=case.center_id,
                tumor_stage=case.tumor_stage,
                tumor_location=case.tumor_location,
                histology=case.histology,
                treatment_plan=case.treatment_plan,
                status=case.status,
                created_at=case.created_at,
                updated_at=case.updated_at
            )
            for case in cases
        ]
        
        return ApiResponse.success_response(
            data=case_responses,
            message=f"Retrieved {len(case_responses)} cases"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cases: {str(e)}"
        )


@router.get("/{case_id}", response_model=ApiResponse[CaseResponse])
async def get_case(
    case_id: str,
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Get a specific case by ID"""
    
    try:
        result = await session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        case_response = CaseResponse(
            id=str(case.id),
            patient_id=str(case.patient_id),
            center_id=case.center_id,
            tumor_stage=case.tumor_stage,
            tumor_location=case.tumor_location,
            histology=case.histology,
            treatment_plan=case.treatment_plan,
            status=case.status,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
        return ApiResponse.success_response(
            data=case_response,
            message="Case retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve case: {str(e)}"
        )


@router.post("", response_model=ApiResponse[CaseResponse])
async def create_case(
    case_data: CaseCreate,
    session: DatabaseSession,
    current_user: CurrentUser,
    encryption: EncryptionService
):
    """Create a new case with encrypted sensitive data"""
    
    try:
        # Create new case
        new_case = Case(
            patient_id=case_data.patient_id,
            center_id=case_data.center_id,
            tumor_stage=case_data.tumor_stage,
            tumor_location=case_data.tumor_location,
            histology=case_data.histology,
            treatment_plan=case_data.treatment_plan,
            status="active",
            created_by=current_user.id
        )
        
        # Encrypt sensitive fields if needed
        if hasattr(case_data, 'notes') and case_data.notes:
            new_case.encrypted_notes = encryption.encrypt_data(case_data.notes)
        
        session.add(new_case)
        await session.commit()
        await session.refresh(new_case)
        
        case_response = CaseResponse(
            id=str(new_case.id),
            patient_id=str(new_case.patient_id),
            center_id=new_case.center_id,
            tumor_stage=new_case.tumor_stage,
            tumor_location=new_case.tumor_location,
            histology=new_case.histology,
            treatment_plan=new_case.treatment_plan,
            status=new_case.status,
            created_at=new_case.created_at,
            updated_at=new_case.updated_at
        )
        
        return ApiResponse.success_response(
            data=case_response,
            message="Case created successfully"
        )
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )


@router.put("/{case_id}", response_model=ApiResponse[CaseResponse])
async def update_case(
    case_id: str,
    case_data: CaseUpdate,
    session: DatabaseSession,
    current_user: CurrentUser,
    encryption: EncryptionService
):
    """Update an existing case"""
    
    try:
        result = await session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Update fields
        for field, value in case_data.dict(exclude_unset=True).items():
            if field == 'notes' and value:
                case.encrypted_notes = encryption.encrypt_data(value)
            else:
                setattr(case, field, value)
        
        case.updated_by = current_user.id
        await session.commit()
        await session.refresh(case)
        
        case_response = CaseResponse(
            id=str(case.id),
            patient_id=str(case.patient_id),
            center_id=case.center_id,
            tumor_stage=case.tumor_stage,
            tumor_location=case.tumor_location,
            histology=case.histology,
            treatment_plan=case.treatment_plan,
            status=case.status,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
        return ApiResponse.success_response(
            data=case_response,
            message="Case updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update case: {str(e)}"
        )


@router.delete("/{case_id}", response_model=ApiResponse[None])
async def delete_case(
    case_id: str,
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Delete a case (soft delete for compliance)"""
    
    try:
        result = await session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Soft delete - mark as inactive
        case.status = "deleted"
        case.updated_by = current_user.id
        await session.commit()
        
        return ApiResponse.success_response(
            message="Case deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete case: {str(e)}"
        )
