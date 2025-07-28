"""
Data Ingestion API
Endpoints for data ingestion from multiple sources
"""

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Path
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Dict, Any, Optional
import json
import tempfile
import os

from features.data_ingestion.pipeline import MultiCenterDataPipeline
from features.auth.service import get_current_user, require_permission, Domain, Scope

router = APIRouter(prefix="/data", tags=["Data Ingestion"])

# Initialize data pipeline
data_pipeline = MultiCenterDataPipeline()

@router.post("/ingest/{center_id}")
async def ingest_data(
    request: Request,
    center_id: str = Path(..., description="Center ID"),
    file: Optional[UploadFile] = File(None),
    api_data: Optional[str] = Form(None),
    current_user = Depends(require_permission(Domain.HEALTHCARE, Scope.WRITE))
):
    """
    Ingest data from CSV, HL7, DICOM, or API
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Determine data source
        if file:
            # File upload (CSV or DICOM)
            content = await file.read()
            
            # Check if DICOM
            if file.content_type == "application/dicom" or file.filename.endswith(".dcm"):
                data = content  # raw bytes for DICOM
            else:
                # Assume CSV, save to temp file and pass path
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                    temp_file.write(content)
                    data = temp_file.name
                    
        elif api_data:
            # API data as JSON
            try:
                data = json.loads(api_data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON format for API data")
        else:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Process data
        result = data_pipeline.ingest(data, center_id, str(current_user.id))
        
        # Check if ingestion was successful
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Ingestion failed"))
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            format_type = result.get("format", "unknown")
            record_count = len(result.get("data", [])) if isinstance(result.get("data", []), list) else 1
            
            html_content = f"""
            <div id="ingestion-result" hx-swap-oob="true">
                <div class="alert alert-success">
                    <h4>Ingestion Successful</h4>
                    <p>Successfully ingested {record_count} records of type {format_type} from center {center_id}</p>
                </div>
            </div>
            """
            return HTMLResponse(content=html_content)
        
        # Default: return JSON
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")
    finally:
        # Clean up temporary files
        if 'temp_file' in locals() and os.path.exists(locals()['temp_file'].name):
            os.unlink(locals()['temp_file'].name)
