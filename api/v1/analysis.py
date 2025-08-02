"""
Analysis API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd
import json
import uuid
from pathlib import Path
from datetime import datetime
from core.utils.id_generator import generate_id
from fastapi.responses import FileResponse

from core.dependencies import require_auth
from features.analysis.analysis_engine import AnalysisEngine
from core.reproducibility.manager import ReproducibilityManager
from core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
analysis_engine = AnalysisEngine()
reproducibility_manager = ReproducibilityManager()


class AnalysisRequest(BaseModel):
    data: Dict[str, Any]
    analysis_type: str = "prospective"


class CohortUploadResponse(BaseModel):
    success: bool
    cohort_id: str
    message: str
    records_count: int
    preview: Optional[Dict[str, Any]] = None


class AnalysisResultsResponse(BaseModel):
    success: bool
    analysis_id: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    reproducible: bool


@router.post("/cohort/upload", response_model=CohortUploadResponse)
async def upload_cohort_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    cohort_name: Optional[str] = None,
    description: Optional[str] = None,
    current_user=Depends(require_auth)
):
    """Upload cohort dataset for analysis"""
    
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload CSV, Excel, or JSON files."
            )
        
        # Generate cohort ID
        cohort_id = f"cohort_{uuid.uuid4().hex[:12]}"
        upload_timestamp = datetime.now()
        
        # Create upload directory
        uploads_dir = Path("data/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        cohort_dir = uploads_dir / cohort_id
        cohort_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = cohort_dir / f"original_{file.filename}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Parse data based on file type
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif file.filename.endswith('.json'):
                with open(file_path) as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            
            # Convert to standardized format
            processed_data = df.to_dict('records')
            
            # Save processed data
            processed_file = cohort_dir / "processed_data.json"
            with open(processed_file, 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing file: {str(e)}"
            )
        
        # Create metadata
        metadata = {
            "cohort_id": cohort_id,
            "cohort_name": cohort_name or f"Cohort {cohort_id}",
            "description": description or f"Uploaded cohort dataset",
            "upload_timestamp": upload_timestamp.isoformat(),
            "uploaded_by": current_user.get("id", "unknown"),
            "original_filename": file.filename,
            "file_size_bytes": len(content),
            "records_count": len(df),
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "summary_stats": df.describe().to_dict() if len(df) > 0 else {}
        }
        
        # Save metadata
        metadata_file = cohort_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Register with reproducibility manager
        dataset_version = reproducibility_manager.register_dataset_version(
            dataset_name=cohort_id,
            data=processed_data,
            metadata=metadata
        )
        
        # Log upload
        logger.info(f"Cohort dataset uploaded: {cohort_id} by {current_user.get('id')}")
        
        # Create preview (first 5 records)
        preview = {
            "sample_records": processed_data[:5] if processed_data else [],
            "total_records": len(processed_data),
            "columns": list(df.columns) if len(df) > 0 else []
        }
        
        return CohortUploadResponse(
            success=True,
            cohort_id=cohort_id,
            message=f"Successfully uploaded cohort dataset with {len(df)} records",
            records_count=len(df),
            preview=preview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading cohort dataset: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/cohort/{cohort_id}")
async def get_cohort_info(
    cohort_id: str,
    current_user=Depends(require_auth)
):
    """Get cohort dataset information"""
    
    try:
        cohort_dir = Path("data/uploads") / cohort_id
        metadata_file = cohort_dir / "metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Cohort {cohort_id} not found"
            )
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        return {"success": True, "cohort_info": metadata}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cohort info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cohort/{cohort_id}/analyze", response_model=AnalysisResultsResponse)
async def analyze_cohort(
    cohort_id: str,
    analysis_config: Dict[str, Any],
    current_user=Depends(require_auth)
):
    """Analyze uploaded cohort dataset"""
    
    try:
        # Load cohort data
        cohort_dir = Path("data/uploads") / cohort_id
        data_file = cohort_dir / "processed_data.json"
        metadata_file = cohort_dir / "metadata.json"
        
        if not data_file.exists() or not metadata_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Cohort {cohort_id} not found"
            )
        
        with open(data_file) as f:
            cohort_data = json.load(f)
        
        with open(metadata_file) as f:
            cohort_metadata = json.load(f)
        
        # Perform analysis
        analysis_type = analysis_config.get("analysis_type", "prospective")
        
        # Prepare analysis request
        analysis_request = {
            "data": cohort_data,
            "cohort_metadata": cohort_metadata,
            **analysis_config
        }
        
        # Run analysis
        analysis_results = analysis_engine.analyze(analysis_request, analysis_type)
        
        # Record analysis run for reproducibility
        run_id = reproducibility_manager.record_analysis_run(
            input_data=cohort_data,
            configuration=analysis_config,
            results=analysis_results,
            analyst_id=current_user.get("id", "unknown")
        )
        
        # Generate analysis ID
        analysis_id = f"analysis_{uuid.uuid4().hex[:12]}"
        
        # Save analysis results
        results_dir = Path("data/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_file = results_dir / f"{analysis_id}.json"
        
        complete_results = {
            "analysis_id": analysis_id,
            "cohort_id": cohort_id,
            "run_id": run_id,
            "analysis_config": analysis_config,
            "results": analysis_results,
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "analyzed_by": current_user.get("id"),
                "cohort_records": len(cohort_data),
                "analysis_type": analysis_type
            }
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(complete_results, f, indent=2, default=str)
        
        logger.info(f"Cohort analysis completed: {analysis_id} for cohort {cohort_id}")
        
        return AnalysisResultsResponse(
            success=True,
            analysis_id=analysis_id,
            results=analysis_results,
            metadata=complete_results["metadata"],
            reproducible=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing cohort: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/results/{analysis_id}")
async def get_analysis_results(
    analysis_id: str,
    current_user=Depends(require_auth)
):
    """Get analysis results"""
    
    try:
        results_file = Path("data/results") / f"{analysis_id}.json"
        
        if not results_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )
        
        with open(results_file) as f:
            results = json.load(f)
        
        return {"success": True, "analysis": results}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results")
async def list_analysis_results(
    limit: int = 20,
    offset: int = 0,
    current_user=Depends(require_auth)
):
    """List all analysis results"""
    
    try:
        results_dir = Path("data/results")
        if not results_dir.exists():
            return {"success": True, "analyses": [], "total": 0}
        
        # Get all result files
        result_files = list(results_dir.glob("*.json"))
        result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Apply pagination
        paginated_files = result_files[offset:offset + limit]
        
        analyses = []
        for result_file in paginated_files:
            try:
                with open(result_file) as f:
                    data = json.load(f)
                
                summary = {
                    "analysis_id": data.get("analysis_id"),
                    "cohort_id": data.get("cohort_id"),
                    "analysis_type": data.get("analysis_config", {}).get("analysis_type"),
                    "analyzed_at": data.get("metadata", {}).get("analyzed_at"),
                    "analyzed_by": data.get("metadata", {}).get("analyzed_by"),
                    "cohort_records": data.get("metadata", {}).get("cohort_records")
                }
                analyses.append(summary)
                
            except Exception as e:
                logger.warning(f"Could not load result file {result_file}: {e}")
        
        return {
            "success": True,
            "analyses": analyses,
            "total": len(result_files),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing analysis results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reproduce/{run_id}")
async def reproduce_analysis(
    run_id: str,
    current_user=Depends(require_auth)
):
    """Reproduce a previous analysis run"""
    
    try:
        reproduction_result = reproducibility_manager.reproduce_analysis(run_id)
        
        if reproduction_result["reproducible"]:
            # Attempt to re-run the analysis with the original configuration
            configuration = reproduction_result["configuration"]
            
            # Note: In a full implementation, you would need to also restore
            # the original dataset and re-run the analysis
            
            return {
                "success": True,
                "message": "Analysis reproduction successful",
                "reproduction_result": reproduction_result,
                "note": "Configuration recovered - dataset would need to be restored for full reproduction"
            }
        else:
            return {
                "success": False,
                "message": "Analysis reproduction has compatibility issues",
                "reproduction_result": reproduction_result
            }
        
    except Exception as e:
        logger.error(f"Error reproducing analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reproduction failed: {str(e)}"
        )


@router.get("/reproducibility/report")
async def get_reproducibility_report(
    current_user=Depends(require_auth)
):
    """Get comprehensive reproducibility report"""
    
    try:
        report = reproducibility_manager.create_reproducibility_report()
        return {"success": True, "report": report}
        
    except Exception as e:
        logger.error(f"Error generating reproducibility report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_data(
    request: AnalysisRequest,
    current_user=Depends(require_auth)
):
    """Perform statistical analysis"""
    try:
        result = analysis_engine.analyze(request.data, request.analysis_type)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/insights/generate", response_model=AnalysisResultsResponse)
async def generate_insights(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_auth)
):
    """
    Generate comprehensive insights from surgical case data for FLOT optimization in gastric surgery
    
    This endpoint processes surgical case data and generates insights for
    FLOT optimization in gastric surgery, using Cox Regression and Random Forest models
    for survival predictors and MCDA for decision-support scoring.
    """
    try:
        logger.info(f"Generating insights for analysis type: {request.analysis_type}")
        
        # Create analysis ID for tracking
        analysis_id = generate_id(prefix="insight_", length=12)
        
        # Log analysis request
        background_tasks.add_task(
            reproducibility_manager.log_analysis_request,
            analysis_id=analysis_id,
            analysis_type=request.analysis_type,
            user_id=current_user.id,
            input_data=request.data
        )
        
        # Process the data and generate insights
        results = await analysis_engine.generate_insights(
            data=request.data,
            analysis_type=request.analysis_type
        )
        
        # Prepare metadata
        metadata = {
            "analysis_id": analysis_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id,
            "analysis_type": request.analysis_type
        }
        
        # Store the results for reproducibility
        background_tasks.add_task(
            reproducibility_manager.store_analysis_results,
            analysis_id=analysis_id,
            results=results,
            metadata=metadata
        )
        
        return AnalysisResultsResponse(
            success=True,
            analysis_id=analysis_id,
            results=results,
            metadata=metadata,
            reproducible=True
        )
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


class PublicationRequest(BaseModel):
    cohort_id: str
    publication_type: str  # "memoir", "article", "infographic"
    title: str
    authors: List[str]
    template_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class PublicationResponse(BaseModel):
    success: bool
    publication_id: str
    download_url: str
    message: str


@router.post("/publication/prepare", response_model=PublicationResponse)
async def prepare_publication(
    request: PublicationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(require_auth)
):
    """
    Prepare a publication (memoir, article, infographic) from cohort data
    
    This endpoint processes cohort data and generates a publication-ready document
    based on the specified publication type and template. The publication is
    stored for download and can include custom fields for further customization.
    """
    try:
        logger.info(f"Preparing {request.publication_type} for cohort: {request.cohort_id}")
        
        # Create publication ID for tracking
        publication_id = generate_id(prefix="pub_", length=8)
        
        # Generate filename
        filename = f"{request.publication_type}_{publication_id}.pdf"
        
        # Get cohort data
        uploads_dir = Path("data/uploads")
        cohort_dir = uploads_dir / request.cohort_id
        processed_file = cohort_dir / "processed_data.json"
        
        if not processed_file.exists():
            raise HTTPException(status_code=404, detail=f"Cohort data not found: {request.cohort_id}")
        
        with open(processed_file, 'r') as f:
            cohort_data = json.load(f)
        
        # Process the publication in the background
        background_tasks.add_task(
            analysis_engine.generate_publication,
            publication_id=publication_id,
            publication_type=request.publication_type,
            title=request.title,
            authors=request.authors,
            cohort_data=cohort_data,
            template_id=request.template_id,
            custom_fields=request.custom_fields,
            user_id=current_user.id
        )
        
        # Create download URL
        download_url = f"/api/v1/analysis/publication/download/{publication_id}"
        
        return PublicationResponse(
            success=True,
            publication_id=publication_id,
            download_url=download_url,
            message=f"{request.publication_type.capitalize()} is being prepared and will be available for download shortly."
        )
        
    except Exception as e:
        logger.error(f"Error preparing publication: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error preparing publication: {str(e)}")


@router.get("/publication/download/{publication_id}")
async def download_publication(
    publication_id: str,
    current_user=Depends(require_auth)
):
    """Download a prepared publication"""
    # Locate the prepared PDF
    file_path = Path("data/uploads/publications") / f"{publication_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Publication not found: {publication_id}")
    return FileResponse(path=str(file_path), media_type="application/pdf", filename=file_path.name)
