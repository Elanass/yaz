"""
Enhanced Data Ingestion API - Advanced CSV Processing Integration
Handles CSV uploads, manual entries, and multi-center domain management with intelligent analytics
"""

import asyncio
import base64
import csv
import io
import json
import os
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
from ...core.models.database_models import (CohortData, IngestionLog,
                                            MediaFile, TextEntry)
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
    notes: Optional[str] = None
    clinical_findings: Optional[str] = None

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


class MediaUploadData(BaseModel):
    patient_id: str
    case_id: Optional[str] = None
    media_type: str  # image, video, audio, document
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator("media_type")
    def validate_media_type(cls, v):
        valid_types = ["image", "video", "audio", "document"]
        if v not in valid_types:
            raise ValueError(f"Media type must be one of: {valid_types}")
        return v


class TextEntryData(BaseModel):
    patient_id: str
    case_id: Optional[str] = None
    entry_type: str  # note, observation, diagnosis, treatment_plan
    title: str
    content: str
    timestamp: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator("entry_type")
    def validate_entry_type(cls, v):
        valid_types = [
            "note",
            "observation",
            "diagnosis",
            "treatment_plan",
            "follow_up",
        ]
        if v not in valid_types:
            raise ValueError(f"Entry type must be one of: {valid_types}")
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


class MediaUploadResponse(BaseModel):
    success: bool
    message: str
    media_id: str
    file_path: str
    metadata: Dict[str, Any]


class TextEntryResponse(BaseModel):
    success: bool
    message: str
    entry_id: str
    timestamp: datetime


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


# New Manual Entry Endpoints


