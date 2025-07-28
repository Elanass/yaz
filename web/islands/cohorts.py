"""
Cohort Management Islands for FastHTML/HTMX
Handles cohort upload, validation, processing, and results visualization
"""

import json
import uuid
from typing import Any, Dict, List, Optional

from fasthtml.common import *


class CohortUploadIsland:
    """Interactive cohort upload component with validation"""
    
    @staticmethod
    def render():
        return Div(
            H2("Cohort Upload & Management", cls="text-2xl font-bold mb-6"),
            
            # Upload Form
            Div(
                Form(
                    # Study Information
                    Div(
                        H3("Study Information", cls="text-lg font-semibold mb-4"),
                        Div(
                            Label("Study Name", for_="study_name", cls="block text-sm font-medium mb-2"),
                            Input(
                                type="text",
                                name="study_name",
                                id="study_name",
                                required=True,
                                placeholder="Enter study name...",
                                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            ),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Description", for_="description", cls="block text-sm font-medium mb-2"),
                            Textarea(
                                name="description",
                                id="description",
                                rows="3",
                                placeholder="Optional study description...",
                                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            ),
                            cls="mb-4"
                        ),
                        cls="bg-gray-50 p-4 rounded-lg mb-6"
                    ),
                    
                    # Upload Method Selection
                    Div(
                        H3("Upload Method", cls="text-lg font-semibold mb-4"),
                        Div(
                            Div(
                                Input(
                                    type="radio",
                                    name="format_type",
                                    value="manual",
                                    id="format_manual",
                                    checked=True,
                                    cls="mr-2",
                                    hx_trigger="change",
                                    hx_target="#upload-content",
                                    hx_get="/cohorts/upload-form/manual"
                                ),
                                Label("Manual Entry", for_="format_manual", cls="text-sm font-medium"),
                                cls="flex items-center mb-2"
                            ),
                            Div(
                                Input(
                                    type="radio",
                                    name="format_type",
                                    value="csv",
                                    id="format_csv",
                                    cls="mr-2",
                                    hx_trigger="change",
                                    hx_target="#upload-content",
                                    hx_get="/cohorts/upload-form/csv"
                                ),
                                Label("CSV File", for_="format_csv", cls="text-sm font-medium"),
                                cls="flex items-center mb-2"
                            ),
                            Div(
                                Input(
                                    type="radio",
                                    name="format_type",
                                    value="json",
                                    id="format_json",
                                    cls="mr-2",
                                    hx_trigger="change",
                                    hx_target="#upload-content",
                                    hx_get="/cohorts/upload-form/json"
                                ),
                                Label("JSON File", for_="format_json", cls="text-sm font-medium"),
                                cls="flex items-center mb-2"
                            ),
                            Div(
                                Input(
                                    type="radio",
                                    name="format_type",
                                    value="fhir",
                                    id="format_fhir",
                                    cls="mr-2",
                                    hx_trigger="change",
                                    hx_target="#upload-content",
                                    hx_get="/cohorts/upload-form/fhir"
                                ),
                                Label("FHIR Bundle", for_="format_fhir", cls="text-sm font-medium"),
                                cls="flex items-center"
                            ),
                            cls="space-y-2"
                        ),
                        cls="bg-gray-50 p-4 rounded-lg mb-6"
                    ),
                    
                    # Processing Configuration
                    Div(
                        H3("Processing Configuration", cls="text-lg font-semibold mb-4"),
                        Div(
                            Label("Decision Engine", for_="engine_name", cls="block text-sm font-medium mb-2"),
                            Select(
                                Option("ADCI Engine", value="adci", selected=True),
                                Option("Gastrectomy Engine", value="gastrectomy"),
                                Option("FLOT Engine", value="flot"),
                                name="engine_name",
                                id="engine_name",
                                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            ),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Confidence Threshold", for_="confidence_threshold", cls="block text-sm font-medium mb-2"),
                            Input(
                                type="range",
                                name="confidence_threshold",
                                id="confidence_threshold",
                                min="0.5",
                                max="1.0",
                                step="0.05",
                                value="0.75",
                                cls="w-full",
                                oninput="document.getElementById('confidence_value').textContent = this.value"
                            ),
                            Span(id="confidence_value", cls="text-sm text-gray-600")("0.75"),
                            cls="mb-4"
                        ),
                        Div(
                            Label(
                                Input(
                                    type="checkbox",
                                    name="include_alternatives",
                                    checked=True,
                                    cls="mr-2"
                                ),
                                "Include Alternative Recommendations",
                                cls="flex items-center text-sm font-medium"
                            ),
                            cls="mb-4"
                        ),
                        cls="bg-gray-50 p-4 rounded-lg mb-6"
                    ),
                    
                    # Dynamic upload content area
                    Div(id="upload-content", cls="mb-6"),
                    
                    # Submit button
                    Div(
                        Button(
                            "Create Cohort Study",
                            type="submit",
                            cls="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50",
                            id="submit-button"
                        ),
                        cls="text-center"
                    ),
                    
                    # Form attributes
                    method="post",
                    action="/api/v1/cohorts/upload",
                    enctype="multipart/form-data",
                    hx_post="/api/v1/cohorts/upload",
                    hx_target="#upload-result",
                    hx_swap="innerHTML",
                    hx_indicator="#loading-indicator"
                ),
                cls="bg-white p-6 rounded-lg shadow-lg"
            ),
            
            # Loading indicator
            Div(
                Div(
                    Div(cls="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"),
                    P("Processing cohort upload...", cls="ml-3 text-sm text-gray-600"),
                    cls="flex items-center justify-center"
                ),
                id="loading-indicator",
                cls="htmx-indicator fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            ),
            
            # Results area
            Div(id="upload-result", cls="mt-6"),
            
            cls="max-w-4xl mx-auto p-6"
        )
    
    @staticmethod
    def render_manual_form():
        """Manual patient entry form"""
        return Div(
            H3("Manual Patient Entry", cls="text-lg font-semibold mb-4"),
            Div(
                id="patients-container",
                # Initial empty patient form
                CohortUploadIsland.render_patient_form(0),
                cls="space-y-4"
            ),
            Div(
                Button(
                    "+ Add Another Patient",
                    type="button",
                    cls="text-blue-600 hover:text-blue-800 text-sm font-medium",
                    onclick="addPatientForm()"
                ),
                cls="text-center mt-4"
            ),
            Script("""
                let patientCount = 1;
                function addPatientForm() {
                    const container = document.getElementById('patients-container');
                    const formHtml = `""" + CohortUploadIsland.render_patient_form("${patientCount}") + """`;
                    container.insertAdjacentHTML('beforeend', formHtml);
                    patientCount++;
                }
                
                function removePatientForm(index) {
                    document.getElementById(`patient-form-${index}`).remove();
                }
            """),
            cls="bg-gray-50 p-4 rounded-lg"
        )
    
    @staticmethod
    def render_patient_form(index):
        """Individual patient form component"""
        return Div(
            Div(
                Div(
                    H4(f"Patient {index + 1 if isinstance(index, int) else '${parseInt(index) + 1}'}", cls="text-md font-medium mb-2"),
                    Button(
                        "Remove",
                        type="button",
                        cls="text-red-600 hover:text-red-800 text-sm",
                        onclick=f"removePatientForm({index})" if isinstance(index, int) else "removePatientForm(${index})"
                    ) if index != 0 else None,
                    cls="flex justify-between items-center mb-3"
                ),
                Div(
                    Div(
                        Label("Patient ID", cls="block text-xs font-medium mb-1"),
                        Input(
                            type="text",
                            name=f"patients[{index}][patient_id]" if isinstance(index, int) else "patients[${index}][patient_id]",
                            required=True,
                            placeholder="Unique patient identifier",
                            cls="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        ),
                        cls="flex-1 mr-2"
                    ),
                    Div(
                        Label("Age", cls="block text-xs font-medium mb-1"),
                        Input(
                            type="number",
                            name=f"patients[{index}][age]" if isinstance(index, int) else "patients[${index}][age]",
                            min="0",
                            max="120",
                            required=True,
                            cls="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        ),
                        cls="w-20 mr-2"
                    ),
                    Div(
                        Label("Gender", cls="block text-xs font-medium mb-1"),
                        Select(
                            Option("Male", value="male"),
                            Option("Female", value="female"),
                            Option("Other", value="other"),
                            name=f"patients[{index}][gender]" if isinstance(index, int) else "patients[${index}][gender]",
                            required=True,
                            cls="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        ),
                        cls="w-24"
                    ),
                    cls="flex mb-3"
                ),
                Div(
                    Label("Clinical Parameters (JSON)", cls="block text-xs font-medium mb-1"),
                    Textarea(
                        name=f"patients[{index}][clinical_parameters]" if isinstance(index, int) else "patients[${index}][clinical_parameters]",
                        rows="3",
                        placeholder='{"tumor_stage": "T2N1M0", "histology": "adenocarcinoma", ...}',
                        cls="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                    ),
                    cls="mb-3"
                ),
                cls="p-3 border border-gray-200 rounded"
            ),
            id=f"patient-form-{index}" if isinstance(index, int) else "patient-form-${index}",
            cls="patient-form"
        )
    
    @staticmethod
    def render_file_upload(format_type: str):
        """File upload form for different formats"""
        format_info = {
            "csv": {
                "title": "CSV File Upload",
                "description": "Upload a CSV file with patient data. Required columns: patient_id, age, gender, clinical_parameters (JSON string)",
                "accept": ".csv",
                "example": "patient_id,age,gender,clinical_parameters\nPT001,65,male,\"{\"\"tumor_stage\"\":\"\"T2N1M0\"\"}\""
            },
            "json": {
                "title": "JSON File Upload", 
                "description": "Upload a JSON file with patient array. Each patient should have: patient_id, age, gender, clinical_parameters",
                "accept": ".json",
                "example": '[{"patient_id": "PT001", "age": 65, "gender": "male", "clinical_parameters": {"tumor_stage": "T2N1M0"}}]'
            },
            "fhir": {
                "title": "FHIR Bundle Upload",
                "description": "Upload a FHIR Bundle with Patient resources and associated clinical observations",
                "accept": ".json",
                "example": '{"resourceType": "Bundle", "entry": [{"resource": {"resourceType": "Patient", ...}}]}'
            }
        }
        
        info = format_info.get(format_type, format_info["csv"])
        
        return Div(
            H3(info["title"], cls="text-lg font-semibold mb-4"),
            P(info["description"], cls="text-sm text-gray-600 mb-4"),
            Div(
                Label("Upload File", for_="file", cls="block text-sm font-medium mb-2"),
                Input(
                    type="file",
                    name="file",
                    id="file",
                    accept=info["accept"],
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                ),
                cls="mb-4"
            ),
            Details(
                Summary("View Format Example", cls="text-sm text-blue-600 cursor-pointer"),
                Pre(
                    Code(info["example"], cls="text-xs"),
                    cls="bg-gray-100 p-2 rounded mt-2 overflow-x-auto"
                ),
                cls="mb-4"
            ),
            cls="bg-gray-50 p-4 rounded-lg"
        )


class CohortResultsIsland:
    """Cohort processing results and visualization component"""
    
    @staticmethod
    def render(cohort_id: str, session_data: Dict[str, Any]):
        return Div(
            # Header with cohort info
            Div(
                H2(f"Cohort Results: {session_data.get('cohort_name', 'Unknown')}", cls="text-2xl font-bold"),
                Div(
                    Span(f"Session: {session_data.get('session_name', 'N/A')}", cls="text-sm text-gray-600 mr-4"),
                    Span(f"Patients: {session_data.get('total_patients', 0)}", cls="text-sm text-gray-600 mr-4"),
                    Span(f"Engine: {session_data.get('engine_name', 'N/A').upper()}", cls="text-sm text-gray-600"),
                    cls="flex items-center space-x-4 mt-2"
                ),
                cls="mb-6"
            ),
            
            # Status and progress
            Div(
                Div(
                    H3("Processing Status", cls="text-lg font-semibold mb-3"),
                    Div(
                        Span(
                            session_data.get('status', 'unknown').title(),
                            cls=f"px-3 py-1 rounded-full text-sm font-medium {
                                'bg-green-100 text-green-800' if session_data.get('status') == 'completed' 
                                else 'bg-yellow-100 text-yellow-800' if session_data.get('status') == 'processing'
                                else 'bg-red-100 text-red-800' if session_data.get('status') == 'failed'
                                else 'bg-gray-100 text-gray-800'
                            }"
                        ),
                        cls="mb-2"
                    ),
                    Progress(
                        value=session_data.get('progress', 0),
                        max=100,
                        cls="w-full h-2 bg-gray-200 rounded-full"
                    ) if session_data.get('status') == 'processing' else None,
                    cls="bg-white p-4 rounded-lg shadow"
                ),
                cls="mb-6"
            ),
            
            # Results summary (if completed)
            Div(
                CohortResultsIsland.render_summary(session_data.get('summary', {})),
                cls="mb-6"
            ) if session_data.get('status') == 'completed' else None,
            
            # Interactive results table
            Div(
                CohortResultsIsland.render_results_table(cohort_id, session_data.get('session_id')),
                cls="mb-6"
            ) if session_data.get('status') == 'completed' else None,
            
            # Export options
            Div(
                CohortResultsIsland.render_export_options(session_data.get('session_id')),
                cls="mb-6"
            ) if session_data.get('status') == 'completed' else None,
            
            # Auto-refresh for processing status
            Script(f"""
                if ('{session_data.get('status')}' === 'processing') {{
                    setTimeout(() => {{
                        htmx.trigger(document.body, 'refresh-results');
                    }}, 5000);
                }}
            """) if session_data.get('status') == 'processing' else None,
            
            # HTMX refresh trigger
            Div(
                hx_get=f"/cohorts/{cohort_id}/results",
                hx_trigger="refresh-results from:body",
                hx_swap="outerHTML",
                style="display: none;"
            ),
            
            cls="max-w-7xl mx-auto p-6"
        )
    
    @staticmethod
    def render_summary(summary: Dict[str, Any]):
        """Render results summary dashboard"""
        return Div(
            H3("Results Summary", cls="text-lg font-semibold mb-4"),
            Div(
                # Key metrics cards
                Div(
                    Div(
                        H4("Total Patients", cls="text-sm font-medium text-gray-600"),
                        P(str(summary.get('total_patients', 0)), cls="text-2xl font-bold text-gray-900"),
                        cls="text-center"
                    ),
                    cls="bg-white p-4 rounded-lg shadow border"
                ),
                Div(
                    Div(
                        H4("High Confidence", cls="text-sm font-medium text-gray-600"),
                        P(f"{summary.get('high_confidence_count', 0)} ({summary.get('high_confidence_pct', 0):.1f}%)", cls="text-2xl font-bold text-green-600"),
                        cls="text-center"
                    ),
                    cls="bg-white p-4 rounded-lg shadow border"
                ),
                Div(
                    Div(
                        H4("Avg Risk Score", cls="text-sm font-medium text-gray-600"),
                        P(f"{summary.get('avg_risk_score', 0):.2f}", cls="text-2xl font-bold text-orange-600"),
                        cls="text-center"
                    ),
                    cls="bg-white p-4 rounded-lg shadow border"
                ),
                Div(
                    Div(
                        H4("Processing Time", cls="text-sm font-medium text-gray-600"),
                        P(f"{summary.get('processing_time_minutes', 0):.1f}m", cls="text-2xl font-bold text-blue-600"),
                        cls="text-center"
                    ),
                    cls="bg-white p-4 rounded-lg shadow border"
                ),
                cls="grid grid-cols-4 gap-4 mb-6"
            ),
            
            # Risk distribution chart
            Div(
                H4("Risk Distribution", cls="text-md font-semibold mb-3"),
                Div(
                    # Simple bar chart representation
                    Div(
                        Div(
                            Span("Low Risk", cls="text-xs text-gray-600"),
                            Div(
                                style=f"width: {summary.get('low_risk_pct', 0)}%; height: 20px; background-color: #10b981;",
                                cls="rounded"
                            ),
                            Span(f"{summary.get('low_risk_count', 0)} patients", cls="text-xs text-gray-600"),
                            cls="mb-2"
                        ),
                        Div(
                            Span("Medium Risk", cls="text-xs text-gray-600"),
                            Div(
                                style=f"width: {summary.get('medium_risk_pct', 0)}%; height: 20px; background-color: #f59e0b;",
                                cls="rounded"
                            ),
                            Span(f"{summary.get('medium_risk_count', 0)} patients", cls="text-xs text-gray-600"),
                            cls="mb-2"
                        ),
                        Div(
                            Span("High Risk", cls="text-xs text-gray-600"),
                            Div(
                                style=f"width: {summary.get('high_risk_pct', 0)}%; height: 20px; background-color: #ef4444;",
                                cls="rounded"
                            ),
                            Span(f"{summary.get('high_risk_count', 0)} patients", cls="text-xs text-gray-600"),
                        ),
                        cls="space-y-2"
                    ),
                    cls="bg-gray-50 p-4 rounded"
                ),
                cls="bg-white p-4 rounded-lg shadow border"
            ),
            
            cls="bg-gray-50 p-4 rounded-lg"
        )
    
    @staticmethod 
    def render_results_table(cohort_id: str, session_id: str):
        """Render interactive results table with filtering"""
        return Div(
            # Filters
            Div(
                H3("Patient Results", cls="text-lg font-semibold mb-4"),
                Form(
                    Div(
                        Div(
                            Label("Risk Threshold", cls="block text-sm font-medium mb-1"),
                            Input(
                                type="range",
                                name="risk_threshold",
                                min="0",
                                max="1",
                                step="0.1",
                                value="0.5",
                                cls="w-full"
                            ),
                            cls="mr-4"
                        ),
                        Div(
                            Label("Confidence Filter", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("All", value=""),
                                Option("High (>0.8)", value="0.8"),
                                Option("Medium (0.6-0.8)", value="0.6"),
                                Option("Low (<0.6)", value="0.6"),
                                name="confidence_filter",
                                cls="px-2 py-1 border rounded"
                            ),
                            cls="mr-4"
                        ),
                        Div(
                            Label("Protocol", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("All Protocols", value=""),
                                Option("Surgical", value="surgical"),
                                Option("Neoadjuvant", value="neoadjuvant"),
                                Option("Palliative", value="palliative"),
                                name="protocol_filter",
                                cls="px-2 py-1 border rounded"
                            ),
                            cls="mr-4"
                        ),
                        Button(
                            "Apply Filters",
                            type="submit",
                            cls="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                        ),
                        cls="flex items-end space-x-4"
                    ),
                    hx_get=f"/api/v1/cohorts/sessions/{session_id}/results",
                    hx_target="#results-table-body",
                    hx_swap="innerHTML",
                    cls="mb-4"
                ),
                cls="bg-white p-4 rounded-lg shadow"
            ),
            
            # Results table
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Patient ID", cls="px-4 py-2 text-left"),
                            Th("Risk Score", cls="px-4 py-2 text-left"),
                            Th("Confidence", cls="px-4 py-2 text-left"),
                            Th("Recommendation", cls="px-4 py-2 text-left"),
                            Th("Protocol", cls="px-4 py-2 text-left"),
                            Th("Actions", cls="px-4 py-2 text-left"),
                            cls="bg-gray-50"
                        )
                    ),
                    Tbody(
                        id="results-table-body",
                        hx_get=f"/api/v1/cohorts/sessions/{session_id}/results",
                        hx_trigger="load",
                        hx_swap="innerHTML"
                    ),
                    cls="w-full border-collapse border border-gray-300"
                ),
                cls="bg-white rounded-lg shadow overflow-hidden"
            ),
            
            cls="space-y-4"
        )
    
    @staticmethod
    def render_export_options(session_id: str):
        """Render export and download options"""
        return Div(
            H3("Export Results", cls="text-lg font-semibold mb-4"),
            Div(
                Form(
                    Div(
                        H4("Export Format", cls="text-md font-medium mb-2"),
                        Div(
                            Label(
                                Input(type="radio", name="export_format", value="csv", checked=True, cls="mr-2"),
                                "CSV Report",
                                cls="flex items-center mb-2"
                            ),
                            Label(
                                Input(type="radio", name="export_format", value="pdf", cls="mr-2"),
                                "PDF Summary",
                                cls="flex items-center mb-2"
                            ),
                            Label(
                                Input(type="radio", name="export_format", value="fhir", cls="mr-2"),
                                "FHIR Bundle",
                                cls="flex items-center mb-2"
                            ),
                            Label(
                                Input(type="radio", name="export_format", value="excel", cls="mr-2"),
                                "Excel Workbook",
                                cls="flex items-center"
                            ),
                            cls="space-y-1"
                        ),
                        cls="mb-4"
                    ),
                    
                    Div(
                        H4("Include Options", cls="text-md font-medium mb-2"),
                        Div(
                            Label(
                                Input(type="checkbox", name="include_summary", checked=True, cls="mr-2"),
                                "Summary Statistics",
                                cls="flex items-center mb-2"
                            ),
                            Label(
                                Input(type="checkbox", name="include_evidence", cls="mr-2"),
                                "Evidence Citations",
                                cls="flex items-center mb-2"
                            ),
                            Label(
                                Input(type="checkbox", name="include_alternatives", cls="mr-2"),
                                "Alternative Recommendations",
                                cls="flex items-center"
                            ),
                            cls="space-y-1"
                        ),
                        cls="mb-4"
                    ),
                    
                    Button(
                        "Generate Export",
                        type="submit",
                        cls="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
                    ),
                    
                    method="post",
                    hx_post=f"/api/v1/cohorts/sessions/{session_id}/export",
                    hx_target="#export-status",
                    hx_swap="innerHTML"
                ),
                
                # Export status area
                Div(id="export-status", cls="mt-4"),
                
                cls="bg-white p-4 rounded-lg shadow"
            ),
            
            cls="space-y-4"
        )
