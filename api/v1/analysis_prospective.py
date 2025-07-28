"""
Prospective Analysis API
Endpoints for prospective statistical analysis (Random Forest, RL)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, UploadFile, File
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import logging

from features.analysis.prospective import ProspectiveAnalyzer
from features.analysis.prospective_analysis import ProspectiveAnalysis
from features.auth.service import get_current_user, require_role, Domain, Scope
from core.utils.helpers import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis/prospective", tags=["Analysis"])

# Initialize prospective analyzer
prospective_analyzer = ProspectiveAnalyzer()
prospective_analysis = ProspectiveAnalysis()

@router.post("/random-forest")
async def run_random_forest(
    request: Request,
    file: UploadFile = File(...),
    outcome_column: str = Query(..., description="Outcome column to predict"),
    feature_columns: List[str] = Query(..., description="Feature columns to use for prediction"),
    n_estimators: int = Query(100, description="Number of trees in the forest"),
    test_size: float = Query(0.2, description="Proportion of data to use for testing"),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Run Random Forest prediction on uploaded data
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Read uploaded file
        content = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(content))
        
        # Run Random Forest
        results = prospective_analyzer.run_random_forest(
            df=df,
            outcome_column=outcome_column,
            feature_columns=feature_columns,
            n_estimators=n_estimators,
            test_size=test_size
        )
        
        # Log action
        log_action(
            user_id=current_user.get("id", "unknown"),
            action="random_forest",
            resource="data_analysis",
            details={
                "file": file.filename,
                "outcome_column": outcome_column,
                "feature_columns": feature_columns,
                "n_estimators": n_estimators
            }
        )
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            from fastapi.responses import HTMLResponse
            
            # Create HTML for feature importance
            importance_html = ""
            for feature, importance in results["feature_importance"].items():
                importance_html += f"""
                <tr>
                    <td>{feature}</td>
                    <td>{importance:.4f}</td>
                </tr>
                """
            
            html_content = f"""
            <div id="random-forest-results" hx-swap-oob="true">
                <div class="card">
                    <div class="card-header">
                        <h3>Random Forest Results</h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Model Performance</h5>
                                <ul class="list-group">
                                    <li class="list-group-item">Accuracy: <strong>{results['metrics']['accuracy']:.4f}</strong></li>
                                    <li class="list-group-item">Precision: <strong>{results['metrics']['precision']:.4f}</strong></li>
                                    <li class="list-group-item">Recall: <strong>{results['metrics']['recall']:.4f}</strong></li>
                                    <li class="list-group-item">F1 Score: <strong>{results['metrics']['f1']:.4f}</strong></li>
                                </ul>
                            </div>
                            
                            <div class="col-md-6">
                                <h5>Feature Importance</h5>
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Feature</th>
                                            <th>Importance</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {importance_html}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <h5>Interpretation</h5>
                            <p>{results['interpretation']}</p>
                        </div>
                    </div>
                </div>
            </div>
            """
            return HTMLResponse(content=html_content)
        
        # Default: return JSON
        return results
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error in Random Forest analysis")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/predict")
async def predict_patient_outcome(
    request: Request,
    patient_data: Dict[str, Any],
    model_type: str = Query("random_forest", description="Model type to use (random_forest or reinforcement_learning)"),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Predict outcomes for a single patient using the specified model
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Run prediction
        results = prospective_analyzer.predict(
            patient_data=patient_data,
            model_type=model_type
        )
        
        # Log action
        log_action(
            user_id=current_user.get("id", "unknown"),
            action="predict_outcome",
            resource="patient_prediction",
            details={
                "model_type": model_type,
                "patient_id": patient_data.get("id", "unknown")
            }
        )
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            from fastapi.responses import HTMLResponse
            
            # Create HTML for prediction results
            prediction_html = f"""
            <div class="alert alert-{'success' if results['prediction'] == 1 else 'warning'}">
                <h4>Prediction: {results['prediction_label']}</h4>
                <p>Confidence: <strong>{results['confidence']:.2f}</strong></p>
            </div>
            """
            
            html_content = f"""
            <div id="prediction-results" hx-swap-oob="true">
                <div class="card">
                    <div class="card-header">
                        <h3>Patient Outcome Prediction</h3>
                    </div>
                    <div class="card-body">
                        {prediction_html}
                        
                        <div class="mt-4">
                            <h5>Explanation</h5>
                            <p>{results['explanation']}</p>
                        </div>
                        
                        <div class="mt-4">
                            <h5>Recommended Actions</h5>
                            <ul>
                                {''.join(f'<li>{action}</li>' for action in results['recommendations'])}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            """
            return HTMLResponse(content=html_content)
        
        # Default: return JSON
        return results
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error in patient prediction")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/analysis/prospective")
def analyze_prospective(data: dict):
    """
    API endpoint to perform prospective analysis.
    """
    if not prospective_analysis.validate_data(data):
        raise HTTPException(status_code=400, detail="Invalid input data")

    results = prospective_analysis.analyze(data)
    return results
