"""
Reports page for the Gastric ADCI Platform
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from typing import Optional, Dict, Any, List
from fasthtml.common import *
import httpx

from features.auth.service import get_current_user, require_role, Domain, Scope
from web.components.layout import create_base_layout
from web.components.interface import clinical_form, clinical_table, clinical_card

router = APIRouter(prefix="/reports")

@router.get("/", response_class=HTMLResponse)
async def list_reports(
    request: Request, 
    page: int = 1,
    per_page: int = 10,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """List all generated reports with filtering and pagination"""
    
    # Fetch reports from API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{request.base_url}api/v1/reports",
            params={"page": page, "per_page": per_page},
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        reports = data.get("items", [])
        total = data.get("total", 0)
    
    # Transform reports to table rows
    headers = ["Report ID", "Case ID", "Generated Date", "Type", "Actions"]
    rows = []
    
    for report in reports:
        rows.append([
            report.get("id", ""),
            report.get("case_id", ""),
            report.get("created_at", "").split("T")[0],
            report.get("report_type", "Clinical"),
            Div(
                A(
                    "View",
                    href=f"/reports/{report.get('id')}",
                    class_="text-blue-600 hover:text-blue-900 mr-3"
                ),
                A(
                    "Download",
                    href=f"/api/v1/reports/download/{report.get('id')}",
                    class_="text-green-600 hover:text-green-900"
                ),
                class_="flex"
            )
        ])
    
    # Create pagination
    pagination = {
        "enabled": True,
        "total": total,
        "page": page,
        "per_page": per_page
    }
    
    # Create content
    content = Div(
        H1("Reports", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        Div(
            A(
                Div(
                    Svg(
                        Path(d="M12 6v6m0 0v6m0-6h6m-6 0H6"),
                        class_="h-5 w-5",
                        stroke="currentColor",
                        stroke_width="2",
                        fill="none",
                        viewBox="0 0 24 24"
                    ),
                    Span("Generate New Report", class_="ml-2"),
                    class_="flex items-center"
                ),
                href="/reports/generate",
                class_="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            ),
            class_="mb-6"
        ),
        
        clinical_table(
            headers=headers,
            rows=rows,
            id="reports-table",
            sortable=True,
            pagination=pagination
        ),
        
        id="main-content",
        class_="container mx-auto px-4 py-8"
    )
    
    return create_base_layout(
        title="Reports",
        content=content,
        user=current_user
    )

@router.get("/generate", response_class=HTMLResponse)
async def generate_report_form(
    request: Request,
    case_id: Optional[str] = None,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.WRITE))
):
    """Form for generating a new report"""
    
    # Fetch cases for dropdown if case_id not provided
    cases = []
    if not case_id:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{request.base_url}api/v1/cases",
                params={"per_page": 100},  # Get a large number for dropdown
                headers={"Authorization": f"Bearer {current_user['token']}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                cases = data.get("items", [])
    
    # Define form fields
    fields = [
        {
            "id": "case_id",
            "label": "Case",
            "type": "select",
            "required": True,
            "options": [
                {"value": c.get("id"), "text": f"{c.get('patient_id')} - {c.get('tumor_stage')}", "selected": c.get("id") == case_id}
                for c in cases
            ] if cases else [{"value": case_id, "text": case_id, "selected": True}]
        },
        {
            "id": "report_type",
            "label": "Report Type",
            "type": "select",
            "required": True,
            "options": [
                {"value": "clinical", "text": "Clinical Summary", "selected": True},
                {"value": "decision", "text": "Decision Support"},
                {"value": "evidence", "text": "Evidence Synthesis"},
                {"value": "comprehensive", "text": "Comprehensive Report"}
            ]
        },
        {
            "id": "include_sections",
            "label": "Include Sections",
            "type": "checkbox",
            "options": [
                {"value": "patient_info", "text": "Patient Information", "checked": True},
                {"value": "tumor_details", "text": "Tumor Details", "checked": True},
                {"value": "treatment_options", "text": "Treatment Options", "checked": True},
                {"value": "simulation_results", "text": "Markov Simulation Results", "checked": True},
                {"value": "supporting_evidence", "text": "Supporting Evidence", "checked": True},
                {"value": "recommendations", "text": "Recommendations", "checked": True}
            ]
        },
        {
            "id": "format",
            "label": "Report Format",
            "type": "radio",
            "options": [
                {"value": "pdf", "text": "PDF", "checked": True},
                {"value": "html", "text": "HTML"},
                {"value": "docx", "text": "Word Document"}
            ]
        },
        {
            "id": "notes",
            "label": "Additional Notes",
            "type": "textarea",
            "rows": 3,
            "placeholder": "Any specific information to include in the report..."
        }
    ]
    
    # Create content
    content = Div(
        H1("Generate Report", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        clinical_card(
            title="Report Parameters",
            content=clinical_form(
                action="/api/v1/reports/generate",
                fields=fields,
                submit_text="Generate Report",
                id="generate-report-form",
                method="post"
            ),
            id="report-params-card"
        ),
        
        # Results container for HTMX response
        Div(id="results"),
        
        id="main-content",
        class_="container mx-auto px-4 py-8 max-w-3xl"
    )
    
    return create_base_layout(
        title="Generate Report",
        content=content,
        user=current_user
    )

@router.get("/{report_id}", response_class=HTMLResponse)
async def view_report(
    request: Request,
    report_id: str,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """View a generated report"""
    
    # Fetch report from API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{request.base_url}api/v1/reports/{report_id}",
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        
        if response.status_code != 200:
            if response.status_code == 404:
                return create_base_layout(
                    title="Report Not Found",
                    content=Div(
                        H1("Report Not Found", class_="text-2xl font-bold text-gray-900 mb-6"),
                        P("The requested report could not be found.", class_="text-gray-600"),
                        A(
                            "Back to Reports",
                            href="/reports",
                            class_="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                        ),
                        class_="container mx-auto px-4 py-8 text-center"
                    ),
                    user=current_user
                )
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        report = response.json()
    
    # Create content
    content = Div(
        H1(f"Report: {report.get('id', '')}", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        Div(
            A(
                "Back to Reports",
                href="/reports",
                class_="text-blue-600 hover:text-blue-900 flex items-center"
            ),
            Div(
                A(
                    Div(
                        Svg(
                            Path(d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"),
                            class_="h-5 w-5",
                            stroke="currentColor",
                            stroke_width="2",
                            fill="none",
                            viewBox="0 0 24 24"
                        ),
                        Span("Download", class_="ml-2"),
                        class_="flex items-center"
                    ),
                    href=f"/api/v1/reports/download/{report_id}",
                    class_="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                ),
                A(
                    Div(
                        Svg(
                            Path(d="M12 6v6m0 0v6m0-6h6m-6 0H6"),
                            class_="h-5 w-5",
                            stroke="currentColor",
                            stroke_width="2",
                            fill="none",
                            viewBox="0 0 24 24"
                        ),
                        Span("New Report", class_="ml-2"),
                        class_="flex items-center"
                    ),
                    href="/reports/generate",
                    class_="ml-3 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                ),
            ),
            class_="flex justify-between mb-6"
        ),
        
        # Report preview
        Div(
            Div(
                Div(
                    H2("Report Preview", class_="text-xl font-bold text-gray-900 mb-4"),
                    P(
                        Span("Generated: ", class_="font-medium"),
                        report.get("created_at", "").replace("T", " ").split(".")[0],
                        class_="text-sm text-gray-500 mb-2"
                    ),
                    P(
                        Span("Format: ", class_="font-medium"),
                        report.get("format", "PDF").upper(),
                        class_="text-sm text-gray-500 mb-4"
                    ),
                    # Show preview if HTML available, otherwise show download prompt
                    Div(
                        Div(
                            report.get("content_html", "Report preview not available"),
                            class_="prose max-w-none"
                        ) if report.get("content_html") else Div(
                            P("This report is available in PDF format.", class_="text-gray-600 mb-4"),
                            A(
                                "Download Report",
                                href=f"/api/v1/reports/download/{report_id}",
                                class_="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                            ),
                            class_="text-center py-8"
                        ),
                        class_="mt-4 p-6 border border-gray-200 rounded-lg bg-white"
                    ),
                    class_="p-6"
                ),
                class_="bg-gray-50 shadow overflow-hidden sm:rounded-lg"
            ),
            class_="mt-6"
        ),
        
        id="main-content",
        class_="container mx-auto px-4 py-8"
    )
    
    return create_base_layout(
        title=f"Report: {report.get('id', '')}",
        content=content,
        user=current_user
    )
