"""Imaging Router - PACS and OHIF Integration

Provides endpoints for medical imaging with Orthanc PACS integration
and OHIF viewer support.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel

from infra.clients.orthanc_client import OrthancClient, OrthancError, create_orthanc_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/imaging", tags=["Medical Imaging"])


# Dependency to get Orthanc client
async def get_orthanc_client() -> OrthancClient:
    """Get configured Orthanc client"""
    return create_orthanc_client()


# Request/Response Models
class StudySearchRequest(BaseModel):
    """Study search parameters"""
    patient_id: Optional[str] = None
    study_date: Optional[str] = None
    accession_number: Optional[str] = None
    study_description: Optional[str] = None


class OHIFConfig(BaseModel):
    """OHIF viewer configuration"""
    study_instance_uid: str
    ohif_base_url: str = "http://localhost:3000"
    

# Error handler for Orthanc errors
async def orthanc_error_handler(request: Request, exc: OrthancError):
    """Handle Orthanc-specific errors"""
    logger.error(f"Orthanc Error: {exc}")
    
    return JSONResponse(
        status_code=exc.status_code or 500,
        content={
            "error": "imaging_error",
            "message": str(exc),
            "details": exc.response if exc.response else None
        }
    )


# System Information
@router.get("/system")
async def get_system_info(client: OrthancClient = Depends(get_orthanc_client)):
    """Get PACS system information"""
    async with client:
        try:
            system_info = await client.get_system()
            stats = await client.get_statistics()
            
            return {
                "system": system_info,
                "statistics": stats,
                "status": "healthy"
            }
        except OrthancError as e:
            logger.error(f"Failed to get PACS system info: {e}")
            raise HTTPException(status_code=500, detail="PACS server unavailable")


# Patient Studies
@router.get("/patients")
async def get_patients(client: OrthancClient = Depends(get_orthanc_client)):
    """Get all patients"""
    async with client:
        patients = await client.get_patients()
        return {"patients": patients, "count": len(patients)}


@router.get("/patients/{patient_id}")
async def get_patient(
    patient_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get patient information"""
    async with client:
        patient = await client.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient


