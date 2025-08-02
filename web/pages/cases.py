"""
Case management pages for the Gastric ADCI Platform
"""

from fastapi import APIRouter as FastAPIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Dict, Any, List
from fasthtml.common import Div, H1, H2, H3, H4, P, Form as FHTMLForm, Input, Button, A, Br, Script, Table, Tr, Td, Th
import httpx

from core.dependencies import require_auth, require_role, Domain, Scope
from web.components.layout import create_base_layout
from web.components.interface import clinical_form, clinical_table, clinical_card

router = FastAPIRouter(prefix="/cases")
    
@router.get("/")
async def list_cases(
    request: Request, 
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """List all cases with filtering and pagination"""
    
    import httpx
    
    # Fetch cases from API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{request.base_url}api/v1/cases",
            params={"page": page, "per_page": per_page, "search": search},
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        cases = data.get("items", [])
        total = data.get("total", 0)
    
    # Create search form
    search_form = Form(
        Div(
            Input(
                type_="search",
                name="search",
                id="search",
                placeholder="Search cases...",
                value=search if search else "",
                class_="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            ),
            Button(
                "Search",
                type_="submit",
                class_="ml-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            ),
            class_="flex"
        ),
        method="get",
        class_="mb-6"
    )
    
    # Transform cases to table rows
    headers = ["Patient ID", "Age", "Gender", "Stage", "Created", "Actions"]
    rows = []
    
    for case in cases:
        rows.append([
            case.get("patient_id", ""),
            str(case.get("age", "")),
            case.get("gender", ""),
            case.get("tumor_stage", ""),
            case.get("created_at", "").split("T")[0],
            Div(
                A(
                    "View",
                    href=f"/cases/{case.get('id')}",
                    class_="text-blue-600 hover:text-blue-900 mr-3"
                ),
                A(
                    "Analyze",
                    href=f"/cases/{case.get('id')}/analyze",
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
        # Header with Add Case button
        Div(
            H1("Case Management", class_="text-2xl font-bold text-[var(--text-primary)] mb-6"),
            A(
                Div(
                    "✚",
                    "Add New Case",
                    class_="flex items-center gap-2"
                ),
                href="/cases/add",
                class_="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            ),
            class_="flex justify-between items-center mb-6"
        ),
        search_form,
        clinical_table(
            headers=headers,
            rows=rows,
            id="cases-table",
            sortable=True,
            pagination=pagination
        ),
        id="main-content",
        class_="container mx-auto px-4 py-8"
    )
    
    return create_base_layout(
        title="Case Management",
        content=content,
        user=current_user
    )

@router.get("/new")
async def new_case_form(
    request: Request,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.WRITE))
):
    """Form for creating a new case"""
    
    
    # Define form fields
    fields = [
        {
            "id": "patient_id",
            "label": "Patient ID",
            "type": "text",
            "required": True,
            "description": "Unique identifier for the patient"
        },
        {
            "id": "age",
            "label": "Age",
            "type": "number",
            "required": True,
            "min": 18,
            "max": 120
        },
        {
            "id": "gender",
            "label": "Gender",
            "type": "select",
            "required": True,
            "options": [
                {"value": "", "text": "Select gender"},
                {"value": "male", "text": "Male"},
                {"value": "female", "text": "Female"},
                {"value": "other", "text": "Other"}
            ]
        },
        {
            "id": "tumor_location",
            "label": "Tumor Location",
            "type": "select",
            "required": True,
            "options": [
                {"value": "", "text": "Select location"},
                {"value": "cardia", "text": "Cardia"},
                {"value": "fundus", "text": "Fundus"},
                {"value": "body", "text": "Body"},
                {"value": "antrum", "text": "Antrum"},
                {"value": "pylorus", "text": "Pylorus"},
                {"value": "diffuse", "text": "Diffuse"}
            ]
        },
        {
            "id": "tumor_stage",
            "label": "Tumor Stage",
            "type": "select",
            "required": True,
            "options": [
                {"value": "", "text": "Select stage"},
                {"value": "T1N0M0", "text": "Stage IA (T1N0M0)"},
                {"value": "T1N1M0", "text": "Stage IB (T1N1M0)"},
                {"value": "T2N0M0", "text": "Stage IB (T2N0M0)"},
                {"value": "T2N1M0", "text": "Stage IIA (T2N1M0)"},
                {"value": "T3N0M0", "text": "Stage IIA (T3N0M0)"},
                {"value": "T3N1M0", "text": "Stage IIB (T3N1M0)"},
                {"value": "T4aN0M0", "text": "Stage IIB (T4aN0M0)"},
                {"value": "T4aN1M0", "text": "Stage IIIA (T4aN1M0)"},
                {"value": "T4bN0M0", "text": "Stage IIIA (T4bN0M0)"},
                {"value": "T4bN1M0", "text": "Stage IIIB (T4bN1M0)"},
                {"value": "T1-4N3M0", "text": "Stage IIIC (T1-4N3M0)"},
                {"value": "T1-4N1-3M1", "text": "Stage IV (T1-4N1-3M1)"}
            ]
        },
        {
            "id": "histology",
            "label": "Histological Type",
            "type": "select",
            "required": True,
            "options": [
                {"value": "", "text": "Select type"},
                {"value": "intestinal", "text": "Intestinal"},
                {"value": "diffuse", "text": "Diffuse"},
                {"value": "mixed", "text": "Mixed"},
                {"value": "indeterminate", "text": "Indeterminate"}
            ]
        },
        {
            "id": "comorbidities",
            "label": "Comorbidities",
            "type": "checkbox",
            "options": [
                {"value": "diabetes", "text": "Diabetes"},
                {"value": "hypertension", "text": "Hypertension"},
                {"value": "cardiovascular", "text": "Cardiovascular Disease"},
                {"value": "pulmonary", "text": "Pulmonary Disease"},
                {"value": "renal", "text": "Renal Disease"},
                {"value": "liver", "text": "Liver Disease"}
            ]
        },
        {
            "id": "previous_treatments",
            "label": "Previous Treatments",
            "type": "checkbox",
            "options": [
                {"value": "chemotherapy", "text": "Chemotherapy"},
                {"value": "radiation", "text": "Radiation Therapy"},
                {"value": "surgery", "text": "Previous Surgery"},
                {"value": "targeted", "text": "Targeted Therapy"}
            ]
        },
        {
            "id": "notes",
            "label": "Clinical Notes",
            "type": "textarea",
            "rows": 4,
            "placeholder": "Additional clinical information..."
        }
    ]
    
    # Create content
    content = Div(
        H1("New Case", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        clinical_card(
            title="Patient Information",
            content=clinical_form(
                action="/api/v1/cases",
                fields=fields,
                submit_text="Create Case",
                id="new-case-form"
            ),
            id="new-case-card"
        ),
        
        # Results container for HTMX response
        Div(id="results"),
        
        id="main-content",
        class_="container mx-auto px-4 py-8 max-w-3xl"
    )
    
    return create_base_layout(
        title="New Case",
        content=content,
        user=current_user
    )

@router.get("/{case_id}")
async def view_case(
    request: Request,
    case_id: str,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """View details of a specific case"""
    
    import httpx
    
    # Fetch case from API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{request.base_url}api/v1/cases/{case_id}",
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        
        if response.status_code != 200:
            if response.status_code == 404:
                return create_base_layout(
                    title="Case Not Found",
                    content=Div(
                        H1("Case Not Found", class_="text-2xl font-bold text-gray-900 mb-6"),
                        P("The requested case could not be found.", class_="text-gray-600"),
                        A(
                            "Back to Cases",
                            href="/cases",
                            class_="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                        ),
                        class_="container mx-auto px-4 py-8 text-center"
                    ),
                    user=current_user
                )
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        case = response.json()
    
    # Create patient info section
    patient_info = Dl(
        *[
            Div(
                Dt(k.replace("_", " ").title(), class_="text-sm font-medium text-gray-500"),
                Dd(
                    str(v) if not isinstance(v, list) else ", ".join(v),
                    class_="mt-1 text-sm text-gray-900"
                ),
                class_="py-3 sm:grid sm:grid-cols-3 sm:gap-4"
            )
            for k, v in case.items()
            if k not in ["id", "audit_trail", "created_at", "updated_at", "created_by"]
        ],
        class_="divide-y divide-gray-200"
    )
    
    # Create audit trail section if it exists
    audit_trail = case.get("audit_trail", [])
    audit_list = []
    
    for entry in audit_trail:
        audit_list.append(
            Li(
                Div(
                    Span(entry.get("timestamp", ""), class_="text-xs text-gray-500"),
                    P(
                        B(entry.get("user", "")),
                        " ",
                        entry.get("action", ""),
                        class_="text-sm"
                    ),
                    class_="mb-2"
                )
            )
        )
    
    # Create content
    content = Div(
        H1(f"Case: {case.get('patient_id', '')}", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        Div(
            A(
                "Back to Cases",
                href="/cases",
                class_="text-blue-600 hover:text-blue-900 flex items-center"
            ),
            Div(
                A(
                    Div(
                        Svg(
                            Path(d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"),
                            class_="h-5 w-5",
                            stroke="currentColor",
                            stroke_width="2",
                            fill="none",
                            viewBox="0 0 24 24"
                        ),
                        Span("Edit", class_="ml-2"),
                        class_="flex items-center"
                    ),
                    href=f"/cases/{case_id}/edit",
                    class_="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 mr-3"
                ),
                A(
                    Div(
                        Svg(
                            Path(d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"),
                            Path(d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"),
                            class_="h-5 w-5",
                            stroke="currentColor",
                            stroke_width="2",
                            fill="none",
                            viewBox="0 0 24 24"
                        ),
                        Span("Analyze", class_="ml-2"),
                        class_="flex items-center"
                    ),
                    href=f"/cases/{case_id}/analyze",
                    class_="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                ),
            ),
            class_="flex justify-between mb-6"
        ),
        
        Div(
            Div(
                clinical_card(
                    title="Patient Information",
                    content=patient_info,
                    id="patient-info-card"
                ),
                class_="lg:col-span-2"
            ),
            Div(
                clinical_card(
                    title="Audit Trail",
                    content=Ul(
                        *audit_list,
                        class_="divide-y divide-gray-200"
                    ) if audit_list else P("No audit records available", class_="text-sm text-gray-500 italic"),
                    id="audit-trail-card"
                ),
                class_="lg:col-span-1"
            ),
            class_="grid grid-cols-1 lg:grid-cols-3 gap-6"
        ),
        
        id="main-content",
        class_="container mx-auto px-4 py-8"
    )
    
    return create_base_layout(
        title=f"Case: {case.get('patient_id', '')}",
        content=content,
        user=current_user
    )

@router.get("/{case_id}/analyze")
async def analyze_case(
    request: Request,
    case_id: str,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.READ))
):
    """Analysis page for a specific case"""
    
    import httpx
    from web.components.interface import treatment_comparison, evidence_panel, risk_indicator
    
    # Fetch case from API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{request.base_url}api/v1/cases/{case_id}",
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        
        if response.status_code != 200:
            if response.status_code == 404:
                return create_base_layout(
                    title="Case Not Found",
                    content=Div(
                        H1("Case Not Found", class_="text-2xl font-bold text-gray-900 mb-6"),
                        P("The requested case could not be found.", class_="text-gray-600"),
                        A(
                            "Back to Cases",
                            href="/cases",
                            class_="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                        ),
                        class_="container mx-auto px-4 py-8 text-center"
                    ),
                    user=current_user
                )
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        case = response.json()
    
    # Create analysis buttons
    analysis_buttons = Div(
        Button(
            "Run Precision Analysis",
            id="run-precision-analysis",
            class_="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
            **{
                "hx-post": f"/api/v1/precision/predict",
                "hx-trigger": "click",
                "hx-target": "#precision-results",
                "hx-swap": "innerHTML",
                "hx-include": "#analysis-form",
                "hx-indicator": "#precision-indicator"
            }
        ),
        Button(
            "Run Markov Simulation",
            id="run-markov-simulation",
            class_="ml-3 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500",
            **{
                "hx-post": f"/api/v1/markov/simulate",
                "hx-trigger": "click",
                "hx-target": "#markov-results",
                "hx-swap": "innerHTML",
                "hx-include": "#analysis-form",
                "hx-indicator": "#markov-indicator"
            }
        ),
        Button(
            "Generate Evidence",
            id="generate-evidence",
            class_="ml-3 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500",
            **{
                "hx-post": f"/api/v1/evidence/generate/gastric",
                "hx-trigger": "click",
                "hx-target": "#evidence-results",
                "hx-swap": "innerHTML",
                "hx-include": "#analysis-form",
                "hx-indicator": "#evidence-indicator"
            }
        ),
        class_="mt-4 flex flex-wrap gap-2"
    )
    
    # Create hidden form with case data
    hidden_form = Form(
        *[
            Input(
                type_="hidden",
                name=k,
                value=str(v) if not isinstance(v, list) else ",".join(v)
            )
            for k, v in case.items()
            if k not in ["id", "audit_trail", "created_at", "updated_at", "created_by"]
        ],
        id="analysis-form"
    )
    
    # Create content
    content = Div(
        H1(f"Analyze Case: {case.get('patient_id', '')}", class_="text-2xl font-bold text-gray-900 mb-6"),
        
        Div(
            A(
                "Back to Case",
                href=f"/cases/{case_id}",
                class_="text-blue-600 hover:text-blue-900 flex items-center"
            ),
            A(
                Div(
                    Svg(
                        Path(d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"),
                        class_="h-5 w-5",
                        stroke="currentColor",
                        stroke_width="2",
                        fill="none",
                        viewBox="0 0 24 24"
                    ),
                    Span("Generate Report", class_="ml-2"),
                    class_="flex items-center"
                ),
                href=f"/reports/generate?case_id={case_id}",
                class_="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            ),
            class_="flex justify-between mb-6"
        ),
        
        Div(
            Div(
                H2("Patient Summary", class_="text-xl font-bold text-gray-900 mb-4"),
                Dl(
                    *[
                        Div(
                            Dt(k.replace("_", " ").title(), class_="text-sm font-medium text-gray-500"),
                            Dd(
                                str(v) if not isinstance(v, list) else ", ".join(v),
                                class_="mt-1 text-sm text-gray-900"
                            ),
                            class_="py-2 sm:grid sm:grid-cols-3 sm:gap-4"
                        )
                        for k, v in case.items()
                        if k in ["patient_id", "age", "gender", "tumor_stage", "tumor_location", "histology"]
                    ],
                    class_="divide-y divide-gray-200"
                ),
                hidden_form,
                analysis_buttons,
                class_="bg-white shadow overflow-hidden sm:rounded-lg p-6"
            ),
            class_="mb-6"
        ),
        
        Div(
            Div(
                # Precision Results
                Div(
                    H2("Precision Decision Analysis", class_="text-xl font-bold text-gray-900 mb-4"),
                    Div(
                        P("Click 'Run Precision Analysis' to generate results.", class_="text-gray-500 italic"),
                        id="precision-results"
                    ),
                    Div(
                        Div(class_="w-6 h-6 border-t-2 border-b-2 border-blue-500 rounded-full animate-spin"),
                        Span("Analyzing...", class_="ml-2 text-gray-700"),
                        id="precision-indicator",
                        class_="htmx-indicator flex items-center justify-center py-4"
                    ),
                    class_="bg-white shadow overflow-hidden sm:rounded-lg p-6 mb-6"
                ),
                
                # Markov Results
                Div(
                    H2("Markov Chain Simulation", class_="text-xl font-bold text-gray-900 mb-4"),
                    Div(
                        P("Click 'Run Markov Simulation' to generate results.", class_="text-gray-500 italic"),
                        id="markov-results"
                    ),
                    Div(
                        Div(class_="w-6 h-6 border-t-2 border-b-2 border-green-500 rounded-full animate-spin"),
                        Span("Simulating...", class_="ml-2 text-gray-700"),
                        id="markov-indicator",
                        class_="htmx-indicator flex items-center justify-center py-4"
                    ),
                    class_="bg-white shadow overflow-hidden sm:rounded-lg p-6 mb-6"
                ),
                
                # Evidence Results
                Div(
                    H2("Evidence Synthesis", class_="text-xl font-bold text-gray-900 mb-4"),
                    Div(
                        P("Click 'Generate Evidence' to retrieve supporting evidence.", class_="text-gray-500 italic"),
                        id="evidence-results"
                    ),
                    Div(
                        Div(class_="w-6 h-6 border-t-2 border-b-2 border-purple-500 rounded-full animate-spin"),
                        Span("Gathering evidence...", class_="ml-2 text-gray-700"),
                        id="evidence-indicator",
                        class_="htmx-indicator flex items-center justify-center py-4"
                    ),
                    class_="bg-white shadow overflow-hidden sm:rounded-lg p-6"
                ),
                
                class_="lg:col-span-2"
            ),
            
            Div(
                Div(
                    H2("Need Help?", class_="text-xl font-bold text-gray-900 mb-4"),
                    Div(
                        H3("Understanding the Analysis", class_="text-lg font-medium text-gray-900 mb-2"),
                        Ul(
                            Li("Precision Analysis: Provides personalized treatment recommendations with confidence scores.", class_="mb-2"),
                            Li("Markov Simulation: Projects disease progression under different treatment scenarios.", class_="mb-2"),
                            Li("Evidence Synthesis: Collects supporting evidence from clinical guidelines and literature.", class_="mb-2"),
                            class_="list-disc pl-5 text-gray-700"
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        H3("Clinical Interpretation", class_="text-lg font-medium text-gray-900 mb-2"),
                        P("All recommendations should be interpreted in the context of clinical judgment and patient preferences.", class_="text-gray-700 mb-2"),
                        P("Confidence scores indicate the strength of evidence supporting each recommendation.", class_="text-gray-700 mb-2"),
                        class_="mb-4"
                    ),
                    A(
                        "View Documentation",
                        href="/docs/clinical",
                        target="_blank",
                        class_="text-blue-600 hover:text-blue-800"
                    ),
                    class_="bg-white shadow overflow-hidden sm:rounded-lg p-6"
                ),
                class_="lg:col-span-1"
            ),
            
            class_="grid grid-cols-1 lg:grid-cols-3 gap-6"
        ),
        
        id="main-content",
        class_="container mx-auto px-4 py-8"
    )
    
    return create_base_layout(
        title=f"Analyze Case: {case.get('patient_id', '')}",
        content=content,
        user=current_user
    )

@router.get("/add")
async def add_case_form(
    request: Request,
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.WRITE))
):
    """Display add case form"""
    
    content = Div(
        H1("Add New Case", class_="text-2xl font-bold text-[var(--text-primary)] mb-6"),
        
        FHTMLForm(
            Div(
                # Patient Information
                H3("Patient Information", class_="text-lg font-semibold mb-4 text-[var(--text-primary)]"),
                Div(
                    Div(
                        Input(
                            type_="text", 
                            name="patient_id", 
                            placeholder="Patient ID", 
                            required=True,
                            class_="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-md text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Input(
                            type_="number", 
                            name="age", 
                            placeholder="Age", 
                            required=True,
                            class_="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-md text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Input(
                            type_="text", 
                            name="gender", 
                            placeholder="Gender (M/F)", 
                            required=True,
                            class_="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-md text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        class_="mb-4"
                    ),
                    class_="grid grid-cols-1 md:grid-cols-3 gap-4"
                ),
                
                # Clinical Information
                H3("Clinical Information", class_="text-lg font-semibold mb-4 mt-6 text-[var(--text-primary)]"),
                Div(
                    Div(
                        Input(
                            type_="text", 
                            name="tumor_stage", 
                            placeholder="Tumor Stage (e.g., T3N1M0)", 
                            required=True,
                            class_="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-md text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        class_="mb-4"
                    ),
                    Div(
                        Input(
                            type_="text", 
                            name="histology", 
                            placeholder="Histology", 
                            class_="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-md text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        class_="mb-4"
                    ),
                    class_="grid grid-cols-1 md:grid-cols-2 gap-4"
                ),
                
                # Actions
                Div(
                    Button(
                        "Create Case",
                        type_="submit",
                        class_="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mr-4"
                    ),
                    A(
                        "Cancel",
                        href="/cases",
                        class_="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md"
                    ),
                    class_="mt-6"
                ),
                class_="bg-[var(--bg-secondary)] p-6 rounded-lg"
            ),
            action="/cases/add",
            method="post"
        ),
        class_="max-w-4xl mx-auto p-6"
    )
    
    return create_base_layout(
        title="Add New Case",
        content=content,
        request=request
    )

@router.post("/add")
async def create_case(
    request: Request,
    patient_id: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    tumor_stage: str = Form(...),
    histology: str = Form(""),
    current_user = Depends(require_role(Domain.HEALTHCARE, Scope.WRITE))
):
    """Create a new case"""
    
    case_data = {
        "patient_id": patient_id,
        "age": age,
        "gender": gender,
        "tumor_stage": tumor_stage,
        "histology": histology
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{request.base_url}api/v1/cases",
                json=case_data,
                headers={"Authorization": f"Bearer {current_user['token']}"}
            )
            
            if response.status_code == 201:
                # Case created successfully
                case = response.json()
                return RedirectResponse(url=f"/cases/{case['id']}", status_code=303)
            else:
                # Handle error
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except Exception as e:
        # For now, redirect back to cases list
        return RedirectResponse(url="/cases", status_code=303)
