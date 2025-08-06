"""
Enhanced Data Ingestion API - Advanced CSV Processing Integration
Handles CSV uploads, manual entries, and multi-center domain management with intelligent analytics
"""

import asyncio
import csv
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form,
                     HTTPException, UploadFile)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from ...core.analytics.insight_generator import InsightGenerator
from ...core.csv_processor import CSVProcessor, ProcessingConfig
from ...core.database import get_db
from ...core.domain_adapter import get_domain_config
from ...core.models.database_models import CohortData, IngestionLog
from ...core.models.processing_models import DataDomain, ProcessingResult
from ...core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize processors
csv_processor = CSVProcessor()
insight_generator = InsightGenerator()


# Pydantic models
class ManualEntryData(BaseModel):
    patient_id: str
    age: int
    stage: str
    gender: Optional[str] = None
    histology: Optional[str] = None
    location: Optional[str] = None
    domain: str = "local"

    @validator("age")
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError("Age must be between 0 and 120")
        return v

    @validator("stage")
    def validate_stage(cls, v):
        valid_stages = ["IA", "IB", "II", "III", "IV"]
        if v not in valid_stages:
            raise ValueError(f"Stage must be one of: {valid_stages}")
        return v


class IngestionResponse(BaseModel):
    success: bool
    message: str
    upload_id: str
    processed_records: int
    errors: List[str] = []
    warnings: List[str] = []
    processing_result_id: Optional[
        str
    ] = None  # New field for linking to processing results
    quality_score: Optional[float] = None
    domain_detected: Optional[str] = None


class AdvancedIngestionResponse(BaseModel):
    """Enhanced response with processing insights"""

    success: bool
    message: str
    upload_id: str
    processing_result: Optional[ProcessingResult] = None
    insights_available: bool = False
    recommended_actions: List[str] = []

    class Config:
        arbitrary_types_allowed = True


