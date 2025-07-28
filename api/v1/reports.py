"""
Reports API
Endpoints for report generation
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from typing import Dict, Any, Optional
import os
import json

from core.utils.helpers import load_csv
from features.export.report_generator import IntelligentReportGenerator
from features.auth.service import get_current_user, require_role, Domain, Scope

router = APIRouter(prefix="/reports", tags=["Reports"])

# Initialize report generator
report_generator = IntelligentReportGenerator()

@router.post("/generate")
async def generate_report(
    request: Request,
    params: Dict[str, Any] = Body(...),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Generate a report based on parameters
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Validate parameters
        required_fields = ["format", "data_source"]
        for field in required_fields:
            if field not in params:
                raise HTTPException(status_code=400, detail=f"Missing required parameter: {field}")
        
        # Load data based on source
        data_source = params.get("data_source")
        
        if data_source == "cases":
            # Load cases data
            cases_path = os.path.join("data", "cases.csv")
            if not os.path.exists(cases_path):
                raise HTTPException(status_code=404, detail="No cases data available")
            
            data = load_csv(cases_path)
            
        elif data_source == "evidence":
            # Load evidence data (domain required)
            domain = params.get("domain")
            if not domain:
                raise HTTPException(status_code=400, detail="Domain parameter required for evidence data source")
            
            # Generate insights from cases
            cases_path = os.path.join("data", "cases.csv")
            if not os.path.exists(cases_path):
                raise HTTPException(status_code=404, detail="No cases data available")
            
            cases = load_csv(cases_path)
            
            # Use evidence engine to generate insights
            from features.evidence.evidence_engine import EvidenceSynthesisEngine
            evidence_engine = EvidenceSynthesisEngine()
            
            result = evidence_engine.generate_insights(domain, cases, str(current_user.id))
            if not result.get("success", False):
                raise HTTPException(status_code=500, detail=result.get("error", "Evidence generation failed"))
            
            data = result.get("insights", {})
            
        elif data_source == "analysis":
            # Load analysis data
            analysis_type = params.get("analysis_type", "random_forest")
            patient_id = params.get("patient_id")
            
            if not patient_id:
                raise HTTPException(status_code=400, detail="patient_id parameter required for analysis data source")
            
            # Use the appropriate analyzer to get prediction
            from features.analysis.prospective import ProspectiveAnalyzer
            analyzer = ProspectiveAnalyzer()
            
            # Get patient data (in a real implementation, this would fetch from a database)
            # For now, we'll use mock data
            patient_data = {
                "id": patient_id,
                "age": 65,
                "tumor_stage": "T2N0M0",
                "comorbidities": ["hypertension"],
                "performance_status": 1
            }
            
            # Get prediction
            prediction = analyzer.predict(patient_data, analysis_type)
            data = {
                "patient_id": patient_id,
                "analysis_type": analysis_type,
                "prediction": prediction
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data_source: {data_source}")
        
        # Generate report
        report_params = {
            "format": params.get("format"),
            "title": params.get("title", f"{data_source.capitalize()} Report"),
            "filters": params.get("filters", {})
        }
        
        result = report_generator.generate_report(data, report_params, str(current_user.id))
        
        # Check if generation was successful
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Report generation failed"))
        
        report = result.get("report", {})
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            html_content = f"""
            <div id="report-result" hx-swap-oob="true">
                <div class="alert alert-success">
                    <h4>Report Generated</h4>
                    <p>Successfully generated {report.get("format", "").upper()} report: {report.get("title", "")}</p>
                </div>
                <div class="card">
                    <div class="card-body">
                        <p><strong>Report ID:</strong> {report.get("id", "")}</p>
                        <p><strong>Timestamp:</strong> {report.get("timestamp", "")}</p>
                        <p><strong>Records:</strong> {report.get("record_count", 0)}</p>
                        <p><strong>File:</strong> {os.path.basename(report.get("file_path", ""))}</p>
                        <a href="/api/v1/reports/download/{report.get("id", "")}" class="btn btn-primary">Download Report</a>
                    </div>
                </div>
            </div>
            """
            return HTMLResponse(content=html_content)
        
        # Default: return JSON
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Download a generated report
    """
    try:
        # Look for report file in reports directory
        reports_dir = report_generator.output_dir
        
        # Find file by report ID in filename
        report_file = None
        for filename in os.listdir(reports_dir):
            if report_id in filename:
                report_file = os.path.join(reports_dir, filename)
                break
        
        if not report_file:
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
        
        # Determine content type
        content_type = "application/octet-stream"  # Default
        if report_file.endswith(".csv"):
            content_type = "text/csv"
        elif report_file.endswith(".json"):
            content_type = "application/json"
        elif report_file.endswith(".pdf"):
            content_type = "application/pdf"
        
        # Return file
        return FileResponse(
            path=report_file,
            filename=os.path.basename(report_file),
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")
