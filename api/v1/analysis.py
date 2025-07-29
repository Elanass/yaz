"""
Consolidated Analysis API
Endpoints for both prospective and retrospective statistical analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, UploadFile, File
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import logging

from features.analysis.analysis import AnalysisEngine
from features.auth.service import get_current_user, require_role, Domain, Scope
from core.utils.helpers import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["Analysis"])

# Initialize analysis engine
analysis_engine = AnalysisEngine()

@router.post("/prospective/random-forest")
async def run_random_forest(
    request: Request,
    file: UploadFile = File(...),
    outcome_column: str = Query(..., description="Outcome column to predict"),
    feature_columns: List[str] = Query(..., description="Feature columns to use for prediction"),
    current_user: dict = Depends(get_current_user)
):
    """
    Run Random Forest analysis on prospective data
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Prepare data for analysis
        features = df[feature_columns].to_dict(orient="records")
        labels = df[outcome_column].tolist()
        
        # Run analysis
        analysis_data = {
            "features": features,
            "labels": labels
        }
        
        results = analysis_engine.analyze(analysis_data, analysis_type="prospective")
        
        # Log action
        log_action(request, "random_forest_analysis", user_id=current_user.get('user_id', 'unknown'))
        
        return results
    except Exception as e:
        logger.error(f"Error in random forest analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/retrospective/cox")
async def run_cox_regression(
    request: Request,
    file: UploadFile = File(...),
    time_column: str = Query(..., description="Time-to-event column"),
    event_column: str = Query(..., description="Event indicator column (1=event, 0=censored)"),
    covariate_columns: List[str] = Query(..., description="Covariate columns for the model"),
    current_user: dict = Depends(get_current_user)
):
    """
    Run Cox Proportional Hazards regression on retrospective data
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Prepare data for analysis
        analysis_data = {
            "patient_id": df.index.tolist(),
            "time_to_event": df[time_column].tolist(),
            "outcome": df[event_column].tolist(),
            "features": {col: df[col].tolist() for col in covariate_columns}
        }
        
        results = analysis_engine.analyze(analysis_data, analysis_type="retrospective")
        
        # Log action
        log_action(request, "cox_regression_analysis", user_id=current_user.get('user_id', 'unknown'))
        
        return results
    except Exception as e:
        logger.error(f"Error in Cox regression analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/retrospective/logistic")
async def run_logistic_regression(
    request: Request,
    file: UploadFile = File(...),
    outcome_column: str = Query(..., description="Binary outcome column (0/1)"),
    feature_columns: List[str] = Query(..., description="Feature columns for the model"),
    current_user: dict = Depends(get_current_user)
):
    """
    Run Logistic Regression on retrospective data
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Prepare data for analysis
        analysis_data = {
            "patient_id": df.index.tolist(),
            "outcome": df[outcome_column].tolist(),
            "time_to_event": [0] * len(df),  # Not used for logistic regression
            "features": {col: df[col].tolist() for col in feature_columns}
        }
        
        results = analysis_engine.analyze(analysis_data, analysis_type="retrospective")
        
        # Extract only the logistic regression results
        if "logistic_regression" in results:
            results = {"logistic_regression": results["logistic_regression"]}
        
        # Log action
        log_action(request, "logistic_regression_analysis", user_id=current_user.get('user_id', 'unknown'))
        
        return results
    except Exception as e:
        logger.error(f"Error in logistic regression analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/impact-metrics")
async def analyze_impact_metrics(
    request: Request,
    data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze impact metrics for clinical outcomes
    """
    try:
        from features.analysis.impact_metrics import ImpactMetricsAnalyzer
        
        # Initialize the impact metrics analyzer
        impact_analyzer = ImpactMetricsAnalyzer()
        
        # Get patient data and procedure type
        patient_data = data.get("patient_data", {})
        procedure_type = data.get("procedure_type", "gastrectomy")
        
        # Run analysis
        results = impact_analyzer.analyze_surgical_outcomes(patient_data, procedure_type)
        
        # Log action
        log_action(request, "impact_metrics_analysis", user_id=current_user.get('user_id', 'unknown'))
        
        return results
    except Exception as e:
        logger.error(f"Error in impact metrics analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
