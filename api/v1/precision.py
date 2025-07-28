"""
Precision API
Endpoints for precision decision engine
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, Optional

from features.decisions.precision_engine import PrecisionEngine
from features.auth.service import get_current_user, require_role, Domain, Scope

router = APIRouter(prefix="/precision", tags=["Precision"])

# Initialize precision engine
precision_engine = PrecisionEngine()

@router.post("/predict")
async def predict_outcomes(
    request: Request,
    patient_data: Dict[str, Any],
    steps: Optional[int] = 5,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Predict outcomes for a patient using precision decision engine
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Validate patient data
        required_fields = ["age", "gender", "tumor_stage", "tumor_location"]
        for field in required_fields:
            if field not in patient_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Make prediction
        results = precision_engine.predict_outcomes(patient_data, steps)
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            from fastapi.responses import HTMLResponse
            html_content = f"""
            <div id="precision-results" hx-swap-oob="true">
                <div class="card">
                    <div class="card-header">
                        <h3>Precision Decision Results</h3>
                    </div>
                    <div class="card-body">
                        <h4>Recommendation: {results["recommendation"]["treatment"]}</h4>
                        <p>Confidence: {results["recommendation"]["confidence"]:.2f}</p>
                        <p>{results["recommendation"]["explanation"]}</p>
                        
                        <h5>Surgery Impact</h5>
                        <p>Risk Level: {results["impact_analysis"]["surgery"]["risk_level"]}</p>
                        <p>Risk Score: {results["impact_analysis"]["surgery"]["adjusted_risk"]:.2f}</p>
                        
                        <h5>FLOT Impact</h5>
                        <p>Risk Level: {results["impact_analysis"]["flot"]["risk_level"]}</p>
                        <p>Risk Score: {results["impact_analysis"]["flot"]["adjusted_risk"]:.2f}</p>
                    </div>
                </div>
            </div>
            """
            return HTMLResponse(content=html_content)
        
        # Default: return JSON
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