@router.get("/patients/{patient_id}/studies")
async def get_patient_studies(
    patient_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get studies for a patient"""
    async with client:
        studies = await client.get_patient_studies(patient_id)
        
        # Get detailed study information
        study_details = []
        for study_id in studies:
            study = await client.get_study(study_id)
            if study:
                study_details.append(study.dict())
        
        return {
            "patient_id": patient_id,
            "studies": study_details,
            "count": len(study_details)
        }


# Studies
@router.get("/studies")
async def get_studies(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get all studies with pagination"""
    async with client:
        all_studies = await client.get_studies()
        
        # Apply pagination
        paginated_studies = all_studies[offset:offset + limit]
        
        # Get detailed study information
        study_details = []
        for study_id in paginated_studies:
            study = await client.get_study(study_id)
            if study:
                study_details.append(study.dict())
        
        return {
            "studies": study_details,
            "total": len(all_studies),
            "count": len(study_details),
            "offset": offset,
            "limit": limit
        }


@router.post("/studies/search")
async def search_studies(
    search_request: StudySearchRequest,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Search for studies"""
    async with client:
        # Build search query
        search_params = {}
        
        if search_request.patient_id:
            search_params["PatientID"] = search_request.patient_id
        if search_request.study_date:
            search_params["StudyDate"] = search_request.study_date
        if search_request.accession_number:
            search_params["AccessionNumber"] = search_request.accession_number
        if search_request.study_description:
            search_params["StudyDescription"] = search_request.study_description
        
        studies = await client.search_studies(**search_params)
        
        # Get detailed study information
        study_details = []
        for study_id in studies:
            study = await client.get_study(study_id)
            if study:
                study_details.append(study.dict())
        
        return {
            "studies": study_details,
            "count": len(study_details),
            "search_params": search_params
        }


@router.get("/studies/{study_id}")
async def get_study(
    study_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get study information"""
    async with client:
        study = await client.get_study(study_id)
        if not study:
            raise HTTPException(status_code=404, detail="Study not found")
        return study.dict()


@router.get("/studies/{study_id}/series")
async def get_study_series(
    study_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get series for a study"""
    async with client:
        series_ids = await client.get_study_series(study_id)
        
        # Get detailed series information
        series_details = []
        for series_id in series_ids:
            series = await client.get_series(series_id)
            if series:
                series_details.append(series.dict())
        
        return {
            "study_id": study_id,
            "series": series_details,
            "count": len(series_details)
        }


# Series
@router.get("/series/{series_id}")
async def get_series(
    series_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get series information"""
    async with client:
        series = await client.get_series(series_id)
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")
        return series.dict()


@router.get("/series/{series_id}/instances")
async def get_series_instances(
    series_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get instances for a series"""
    async with client:
        instance_ids = await client.get_series_instances(series_id)
        
        # Get detailed instance information
        instance_details = []
        for instance_id in instance_ids:
            instance = await client.get_instance(instance_id)
            if instance:
                instance_details.append(instance.dict())
        
        return {
            "series_id": series_id,
            "instances": instance_details,
            "count": len(instance_details)
        }


# Instances
@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get instance information"""
    async with client:
        instance = await client.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        return instance.dict()


@router.get("/instances/{instance_id}/file")
async def get_instance_dicom(
    instance_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Download DICOM file for instance"""
    async with client:
        dicom_data = await client.get_instance_dicom(instance_id)
        if not dicom_data:
            raise HTTPException(status_code=404, detail="Instance not found")
        
        return StreamingResponse(
            io.BytesIO(dicom_data),
            media_type="application/dicom",
            headers={
                "Content-Disposition": f"attachment; filename=instance_{instance_id}.dcm"
            }
        )


@router.get("/instances/{instance_id}/tags")
async def get_instance_tags(
    instance_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get DICOM tags for instance"""
    async with client:
        tags = await client.get_instance_tags(instance_id)
        if not tags:
            raise HTTPException(status_code=404, detail="Instance not found")
        return tags


# DICOM Upload
@router.post("/upload")
async def upload_dicom(
    file: UploadFile = File(...),
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Upload DICOM file"""
    # Validate file type
    if not file.filename.lower().endswith('.dcm'):
        raise HTTPException(
            status_code=400, 
            detail="File must be a DICOM file (.dcm extension)"
        )
    
    async with client:
        try:
            # Read file content
            dicom_data = await file.read()
            
            # Upload to Orthanc
            result = await client.upload_dicom(dicom_data)
            
            return {
                "message": "DICOM file uploaded successfully",
                "result": result,
                "filename": file.filename
            }
        except OrthancError as e:
            logger.error(f"DICOM upload failed: {e}")
            raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")


@router.post("/upload/multiple")
async def upload_multiple_dicom(
    files: List[UploadFile] = File(...),
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Upload multiple DICOM files"""
    results = []
    
    async with client:
        for file in files:
            try:
                # Validate file
                if not file.filename.lower().endswith('.dcm'):
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "message": "Invalid file type"
                    })
                    continue
                
                # Read and upload
                dicom_data = await file.read()
                result = await client.upload_dicom(dicom_data)
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": str(e)
                })
    
    return {
        "message": f"Processed {len(files)} files",
        "results": results,
        "success_count": len([r for r in results if r["status"] == "success"]),
        "error_count": len([r for r in results if r["status"] == "error"])
    }


# OHIF Viewer Integration
@router.get("/viewer")
async def open_ohif_viewer(
    study_id: Optional[str] = None,
    ohif_url: Optional[str] = None
):
    """Redirect to OHIF viewer"""
    ohif_base = ohif_url or "http://localhost:3000"
    
    if study_id:
        viewer_url = f"{ohif_base}/viewer?studyInstanceUIDs={study_id}"
    else:
        viewer_url = f"{ohif_base}/studylist"
    
    return RedirectResponse(url=viewer_url)


@router.get("/viewer/{study_id}")
async def view_study(
    study_id: str,
    ohif_url: Optional[str] = None,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """View specific study in OHIF"""
    async with client:
        # Verify study exists
        study = await client.get_study(study_id)
        if not study:
            raise HTTPException(status_code=404, detail="Study not found")
        
        # Get OHIF viewer URL
        ohif_base = ohif_url or "http://localhost:3000"
        viewer_url = await client.get_ohif_viewer_url(study_id, ohif_base)
        
        if not viewer_url:
            raise HTTPException(status_code=500, detail="Failed to generate viewer URL")
        
        return RedirectResponse(url=viewer_url)


@router.get("/studies/{study_id}/ohif-data")
async def get_ohif_study_data(
    study_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Get study data formatted for OHIF viewer"""
    async with client:
        ohif_data = await client.get_ohif_study_data(study_id)
        if not ohif_data:
            raise HTTPException(status_code=404, detail="Study not found")
        return ohif_data


# Archive and Export
@router.post("/studies/{study_id}/archive")
async def create_study_archive(
    study_id: str,
    client: OrthancClient = Depends(get_orthanc_client)
):
    """Create ZIP archive of study"""
    async with client:
        # Verify study exists
        study = await client.get_study(study_id)
        if not study:
            raise HTTPException(status_code=404, detail="Study not found")
        
        archive_id = await client.create_archive([study_id], "studies")
        
        return {
            "study_id": study_id,
            "archive_id": archive_id,
            "download_url": f"/imaging/archives/{archive_id}"
        }


# Health Check
@router.get("/health")
async def health_check(client: OrthancClient = Depends(get_orthanc_client)):
    """Check PACS server health"""
    async with client:
        try:
            system_info = await client.get_system()
            stats = await client.get_statistics()
            
            return {
                "status": "healthy",
                "pacs_server": "Orthanc",
                "version": system_info.get("Version", "Unknown"),
                "statistics": {
                    "studies": stats.get("CountStudies", 0),
                    "series": stats.get("CountSeries", 0),
                    "instances": stats.get("CountInstances", 0)
                },
                "timestamp": "2025-08-11T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"PACS health check failed: {e}")
            raise HTTPException(status_code=503, detail="PACS server unavailable")


# Import required modules at the top
import io
