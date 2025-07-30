"""
Cases API endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from core.dependencies import get_current_user

router = APIRouter()


class CaseRequest(BaseModel):
    patient_id: str
    diagnosis: str
    stage: str


class CaseResponse(BaseModel):
    case_id: str
    patient_id: str
    diagnosis: str
    stage: str
    created_at: str


@router.post("/", response_model=CaseResponse)
async def create_case(
    request: CaseRequest,
    current_user=Depends(get_current_user)
):
    """Create a new case"""
    return CaseResponse(
        case_id="case-123",
        patient_id=request.patient_id,
        diagnosis=request.diagnosis,
        stage=request.stage,
        created_at="2025-07-30T12:00:00Z"
    )


@router.get("/", response_model=List[CaseResponse])
async def list_cases(current_user=Depends(get_current_user)):
    """List all cases"""
    return []


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, current_user=Depends(get_current_user)):
    """Get specific case"""
    return CaseResponse(
        case_id=case_id,
        patient_id="patient-123",
        diagnosis="Gastric Adenocarcinoma",
        stage="T3N1M0",
        created_at="2025-07-30T12:00:00Z"
    )
