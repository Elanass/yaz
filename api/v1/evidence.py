"""
Evidence API
Endpoints for evidence synthesis
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Path
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Dict, Any, Optional
import os
import json

from core.utils.helpers import load_csv
from features.evidence.evidence_engine import EvidenceSynthesisEngine
from features.auth.service import get_current_user, require_role, Domain, Scope

router = APIRouter(prefix="/evidence", tags=["Evidence"])

# Initialize evidence synthesis engine
evidence_engine = EvidenceSynthesisEngine()

@router.get("/generate/{domain}")
async def generate_evidence(
    request: Request,
    domain: str = Path(..., description="Domain area for insights"),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """
    Generate insights for a specific domain
    
    Returns JSON or HTML partial based on Accept header
    """
    try:
        # Validate domain
        if domain not in evidence_engine.domains:
            raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}. Supported domains: {evidence_engine.domains}")
        
        # Load data
        cases_path = os.path.join("data", "cases.csv")
        if not os.path.exists(cases_path):
            raise HTTPException(status_code=404, detail="No cases data available")
        
        cases = load_csv(cases_path)
        
        # Generate insights
        result = evidence_engine.generate_insights(domain, cases, str(current_user.id))
        
        # Check if generation was successful
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Evidence generation failed"))
        
        insights = result.get("insights", {})
        
        # Check if client wants HTML (HTMX request)
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            # Return HTMX-compatible partial
            html_content = f"""
            <div id="evidence-result" hx-swap-oob="true">
                <div class="card">
                    <div class="card-header">
                        <h3>Evidence Synthesis: {domain}</h3>
                        <span class="badge bg-primary">{insights.get("record_count", 0)} records</span>
                    </div>
                    <div class="card-body">
                        <h4>Key Statistics</h4>
                        <div class="row">
            """
            
            # Add statistics
            for field, stats in insights.get("statistics", {}).items():
                if stats.get("count", 0) > 0:
                    html_content += f"""
                            <div class="col-md-4 mb-3">
                                <div class="card">
                                    <div class="card-header">{field}</div>
                                    <div class="card-body">
                                        <p>Mean: {stats.get("mean", 0):.2f}</p>
                                        <p>Median: {stats.get("median", 0):.2f}</p>
                                        <p>Min: {stats.get("min", 0):.2f}</p>
                                        <p>Max: {stats.get("max", 0):.2f}</p>
                                    </div>
                                </div>
                            </div>
                    """
            
            html_content += """
                        </div>
                        
                        <h4>Comparisons</h4>
                        <div class="row">
            """
            
            # Add comparisons
            for comp_name, comp_data in insights.get("comparisons", {}).items():
                html_content += f"""
                            <div class="col-md-6 mb-3">
                                <div class="card">
                                    <div class="card-header">{comp_name}</div>
                                    <div class="card-body">
                """
                
                # Add statistical tests if available
                if "statistical_tests" in comp_data:
                    for test_name, test_result in comp_data["statistical_tests"].items():
                        significance = "Significant" if test_result.get("significant", False) else "Not significant"
                        html_content += f"""
                                        <div class="alert {'alert-success' if test_result.get('significant', False) else 'alert-secondary'}">
                                            <p>{test_name}: {significance} (p={test_result.get("p_value", 0):.4f})</p>
                                        </div>
                        """
                
                html_content += """
                                    </div>
                                </div>
                            </div>
                """
            
            html_content += """
                        </div>
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
        raise HTTPException(status_code=500, detail=f"Evidence generation failed: {str(e)}")
