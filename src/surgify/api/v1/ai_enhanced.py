"""
Enhanced AI API endpoints with local ML models integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import os

from ...ai.enhanced_ai_service import enhanced_ai_service

logger = logging.getLogger(__name__)
enhanced_router = APIRouter(prefix="/ai/enhanced", tags=["Enhanced AI Services"])

# Enhanced request models
class MedicalAnalysisRequest(BaseModel):
    """Request for medical text analysis using local ML models"""
    text: str = Field(..., description="Medical text to analyze")
    context: str = Field("clinical", description="Medical context")
    extract_entities: bool = Field(True, description="Extract medical entities")
    assess_risk: bool = Field(True, description="Assess risk indicators")

class RiskAssessmentRequest(BaseModel):
    """Request for ML-powered surgical risk assessment"""
    patient_data: Dict[str, Any] = Field(..., description="Patient information")
    procedure_type: str = Field(..., description="Type of procedure")
    use_ml_models: bool = Field(True, description="Use ML models for assessment")

class OutcomePredictionRequest(BaseModel):
    """Request for outcome prediction using enhanced models"""
    case_data: Dict[str, Any] = Field(..., description="Case information")
    include_timeline: bool = Field(True, description="Include timeline predictions")
    confidence_threshold: float = Field(0.7, description="Minimum confidence threshold")

# Enhanced API endpoints
@enhanced_router.post("/analyze-medical-text")
async def analyze_medical_text_enhanced(request: MedicalAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze medical text using local BioClinicalBERT models
    Falls back to Hugging Face API if needed - much cheaper than OpenAI!
    """
    try:
        logger.info(f"🧠 Analyzing medical text with enhanced AI models")
        
        result = await enhanced_ai_service.analyze_medical_text(
            text=request.text,
            context=request.context
        )
        
        return {
            "status": "success",
            "analysis": result,
            "cost": "free" if result.get("method") == "local_biobert" else "low",
            "processing_time": result.get("processing_time_ms", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Medical text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@enhanced_router.post("/assess-surgical-risk")
async def assess_surgical_risk_enhanced(request: RiskAssessmentRequest) -> Dict[str, Any]:
    """
    Enhanced surgical risk assessment using ML models
    Combines local models with statistical analysis - completely free!
    """
    try:
        logger.info(f"⚕️ Performing enhanced surgical risk assessment")
        
        # Prepare patient data
        patient_data = request.patient_data.copy()
        patient_data["procedure"] = request.procedure_type
        
        result = await enhanced_ai_service.assess_surgical_risk(patient_data)
        
        return {
            "status": "success",
            "risk_assessment": result,
            "cost": "free",
            "recommendations": _generate_risk_recommendations(result)
        }
        
    except Exception as e:
        logger.error(f"❌ Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@enhanced_router.post("/predict-outcome")
async def predict_outcome_enhanced(request: OutcomePredictionRequest) -> Dict[str, Any]:
    """
    Enhanced outcome prediction combining multiple AI approaches
    Uses local models + statistical analysis - no API costs!
    """
    try:
        logger.info(f"🔮 Predicting outcomes with enhanced AI models")
        
        result = await enhanced_ai_service.predict_outcome(request.case_data)
        
        # Filter results by confidence threshold
        if result.get("confidence", 0) < request.confidence_threshold:
            result["warning"] = f"Prediction confidence below threshold ({request.confidence_threshold})"
        
        return {
            "status": "success",
            "prediction": result,
            "cost": "free",
            "confidence_met": result.get("confidence", 0) >= request.confidence_threshold
        }
        
    except Exception as e:
        logger.error(f"❌ Outcome prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@enhanced_router.get("/model-status")
async def get_model_status() -> Dict[str, Any]:
    """
    Check status of available AI models (local vs API)
    """
    try:
        # Check which models are loaded locally
        local_models = list(enhanced_ai_service._model_cache.keys())
        
        return {
            "status": "healthy",
            "local_models_available": local_models,
            "local_models_count": len(local_models),
            "huggingface_api_available": bool(enhanced_ai_service.hf_api_key),
            "openai_api_available": bool(os.getenv("OPENAI_API_KEY")),
            "cost_status": {
                "local_inference": "free",
                "hf_api_calls": "low_cost",
                "openai_calls": "high_cost"
            },
            "recommendation": "Using local models for maximum cost efficiency"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _generate_risk_recommendations(risk_result: Dict[str, Any]) -> List[str]:
    """Generate specific recommendations based on risk assessment"""
    recommendations = []
    risk_level = risk_result.get("risk_level", "medium")
    factors = risk_result.get("factors", [])
    
    if risk_level == "high":
        recommendations.extend([
            "Consider specialist consultation before proceeding",
            "Ensure ICU availability post-procedure",
            "Review alternative treatment options",
            "Obtain additional patient consent for high-risk factors"
        ])
    elif risk_level == "medium":
        recommendations.extend([
            "Standard monitoring protocols recommended",
            "Prepare for potential complications",
            "Consider extended observation period"
        ])
    else:
        recommendations.append("Standard protocol appropriate")
    
    # Factor-specific recommendations
    if "advanced_age" in factors:
        recommendations.append("Consider geriatric-specific protocols")
    if "diabetes" in factors:
        recommendations.append("Monitor glucose levels closely")
    if "obesity" in factors:
        recommendations.append("Use appropriate positioning and equipment")
    
    return recommendations

# Export the enhanced router
__all__ = ["enhanced_router"]
