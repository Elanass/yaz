#!/usr/bin/env python3
"""
Application entry point moved to app package
"""

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
from core.config.platform_config import config
from features.decisions.precision_engine import PrecisionEngine
from features.decisions.adci_engine import ADCIEngine
from features.protocols.flot_analyzer import FLOTAnalyzer
from features.analysis.surgery_analyzer import IntegratedSurgeryAnalyzer
from api.v1.dashboard import router as dashboard_router
from api.v1.reports import router as reports_router
from api.v1.surgery import router as surgery_router

app = FastAPI(title=config.api_title, version=config.api_version)

# Include routers from api v1
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(surgery_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": config.api_version}

@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    engine = PrecisionEngine()
    records = df.to_dict(orient="records")
    insights = engine.analyze(records)
    return {"insights": insights}

@app.post("/predict/adci")
async def predict_adci(patient: dict):
    engine = ADCIEngine()
    if not engine.validate_input(patient):
        raise HTTPException(status_code=400, detail="Invalid patient data for ADCI engine")
    result = engine.predict(patient)
    return result

@app.post("/predict/flot")
async def predict_flot(patient: dict):
    """Predict FLOT chemotherapy protocol eligibility and recommendations."""
    analyzer = FLOTAnalyzer()
    if not analyzer.validate_input(patient):
        raise HTTPException(status_code=400, detail="Invalid patient data for FLOT protocol")
    result = analyzer.analyze_patient(patient)
    return result

@app.post("/predict/surgery")
async def predict_surgery(case_data: dict, surgery_type: str = None):
    """Comprehensive surgical case analysis with integrated analyzer."""
    try:
        # Use surgery_type from query parameter or from case_data
        surgery_type = surgery_type or case_data.get("surgery_type")
        
        if not surgery_type:
            raise HTTPException(status_code=400, detail="Surgery type must be specified")
        
        # Initialize integrated analyzer
        analyzer = IntegratedSurgeryAnalyzer()
        
        # Perform comprehensive analysis
        analysis_results = await analyzer.analyze_surgical_case(case_data, surgery_type)
        
        # Generate recommendations and impact metrics
        recommendations = await analyzer.generate_surgical_recommendations(analysis_results)
        impact_metrics = await analyzer.calculate_surgical_impact(case_data, analysis_results)
        
        return {
            "status": "success",
            "case_id": case_data.get("case_id"),
            "surgery_type": surgery_type,
            "analysis": analysis_results,
            "recommendations": recommendations,
            "impact_metrics": impact_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Surgery analysis failed: {str(e)}")

@app.post("/predict/precision")
async def predict_precision(patient: dict):
    engine = PrecisionEngine()
    insights = engine.analyze([patient])
    return insights[0]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=config.host, port=config.port, reload=config.debug)
