"""
Analysis API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any
from core.dependencies import get_current_user
from features.analysis.analysis import AnalysisEngine

router = APIRouter()
analysis_engine = AnalysisEngine()


class AnalysisRequest(BaseModel):
    data: Dict[str, Any]
    analysis_type: str = "prospective"


@router.post("/analyze")
async def analyze_data(
    request: AnalysisRequest,
    current_user=Depends(get_current_user)
):
    """Perform statistical analysis"""
    try:
        result = analysis_engine.analyze(request.data, request.analysis_type)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload data file for analysis"""
    return {"message": f"File {file.filename} uploaded successfully"}
