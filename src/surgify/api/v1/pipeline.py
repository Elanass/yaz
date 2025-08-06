"""
CSV-to-Insights Pipeline API - Complete Workflow Endpoint
Handles the entire workflow from CSV upload to professional deliverable generation
"""

import asyncio
import io
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.analytics.insight_generator import InsightGenerator
from ...core.csv_processor import CSVProcessor, ProcessingConfig
from ...core.database import get_db
from ...core.deliverable_factory import DeliverableFactory
from ...core.models.processing_models import (
    AudienceType,
    DataDomain,
    DeliverableFormat,
    DeliverableRequest,
    InsightPackage,
    ProcessingResult,
)
from ...core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/pipeline", tags=["CSV-to-Insights Pipeline"])

# Initialize components
csv_processor = CSVProcessor()
insight_generator = InsightGenerator()
deliverable_factory = DeliverableFactory()

# In-memory storage (replace with database in production)
pipeline_jobs = {}
processing_results = {}
insights_cache = {}


class PipelineRequest(BaseModel):
    """Complete pipeline processing request"""

    domain: Optional[str] = None
    generate_insights: bool = True
    deliverable_formats: List[DeliverableFormat] = [DeliverableFormat.PDF]
    target_audiences: List[AudienceType] = [AudienceType.EXECUTIVE]
    include_interactive: bool = False
    custom_title: Optional[str] = None


class PipelineResponse(BaseModel):
    """Complete pipeline processing response"""

    success: bool
    job_id: str
    message: str
    processing_summary: Dict[str, Any]
    deliverables_info: List[Dict[str, Any]] = []
    estimated_completion: Optional[datetime] = None


class PipelineStatus(BaseModel):
    """Pipeline job status"""

    job_id: str
    status: str  # uploading, processing, analyzing, generating, completed, failed
    progress: int  # 0-100
    current_stage: str
    stages_completed: List[str] = []
    errors: List[str] = []
    warnings: List[str] = []
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    deliverables_ready: List[str] = []


@router.post("/process-csv", response_model=PipelineResponse)
async def process_csv_complete_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    pipeline_config: str = Form(...),  # JSON string of PipelineRequest
    db: Session = Depends(get_db),
):
    """
    Complete CSV-to-Insights pipeline: Upload → Process → Analyze → Generate Deliverables

    This endpoint handles the entire workflow:
    1. CSV upload and validation
    2. Intelligent data processing and quality assessment
    3. Domain-specific insight generation
    4. Professional deliverable creation in multiple formats
    5. Real-time status tracking
    """
    try:
        # Parse pipeline configuration
        try:
            config = PipelineRequest.parse_raw(pipeline_config)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid pipeline configuration: {str(e)}"
            )

        # Validate file
        if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(
                status_code=400, detail="Only CSV and Excel files are supported"
            )

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Read file content
        file_content = await file.read()

        # Validate file size (100MB limit)
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 100MB)")

        # Create job tracking
        pipeline_jobs[job_id] = PipelineStatus(
            job_id=job_id,
            status="processing",
            progress=10,
            current_stage="CSV Processing",
            started_at=datetime.utcnow(),
        )

        # Start background processing
        background_tasks.add_task(
            process_pipeline_async, job_id, file_content, file.filename, config
        )

        return PipelineResponse(
            success=True,
            job_id=job_id,
            message="CSV processing pipeline started successfully",
            processing_summary={
                "filename": file.filename,
                "file_size_mb": round(len(file_content) / (1024 * 1024), 2),
                "domain": config.domain or "auto-detect",
                "target_formats": [f.value for f in config.deliverable_formats],
                "target_audiences": [a.value for a in config.target_audiences],
            },
            estimated_completion=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline initiation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Pipeline failed to start: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=PipelineStatus)
async def get_pipeline_status(job_id: str):
    """
    Get real-time status of a pipeline job
    """
    try:
        if job_id not in pipeline_jobs:
            raise HTTPException(status_code=404, detail="Pipeline job not found")

        return pipeline_jobs[job_id]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get pipeline status: {str(e)}"
        )


