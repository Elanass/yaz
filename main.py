#!/usr/bin/env python3
"""
MVP Precision Decision Platform - Main Entry Point
"""

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
from core.config.platform_config import config
from features.decisions.precision_engine import PrecisionEngine
from features.decisions.adci_engine import ADCIEngine

app = FastAPI(title=config.api_title, version=config.api_version)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": config.api_version}

@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)):
    """Process uploaded CSV file and return precision engine insights"""
    df = pd.read_csv(file.file)
    engine = PrecisionEngine()
    records = df.to_dict(orient="records")
    insights = engine.analyze(records)
    return {"insights": insights}

@app.post("/predict/adci")
async def predict_adci(patient: dict):
    """Predict using the ADCI surgery decision engine for a single patient."""
    engine = ADCIEngine()
    if not engine.validate_input(patient):
        raise HTTPException(status_code=400, detail="Invalid patient data for ADCI engine")
    result = engine.predict(patient)
    return result

@app.post("/predict/precision")
async def predict_precision(patient: dict):
    """Predict impact analysis for a single patient."""
    engine = PrecisionEngine()
    insights = engine.analyze([patient])
    return insights[0]

if __name__ == "__main__":
    uvicorn.run(app, host=config.host, port=config.port, reload=config.debug)
