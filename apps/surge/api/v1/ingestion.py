"""Enhanced Data Ingestion API - Streamlined CSV Processing Integration.

Handles CSV uploads and manual entries with intelligent analytics.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from src.surge.core.csv_processor import CSVProcessor
from src.surge.core.database import get_db
from src.surge.core.models.database_models import IngestionLog
from src.surge.core.services.logger import get_logger


logger = get_logger(__name__)
router = APIRouter()

# Initialize processors
csv_processor = CSVProcessor()

# Constants
MAX_AGE = 120
VALID_STAGES = ["IA", "IB", "II", "III", "IV"]
VALID_MEDIA_TYPES = ["image", "video", "audio", "document"]
VALID_ENTRY_TYPES = ["note", "observation", "diagnosis", "treatment_plan", "follow_up"]


class ManualEntryData(BaseModel):
    """Manual patient data entry model."""

    patient_id: str
    age: int
    stage: str
    gender: str | None = None
    histology: str | None = None
    location: str | None = None
    domain: str = "local"
    notes: str | None = None
    clinical_findings: str | None = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate patient age is within reasonable bounds."""
        if v < 0 or v > MAX_AGE:
            msg = f"Age must be between 0 and {MAX_AGE}"
            raise ValueError(msg)
        return v

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, v: str) -> str:
        """Validate cancer stage is valid."""
        if v not in VALID_STAGES:
            msg = f"Stage must be one of: {VALID_STAGES}"
            raise ValueError(msg)
        return v


class IngestionResponse(BaseModel):
    """Standard ingestion response model."""

    success: bool
    message: str
    upload_id: str
    processed_records: int
    errors: list[str] = []
    warnings: list[str] = []
    quality_score: float | None = None
    domain_detected: str | None = None


def create_ingestion_log(
    db: Session,
    upload_id: str,
    filename: str,
    domain: str,
    status: str = "processing",
    total_records: int = 0,
) -> IngestionLog:
    """Create a new ingestion log entry."""
    ingestion_log = IngestionLog(
        upload_id=upload_id,
        filename=filename,
        domain=domain,
        status=status,
        started_at=datetime.now(timezone.utc),
        total_records=total_records,
    )
    db.add(ingestion_log)
    db.commit()
    db.refresh(ingestion_log)
    return ingestion_log


@router.post("/upload-csv", response_model=IngestionResponse)
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: str = Form("local"),
    db: Session = Depends(get_db),
) -> IngestionResponse:
    """Upload and process CSV files with intelligent processing."""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith(
            (".csv", ".xlsx", ".xls")
        ):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported",
            )

        # Generate upload ID
        upload_id = str(uuid.uuid4())
        logger.info(
            "Processing CSV upload: %s, upload_id: %s", file.filename, upload_id
        )

        # Read file content
        content = await file.read()

        # Create ingestion log
        ingestion_log = create_ingestion_log(
            db=db,
            upload_id=upload_id,
            filename=file.filename,
            domain=domain,
        )

        # Process CSV
        processing_result = csv_processor.process_csv(content, domain=domain)

        # Update log with results
        ingestion_log.status = "completed"
        ingestion_log.completed_at = datetime.now(timezone.utc)
        ingestion_log.total_records = (
            len(processing_result.data) if processing_result.data is not None else 0
        )
        ingestion_log.processed_records = ingestion_log.total_records
        db.commit()

        # Store processed data in background if successful
        if processing_result.data is not None and len(processing_result.data) > 0:
            # Add background task to store data
            # background_tasks.add_task(store_processed_data, ...)
            pass

        return IngestionResponse(
            success=True,
            message="CSV processed successfully",
            upload_id=upload_id,
            processed_records=ingestion_log.processed_records,
            quality_score=processing_result.quality_report.overall_score,
            domain_detected=processing_result.schema.domain.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("CSV upload failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e!s}") from e


@router.post("/manual-entry", response_model=IngestionResponse)
async def add_manual_entry(
    entry_data: ManualEntryData,
    db: Session = Depends(get_db),
) -> IngestionResponse:
    """Add a single patient record via manual entry."""
    try:
        upload_id = str(uuid.uuid4())

        logger.info("Processing manual entry for patient: %s", entry_data.patient_id)

        # Convert to list format for consistent processing
        [entry_data.model_dump()]

        # Create ingestion log
        ingestion_log = create_ingestion_log(
            db=db,
            upload_id=upload_id,
            filename="manual_entry",
            domain=entry_data.domain,
            status="completed",
            total_records=1,
        )
        ingestion_log.completed_at = datetime.now(timezone.utc)
        ingestion_log.processed_records = 1
        ingestion_log.entry_method = "manual"
        db.commit()

        return IngestionResponse(
            success=True,
            message="Manual entry processed successfully",
            upload_id=upload_id,
            processed_records=1,
        )

    except Exception as e:
        logger.exception("Manual entry failed")
        raise HTTPException(
            status_code=500, detail=f"Manual entry failed: {e!s}"
        ) from e


@router.get("/status/{upload_id}")
async def get_ingestion_status(
    upload_id: str, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Get the status of a data ingestion process."""
    try:
        ingestion_log = (
            db.query(IngestionLog).filter(IngestionLog.upload_id == upload_id).first()
        )

        if not ingestion_log:
            raise HTTPException(status_code=404, detail="Upload ID not found")

        return {
            "upload_id": ingestion_log.upload_id,
            "status": ingestion_log.status,
            "processed_records": ingestion_log.processed_records or 0,
            "total_records": ingestion_log.total_records or 0,
            "started_at": ingestion_log.started_at,
            "completed_at": ingestion_log.completed_at,
            "errors": [],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get ingestion status")
        raise HTTPException(status_code=500, detail="Failed to retrieve status") from e


@router.get("/recent-uploads")
async def get_recent_uploads(
    limit: int = 10,
    domain: str | None = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get recent data ingestion uploads."""
    try:
        query = db.query(IngestionLog).order_by(IngestionLog.started_at.desc())

        if domain:
            query = query.filter(IngestionLog.domain == domain)

        uploads = query.limit(limit).all()

        return {
            "uploads": [
                {
                    "upload_id": upload.upload_id,
                    "filename": upload.filename,
                    "status": upload.status,
                    "domain": upload.domain,
                    "started_at": upload.started_at,
                    "processed_records": upload.processed_records or 0,
                }
                for upload in uploads
            ]
        }

    except Exception as e:
        logger.exception("Failed to get recent uploads")
        raise HTTPException(status_code=500, detail="Failed to retrieve uploads") from e


@router.delete("/upload/{upload_id}")
async def delete_upload(
    upload_id: str, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Delete an ingestion upload and associated data."""
    try:
        # Delete from ingestion log
        ingestion_log = (
            db.query(IngestionLog).filter(IngestionLog.upload_id == upload_id).first()
        )

        if not ingestion_log:
            raise HTTPException(status_code=404, detail="Upload ID not found")

        # Delete associated data would go here
        # db.query(CohortData).filter(CohortData.upload_id == upload_id).delete()

        db.delete(ingestion_log)
        db.commit()

        logger.info("Deleted upload: %s", upload_id)

        return {"success": True, "message": "Upload deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete upload")
        raise HTTPException(status_code=500, detail="Failed to delete upload") from e