@router.get("/results/{job_id}")
async def get_pipeline_results(job_id: str):
    """
    Get comprehensive results from a completed pipeline job
    """
    try:
        if job_id not in pipeline_jobs:
            raise HTTPException(status_code=404, detail="Pipeline job not found")

        job_status = pipeline_jobs[job_id]

        if job_status.status != "completed":
            return {
                "job_id": job_id,
                "status": job_status.status,
                "message": "Pipeline not yet completed",
                "progress": job_status.progress,
                "current_stage": job_status.current_stage,
            }

        # Get processing results
        processing_result = processing_results.get(job_id)
        insights = insights_cache.get(job_id)

        if not processing_result:
            raise HTTPException(status_code=404, detail="Processing results not found")

        # Prepare comprehensive results
        results = {
            "job_id": job_id,
            "status": "completed",
            "processing_completed_at": job_status.started_at.isoformat(),
            "data_summary": {
                "domain": processing_result.schema.domain.value,
                "total_records": len(processing_result.data)
                if processing_result.data is not None
                else 0,
                "valid_records": processing_result.quality_report.valid_records,
                "data_quality_score": processing_result.quality_report.overall_score,
            },
            "quality_assessment": {
                "completeness": processing_result.quality_report.completeness_score,
                "consistency": processing_result.quality_report.consistency_score,
                "validity": processing_result.quality_report.validity_score,
                "errors_count": len(processing_result.quality_report.errors),
                "warnings_count": len(processing_result.quality_report.warnings),
            },
            "insights_available": insights is not None,
            "deliverables_ready": job_status.deliverables_ready,
            "download_urls": {
                deliverable_id: f"/api/v1/pipeline/download/{deliverable_id}"
                for deliverable_id in job_status.deliverables_ready
            },
        }

        # Add insights summary if available
        if insights:
            results["insights_summary"] = {
                "confidence_level": insights.confidence_level,
                "key_findings_count": len(insights.executive_summary.critical_findings),
                "recommendations_count": len(
                    insights.executive_summary.recommendations
                ),
                "visualizations_count": len(insights.visualizations),
            }

            # Add domain-specific insights
            if insights.clinical_findings:
                results["clinical_summary"] = {
                    "risk_factors_identified": len(
                        insights.clinical_findings.risk_factors
                    ),
                    "patient_outcomes_analyzed": bool(
                        insights.clinical_findings.patient_outcomes
                    ),
                    "clinical_recommendations": len(
                        insights.clinical_findings.clinical_recommendations
                    ),
                }

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.get("/download/{deliverable_id}")
async def download_pipeline_deliverable(deliverable_id: str):
    """
    Download a deliverable generated by the pipeline
    """
    try:
        # This would integrate with the deliverables API
        # For now, return a placeholder response
        return JSONResponse(
            {
                "message": "Deliverable download endpoint",
                "deliverable_id": deliverable_id,
                "note": "This would stream the actual deliverable file",
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/list-jobs")
async def list_pipeline_jobs(status: Optional[str] = None, limit: int = 20):
    """
    List recent pipeline jobs with optional status filtering
    """
    try:
        jobs = list(pipeline_jobs.values())

        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job.status == status]

        # Sort by start time (newest first)
        jobs.sort(key=lambda x: x.started_at, reverse=True)

        # Apply limit
        jobs = jobs[:limit]

        return [
            {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "current_stage": job.current_stage,
                "started_at": job.started_at.isoformat(),
                "deliverables_ready": len(job.deliverables_ready),
                "has_errors": len(job.errors) > 0,
            }
            for job in jobs
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.delete("/job/{job_id}")
async def cancel_or_delete_pipeline_job(job_id: str):
    """
    Cancel a running pipeline job or delete a completed one
    """
    try:
        if job_id not in pipeline_jobs:
            raise HTTPException(status_code=404, detail="Pipeline job not found")

        job_status = pipeline_jobs[job_id]

        if job_status.status in ["processing", "analyzing", "generating"]:
            # Cancel running job
            job_status.status = "cancelled"
            job_status.current_stage = "Cancelled by user"
            message = "Pipeline job cancelled successfully"
        else:
            # Delete completed/failed job
            del pipeline_jobs[job_id]

            # Clean up related data
            processing_results.pop(job_id, None)
            insights_cache.pop(job_id, None)

            message = "Pipeline job deleted successfully"

        return {"success": True, "message": message}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel/delete job: {str(e)}"
        )


# Background processing function
async def process_pipeline_async(
    job_id: str, file_content: bytes, filename: str, config: PipelineRequest
):
    """
    Background task to process the complete pipeline
    """
    job_status = pipeline_jobs[job_id]

    try:
        logger.info(f"Starting pipeline processing for job {job_id}")

        # Stage 1: CSV Processing
        job_status.current_stage = "Processing CSV Data"
        job_status.progress = 20

        processing_config = ProcessingConfig(
            auto_detect_types=True,
            domain=DataDomain(config.domain) if config.domain else None,
        )

        processing_result = await csv_processor.analyze_csv(
            file_content=file_content, domain=config.domain
        )

        processing_results[job_id] = processing_result
        job_status.stages_completed.append("CSV Processing")
        job_status.progress = 40

        logger.info(f"CSV processing completed for job {job_id}")

        # Stage 2: Insight Generation
        if config.generate_insights:
            job_status.current_stage = "Generating Insights"
            job_status.progress = 60

            try:
                insights = await insight_generator.generate_comprehensive_insights(
                    processing_result
                )
                insights_cache[job_id] = insights
                job_status.stages_completed.append("Insight Generation")
                logger.info(f"Insights generated for job {job_id}")
            except Exception as e:
                job_status.warnings.append(f"Insight generation failed: {str(e)}")
                insights = None
        else:
            insights = None

        job_status.progress = 75

        # Stage 3: Deliverable Generation
        job_status.current_stage = "Generating Deliverables"

        deliverable_tasks = []
        for audience in config.target_audiences:
            for format_type in config.deliverable_formats:
                deliverable_tasks.append((audience, format_type))

        # Generate deliverables
        for audience, format_type in deliverable_tasks:
            try:
                deliverable_request = DeliverableRequest(
                    processing_result_id=job_id, audience=audience, format=format_type
                )

                if insights:
                    deliverable = await deliverable_factory.generate_deliverable(
                        processing_result, insights, deliverable_request
                    )

                    # Store deliverable (simplified - would use proper storage)
                    deliverable_id = f"{job_id}_{audience.value}_{format_type.value}"
                    # deliverables_store[deliverable_id] = deliverable
                    job_status.deliverables_ready.append(deliverable_id)

                    logger.info(f"Deliverable generated: {deliverable_id}")

            except Exception as e:
                error_msg = f"Failed to generate {format_type.value} for {audience.value}: {str(e)}"
                job_status.errors.append(error_msg)
                logger.error(error_msg)

        job_status.stages_completed.append("Deliverable Generation")
        job_status.progress = 100
        job_status.status = "completed"
        job_status.current_stage = "Completed Successfully"

        logger.info(f"Pipeline processing completed successfully for job {job_id}")

    except Exception as e:
        error_msg = f"Pipeline processing failed: {str(e)}"
        job_status.status = "failed"
        job_status.current_stage = "Failed"
        job_status.errors.append(error_msg)
        logger.error(f"Pipeline failed for job {job_id}: {str(e)}")


@router.get("/templates")
async def get_available_templates():
    """
    Get available report templates and customization options
    """
    return {
        "audiences": [
            {
                "value": "executive",
                "name": "Executive Summary",
                "description": "High-level insights for leadership",
            },
            {
                "value": "clinical",
                "name": "Clinical Report",
                "description": "Detailed medical analysis",
            },
            {
                "value": "technical",
                "name": "Technical Analysis",
                "description": "Statistical methodology and details",
            },
            {
                "value": "operational",
                "name": "Operational Guide",
                "description": "Action items and implementation",
            },
        ],
        "formats": [
            {
                "value": "pdf",
                "name": "PDF Report",
                "description": "Professional printable document",
            },
            {
                "value": "interactive",
                "name": "Interactive Dashboard",
                "description": "Web-based interactive report",
            },
            {
                "value": "presentation",
                "name": "Presentation",
                "description": "Slide-based presentation format",
            },
            {
                "value": "api",
                "name": "API Response",
                "description": "Structured JSON data",
            },
        ],
        "domains": [
            {
                "value": "surgery",
                "name": "Surgery",
                "description": "Surgical outcomes and protocols",
            },
            {
                "value": "logistics",
                "name": "Logistics",
                "description": "Resource allocation and efficiency",
            },
            {
                "value": "insurance",
                "name": "Insurance",
                "description": "Risk assessment and claims",
            },
        ],
    }


@router.get("/sample-data")
async def get_sample_data():
    """
    Provide sample CSV data for testing the pipeline
    """
    sample_data = {
        "surgery_sample": {
            "description": "Sample surgical outcomes data",
            "headers": [
                "patient_id",
                "age",
                "gender",
                "procedure",
                "stage",
                "outcome",
                "complications",
                "los",
            ],
            "sample_rows": [
                ["P001", 65, "M", "Gastric Resection", "II", "Good", "None", 7],
                [
                    "P002",
                    72,
                    "F",
                    "Gastric Resection",
                    "III",
                    "Fair",
                    "Minor bleeding",
                    9,
                ],
                ["P003", 58, "M", "Gastric Resection", "I", "Excellent", "None", 5],
            ],
        },
        "logistics_sample": {
            "description": "Sample logistics and resource data",
            "headers": [
                "resource_id",
                "type",
                "capacity",
                "utilization",
                "efficiency",
                "cost",
                "downtime",
            ],
            "sample_rows": [
                ["OR001", "Operating Room", 16, 0.85, 0.92, 5000, 2],
                ["OR002", "Operating Room", 16, 0.78, 0.88, 5000, 4],
                ["EQ001", "Equipment", 1, 0.95, 0.98, 2000, 0.5],
            ],
        },
    }

    return sample_data
