"""
Cases API
Endpoints for managing retrospective and prospective case data
"""

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Dict, Any, Optional
import csv
import io
import json
import tempfile
import os
from datetime import datetime

from core.utils.helpers import load_csv, log_action
from features.auth.service import get_current_user, require_role, require_permission, Domain, Scope

router = APIRouter(prefix="/cases", tags=["Cases"])

# Path to cases data file
CASES_DATA_PATH = os.path.join("data", "cases.csv")

@router.get("")
async def get_cases(
    request: Request,
    limit: int = Query(100, description="Maximum number of cases to return"),
    offset: int = Query(0, description="Number of cases to skip"),
    center_id: Optional[str] = Query(None, description="Filter by center ID"),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Get cases from the database or CSV file
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Load cases from CSV file
        cases = []
        
        if os.path.exists(CASES_DATA_PATH):
            # Load from CSV
            all_cases = load_csv(CASES_DATA_PATH)
            
            # Apply filters
            if center_id:
                all_cases = [case for case in all_cases if case.get("center_id") == center_id]
            
            # Apply pagination
            cases = all_cases[offset:offset+limit]
        
        # Prepare results
        results = {
            "total": len(cases),
            "limit": limit,
            "offset": offset,
            "cases": cases
        }
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            
            # Create HTML representation of the cases
            cases_html = ""
            for case in cases:
                cases_html += f"""
                <tr>
                    <td>{case.get("id", "")}</td>
                    <td>{case.get("center_id", "")}</td>
                    <td>{case.get("age", "")}</td>
                    <td>{case.get("gender", "")}</td>
                    <td>{case.get("tumor_stage", "")}</td>
                    <td>{case.get("tumor_location", "")}</td>
                    <td>{case.get("treatment", "")}</td>
                    <td>{case.get("outcome", "")}</td>
                </tr>
                """
            
            html_content = f"""
            <div id="cases-table" hx-swap-oob="true">
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Center</th>
                            <th>Age</th>
                            <th>Gender</th>
                            <th>Stage</th>
                            <th>Location</th>
                            <th>Treatment</th>
                            <th>Outcome</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cases_html}
                    </tbody>
                </table>
                <div class="pagination">
                    <button class="btn btn-sm" hx-get="/api/v1/cases?offset={max(0, offset-limit)}&limit={limit}" hx-target="#cases-table">Previous</button>
                    <span>Page {offset//limit + 1}</span>
                    <button class="btn btn-sm" hx-get="/api/v1/cases?offset={offset+limit}&limit={limit}" hx-target="#cases-table">Next</button>
                </div>
            </div>
            """
            return HTMLResponse(content=html_content)
        
        # Default: return JSON
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cases: {str(e)}")

@router.post("")
async def upload_cases(
    request: Request,
    file: UploadFile = File(...),
    current_user = Depends(require_permission(Domain.HEALTHCARE, Scope.WRITE))
):
    """
    Upload cases from a CSV file
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(CASES_DATA_PATH), exist_ok=True)
        
        # Read CSV content
        content = await file.read()
        
        # Validate CSV format
        try:
            csv_content = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_content))
            
            # Check for required headers
            required_fields = ["id", "age", "gender", "tumor_stage", "tumor_location"]
            headers = reader.fieldnames or []
            
            missing_fields = [field for field in required_fields if field not in headers]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Count rows
            rows = list(reader)
            row_count = len(rows)
            
            # Write to file
            with open(CASES_DATA_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            
            # Log action
            log_action(str(current_user.id), "upload_cases", {
                "file_name": file.filename,
                "row_count": row_count
            })
            
            # Prepare response
            response_data = {
                "success": True,
                "message": f"Successfully uploaded {row_count} cases",
                "file_name": file.filename,
                "row_count": row_count
            }
            
            # Check if client wants HTML (HTMX request)
            accept = request.headers.get("Accept", "")
            if "text/html" in accept:
                # Return HTMX-compatible partial
                html_content = f"""
                <div id="upload-result" hx-swap-oob="true">
                    <div class="alert alert-success">
                        <h4>Upload Successful</h4>
                        <p>Successfully uploaded {row_count} cases from {file.filename}</p>
                    </div>
                    <button class="btn btn-primary" hx-get="/api/v1/cases" hx-target="#cases-table">Refresh Cases</button>
                </div>
                """
                return HTMLResponse(content=html_content)
            
            # Default: return JSON
            return response_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload cases: {str(e)}")
