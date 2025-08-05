from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from surgify.core.services.ai_service import AIService

# Universal Research Integration (Optional Enhancement)
try:
    from surgify.core.database import get_db
    from surgify.core.services.case_service import CaseService
    from surgify.modules.universal_research.adapters.legacy_bridge import LegacyBridge
    from surgify.modules.universal_research.adapters.surgify_adapter import (
        SurgifyAdapter,
    )

    RESEARCH_AVAILABLE = True
    LegacyBridge = LegacyBridge  # Make available for type hints
except ImportError:
    RESEARCH_AVAILABLE = False
    LegacyBridge = None  # Provide None fallback

router = APIRouter()

# Dependencies
ai_service = AIService()


# Research enhancement dependencies (optional)
def get_legacy_bridge() -> Optional[Any]:
    """Get legacy bridge for research enhancements (optional)"""
    if not RESEARCH_AVAILABLE or LegacyBridge is None:
        return None
    try:
        from sqlalchemy.orm import Session

        db_session = next(get_db())
        surgify_adapter = SurgifyAdapter(db_session)
        case_service = CaseService(db_session)
        return LegacyBridge(case_service, surgify_adapter)
    except Exception:
        return None


@router.post("/recommendations/risk", response_model=float)
def assess_risk(patient_data: dict):
    try:
        risk_score = ai_service.assess_patient_risk(patient_data)
        return risk_score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations", response_model=list)
def get_recommendations(
    patient_data: dict,
    include_research: bool = Query(
        False, description="Include research-based recommendations (optional)"
    ),
    legacy_bridge: Optional[Union[LegacyBridge, None]] = Depends(get_legacy_bridge),
):
    """
    Get recommendations for patient
    ENHANCED: Now supports optional evidence-based research recommendations
    BACKWARD COMPATIBLE: Works exactly as before when include_research=false (default)
    """
    try:
        # Get original AI recommendations (unchanged)
        recommendations = ai_service.get_recommendations(patient_data)

        # RESEARCH ENHANCEMENT (Optional - maintains backward compatibility)
        if include_research and legacy_bridge and RESEARCH_AVAILABLE:
            try:
                # Convert patient_data to case format for research analysis
                case_data = {
                    "case_id": patient_data.get("case_id", "temp_case"),
                    "patient_demographics": patient_data,
                    "procedure_type": patient_data.get("procedure_type"),
                    "risk_score": patient_data.get("risk_score"),
                }

                # Get research-enhanced recommendations
                enhanced_recommendations = (
                    legacy_bridge.enhance_recommendations_response(
                        {
                            "recommendations": recommendations,
                            "case_id": case_data["case_id"],
                        },
                        include_research=True,
                    )
                )

                # Merge original with research recommendations
                if "research_recommendations" in enhanced_recommendations:
                    research_recs = enhanced_recommendations["research_recommendations"]

                    # Add research-based recommendations to the list
                    if isinstance(research_recs, dict):
                        for category, recs in research_recs.items():
                            if isinstance(recs, list):
                                recommendations.extend(
                                    [f"[Research-Based] {rec}" for rec in recs]
                                )

            except Exception as e:
                # Fallback to original recommendations if research enhancement fails
                pass

        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/outcome", response_model=dict)
def predict_outcome(
    patient_data: dict,
    include_research: bool = Query(
        False, description="Include research-based outcome prediction (optional)"
    ),
    legacy_bridge: Optional[Union[LegacyBridge, None]] = Depends(get_legacy_bridge),
):
    """
    Predict patient outcome
    ENHANCED: Now supports optional research-based outcome predictions
    BACKWARD COMPATIBLE: Works exactly as before when include_research=false (default)
    """
    try:
        # Get original AI outcome prediction (unchanged)
        outcome = ai_service.predict_patient_outcome(patient_data)

        # RESEARCH ENHANCEMENT (Optional - maintains backward compatibility)
        if include_research and legacy_bridge and RESEARCH_AVAILABLE:
            try:
                # Convert patient_data to case format for research analysis
                case_data = {
                    "case_id": patient_data.get("case_id", "temp_case"),
                    "patient_demographics": patient_data,
                    "procedure_type": patient_data.get("procedure_type"),
                    "risk_score": patient_data.get("risk_score"),
                }

                # Add research-based outcome insights
                from surgify.modules.universal_research.adapters.surgify_adapter import (
                    SurgifyAdapter,
                )
                from surgify.modules.universal_research.engines.outcome_predictor import (
                    OutcomePredictor,
                )

                db_session = next(get_db())
                adapter = SurgifyAdapter(db_session)
                predictor = OutcomePredictor(adapter)

                research_prediction = predictor.predict_case_outcome(case_data)

                # Enhance original outcome with research insights
                outcome["research_insights"] = {
                    "evidence_based_probability": research_prediction.get(
                        "primary_prediction", {}
                    ),
                    "confidence_level": research_prediction.get(
                        "evidence_metrics", {}
                    ).get("confidence_level"),
                    "similar_cases_analyzed": research_prediction.get(
                        "evidence_metrics", {}
                    ).get("sample_size", 0),
                }

            except Exception as e:
                # Fallback to original outcome if research enhancement fails
                outcome["research_note"] = "Research insights unavailable"

        return outcome

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/alerts", response_model=list)
def generate_alerts(patient_data: dict):
    try:
        alerts = ai_service.generate_patient_alerts(patient_data)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