@router.post("/manual-entry/text", response_model=TextEntryResponse)
async def add_text_entry(
    entry_data: TextEntryData,
    db: Session = Depends(get_db),
):
    """
    Add a manual text entry (note, observation, diagnosis, etc.)
    """
    try:
        entry_id = str(uuid.uuid4())
        timestamp = entry_data.timestamp or datetime.utcnow()

        # Create text entry in database
        text_entry = TextEntry(
            id=entry_id,
            patient_id=entry_data.patient_id,
            case_id=entry_data.case_id,
            entry_type=entry_data.entry_type,
            title=entry_data.title,
            content=entry_data.content,
            tags=json.dumps(entry_data.tags or []),
            metadata=json.dumps(entry_data.metadata or {}),
            created_at=timestamp,
        )

        db.add(text_entry)
        db.commit()

        logger.info(
            f"Text entry created: {entry_id} for patient {entry_data.patient_id}"
        )

        return TextEntryResponse(
            success=True,
            message="Text entry added successfully",
            entry_id=entry_id,
            timestamp=timestamp,
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Text entry failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text entry failed: {str(e)}")


@router.post("/manual-entry/media", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    media_type: str = Form(...),
    title: str = Form(...),
    case_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags array
    db: Session = Depends(get_db),
):
    """
    Upload media files (images, video, audio, documents)
    """
    try:
        # Validate media type
        valid_types = ["image", "video", "audio", "document"]
        if media_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid media type. Must be one of: {valid_types}",
            )

        # Validate file type based on media type
        file_ext = file.filename.lower().split(".")[-1] if file.filename else ""

        type_extensions = {
            "image": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
            "video": ["mp4", "avi", "mov", "wmv", "flv", "webm", "mkv"],
            "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"],
            "document": ["pdf", "doc", "docx", "txt", "rtf"],
        }

        if file_ext not in type_extensions.get(media_type, []):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file_ext}' for media type '{media_type}'",
            )

        # Generate unique filename
        media_id = str(uuid.uuid4())
        safe_filename = f"{media_id}_{file.filename}"

        # Create upload directory if it doesn't exist
        upload_dir = Path("data/uploads/media")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = upload_dir / safe_filename
        content = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Parse tags if provided
        parsed_tags = []
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = [tag.strip() for tag in tags.split(",")]

        # Extract metadata
        metadata = {
            "original_filename": file.filename,
            "file_size": len(content),
            "upload_timestamp": datetime.utcnow().isoformat(),
            "content_type": file.content_type,
            "file_extension": file_ext,
        }

        # Additional metadata based on media type
        if media_type == "image":
            # TODO: Extract image dimensions, EXIF data, etc.
            metadata.update(
                {
                    "media_type": "image",
                    "dimensions": "unknown",  # Would extract actual dimensions
                    "color_space": "unknown",
                }
            )
        elif media_type == "video":
            # TODO: Extract video duration, resolution, codec, etc.
            metadata.update(
                {
                    "media_type": "video",
                    "duration": "unknown",
                    "resolution": "unknown",
                    "codec": "unknown",
                }
            )
        elif media_type == "audio":
            # TODO: Extract audio duration, bitrate, format, etc.
            metadata.update(
                {
                    "media_type": "audio",
                    "duration": "unknown",
                    "bitrate": "unknown",
                    "sample_rate": "unknown",
                }
            )

        # Store media record in database
        media_record = MediaFile(
            id=media_id,
            patient_id=patient_id,
            case_id=case_id,
            media_type=media_type,
            title=title,
            description=description,
            file_path=str(file_path),
            original_filename=file.filename,
            file_size=len(content),
            content_type=file.content_type,
            tags=json.dumps(parsed_tags),
            metadata=json.dumps(metadata),
            created_at=datetime.utcnow(),
        )

        db.add(media_record)
        db.commit()

        logger.info(
            f"Media uploaded: {media_id} - {media_type} for patient {patient_id}"
        )

        return MediaUploadResponse(
            success=True,
            message=f"{media_type.capitalize()} uploaded successfully",
            media_id=media_id,
            file_path=str(file_path),
            metadata=metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Media upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Media upload failed: {str(e)}")


@router.get("/manual-entry/text/{patient_id}")
async def get_text_entries(
    patient_id: str,
    entry_type: Optional[str] = None,
    case_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get text entries for a patient
    """
    try:
        # Build query
        query = db.query(TextEntry).filter(TextEntry.patient_id == patient_id)

        if entry_type:
            query = query.filter(TextEntry.entry_type == entry_type)
        if case_id:
            query = query.filter(TextEntry.case_id == case_id)

        # Get entries with limit
        entries = query.order_by(TextEntry.created_at.desc()).limit(limit).all()

        # Convert to dict format
        entries_data = []
        for entry in entries:
            entry_dict = {
                "id": entry.id,
                "patient_id": entry.patient_id,
                "case_id": entry.case_id,
                "entry_type": entry.entry_type,
                "title": entry.title,
                "content": entry.content,
                "tags": json.loads(entry.tags) if entry.tags else [],
                "metadata": json.loads(entry.metadata) if entry.metadata else {},
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
            }
            entries_data.append(entry_dict)

        return {
            "success": True,
            "patient_id": patient_id,
            "entries": entries_data,
            "total": len(entries_data),
        }

    except Exception as e:
        logger.error(f"Failed to get text entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve text entries")


@router.get("/manual-entry/media/{patient_id}")
async def get_media_files(
    patient_id: str,
    media_type: Optional[str] = None,
    case_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get media files for a patient
    """
    try:
        # Build query
        query = db.query(MediaFile).filter(MediaFile.patient_id == patient_id)

        if media_type:
            query = query.filter(MediaFile.media_type == media_type)
        if case_id:
            query = query.filter(MediaFile.case_id == case_id)

        # Get media files with limit
        media_files = query.order_by(MediaFile.created_at.desc()).limit(limit).all()

        # Convert to dict format
        media_data = []
        for media in media_files:
            media_dict = {
                "id": media.id,
                "patient_id": media.patient_id,
                "case_id": media.case_id,
                "media_type": media.media_type,
                "title": media.title,
                "description": media.description,
                "file_path": media.file_path,
                "original_filename": media.original_filename,
                "file_size": media.file_size,
                "content_type": media.content_type,
                "tags": json.loads(media.tags) if media.tags else [],
                "metadata": json.loads(media.metadata) if media.metadata else {},
                "created_at": media.created_at,
                "updated_at": media.updated_at,
            }
            media_data.append(media_dict)

        return {
            "success": True,
            "patient_id": patient_id,
            "media_files": media_data,
            "total": len(media_data),
        }

    except Exception as e:
        logger.error(f"Failed to get media files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve media files")


@router.delete("/manual-entry/text/{entry_id}")
async def delete_text_entry(
    entry_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a text entry
    """
    try:
        # Find and delete text entry
        text_entry = db.query(TextEntry).filter(TextEntry.id == entry_id).first()

        if not text_entry:
            raise HTTPException(status_code=404, detail="Text entry not found")

        db.delete(text_entry)
        db.commit()

        logger.info(f"Text entry deleted: {entry_id}")

        return {"success": True, "message": "Text entry deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete text entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete text entry")


@router.delete("/manual-entry/media/{media_id}")
async def delete_media_file(
    media_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a media file
    """
    try:
        # Find media file
        media_file = db.query(MediaFile).filter(MediaFile.id == media_id).first()

        if not media_file:
            raise HTTPException(status_code=404, detail="Media file not found")

        # Delete file from filesystem
        try:
            if os.path.exists(media_file.file_path):
                os.remove(media_file.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file {media_file.file_path}: {str(e)}")

        # Delete from database
        db.delete(media_file)
        db.commit()

        logger.info(f"Media file deleted: {media_id}")

        return {"success": True, "message": "Media file deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete media file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete media file")


# Domain-Specific Text and Image Processing Endpoints

@router.post("/domains/{domain}/process-text", response_model=TextEntryResponse)
async def process_domain_text(
    domain: str,
    text_content: str = Form(...),
    patient_id: str = Form(...),
    case_id: Optional[str] = Form(None),
    title: str = Form(...),
    content_type: str = Form("clinical_note"),
    metadata: Optional[str] = Form(None),  # JSON string
    db: Session = Depends(get_db),
):
    """
    Process text data for a specific domain (surgery, logistics, insurance)
    with domain-appropriate parsing and analysis
    """
    try:
        # Validate domain
        valid_domains = ["surgery", "logistics", "insurance", "general"]
        if domain not in valid_domains:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain. Must be one of: {valid_domains}"
            )

        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"Invalid metadata JSON, ignoring: {metadata}")

        # Process text with domain-specific parser
        from ...core.parsers import get_parser_for_domain
        parser = get_parser_for_domain(domain)
        parsing_result = parser.parse(text_content)

        # Create enhanced metadata combining input and parsing results
        enhanced_metadata = {
            **parsed_metadata,
            "domain": domain,
            "parsing_result": parsing_result,
            "content_type": content_type,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "word_count": len(text_content.split()),
            "character_count": len(text_content),
        }

        # Generate entry ID and store in database
        entry_id = str(uuid.uuid4())
        
        text_entry = TextEntry(
            id=entry_id,
            patient_id=patient_id,
            case_id=case_id,
            entry_type=f"{domain}_{content_type}",
            title=title,
            content=text_content,
            tags=json.dumps([domain, content_type]),
            metadata=json.dumps(enhanced_metadata),
            created_at=datetime.utcnow(),
        )

        db.add(text_entry)
        db.commit()

        logger.info(f"Domain text processed: {entry_id} for {domain} domain, patient {patient_id}")

        return TextEntryResponse(
            success=True,
            message=f"Text processed successfully for {domain} domain",
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Domain text processing failed for {domain}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Text processing failed for {domain}: {str(e)}"
        )


@router.post("/domains/{domain}/process-images", response_model=MediaUploadResponse)
async def process_domain_images(
    domain: str,
    files: List[UploadFile] = File(...),
    patient_id: str = Form(...),
    case_id: Optional[str] = Form(None),
    image_category: str = Form("general"),
    description: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),  # JSON string
    db: Session = Depends(get_db),
):
    """
    Process multiple image files for a specific domain with domain-appropriate
    categorization and analysis
    """
    try:
        # Validate domain
        valid_domains = ["surgery", "logistics", "insurance", "general"]
        if domain not in valid_domains:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain. Must be one of: {valid_domains}"
            )

        # Validate file types
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.pdf', '.dcm']
        
        processed_files = []
        
        for file in files:
            file_ext = file.filename.lower().split('.')[-1] if file.filename else ''
            if f'.{file_ext}' not in valid_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type '{file_ext}'. Supported: {valid_extensions}"
                )

            # Generate unique filename
            media_id = str(uuid.uuid4())
            safe_filename = f"{domain}_{media_id}_{file.filename}"

            # Create domain-specific upload directory
            upload_dir = Path(f"data/uploads/media/{domain}")
            upload_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            file_path = upload_dir / safe_filename
            content = await file.read()

            with open(file_path, "wb") as buffer:
                buffer.write(content)

            # Parse metadata if provided
            parsed_metadata = {}
            if metadata:
                try:
                    parsed_metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid metadata JSON, ignoring: {metadata}")

            # Process images with domain-specific parser
            from ...core.parsers import get_parser_for_domain
            parser = get_parser_for_domain(domain)
            parsing_result = parser.parse([str(file_path)])  # Pass as list for image parsing

            # Create enhanced metadata
            enhanced_metadata = {
                **parsed_metadata,
                "domain": domain,
                "image_category": image_category,
                "parsing_result": parsing_result,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "original_filename": file.filename,
                "file_size": len(content),
                "content_type": file.content_type,
                "file_extension": file_ext,
            }

            # Domain-specific image categorization
            domain_specific_type = f"{domain}_{image_category}"
            if domain == "surgery":
                if "ct" in file.filename.lower() or "scan" in file.filename.lower():
                    domain_specific_type = "surgery_ct_scan"
                elif "mri" in file.filename.lower():
                    domain_specific_type = "surgery_mri"
                elif "pathology" in file.filename.lower():
                    domain_specific_type = "surgery_pathology"
            elif domain == "logistics":
                if "product" in file.filename.lower():
                    domain_specific_type = "logistics_product"
                elif "shipment" in file.filename.lower():
                    domain_specific_type = "logistics_shipment"
                elif "damage" in file.filename.lower():
                    domain_specific_type = "logistics_damage"
            elif domain == "insurance":
                if "incident" in file.filename.lower():
                    domain_specific_type = "insurance_incident"
                elif "damage" in file.filename.lower():
                    domain_specific_type = "insurance_damage"
                elif "medical" in file.filename.lower():
                    domain_specific_type = "insurance_medical"

            # Store media record in database
            media_record = MediaFile(
                id=media_id,
                patient_id=patient_id,
                case_id=case_id,
                media_type=domain_specific_type,
                title=f"{domain.title()} {image_category} - {file.filename}",
                description=description or f"Processed image for {domain} domain",
                file_path=str(file_path),
                original_filename=file.filename,
                file_size=len(content),
                content_type=file.content_type,
                tags=json.dumps([domain, image_category, domain_specific_type]),
                metadata=json.dumps(enhanced_metadata),
                created_at=datetime.utcnow(),
            )

            db.add(media_record)
            processed_files.append({
                "media_id": media_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "type": domain_specific_type,
                "metadata": enhanced_metadata
            })

        db.commit()

        logger.info(f"Domain images processed: {len(processed_files)} files for {domain} domain, patient {patient_id}")

        return MediaUploadResponse(
            success=True,
            message=f"{len(processed_files)} images processed successfully for {domain} domain",
            media_id=processed_files[0]["media_id"] if processed_files else "",
            file_path=processed_files[0]["file_path"] if processed_files else "",
            metadata={"processed_files": processed_files, "total_count": len(processed_files)},
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Domain image processing failed for {domain}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed for {domain}: {str(e)}"
        )


