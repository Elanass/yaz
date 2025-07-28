"""
Decision Engine Island - Interactive decision support interface.
"""

import json
from typing import Any, Dict, List, Optional

from fasthtml.common import *


def PatientInputForm(patient_data: Dict = None) -> Div:
    """Patient data input form for decision engine."""
    if patient_data is None:
        patient_data = {}
    
    return Div(
        cls="card bg-base-100 shadow-md",
        children=[
            Div(
                cls="card-body",
                children=[
                    H3("Patient Information", cls="card-title text-lg text-primary mb-4"),
                    
                    Form(
                        id="patient-form",
                        cls="space-y-4",
                        children=[
                            # Basic demographics
                            Div(
                                cls="grid grid-cols-1 md:grid-cols-2 gap-4",
                                children=[
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("Age", cls="label label-text font-medium"),
                                            Input(
                                                type="number",
                                                name="age",
                                                min="18",
                                                max="120",
                                                value=patient_data.get("age", ""),
                                                cls="input input-bordered",
                                                placeholder="Patient age",
                                                required=True
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("Gender", cls="label label-text font-medium"),
                                            Select(
                                                name="gender",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select gender", value="", disabled=True,
                                                          selected="" == patient_data.get("gender", "")),
                                                    Option("Male", value="male",
                                                          selected="male" == patient_data.get("gender")),
                                                    Option("Female", value="female",
                                                          selected="female" == patient_data.get("gender")),
                                                    Option("Other", value="other",
                                                          selected="other" == patient_data.get("gender"))
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # Cancer staging
                            Div(
                                cls="grid grid-cols-1 md:grid-cols-3 gap-4",
                                children=[
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("T Stage", cls="label label-text font-medium"),
                                            Select(
                                                name="t_stage",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select T stage", value="", disabled=True),
                                                    Option("Tis", value="Tis"),
                                                    Option("T1a", value="T1a"),
                                                    Option("T1b", value="T1b"),
                                                    Option("T2", value="T2"),
                                                    Option("T3", value="T3"),
                                                    Option("T4a", value="T4a"),
                                                    Option("T4b", value="T4b")
                                                ]
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("N Stage", cls="label label-text font-medium"),
                                            Select(
                                                name="n_stage",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select N stage", value="", disabled=True),
                                                    Option("N0", value="N0"),
                                                    Option("N1", value="N1"),
                                                    Option("N2", value="N2"),
                                                    Option("N3a", value="N3a"),
                                                    Option("N3b", value="N3b")
                                                ]
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("M Stage", cls="label label-text font-medium"),
                                            Select(
                                                name="m_stage",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select M stage", value="", disabled=True),
                                                    Option("M0", value="M0"),
                                                    Option("M1", value="M1")
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # Performance status and comorbidities
                            Div(
                                cls="grid grid-cols-1 md:grid-cols-2 gap-4",
                                children=[
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("ECOG Performance Status", cls="label label-text font-medium"),
                                            Select(
                                                name="ecog_status",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select ECOG status", value="", disabled=True),
                                                    Option("0 - Fully active", value="0"),
                                                    Option("1 - Restricted in strenuous activity", value="1"),
                                                    Option("2 - Ambulatory, up >50% of time", value="2"),
                                                    Option("3 - Limited self-care", value="3"),
                                                    Option("4 - Completely disabled", value="4")
                                                ]
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("ASA Score", cls="label label-text font-medium"),
                                            Select(
                                                name="asa_score",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select ASA score", value="", disabled=True),
                                                    Option("I - Normal healthy patient", value="1"),
                                                    Option("II - Mild systemic disease", value="2"),
                                                    Option("III - Severe systemic disease", value="3"),
                                                    Option("IV - Life-threatening disease", value="4"),
                                                    Option("V - Moribund patient", value="5")
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # Laboratory values
                            Div(
                                cls="grid grid-cols-1 md:grid-cols-3 gap-4",
                                children=[
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("Hemoglobin (g/dL)", cls="label label-text font-medium"),
                                            Input(
                                                type="number",
                                                name="hemoglobin",
                                                step="0.1",
                                                min="0",
                                                max="20",
                                                value=patient_data.get("hemoglobin", ""),
                                                cls="input input-bordered",
                                                placeholder="e.g., 12.5"
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("Albumin (g/dL)", cls="label label-text font-medium"),
                                            Input(
                                                type="number",
                                                name="albumin",
                                                step="0.1",
                                                min="0",
                                                max="10",
                                                value=patient_data.get("albumin", ""),
                                                cls="input input-bordered",
                                                placeholder="e.g., 3.5"
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("CEA (ng/mL)", cls="label label-text font-medium"),
                                            Input(
                                                type="number",
                                                name="cea",
                                                step="0.1",
                                                min="0",
                                                value=patient_data.get("cea", ""),
                                                cls="input input-bordered",
                                                placeholder="e.g., 5.2"
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # Tumor characteristics
                            Div(
                                cls="grid grid-cols-1 md:grid-cols-2 gap-4",
                                children=[
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("Tumor Location", cls="label label-text font-medium"),
                                            Select(
                                                name="tumor_location",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select location", value="", disabled=True),
                                                    Option("Proximal third", value="proximal"),
                                                    Option("Middle third", value="middle"),
                                                    Option("Distal third", value="distal"),
                                                    Option("GEJ (Siewert I)", value="gej_siewert_1"),
                                                    Option("GEJ (Siewert II)", value="gej_siewert_2"),
                                                    Option("GEJ (Siewert III)", value="gej_siewert_3"),
                                                    Option("Diffuse", value="diffuse")
                                                ]
                                            )
                                        ]
                                    ),
                                    Div(
                                        cls="form-control",
                                        children=[
                                            Label("Histology", cls="label label-text font-medium"),
                                            Select(
                                                name="histology",
                                                cls="select select-bordered",
                                                required=True,
                                                children=[
                                                    Option("Select histology", value="", disabled=True),
                                                    Option("Adenocarcinoma (intestinal)", value="adenocarcinoma_intestinal"),
                                                    Option("Adenocarcinoma (diffuse)", value="adenocarcinoma_diffuse"),
                                                    Option("Adenocarcinoma (mixed)", value="adenocarcinoma_mixed"),
                                                    Option("Signet ring cell", value="signet_ring"),
                                                    Option("Neuroendocrine", value="neuroendocrine"),
                                                    Option("Other", value="other")
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # Biomarkers
                            Fieldset(
                                cls="border border-base-300 rounded-lg p-4",
                                children=[
                                    Legend("Biomarkers", cls="text-sm font-medium px-2"),
                                    Div(
                                        cls="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2",
                                        children=[
                                            Div(
                                                cls="form-control",
                                                children=[
                                                    Label(
                                                        cls="label cursor-pointer",
                                                        children=[
                                                            Span("HER2 Positive", cls="label-text"),
                                                            Input(
                                                                type="checkbox",
                                                                name="her2_positive",
                                                                cls="checkbox checkbox-primary",
                                                                checked=patient_data.get("her2_positive", False)
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            Div(
                                                cls="form-control",
                                                children=[
                                                    Label(
                                                        cls="label cursor-pointer",
                                                        children=[
                                                            Span("MSI-H/dMMR", cls="label-text"),
                                                            Input(
                                                                type="checkbox",
                                                                name="msi_high",
                                                                cls="checkbox checkbox-primary",
                                                                checked=patient_data.get("msi_high", False)
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            Div(
                                                cls="form-control",
                                                children=[
                                                    Label(
                                                        cls="label cursor-pointer",
                                                        children=[
                                                            Span("PD-L1 Positive", cls="label-text"),
                                                            Input(
                                                                type="checkbox",
                                                                name="pdl1_positive",
                                                                cls="checkbox checkbox-primary",
                                                                checked=patient_data.get("pdl1_positive", False)
                                                            )
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
                ]
            )
        ]
    )

def ProtocolSelector(available_protocols: List[Dict] = None, 
                    selected_protocol: str = None) -> Div:
    """Protocol selection component."""
    if available_protocols is None:
        available_protocols = []
    
    protocol_options = [Option("Select a protocol", value="", disabled=True)]
    for protocol in available_protocols:
        protocol_options.append(
            Option(
                f"{protocol['name']} (Level {protocol.get('evidence_level', '5')})",
                value=protocol['id'],
                selected=protocol['id'] == selected_protocol
            )
        )
    
    return Div(
        cls="card bg-base-100 shadow-md",
        children=[
            Div(
                cls="card-body",
                children=[
                    H3("Treatment Protocol", cls="card-title text-lg text-primary mb-4"),
                    
                    Div(
                        cls="form-control",
                        children=[
                            Label("Select Protocol", cls="label label-text font-medium"),
                            Select(
                                name="protocol_id",
                                cls="select select-bordered",
                                required=True,
                                hx_get="/decision/protocol-info",
                                hx_target="#protocol-info",
                                hx_trigger="change",
                                children=protocol_options
                            )
                        ]
                    ),
                    
                    # Protocol information will be loaded here
                    Div(id="protocol-info", cls="mt-4")
                ]
            )
        ]
    )

def DecisionResults(results: Dict = None) -> Div:
    """Display decision engine results."""
    if results is None:
        return Div(
            cls="card bg-base-100 shadow-md",
            children=[
                Div(
                    cls="card-body text-center py-12",
                    children=[
                        Div("🤖", cls="text-6xl mb-4"),
                        H3("Ready for Analysis", cls="text-xl font-semibold mb-2"),
                        P("Complete the patient information and select a protocol to get AI-powered recommendations.",
                          cls="text-base-content/60")
                    ]
                )
            ]
        )
    
    # Confidence level styling
    confidence = results.get("confidence_score", 0)
    confidence_class = "text-success" if confidence >= 0.8 else "text-warning" if confidence >= 0.6 else "text-error"
    confidence_bg = "bg-success/20" if confidence >= 0.8 else "bg-warning/20" if confidence >= 0.6 else "bg-error/20"
    
    # Risk level styling
    risk_level = results.get("risk_assessment", {}).get("overall_risk", "moderate")
    risk_class = "text-success" if risk_level == "low" else "text-warning" if risk_level == "moderate" else "text-error"
    risk_bg = "bg-success/20" if risk_level == "low" else "bg-warning/20" if risk_level == "moderate" else "bg-error/20"
    
    return Div(
        cls="space-y-6",
        children=[
            # Primary recommendation
            Div(
                cls=f"card bg-base-100 shadow-md border-l-4 border-primary",
                children=[
                    Div(
                        cls="card-body",
                        children=[
                            H3("Primary Recommendation", cls="card-title text-lg text-primary mb-4"),
                            
                            # Main recommendation
                            Div(
                                cls=f"alert {confidence_bg} mb-4",
                                children=[
                                    Div(
                                        cls="flex items-center gap-3",
                                        children=[
                                            Div("🎯", cls="text-2xl"),
                                            Div(
                                                children=[
                                                    H4(results.get("primary_recommendation", "No recommendation available"),
                                                       cls="font-semibold text-lg"),
                                                    P(results.get("recommendation_rationale", ""),
                                                      cls="text-sm mt-1")
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            
                            # Confidence and evidence
                            Div(
                                cls="stats shadow w-full",
                                children=[
                                    Div(
                                        cls="stat",
                                        children=[
                                            Div("Confidence Score", cls="stat-title"),
                                            Div(f"{confidence:.1%}", cls=f"stat-value {confidence_class}"),
                                            Div(results.get("confidence_explanation", ""), cls="stat-desc")
                                        ]
                                    ),
                                    Div(
                                        cls="stat",
                                        children=[
                                            Div("Evidence Level", cls="stat-title"),
                                            Div(f"Level {results.get('evidence_level', 'N/A')}", cls="stat-value"),
                                            Div(results.get("evidence_quality", ""), cls="stat-desc")
                                        ]
                                    ),
                                    Div(
                                        cls="stat",
                                        children=[
                                            Div("Risk Assessment", cls="stat-title"),
                                            Div(risk_level.title(), cls=f"stat-value {risk_class}"),
                                            Div("Overall surgical risk", cls="stat-desc")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Alternative recommendations
            Div(
                cls="card bg-base-100 shadow-md",
                children=[
                    Div(
                        cls="card-body",
                        children=[
                            H3("Alternative Options", cls="card-title text-lg mb-4"),
                            
                            Div(
                                cls="space-y-3",
                                children=[
                                    Div(
                                        cls="flex items-center justify-between p-3 bg-base-200 rounded-lg",
                                        children=[
                                            Div(
                                                children=[
                                                    P(alt.get("treatment", ""), cls="font-medium"),
                                                    P(alt.get("rationale", ""), cls="text-sm text-base-content/60")
                                                ]
                                            ),
                                            Div(
                                                f"{alt.get('confidence', 0):.1%}",
                                                cls="badge badge-outline"
                                            )
                                        ]
                                    ) for alt in results.get("alternative_recommendations", [])
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Risk factors and considerations
            Div(
                cls="grid grid-cols-1 md:grid-cols-2 gap-6",
                children=[
                    # Risk factors
                    Div(
                        cls="card bg-base-100 shadow-md",
                        children=[
                            Div(
                                cls="card-body",
                                children=[
                                    H4("Risk Factors", cls="card-title text-md mb-3"),
                                    Div(
                                        cls="space-y-2",
                                        children=[
                                            Div(
                                                cls="flex items-center gap-2",
                                                children=[
                                                    Div("⚠️", cls="text-warning"),
                                                    Span(factor, cls="text-sm")
                                                ]
                                            ) for factor in results.get("risk_factors", [])
                                        ] if results.get("risk_factors") else [
                                            P("No significant risk factors identified.", 
                                              cls="text-sm text-base-content/60")
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Clinical considerations
                    Div(
                        cls="card bg-base-100 shadow-md",
                        children=[
                            Div(
                                cls="card-body",
                                children=[
                                    H4("Clinical Considerations", cls="card-title text-md mb-3"),
                                    Div(
                                        cls="space-y-2",
                                        children=[
                                            Div(
                                                cls="flex items-center gap-2",
                                                children=[
                                                    Div("💡", cls="text-info"),
                                                    Span(consideration, cls="text-sm")
                                                ]
                                            ) for consideration in results.get("clinical_considerations", [])
                                        ] if results.get("clinical_considerations") else [
                                            P("No special considerations noted.", 
                                              cls="text-sm text-base-content/60")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Actions
            Div(
                cls="flex gap-4 justify-center",
                children=[
                    Button(
                        "📄 Generate Report",
                        cls="btn btn-outline",
                        hx_post="/decision/generate-report",
                        hx_include="#patient-form, [name='protocol_id']",
                        hx_target="#report-modal .modal-box"
                    ),
                    Button(
                        "💾 Save Decision",
                        cls="btn btn-primary",
                        hx_post="/decision/save",
                        hx_include="#patient-form, [name='protocol_id']",
                        hx_target="#decision-save-status"
                    ),
                    Button(
                        "🔄 New Analysis",
                        cls="btn btn-secondary",
                        onclick="window.location.reload()"
                    )
                ]
            ),
            
            # Save status
            Div(id="decision-save-status")
        ]
    )

def DecisionIsland(protocols: List[Dict] = None, patient_data: Dict = None, 
                  results: Dict = None, selected_protocol: str = None) -> Div:
    """Complete decision engine island."""
    if protocols is None:
        protocols = []
    
    return Div(
        cls="container mx-auto px-4 py-8",
        children=[
            # Page header
            Div(
                cls="hero bg-gradient-to-r from-accent/10 to-primary/10 rounded-lg mb-8",
                children=[
                    Div(
                        cls="hero-content text-center py-12",
                        children=[
                            Div(
                                cls="max-w-md",
                                children=[
                                    H1("Decision Support Engine", cls="text-4xl font-bold text-primary mb-4"),
                                    P("AI-powered treatment recommendations based on clinical evidence and patient data.",
                                      cls="text-lg text-base-content/80")
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Main content
            Div(
                cls="grid grid-cols-1 lg:grid-cols-2 gap-8",
                children=[
                    # Input section
                    Div(
                        cls="space-y-6",
                        children=[
                            PatientInputForm(patient_data),
                            ProtocolSelector(protocols, selected_protocol),
                            
                            # Analysis button
                            Div(
                                cls="text-center",
                                children=[
                                    Button(
                                        "🧠 Analyze & Recommend",
                                        cls="btn btn-primary btn-lg",
                                        hx_post="/decision/analyze",
                                        hx_include="#patient-form, [name='protocol_id']",
                                        hx_target="#decision-results",
                                        hx_indicator="#analysis-spinner"
                                    )
                                ]
                            ),
                            
                            # Loading indicator
                            Div(
                                id="analysis-spinner",
                                cls="htmx-indicator text-center py-8",
                                children=[
                                    Div(cls="loading loading-spinner loading-lg"),
                                    P("Analyzing patient data...", cls="mt-2 text-base-content/60")
                                ]
                            )
                        ]
                    ),
                    
                    # Results section
                    Div(
                        id="decision-results",
                        children=[DecisionResults(results)]
                    )
                ]
            ),
            
            # Report modal
            Dialog(
                id="report-modal",
                cls="modal",
                children=[
                    Div(
                        cls="modal-box w-11/12 max-w-4xl",
                        children=[
                            # Content will be loaded via HTMX
                            Div("Loading report...", cls="loading loading-spinner")
                        ]
                    ),
                    Form(
                        method="dialog",
                        cls="modal-backdrop",
                        children=[Button("close")]
                    )
                ]
            )
        ]
    )
