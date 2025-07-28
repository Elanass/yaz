"""
Retrospective Analysis API
Endpoints for retrospective statistical analysis (Cox & Logistic Regression)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, UploadFile, File
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import logging

from features.analysis.retrospective import RetrospectiveAnalyzer
from features.analysis.retrospective_analysis import RetrospectiveAnalysis
from features.auth.service import get_current_user, require_role, Domain, Scope
from core.utils.helpers import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis/retrospective", tags=["Analysis"])

# Initialize retrospective analyzer
retrospective_analyzer = RetrospectiveAnalyzer()
retrospective_analysis = RetrospectiveAnalysis()

@router.post("/cox")
async def run_cox_regression(
    request: Request,
    file: UploadFile = File(...),
    time_column: str = Query(..., description="Time-to-event column"),
    event_column: str = Query(..., description="Event indicator column (1=event, 0=censored)"),
    covariates: List[str] = Query(..., description="Covariates to include in the model"),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Run Cox Proportional Hazards regression on uploaded data
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Read uploaded file
        content = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(content))
        
        # Run Cox regression
        results = retrospective_analyzer.run_cox_regression(
            df=df,
            time_column=time_column,
            event_column=event_column,
            covariates=covariates
        )
        
        # Log action
        log_action(
            user_id=current_user.get("id", "unknown"),
            action="cox_regression",
            resource="data_analysis",
            details={
                "file": file.filename,
                "time_column": time_column,
                "event_column": event_column,
                "covariates": covariates
            }
        )
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            from fastapi.responses import HTMLResponse
            
            # Create HTML table for coefficients
            coef_html = ""
            for var, values in results["summary"].items():
                coef_html += f"""
                <tr>
                    <td>{var}</td>
                    <td>{values['coef']:.4f}</td>
                    <td>{values['exp(coef)']:.4f}</td>
                    <td>{values['p']:.4f}</td>
                    <td>{values['lower 0.95']:.4f} - {values['upper 0.95']:.4f}</td>
                </tr>
                """
            
            html_content = f"""
            <div id="cox-results" hx-swap-oob="true">
                <div class="card">
                    <div class="card-header">
                        <h3>Cox Regression Results</h3>
                    </div>
                    <div class="card-body">
                        <p>Model Fit: <strong>Concordance: {results['concordance']:.4f}</strong></p>
                        <p>Log-Likelihood Ratio Test: <strong>p = {results['log_likelihood_test']['p']:.4f}</strong></p>
                        
                        <h5>Coefficients</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Variable</th>
                                    <th>Coefficient</th>
                                    <th>Hazard Ratio</th>
                                    <th>p-value</th>
                                    <th>95% CI</th>
                                </tr>
                            </thead>
                            <tbody>
                                {coef_html}
                            </tbody>
                        </table>
                        
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
        logger.exception("Error in Cox regression")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/logistic")
async def run_logistic_regression(
    request: Request,
    file: UploadFile = File(...),
    outcome_column: str = Query(..., description="Binary outcome column (1=event, 0=non-event)"),
    covariates: List[str] = Query(..., description="Covariates to include in the model"),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Run Logistic regression on uploaded data
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Read uploaded file
        content = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(content))
        
        # Run Logistic regression
        results = retrospective_analyzer.run_logistic_regression(
            df=df,
            outcome_column=outcome_column,
            covariates=covariates
        )
        
        # Log action
        log_action(
            user_id=current_user.get("id", "unknown"),
            action="logistic_regression",
            resource="data_analysis",
            details={
                "file": file.filename,
                "outcome_column": outcome_column,
                "covariates": covariates
            }
        )
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            from fastapi.responses import HTMLResponse
            
            # Create HTML table for coefficients
            coef_html = ""
            for var, values in results["summary"].items():
                coef_html += f"""
                <tr>
                    <td>{var}</td>
                    <td>{values['coef']:.4f}</td>
                    <td>{values['odds_ratio']:.4f}</td>
                    <td>{values['p']:.4f}</td>
                    <td>{values['95% CI'][0]:.4f} - {values['95% CI'][1]:.4f}</td>
                </tr>
                """
            
            html_content = f"""
            <div id="logistic-results" hx-swap-oob="true">
                <div class="card">
                    <div class="card-header">
                        <h3>Logistic Regression Results</h3>
                    </div>
                    <div class="card-body">
                        <p>Model Fit: <strong>AUC: {results['auc']:.4f}</strong></p>
                        <p>Model Accuracy: <strong>{results['accuracy']:.4f}</strong></p>
                        
                        <h5>Coefficients</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Variable</th>
                                    <th>Coefficient</th>
                                    <th>Odds Ratio</th>
                                    <th>p-value</th>
                                    <th>95% CI</th>
                                </tr>
                            </thead>
                            <tbody>
                                {coef_html}
                            </tbody>
                        </table>
                        
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
        logger.exception("Error in Logistic regression")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analysis/retrospective")
def analyze_retrospective(data: dict):
    """
    API endpoint to perform retrospective analysis.
    """
    if not retrospective_analysis.validate_data(data):
        raise HTTPException(status_code=400, detail="Invalid input data")

    results = retrospective_analysis.analyze(data)
    return results