@router.get("/domains/{domain}/text/{patient_id}")
async def get_domain_text_entries(
    domain: str,
    patient_id: str,
    case_id: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get text entries for a patient within a specific domain
    """
    try:
        # Validate domain
        valid_domains = ["surgery", "logistics", "insurance", "general"]
        if domain not in valid_domains:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain. Must be one of: {valid_domains}"
            )

        # Build query for domain-specific text entries
        query = db.query(TextEntry).filter(TextEntry.patient_id == patient_id)
        
        # Filter by domain in entry_type
        query = query.filter(TextEntry.entry_type.like(f"{domain}_%"))

        if case_id:
            query = query.filter(TextEntry.case_id == case_id)

        if content_type:
            query = query.filter(TextEntry.entry_type.like(f"{domain}_{content_type}%"))

        # Order by creation date and limit
        entries = query.order_by(TextEntry.created_at.desc()).limit(limit).all()

        # Convert to response format
        result = []
        for entry in entries:
            entry_data = {
                "id": entry.id,
                "patient_id": entry.patient_id,
                "case_id": entry.case_id,
                "entry_type": entry.entry_type,
                "title": entry.title,
                "content": entry.content,
                "tags": json.loads(entry.tags) if entry.tags else [],
                "metadata": json.loads(entry.metadata) if entry.metadata else {},
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "domain": domain,
            }
            result.append(entry_data)

        return {
            "success": True,
            "domain": domain,
            "patient_id": patient_id,
            "total_entries": len(result),
            "entries": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get domain text entries for {domain}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get text entries for {domain}: {str(e)}"
        )


@router.get("/domains/{domain}/images/{patient_id}")
async def get_domain_image_entries(
    domain: str,
    patient_id: str,
    case_id: Optional[str] = None,
    image_category: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get image entries for a patient within a specific domain
    """
    try:
        # Validate domain
        valid_domains = ["surgery", "logistics", "insurance", "general"]
        if domain not in valid_domains:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain. Must be one of: {valid_domains}"
            )

        # Build query for domain-specific image entries
        query = db.query(MediaFile).filter(MediaFile.patient_id == patient_id)
        
        # Filter by domain in media_type
        query = query.filter(MediaFile.media_type.like(f"{domain}_%"))

        if case_id:
            query = query.filter(MediaFile.case_id == case_id)

        if image_category:
            query = query.filter(MediaFile.media_type.like(f"{domain}_{image_category}%"))

        # Order by creation date and limit
        images = query.order_by(MediaFile.created_at.desc()).limit(limit).all()

        # Convert to response format
        result = []
        for image in images:
            image_data = {
                "id": image.id,
                "patient_id": image.patient_id,
                "case_id": image.case_id,
                "media_type": image.media_type,
                "title": image.title,
                "description": image.description,
                "file_path": image.file_path,
                "original_filename": image.original_filename,
                "file_size": image.file_size,
                "content_type": image.content_type,
                "tags": json.loads(image.tags) if image.tags else [],
                "metadata": json.loads(image.metadata) if image.metadata else {},
                "created_at": image.created_at.isoformat(),
                "updated_at": image.updated_at.isoformat(),
                "domain": domain,
            }
            result.append(image_data)

        return {
            "success": True,
            "domain": domain,
            "patient_id": patient_id,
            "total_images": len(result),
            "images": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get domain image entries for {domain}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get image entries for {domain}: {str(e)}"
        )
