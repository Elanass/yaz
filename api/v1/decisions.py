"""
Decision support API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path

from core.dependencies import get_current_user
from feature.decisions.adci_engine import ADCIEngine
from feature.decisions.precision_engine import MCDAEngine
from core.reproducibility.manager import ReproducibilityManager
from core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
adci_engine = ADCIEngine()
mcda_engine = MCDAEngine()
reproducibility_manager = ReproducibilityManager()


class DecisionRequest(BaseModel):
    patient_data: Dict[str, Any]
    analysis_type: str = "adci"
    context: Optional[Dict[str, Any]] = None


class DecisionResponse(BaseModel):
    decision_id: str
    confidence_score: float
    recommendation: str
    reasoning: str
    protocol_adherence: Optional[Dict[str, Any]] = None
    precision_score: Optional[float] = None
    evidence_level: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None


class PrecisionTrackingRequest(BaseModel):
    case_id: str
    decision_id: str
    implemented: bool
    outcome: Optional[Dict[str, Any]] = None
    adherence_score: Optional[float] = None
    notes: Optional[str] = None


class PrecisionTrackingResponse(BaseModel):
    success: bool
    tracking_id: str
    impact_score: Optional[float] = None
    message: str


@router.post("/analyze", response_model=DecisionResponse)
async def analyze_decision(
    request: DecisionRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    """
    Analyze surgical decision using ADCI framework
    
    This endpoint uses the Adaptive Decision Confidence Index (ADCI) engine
    to analyze surgical decisions for gastric cancer cases with FLOT protocol.
    It provides decision support with confidence metrics and protocol adherence
    tracking for precision medicine.
    """
    try:
        # Generate decision ID
        decision_id = f"decision_{uuid.uuid4().hex[:12]}"
        
        # Analyze using ADCI engine
        adci_result = await adci_engine.predict(
            patient_data=request.patient_data,
            collaboration_context=request.context
        )
        
        # Run MCDA analysis for precision scoring if needed
        precision_score = None
        alternatives = None
        
        if request.analysis_type == "precision_mcda":
            mcda_result = await mcda_engine.analyze(
                patient_data=request.patient_data,
                context=request.context
            )
            precision_score = mcda_result.get("overall_score")
            alternatives = mcda_result.get("alternatives")
        
        # Extract decision recommendation
        confidence = adci_result["confidence_metrics"]["overall_confidence"]
        recommendation = adci_result["adci"].get("recommended_action", "No specific recommendation")
        reasoning = adci_result["adci"].get("reasoning", "")
        
        # Calculate protocol adherence if FLOT analysis exists
        protocol_adherence = None
        if "flot_analysis" in adci_result:
            protocol_adherence = {
                "protocol": "FLOT",
                "adherence_score": adci_result["flot_analysis"].get("protocol_adherence", {}).get("score", 0.0),
                "deviations": adci_result["flot_analysis"].get("protocol_adherence", {}).get("deviations", []),
                "recommendations": adci_result["flot_analysis"].get("protocol_adherence", {}).get("recommendations", [])
            }
        
        # Store decision for tracking
        background_tasks.add_task(
            _store_decision,
            decision_id=decision_id,
            user_id=current_user.id,
            patient_data=request.patient_data,
            adci_result=adci_result,
            precision_score=precision_score
        )
        
        return DecisionResponse(
            decision_id=decision_id,
            confidence_score=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            protocol_adherence=protocol_adherence,
            precision_score=precision_score,
            evidence_level=adci_result.get("evidence_level", "B"),
            alternatives=alternatives
        )
        
    except Exception as e:
        logger.error(f"Error analyzing decision: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing decision: {str(e)}")


@router.post("/track", response_model=PrecisionTrackingResponse)
async def track_decision_impact(
    request: PrecisionTrackingRequest,
    current_user=Depends(get_current_user)
):
    """
    Track the impact of decisions on patient outcomes
    
    This endpoint allows tracking the implementation of recommendations
    and their impact on patient outcomes, supporting the precision
    medicine approach and continuous improvement.
    """
    try:
        # Generate tracking ID
        tracking_id = f"track_{uuid.uuid4().hex[:8]}"
        
        # Calculate preliminary impact score (more sophisticated calculation to be implemented)
        impact_score = 0.0
        if request.implemented and request.adherence_score:
            impact_score = request.adherence_score * 0.85  # Simple calculation for MVP
        
        # Store tracking data
        tracking_data = {
            "tracking_id": tracking_id,
            "case_id": request.case_id,
            "decision_id": request.decision_id,
            "user_id": current_user.id,
            "implemented": request.implemented,
            "outcome": request.outcome,
            "adherence_score": request.adherence_score,
            "impact_score": impact_score,
            "notes": request.notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save tracking data to storage
        tracking_dir = Path("data/tracking")
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        with open(tracking_dir / f"{tracking_id}.json", "w") as f:
            json.dump(tracking_data, f, indent=2, default=str)
        
        return PrecisionTrackingResponse(
            success=True,
            tracking_id=tracking_id,
            impact_score=impact_score,
            message="Decision impact tracking recorded successfully."
        )
        
    except Exception as e:
        logger.error(f"Error tracking decision impact: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error tracking decision impact: {str(e)}")


@router.get("/history")
async def get_decision_history(
    case_id: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """
    Get user's decision history with filtering options
    
    This endpoint retrieves the decision history for the current user,
    with optional filtering by case ID. It includes tracking data for
    implemented decisions and their outcomes.
    """
    try:
        # Simple implementation for MVP - will be enhanced with database integration
        decisions_dir = Path("data/decisions")
        tracking_dir = Path("data/tracking")
        
        if not decisions_dir.exists():
            return {"decisions": [], "total": 0}
        
        # Get all decision files
        decision_files = list(decisions_dir.glob("*.json"))
        decisions = []
        
        for file in decision_files:
            try:
                with open(file, "r") as f:
                    decision = json.load(f)
                
                # Filter by case_id if provided
                if case_id and decision.get("patient_data", {}).get("case_id") != case_id:
                    continue
                
                # Filter by user_id to only show current user's decisions
                if decision.get("user_id") == current_user.id:
                    # Get tracking data if available
                    decision_id = decision.get("decision_id")
                    tracking_files = list(tracking_dir.glob(f"*_{decision_id}.json"))
                    
                    if tracking_files:
                        with open(tracking_files[0], "r") as tf:
                            tracking = json.load(tf)
                            decision["tracking"] = tracking
                    
                    decisions.append(decision)
            except Exception as e:
                logger.error(f"Error loading decision file {file}: {str(e)}")
        
        # Sort by timestamp descending
        decisions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {"decisions": decisions, "total": len(decisions)}
        
    except Exception as e:
        logger.error(f"Error getting decision history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting decision history: {str(e)}")


async def _store_decision(decision_id: str, user_id: str, patient_data: Dict[str, Any], 
                          adci_result: Dict[str, Any], precision_score: Optional[float] = None):
    """Store decision data for tracking"""
    try:
        # Prepare decision data
        decision_data = {
            "decision_id": decision_id,
            "user_id": user_id,
            "patient_data": patient_data,
            "adci_result": adci_result,
            "precision_score": precision_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save decision data to storage
        decisions_dir = Path("data/decisions")
        decisions_dir.mkdir(parents=True, exist_ok=True)
        
        with open(decisions_dir / f"{decision_id}.json", "w") as f:
            json.dump(decision_data, f, indent=2, default=str)
            
        logger.info(f"Decision {decision_id} stored successfully")
            
    except Exception as e:
        logger.error(f"Error storing decision {decision_id}: {str(e)}", exc_info=True)
