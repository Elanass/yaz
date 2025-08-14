"""
CSV Processing API endpoint for Surge platform.
Handles file uploads, processing, and result generation.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..core.csv_processor import CSVProcessor, ProcessingConfig
from ..core.models.processing_models import DataDomain

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/csv", tags=["csv-processing"])

# Initialize processor
processor = CSVProcessor(ProcessingConfig(
    max_file_size_mb=100,
    streaming_threshold_rows=10000,
    validation_sample_size=1000,
    auto_detect_types=True
))

@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    domain: Optional[str] = Form(None)
):
    """
    Analyze uploaded CSV file and return processing results.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )
        
        # Check file size (approximate)
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > processor.config.max_file_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {processor.config.max_file_size_mb}MB"
            )
        
        # Process the file
        logger.info(f"Processing CSV file: {file.filename} ({file_size_mb:.2f}MB)")
        
        result = await processor.analyze_csv(
            file_content=content,
            domain=domain
        )
        
        # Convert result to dict for JSON response
        response_data = {
            "schema": {
                "fields": [
                    {
                        "name": field.name,
                        "type": field.type.value,
                        "nullable": field.nullable,
                        "description": field.description
                    }
                    for field in result.schema.fields
                ],
                "domain": result.schema.domain.value,
                "confidence": result.schema.confidence
            },
            "quality_report": {
                "total_rows": result.quality_report.total_rows,
                "valid_rows": result.quality_report.valid_rows,
                "issues": [
                    {
                        "type": issue.type,
                        "message": issue.message,
                        "count": issue.count
                    }
                    for issue in result.quality_report.issues
                ]
            },
            "insights": {
                "summary": result.insights.summary,
                "patterns": [
                    {
                        "type": pattern.type,
                        "description": pattern.description,
                        "confidence": pattern.confidence
                    }
                    for pattern in result.insights.patterns
                ]
            },
            "processing_metadata": {
                "original_rows": result.processing_metadata["original_rows"],
                "processed_rows": result.processing_metadata["processed_rows"],
                "processing_time": result.processing_metadata["processing_time"].isoformat(),
                "domain": result.processing_metadata["domain"],
                "filename": file.filename,
                "file_size_mb": round(file_size_mb, 2)
            }
        }
        
        logger.info(f"Successfully processed {file.filename}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing CSV file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@router.get("/sample-datasets")
async def get_sample_datasets():
    """
    Get list of available sample datasets for demonstration.
    """
    try:
        # Path to sample datasets
        samples_path = Path(__file__).parent.parent.parent / "data" / "test_samples"
        
        if not samples_path.exists():
            return JSONResponse(content={"datasets": []})
        
        datasets = []
        for csv_file in samples_path.glob("*.csv"):
            try:
                # Read first few lines to get basic info
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                
                datasets.append({
                    "name": csv_file.stem.replace('_', ' ').title(),
                    "filename": csv_file.name,
                    "path": str(csv_file),
                    "rows": len(lines) - 1,  # Subtract header
                    "columns": len(lines[0].split(',')) if lines else 0,
                    "size_kb": round(csv_file.stat().st_size / 1024, 2),
                    "description": _get_dataset_description(csv_file.stem)
                })
            except Exception as e:
                logger.warning(f"Could not read sample dataset {csv_file}: {e}")
                continue
        
        return JSONResponse(content={"datasets": datasets})
        
    except Exception as e:
        logger.error(f"Error fetching sample datasets: {str(e)}")
        return JSONResponse(content={"datasets": []})

@router.post("/analyze-sample/{filename}")
async def analyze_sample_dataset(filename: str):
    """
    Analyze a sample dataset by filename.
    """
    try:
        samples_path = Path(__file__).parent.parent.parent / "data" / "test_samples"
        sample_file = samples_path / filename
        
        if not sample_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Sample dataset '{filename}' not found"
            )
        
        # Process the sample file
        result = await processor.analyze_csv(file_path=str(sample_file))
        
        # Convert result to dict (same as analyze_csv endpoint)
        response_data = {
            "schema": {
                "fields": [
                    {
                        "name": field.name,
                        "type": field.type.value,
                        "nullable": field.nullable,
                        "description": field.description
                    }
                    for field in result.schema.fields
                ],
                "domain": result.schema.domain.value,
                "confidence": result.schema.confidence
            },
            "quality_report": {
                "total_rows": result.quality_report.total_rows,
                "valid_rows": result.quality_report.valid_rows,
                "issues": [
                    {
                        "type": issue.type,
                        "message": issue.message,
                        "count": issue.count
                    }
                    for issue in result.quality_report.issues
                ]
            },
            "insights": {
                "summary": result.insights.summary,
                "patterns": [
                    {
                        "type": pattern.type,
                        "description": pattern.description,
                        "confidence": pattern.confidence
                    }
                    for pattern in result.insights.patterns
                ]
            },
            "processing_metadata": {
                "original_rows": result.processing_metadata["original_rows"],
                "processed_rows": result.processing_metadata["processed_rows"],
                "processing_time": result.processing_metadata["processing_time"].isoformat(),
                "domain": result.processing_metadata["domain"],
                "filename": filename,
                "file_size_mb": round(sample_file.stat().st_size / (1024 * 1024), 2)
            }
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing sample dataset {filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

def _get_dataset_description(filename_stem: str) -> str:
    """Get description for sample datasets."""
    descriptions = {
        "sample_gastric_cohort": "Gastric cancer patient cohort with surgical outcomes and survival data",
        "enhanced_srcc_surgical": "Enhanced signet ring cell carcinoma surgical cases with detailed staging",
        "sample_cell_entities": "Cellular entity classification data for pathology analysis",
        "sample_gastric_systems": "Gastric system analysis with treatment protocols",
        "sample_tumor_units": "Tumor unit measurements and classification data"
    }
    return descriptions.get(filename_stem, "Sample clinical dataset for analysis")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for CSV processing service."""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "processor_config": {
            "max_file_size_mb": processor.config.max_file_size_mb,
            "streaming_threshold_rows": processor.config.streaming_threshold_rows,
            "auto_detect_types": processor.config.auto_detect_types
        }
    })