class IngestionStatus(BaseModel):
    upload_id: str
    status: str  # uploading, processing, analyzing, completed, failed
    progress: int
    processed_records: int
    total_records: int
    errors: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    quality_metrics: Optional[Dict[str, float]] = None
    insights_ready: bool = False


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_data(
    background_tasks: BackgroundTasks,
    data: Optional[List[Dict[str, Any]]] = None,
    domain: str = "local",
    upload_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Ingest data from various sources (CSV upload or manual entry)
    Supports both local and multi-center domains
    """
    try:
        if not upload_id:
            upload_id = str(uuid.uuid4())

        logger.info(
            f"Starting data ingestion for upload_id: {upload_id}, domain: {domain}"
        )

        # Validate domain configuration
        domain_config = get_domain_config(domain)
        if not domain_config:
            raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")

        # Create ingestion log entry
        ingestion_log = IngestionLog(
            upload_id=upload_id,
            domain=domain,
            status="processing",
            started_at=datetime.utcnow(),
            total_records=len(data) if data else 0,
        )
        db.add(ingestion_log)
        db.commit()

        # Process data in background
        background_tasks.add_task(
            process_ingestion_data, data=data, domain=domain, upload_id=upload_id, db=db
        )

        return IngestionResponse(
            success=True,
            message="Data ingestion started successfully",
            upload_id=upload_id,
            processed_records=0,
        )

    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/upload-csv-advanced", response_model=AdvancedIngestionResponse)
async def upload_csv_advanced(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: Optional[str] = Form(None),  # Auto-detect if not provided
    enable_insights: bool = Form(True),
    stream_processing: bool = Form(False),
    db: Session = Depends(get_db),
):
    """
    Advanced CSV upload with intelligent processing, domain detection, and insight generation
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(
                status_code=400, detail="Only CSV and Excel files are supported"
            )

        # Generate upload ID
        upload_id = str(uuid.uuid4())
        logger.info(
            f"Advanced CSV processing started: {file.filename}, upload_id: {upload_id}"
        )

        # Read file content
        content = await file.read()

        # Validate file size
        max_size = 100 * 1024 * 1024  # 100MB
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File too large (max 100MB)")

        # Create ingestion log
        ingestion_log = IngestionLog(
            upload_id=upload_id,
            domain=domain or "auto-detect",
            filename=file.filename,
            status="processing",
            started_at=datetime.utcnow(),
            total_records=0,  # Will be updated during processing
        )
        db.add(ingestion_log)
        db.commit()

        # Configure processing
        config = ProcessingConfig(
            max_file_size_mb=100,
            streaming_threshold_rows=10000 if stream_processing else 50000,
            auto_detect_types=True,
            domain=DataDomain(domain) if domain and domain != "auto-detect" else None,
        )

        # Process CSV with advanced engine
        processing_result = await csv_processor.analyze_csv(
            file_content=content, domain=domain
        )

        # Update ingestion log with results
        ingestion_log.status = "analyzing"
        ingestion_log.total_records = (
            len(processing_result.data) if processing_result.data is not None else 0
        )
        ingestion_log.processed_records = processing_result.quality_report.valid_records
        db.commit()

        # Generate insights if requested
        insights = None
        if enable_insights:
            try:
                insights = await insight_generator.generate_comprehensive_insights(
                    processing_result
                )
                ingestion_log.status = "completed"
            except Exception as e:
                logger.warning(f"Insight generation failed: {str(e)}")
                ingestion_log.status = "completed_without_insights"
        else:
            ingestion_log.status = "completed"

        ingestion_log.completed_at = datetime.utcnow()
        db.commit()

        # Generate recommendations
        recommended_actions = []
        if processing_result.quality_report.overall_score < 0.7:
            recommended_actions.append("Review data quality - consider data cleaning")
        if len(processing_result.insights.recommendations) > 0:
            recommended_actions.extend(processing_result.insights.recommendations[:3])

        return AdvancedIngestionResponse(
            success=True,
            message=f"CSV processed successfully. Domain: {processing_result.schema.domain.value}, Quality: {processing_result.quality_report.overall_score:.1%}",
            upload_id=upload_id,
            processing_result=processing_result,
            insights_available=insights is not None,
            recommended_actions=recommended_actions,
        )

    except Exception as e:
        logger.error(f"Advanced CSV processing failed: {str(e)}")
        # Update ingestion log with error
        if "ingestion_log" in locals():
            ingestion_log.status = "failed"
            ingestion_log.error_message = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/upload-csv")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: str = Form("local"),
    db: Session = Depends(get_db),
):
    """
    Enhanced CSV upload with intelligent processing (backward compatible)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(
                status_code=400, detail="Only CSV and Excel files are supported"
            )

        # Generate upload ID
        upload_id = str(uuid.uuid4())
        logger.info(f"Processing CSV upload: {file.filename}, upload_id: {upload_id}")

        # Read file content
        content = await file.read()

        # Use advanced processor for better results
        processing_result = await csv_processor.analyze_csv(
            file_content=content, domain=domain if domain != "local" else None
        )

        # Create ingestion log with enhanced data
        ingestion_log = IngestionLog(
            upload_id=upload_id,
            domain=processing_result.schema.domain.value,
            filename=file.filename,
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_records=len(processing_result.data)
            if processing_result.data is not None
            else 0,
            processed_records=processing_result.quality_report.valid_records,
        )
        db.add(ingestion_log)
        db.commit()

        # Store processed data (simplified for backward compatibility)
        if processing_result.data is not None and len(processing_result.data) > 0:
            background_tasks.add_task(
                store_processed_data,
                data=processing_result.data.to_dict("records"),
                domain=processing_result.schema.domain.value,
                upload_id=upload_id,
                db=db,
            )

        return IngestionResponse(
            success=True,
            message="CSV processed successfully",
            upload_id=upload_id,
            processed_records=processing_result.quality_report.valid_records,
            warnings=[
                str(error.message) for error in processing_result.quality_report.errors
            ],
            quality_score=processing_result.quality_report.overall_score,
            domain_detected=processing_result.schema.domain.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/manual-entry", response_model=IngestionResponse)
async def add_manual_entry(
    entry_data: ManualEntryData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Add a single patient record via manual entry
    """
    try:
        upload_id = str(uuid.uuid4())

        logger.info(f"Processing manual entry for patient: {entry_data.patient_id}")

        # Convert to list format for consistent processing
        data = [entry_data.dict()]

        # Create ingestion log
        ingestion_log = IngestionLog(
            upload_id=upload_id,
            domain=entry_data.domain,
            status="processing",
            started_at=datetime.utcnow(),
            total_records=1,
            entry_method="manual",
        )
        db.add(ingestion_log)
        db.commit()

        # Process immediately for manual entries
        await process_ingestion_data(
            data=data, domain=entry_data.domain, upload_id=upload_id, db=db
        )

        return IngestionResponse(
            success=True,
            message="Manual entry processed successfully",
            upload_id=upload_id,
            processed_records=1,
        )

    except Exception as e:
        logger.error(f"Manual entry failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Manual entry failed: {str(e)}")


