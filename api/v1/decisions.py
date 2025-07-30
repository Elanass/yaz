"""
Decision support API endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from core.dependencies import get_current_user

router = APIRouter()


class DecisionRequest(BaseModel):
    patient_data: Dict[str, Any]
    analysis_type: str = "adci"


class DecisionResponse(BaseModel):
    decision_id: str
    confidence_score: float
    recommendation: str
    reasoning: str


@router.post("/analyze", response_model=DecisionResponse)
async def analyze_decision(
    request: DecisionRequest,
    current_user=Depends(get_current_user)
):
    """Analyze surgical decision using ADCI framework"""
    # Simplified decision analysis for MVP
    return DecisionResponse(
        decision_id="demo-123",
        confidence_score=0.85,
        recommendation="Proceed with gastric resection",
        reasoning="Based on tumor characteristics and patient factors"
    )


@router.get("/history")
async def get_decision_history(current_user=Depends(get_current_user)):
    """Get user's decision history"""
    return {"decisions": [], "total": 0}
