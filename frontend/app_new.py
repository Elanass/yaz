"""
FastHTML frontend application for Gastric ADCI Platform
Integrates HTMX for reactive UI and Gun.js for distributed state
"""

import os
import json
from fasthtml.common import *
from .islands.protocols import ProtocolsIsland
from .islands.decision import DecisionIsland
from .components.layout import BaseLayout
from .components.pwa import generate_manifest, generate_service_worker

# Initialize FastHTML app
app = FastHTML(
    title="Gastric ADCI Platform",
    pico=False,  # We'll use our custom CSS
    hdrs=[
        Link(rel="stylesheet", href="/static/css/app.css"),
        Link(rel="manifest", href="/manifest.json"),
        Meta(name="theme-color", content="#2563eb"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Script(src="/static/js/app.js", defer=True),
        Script(src="/static/js/gun-integration.js", defer=True),
        Script(src="https://unpkg.com/htmx.org@1.9.10", defer=True)
    ],
    static_path="frontend/static"
)

# Mock data for development
MOCK_PROTOCOLS = [
    {
        "id": "1",
        "name": "ADCI Gastric Cancer Protocol",
        "category": "surgical",
        "description": "Adaptive Decision Confidence Index protocol for gastric cancer surgical intervention. Evidence-based approach with real-time confidence scoring.",
        "version": "2.1",
        "status": "active",
        "applicable_stages": ["I", "II", "III"],
        "evidence_level": "1",
        "total_patients_treated": 342,
        "success_rate": 87.3,
        "updated_at": "2024-01-15T10:30:00Z",
        "guidelines_source": "NCCN 2024"
    },
    {
        "id": "2", 
        "name": "FLOT Neoadjuvant Protocol",
        "category": "chemotherapy",
        "description": "Fluorouracil, Leucovorin, Oxaliplatin, and Docetaxel neoadjuvant chemotherapy protocol for resectable gastric adenocarcinoma.",
        "version": "1.8",
        "status": "active", 
        "applicable_stages": ["II", "III"],
        "evidence_level": "1",
        "total_patients_treated": 198,
        "success_rate": 92.1,
        "updated_at": "2024-01-10T14:20:00Z",
        "guidelines_source": "ESMO 2023"
    },
    {
        "id": "3",
        "name": "Minimally Invasive Gastrectomy",
        "category": "surgical", 
        "description": "Laparoscopic and robotic gastrectomy techniques with enhanced recovery protocols.",
        "version": "3.0",
        "status": "active",
        "applicable_stages": ["0", "I", "II"],
        "evidence_level": "2",
        "total_patients_treated": 156,
        "success_rate": 89.7,
        "updated_at": "2024-01-05T09:15:00Z",
        "guidelines_source": "JGCA 2024"
    }
]

# Routes
@app.get("/")
def landing_page():
    """Landing page - main entry point"""
    content = Div(
        cls="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10",
        children=[
            # Hero section
            Div(
                cls="hero min-h-screen",
                children=[
                    Div(
                        cls="hero-content text-center",
                        children=[
                            Div(
                                cls="max-w-md",
                                children=[
                                    H1("Gastric ADCI Platform", cls="text-5xl font-bold text-primary mb-6"),
                                    P("Precision oncology decision support for gastric surgery using the Adaptive Decision Confidence Index framework.",
                                      cls="text-lg mb-8 text-base-content/80"),
                                    Div(
                                        cls="flex gap-4 justify-center",
                                        children=[
                                            A("View Protocols", href="/protocols", cls="btn btn-primary btn-lg"),
                                            A("Decision Engine", href="/decision", cls="btn btn-outline btn-lg")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Features preview
            Div(
                cls="container mx-auto px-4 py-16",
                children=[
                    H2("Key Features", cls="text-3xl font-bold text-center mb-12"),
                    Div(
                        cls="grid grid-cols-1 md:grid-cols-3 gap-8",
                        children=[
                            Div(
                                cls="card bg-base-100 shadow-lg",
                                children=[
                                    Div(
                                        cls="card-body text-center",
                                        children=[
                                            Div("🧠", cls="text-4xl mb-4"),
                                            H3("AI Decision Support", cls="card-title justify-center"),
                                            P("Advanced algorithms provide evidence-based treatment recommendations with confidence scoring.")
                                        ]
                                    )
                                ]
                            ),
                            Div(
                                cls="card bg-base-100 shadow-lg",
                                children=[
                                    Div(
                                        cls="card-body text-center",
                                        children=[
                                            Div("📋", cls="text-4xl mb-4"),
                                            H3("Clinical Protocols", cls="card-title justify-center"),
                                            P("Comprehensive library of evidence-based protocols for gastric oncology and surgery.")
                                        ]
                                    )
                                ]
                            ),
                            Div(
                                cls="card bg-base-100 shadow-lg",
                                children=[
                                    Div(
                                        cls="card-body text-center",
                                        children=[
                                            Div("📊", cls="text-4xl mb-4"),
                                            H3("Evidence Analytics", cls="card-title justify-center"),
                                            P("Real-time analysis of treatment outcomes and comparative effectiveness data.")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    
    return BaseLayout(
        title="Gastric ADCI Platform",
        content=content
    )

@app.get("/protocols")
def protocols_page(
    search: str = "",
    category: str = "",
    status: str = "",
    stage: str = "",
    evidence_level: str = "",
    page: int = 1
):
    """Clinical protocols listing and management"""
    # Filter protocols based on parameters
    filtered_protocols = MOCK_PROTOCOLS.copy()
    
    if search:
        filtered_protocols = [p for p in filtered_protocols 
                            if search.lower() in p["name"].lower() or 
                               search.lower() in p["description"].lower()]
    
    if category:
        filtered_protocols = [p for p in filtered_protocols if p["category"] == category]
    
    if status:
        filtered_protocols = [p for p in filtered_protocols if p["status"] == status]
    
    if stage:
        filtered_protocols = [p for p in filtered_protocols if stage in p["applicable_stages"]]
    
    if evidence_level:
        filtered_protocols = [p for p in filtered_protocols if p["evidence_level"] == evidence_level]
    
    filters = {
        "search": search,
        "category": category, 
        "status": status,
        "stage": stage,
        "evidence_level": evidence_level
    }
    
    content = ProtocolsIsland(
        protocols=filtered_protocols,
        total=len(filtered_protocols),
        current_page=page,
        filters=filters
    )
    
    return BaseLayout(
        title="Clinical Protocols - Gastric ADCI",
        content=content
    )

@app.get("/decision")
def decision_page():
    """Decision support engine"""
    content = DecisionIsland(
        protocols=MOCK_PROTOCOLS
    )
    
    return BaseLayout(
        title="Decision Engine - Gastric ADCI", 
        content=content
    )

@app.post("/decision/analyze")
def analyze_decision(request):
    """Analyze patient data and provide recommendations"""
    # Mock analysis results
    mock_results = {
        "primary_recommendation": "Neoadjuvant FLOT followed by D2 gastrectomy",
        "recommendation_rationale": "Based on T3N2M0 staging and favorable performance status, neoadjuvant chemotherapy followed by surgery offers the best long-term outcome.",
        "confidence_score": 0.87,
        "confidence_explanation": "High confidence based on strong evidence from multiple RCTs",
        "evidence_level": "1",
        "evidence_quality": "High quality randomized controlled trials",
        "risk_assessment": {
            "overall_risk": "moderate",
            "surgical_risk": "low",
            "treatment_toxicity": "moderate"
        },
        "alternative_recommendations": [
            {
                "treatment": "Immediate surgery with adjuvant therapy",
                "rationale": "Alternative for patients who cannot tolerate neoadjuvant treatment",
                "confidence": 0.72
            },
            {
                "treatment": "Palliative chemotherapy",
                "rationale": "If staging reveals unexpected metastatic disease",
                "confidence": 0.15
            }
        ],
        "risk_factors": [
            "Advanced nodal involvement (N2)",
            "Age >70 years increases surgical risk",
            "Previous cardiac history"
        ],
        "clinical_considerations": [
            "Consider cardiac clearance before surgery",
            "Monitor for treatment-related toxicity",
            "Multidisciplinary team review recommended"
        ]
    }
    
    from .islands.decision import DecisionResults
    return DecisionResults(mock_results)

# PWA routes
@app.get("/manifest.json")
def pwa_manifest():
    """PWA manifest file"""
    return generate_manifest()

@app.get("/sw.js")
def service_worker():
    """Service worker for PWA functionality"""
    return generate_service_worker()

# API Base URL configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