@router.get("/status/{upload_id}", response_model=IngestionStatus)
async def get_ingestion_status(upload_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a data ingestion process
    """
    try:
        ingestion_log = (
            db.query(IngestionLog).filter(IngestionLog.upload_id == upload_id).first()
        )

        if not ingestion_log:
            raise HTTPException(status_code=404, detail="Upload ID not found")

        return IngestionStatus(
            upload_id=ingestion_log.upload_id,
            status=ingestion_log.status,
            progress=ingestion_log.progress or 0,
            processed_records=ingestion_log.processed_records or 0,
            total_records=ingestion_log.total_records or 0,
            errors=json.loads(ingestion_log.errors) if ingestion_log.errors else [],
            started_at=ingestion_log.started_at,
            completed_at=ingestion_log.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status")


@router.get("/recent-uploads")
async def get_recent_uploads(
    limit: int = 10, domain: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    Get recent data ingestion uploads
    """
    try:
        query = db.query(IngestionLog).order_by(IngestionLog.started_at.desc())

        if domain:
            query = query.filter(IngestionLog.domain == domain)

        uploads = query.limit(limit).all()

        return [
            {
                "upload_id": log.upload_id,
                "domain": log.domain,
                "filename": log.filename,
                "status": log.status,
                "processed_records": log.processed_records,
                "total_records": log.total_records,
                "started_at": log.started_at,
                "completed_at": log.completed_at,
                "entry_method": log.entry_method,
            }
            for log in uploads
        ]

    except Exception as e:
        logger.error(f"Failed to get recent uploads: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve uploads")


@router.delete("/upload/{upload_id}")
async def delete_upload(upload_id: str, db: Session = Depends(get_db)):
    """
    Delete an ingestion upload and associated data
    """
    try:
        # Delete from ingestion log
        ingestion_log = (
            db.query(IngestionLog).filter(IngestionLog.upload_id == upload_id).first()
        )

        if not ingestion_log:
            raise HTTPException(status_code=404, detail="Upload ID not found")

        # Delete associated cohort data
        db.query(CohortData).filter(CohortData.upload_id == upload_id).delete()

        # Delete ingestion log
        db.delete(ingestion_log)
        db.commit()

        logger.info(f"Deleted upload: {upload_id}")

        return {"success": True, "message": "Upload deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete upload")


# Background processing functions
async def store_processed_data(
    data: List[Dict], domain: str, upload_id: str, db: Session
):
    """
    Background task to store processed data from advanced CSV processing
    """
    try:
        logger.info(f"Storing processed data for upload_id: {upload_id}")

        stored_count = 0
        errors = []

        for record in data:
            try:
                # Create cohort data record
                cohort_record = CohortData(
                    upload_id=upload_id,
                    domain=domain,
                    patient_id=record.get("patient_id", f"auto_{uuid.uuid4().hex[:8]}"),
                    data=json.dumps(record),
                    created_at=datetime.utcnow(),
                )

                db.add(cohort_record)
                stored_count += 1

            except Exception as e:
                errors.append(f"Error storing record: {str(e)}")
                continue

        db.commit()
        logger.info(f"Stored {stored_count} records for upload_id: {upload_id}")

    except Exception as e:
        logger.error(f"Error storing processed data for {upload_id}: {str(e)}")


async def process_ingestion_data(
    data: List[Dict], domain: str, upload_id: str, db: Session
):
    """
    Background task to process ingested data
    """
    try:
        logger.info(f"Starting background processing for upload_id: {upload_id}")

        errors = []
        processed_count = 0

        # Update status to processing
        update_ingestion_status(db, upload_id, "analyzing", 25)

        for i, record in enumerate(data):
            try:
                # Validate and clean record
                cleaned_record = validate_and_clean_record(record, domain)

                # Create cohort data entry
                cohort_data = CohortData(
                    upload_id=upload_id,
                    patient_id=cleaned_record.get("patient_id"),
                    age=cleaned_record.get("age"),
                    stage=cleaned_record.get("stage"),
                    gender=cleaned_record.get("gender"),
                    histology=cleaned_record.get("histology"),
                    location=cleaned_record.get("location"),
                    domain=domain,
                    created_at=datetime.utcnow(),
                )

                db.add(cohort_data)
                processed_count += 1

                # Update progress
                progress = int((i + 1) / len(data) * 75) + 25  # 25-100%
                if i % 10 == 0:  # Update every 10 records
                    update_ingestion_status(
                        db, upload_id, "processing", progress, processed_count
                    )

            except Exception as e:
                error_msg = f"Record {i + 1}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"Failed to process record {i + 1}: {str(e)}")

        # Commit all changes
        db.commit()

        # Final status update
        final_status = "completed" if not errors else "completed_with_errors"
        update_ingestion_status(
            db,
            upload_id,
            final_status,
            100,
            processed_count,
            errors=errors,
            completed_at=datetime.utcnow(),
        )

        logger.info(
            f"Completed processing upload_id: {upload_id}, processed: {processed_count}, errors: {len(errors)}"
        )

    except Exception as e:
        logger.error(
            f"Background processing failed for upload_id {upload_id}: {str(e)}"
        )
        update_ingestion_status(db, upload_id, "failed", 0, 0, errors=[str(e)])


def validate_and_clean_record(record: Dict, domain: str) -> Dict:
    """
    Validate and clean a single data record
    """
    # Required fields validation
    required_fields = ["patient_id", "age", "stage"]
    for field in required_fields:
        if field not in record or record[field] is None:
            raise ValueError(f"Missing required field: {field}")

    # Age validation
    age = int(record["age"])
    if age < 0 or age > 120:
        raise ValueError(f"Invalid age: {age}")

    # Stage validation
    valid_stages = ["IA", "IB", "II", "III", "IV"]
    stage = str(record["stage"]).upper()
    if stage not in valid_stages:
        raise ValueError(f"Invalid stage: {stage}")

    # Clean and return record
    cleaned = {
        "patient_id": str(record["patient_id"]).strip(),
        "age": age,
        "stage": stage,
        "gender": record.get("gender", "").strip() if record.get("gender") else None,
        "histology": record.get("histology", "").strip()
        if record.get("histology")
        else None,
        "location": record.get("location", "").strip()
        if record.get("location")
        else None,
    }

    return cleaned


def update_ingestion_status(
    db: Session,
    upload_id: str,
    status: str,
    progress: int,
    processed_records: int = 0,
    errors: List[str] = None,
    completed_at: datetime = None,
):
    """
    Update ingestion status in database
    """
    try:
        ingestion_log = (
            db.query(IngestionLog).filter(IngestionLog.upload_id == upload_id).first()
        )

        if ingestion_log:
            ingestion_log.status = status
            ingestion_log.progress = progress
            ingestion_log.processed_records = processed_records

            if errors:
                ingestion_log.errors = json.dumps(errors)

            if completed_at:
                ingestion_log.completed_at = completed_at

            db.commit()

    except Exception as e:
        logger.error(f"Failed to update ingestion status: {str(e)}")
        db.rollback()
