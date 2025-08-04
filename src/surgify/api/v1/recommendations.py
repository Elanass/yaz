from fastapi import APIRouter, HTTPException
from surgify.core.services.ai_service import AIService

router = APIRouter()

# Dependency
ai_service = AIService()

@router.post("/recommendations/risk", response_model=float)
def assess_risk(patient_data: dict):
    try:
        risk_score = ai_service.assess_patient_risk(patient_data)
        return risk_score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations", response_model=list)
def get_recommendations(patient_data: dict):
    try:
        recommendations = ai_service.get_recommendations(patient_data)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/outcome", response_model=dict)
def predict_outcome(patient_data: dict):
    try:
        outcome = ai_service.predict_patient_outcome(patient_data)
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
