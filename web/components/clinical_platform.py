"""
Clinical Platform Components

This module provides components for the clinical decision support platform,
including interactive components for visualization, analysis, and decision support.
"""

from fasthtml.common import *
from typing import Dict, List, Any, Optional

def create_adaptive_decision_component(patient_data: Dict[str, Any], predictions: Dict[str, Any] = None):
    """
    Creates an adaptive decision component that displays patient data and 
    decision recommendations based on ADCI framework
    """
    return Div(
        H3("Adaptive Decision Component", class_="text-xl font-semibold mb-4"),
        
        # Patient summary section
        Div(
            H4("Patient Summary", class_="text-lg font-medium mb-2"),
            Dl(
                *[
                    Div(
                        Dt(k.replace("_", " ").title(), class_="text-sm font-medium text-gray-500"),
                        Dd(str(v), class_="mt-1 text-sm text-gray-900"),
                        class_="grid grid-cols-3 gap-4 py-2"
                    )
                    for k, v in patient_data.items()
                    if k in ["age", "gender", "tumor_stage", "tumor_location", "histology"]
                ],
                class_="divide-y divide-gray-200"
            ),
            class_="mb-6 p-4 bg-gray-50 rounded-lg"
        ),
        
        # Decision analysis section
        Div(
            H4("Decision Analysis", class_="text-lg font-medium mb-2"),
            Div(
                # Show predictions if available, otherwise show placeholder
                Div(
                    P(f"Recommended Treatment: {predictions['recommendation']['treatment']}", 
                      class_="font-medium"),
                    P(f"Confidence: {predictions['recommendation']['confidence']:.2f}", 
                      class_="text-sm"),
                    P(predictions["recommendation"]["explanation"], 
                      class_="mt-2 text-sm text-gray-600"),
                    class_="mb-4"
                ) if predictions and "recommendation" in predictions else
                P("No predictions available. Run analysis to generate recommendations.", 
                  class_="text-gray-500 italic"),
                
                # Risk visualization if available
                Div(
                    H5("Risk Assessment", class_="text-md font-medium mb-2"),
                    Div(
                        Div(
                            P("Surgery Risk", class_="text-sm font-medium"),
                            Div(
                                Div(
                                    class_=f"bg-{predictions['impact_analysis']['surgery']['color']}-500 h-2 rounded-full",
                                    style=f"width: {predictions['impact_analysis']['surgery']['adjusted_risk'] * 100}%"
                                ),
                                class_="w-full bg-gray-200 rounded-full h-2"
                            ),
                            P(
                                f"{predictions['impact_analysis']['surgery']['risk_level']} ({predictions['impact_analysis']['surgery']['adjusted_risk']:.2f})",
                                class_="text-xs text-gray-500 mt-1"
                            ),
                            class_="mb-3"
                        ),
                        Div(
                            P("FLOT Risk", class_="text-sm font-medium"),
                            Div(
                                Div(
                                    class_=f"bg-{predictions['impact_analysis']['flot']['color']}-500 h-2 rounded-full",
                                    style=f"width: {predictions['impact_analysis']['flot']['adjusted_risk'] * 100}%"
                                ),
                                class_="w-full bg-gray-200 rounded-full h-2"
                            ),
                            P(
                                f"{predictions['impact_analysis']['flot']['risk_level']} ({predictions['impact_analysis']['flot']['adjusted_risk']:.2f})",
                                class_="text-xs text-gray-500 mt-1"
                            ),
                            class_="mb-3"
                        ),
                        class_="mt-3"
                    ) if predictions and "impact_analysis" in predictions else ""
                ),
                class_="p-4 bg-white border border-gray-200 rounded-lg"
            ),
            class_="mb-6"
        ),
        
        # Action buttons
        Div(
            Button(
                "Run Analysis",
                id="run-analysis",
                class_="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
                **{
                    "hx-post": "/api/v1/precision/predict",
                    "hx-include": "[name='patient_data']",
                    "hx-target": "#decision-results",
                    "hx-swap": "innerHTML"
                }
            ),
            A(
                "Generate Report",
                href="#",
                class_="ml-3 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300",
                **{
                    "hx-get": "/api/v1/reports/new",
                    "hx-target": "#report-modal",
                    "hx-trigger": "click"
                }
            ),
            class_="flex"
        ),
        
        # Results container for HTMX updates
        Div(
            id="decision-results"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_simulation_component(simulation_config: Dict[str, Any] = None, results: Dict[str, Any] = None):
    """
    Creates a Markov simulation component that allows configuration and 
    visualization of disease progression simulations
    """
    # Default config if none provided
    if not simulation_config:
        simulation_config = {
            "steps": 5,
            "simulations": 1000,
            "include_confidence": True
        }
    
    return Div(
        H3("Disease Progression Simulation", class_="text-xl font-semibold mb-4"),
        
        # Configuration form
        Form(
            Div(
                Label("Number of steps:", for_="steps", class_="block text-sm font-medium text-gray-700"),
                Input(
                    type_="number",
                    name="steps",
                    id="steps",
                    value=simulation_config.get("steps", 5),
                    min=1,
                    max=20,
                    class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                ),
                class_="mb-4"
            ),
            Div(
                Label("Number of simulations:", for_="simulations", class_="block text-sm font-medium text-gray-700"),
                Input(
                    type_="number",
                    name="simulations",
                    id="simulations",
                    value=simulation_config.get("simulations", 1000),
                    min=100,
                    max=10000,
                    step=100,
                    class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                ),
                class_="mb-4"
            ),
            Div(
                Div(
                    Input(
                        type_="checkbox",
                        name="include_confidence",
                        id="include_confidence",
                        checked=simulation_config.get("include_confidence", True),
                        class_="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    ),
                    Label(
                        "Include confidence intervals",
                        for_="include_confidence",
                        class_="ml-2 block text-sm text-gray-900"
                    ),
                    class_="flex items-center"
                ),
                class_="mb-4"
            ),
            Button(
                "Run Simulation",
                type_="submit",
                class_="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            ),
            **{
                "hx-post": "/api/v1/markov/simulate",
                "hx-target": "#simulation-results",
                "hx-swap": "innerHTML",
                "hx-indicator": "#simulation-indicator"
            },
            class_="p-4 bg-white border border-gray-200 rounded-lg mb-6"
        ),
        
        # Results container
        Div(
            # Show simulation results if available
            Div(
                H4("Simulation Results", class_="text-lg font-medium mb-4"),
                Div(
                    # This would be replaced with a proper chart using Chart.js
                    Div(
                        id="simulation-chart",
                        class_="bg-gray-100 rounded-lg p-4 text-center",
                        style="height: 300px;"
                    ),
                    Script("""
                        document.addEventListener('DOMContentLoaded', function() {
                            const ctx = document.getElementById('simulation-chart').getContext('2d');
                            // Chart.js code would go here to render the simulation results
                        });
                    """) if results else "",
                    class_="mb-4"
                ),
                Div(
                    H5("Key Metrics", class_="text-md font-medium mb-2"),
                    Dl(
                        *[
                            Div(
                                Dt(k.replace("_", " ").title(), class_="text-sm font-medium text-gray-500"),
                                Dd(
                                    f"{v:.2f}" if isinstance(v, float) else str(v),
                                    class_="mt-1 text-sm text-gray-900"
                                ),
                                class_="grid grid-cols-3 gap-4 py-2"
                            )
                            for k, v in results.get("metrics", {}).items()
                        ] if results and "metrics" in results else [
                            Div(
                                P("No simulation results available", class_="text-gray-500 italic"),
                                class_="py-2"
                            )
                        ],
                        class_="divide-y divide-gray-200"
                    ),
                    class_="mt-3"
                ),
                class_="p-4 bg-white border border-gray-200 rounded-lg"
            ) if results else Div(
                P("Run a simulation to see results", class_="text-gray-500 italic"),
                class_="p-4 bg-gray-50 border border-gray-200 rounded-lg text-center"
            ),
            id="simulation-results"
        ),
        
        # Loading indicator
        Div(
            Div(class_="w-6 h-6 border-t-2 border-blue-500 border-r-2 rounded-full animate-spin mx-auto"),
            P("Running simulation...", class_="text-center text-gray-700 mt-2"),
            id="simulation-indicator",
            class_="htmx-indicator py-4"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_evidence_synthesis_component(query: str = "", evidence_items: List[Dict[str, Any]] = None):
    """
    Creates an evidence synthesis component that displays supporting clinical 
    evidence for recommendations
    """
    return Div(
        H3("Evidence Synthesis", class_="text-xl font-semibold mb-4"),
        
        # Search form
        Form(
            Div(
                Label("Search clinical evidence:", for_="evidence_query", class_="block text-sm font-medium text-gray-700"),
                Div(
                    Input(
                        type_="text",
                        name="query",
                        id="evidence_query",
                        value=query,
                        placeholder="e.g., FLOT chemotherapy for stage III gastric cancer",
                        class_="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                    ),
                    Button(
                        Svg(
                            Path(d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"),
                            class_="w-5 h-5",
                            stroke="currentColor",
                            stroke_width="2",
                            fill="none",
                            viewBox="0 0 24 24"
                        ),
                        type_="submit",
                        class_="absolute inset-y-0 right-0 px-3 py-2 text-gray-400"
                    ),
                    class_="mt-1 relative rounded-md shadow-sm"
                ),
                class_="mb-4"
            ),
            **{
                "hx-get": "/api/v1/evidence/search",
                "hx-target": "#evidence-results",
                "hx-swap": "innerHTML",
                "hx-trigger": "submit",
                "hx-indicator": "#evidence-indicator"
            },
            class_="p-4 bg-white border border-gray-200 rounded-lg mb-6"
        ),
        
        # Results container
        Div(
            # Show evidence if available
            Div(
                H4("Supporting Evidence", class_="text-lg font-medium mb-4"),
                Div(
                    *[
                        Div(
                            Div(
                                Span(
                                    item.get("source_type", "Article"),
                                    class_="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
                                ),
                                Span(
                                    f"Confidence: {item.get('confidence', 0):.2f}",
                                    class_="ml-2 px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full"
                                ),
                                class_="flex items-center"
                            ),
                            H5(
                                item.get("title", ""),
                                class_="text-md font-medium text-gray-900 mt-2"
                            ),
                            P(
                                item.get("description", ""),
                                class_="mt-1 text-sm text-gray-600"
                            ),
                            P(
                                Span("Source: ", class_="font-medium"),
                                A(
                                    item.get("source", "Unknown"),
                                    href=item.get("url", "#"),
                                    target="_blank",
                                    class_="text-blue-600 hover:text-blue-800"
                                ),
                                Span(f" ({item.get('year', 'N/A')})", class_="text-gray-500"),
                                class_="mt-2 text-xs text-gray-500"
                            ),
                            class_="p-4 bg-white border border-gray-200 rounded-lg mb-3"
                        )
                        for item in evidence_items
                    ] if evidence_items else [
                        Div(
                            P("No evidence found. Try a different search query.", class_="text-gray-500 italic"),
                            class_="p-4 bg-gray-50 border border-gray-200 rounded-lg text-center"
                        )
                    ],
                    class_="mt-3"
                ),
                class_=""
            ) if evidence_items is not None else Div(
                P("Search for evidence using the form above.", class_="text-gray-500 italic"),
                class_="p-4 bg-gray-50 border border-gray-200 rounded-lg text-center"
            ),
            id="evidence-results"
        ),
        
        # Loading indicator
        Div(
            Div(class_="w-6 h-6 border-t-2 border-blue-500 border-r-2 rounded-full animate-spin mx-auto"),
            P("Gathering evidence...", class_="text-center text-gray-700 mt-2"),
            id="evidence-indicator",
            class_="htmx-indicator py-4"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_clinical_dashboard(patient_data: Dict[str, Any], metrics: Dict[str, Any] = None):
    """
    Creates a clinical dashboard with key metrics and visualizations for 
    monitoring patient outcomes
    """
    return Div(
        H3("Clinical Dashboard", class_="text-xl font-semibold mb-4"),
        
        # Patient identifier
        Div(
            Span(
                f"Patient ID: {patient_data.get('patient_id', 'Unknown')}",
                class_="text-lg font-medium"
            ),
            Span(
                f"Age: {patient_data.get('age', 'N/A')} | " +
                f"Gender: {patient_data.get('gender', 'N/A')} | " +
                f"Stage: {patient_data.get('tumor_stage', 'N/A')}",
                class_="ml-4 text-sm text-gray-600"
            ),
            class_="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg flex flex-wrap items-center justify-between"
        ),
        
        # Metrics grid
        Div(
            Div(
                Div(
                    P("Survival Probability", class_="text-sm font-medium text-gray-500"),
                    P(
                        f"{metrics.get('survival_probability', 0) * 100:.1f}%",
                        class_="mt-1 text-3xl font-semibold text-gray-900"
                    ),
                    P(
                        f"{metrics.get('survival_trend', 0) * 100:+.1f}% from baseline",
                        class_=f"mt-1 text-sm {'text-green-600' if metrics.get('survival_trend', 0) >= 0 else 'text-red-600'}"
                    ) if metrics and "survival_trend" in metrics else "",
                    class_="p-5 bg-white rounded-lg border border-gray-200"
                ),
                class_="col-span-1"
            ),
            Div(
                Div(
                    P("Quality of Life", class_="text-sm font-medium text-gray-500"),
                    P(
                        f"{metrics.get('quality_of_life', 0):.1f}/10",
                        class_="mt-1 text-3xl font-semibold text-gray-900"
                    ),
                    P(
                        f"{metrics.get('qol_trend', 0):+.1f} from baseline",
                        class_=f"mt-1 text-sm {'text-green-600' if metrics.get('qol_trend', 0) >= 0 else 'text-red-600'}"
                    ) if metrics and "qol_trend" in metrics else "",
                    class_="p-5 bg-white rounded-lg border border-gray-200"
                ),
                class_="col-span-1"
            ),
            Div(
                Div(
                    P("Recurrence Risk", class_="text-sm font-medium text-gray-500"),
                    P(
                        f"{metrics.get('recurrence_risk', 0) * 100:.1f}%",
                        class_="mt-1 text-3xl font-semibold text-gray-900"
                    ),
                    P(
                        f"{metrics.get('recurrence_trend', 0) * 100:+.1f}% from baseline",
                        class_=f"mt-1 text-sm {'text-red-600' if metrics.get('recurrence_trend', 0) >= 0 else 'text-green-600'}"
                    ) if metrics and "recurrence_trend" in metrics else "",
                    class_="p-5 bg-white rounded-lg border border-gray-200"
                ),
                class_="col-span-1"
            ),
            class_="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
        ) if metrics else Div(
            P("No metrics available for this patient.", class_="text-gray-500 italic text-center p-4"),
            class_="mb-6 bg-gray-50 rounded-lg"
        ),
        
        # Charts container
        Div(
            Div(
                H4("Outcome Projections", class_="text-lg font-medium mb-3"),
                Div(
                    id="outcome-chart",
                    class_="bg-gray-100 rounded-lg p-4 text-center",
                    style="height: 300px;"
                ),
                Script("""
                    document.addEventListener('DOMContentLoaded', function() {
                        const ctx = document.getElementById('outcome-chart').getContext('2d');
                        // Chart.js code would go here to render outcome projections
                    });
                """) if metrics else "",
                class_="p-4 bg-white border border-gray-200 rounded-lg mb-4"
            ),
            Div(
                H4("Treatment Response", class_="text-lg font-medium mb-3"),
                Div(
                    id="response-chart",
                    class_="bg-gray-100 rounded-lg p-4 text-center",
                    style="height: 300px;"
                ),
                Script("""
                    document.addEventListener('DOMContentLoaded', function() {
                        const ctx = document.getElementById('response-chart').getContext('2d');
                        // Chart.js code would go here to render treatment response
                    });
                """) if metrics else "",
                class_="p-4 bg-white border border-gray-200 rounded-lg"
            ),
            class_="grid grid-cols-1 lg:grid-cols-2 gap-6"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_case_timeline_component(case_data: Dict[str, Any], timeline_events: List[Dict[str, Any]] = None):
    """
    Creates a timeline view for case coordination and tracking
    Integrates with EMR data via OpenMRS adapter
    """
    return Div(
        H3("Case Timeline", class_="text-xl font-semibold mb-4"),
        
        # Case summary
        Div(
            Div(
                H4(f"Case #{case_data.get('case_id', 'Unknown')}", class_="text-lg font-medium"),
                Span(
                    case_data.get("status", "Active"),
                    class_=f"ml-2 px-2 py-1 text-xs font-medium rounded-full {'bg-green-100 text-green-800' if case_data.get('status') == 'Active' else 'bg-gray-100 text-gray-800'}"
                ),
                class_="flex items-center"
            ),
            P(
                f"Patient: {case_data.get('patient_name', 'Unknown')} ({case_data.get('patient_id', '')})",
                class_="text-sm text-gray-600 mt-1"
            ),
            P(
                f"Opened: {case_data.get('opened_date', 'Unknown')} | Last updated: {case_data.get('last_updated', 'Unknown')}",
                class_="text-xs text-gray-500 mt-1"
            ),
            class_="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg"
        ),
        
        # Timeline
        Div(
            H4("Event Timeline", class_="text-lg font-medium mb-4"),
            Div(
                *[
                    Div(
                        Div(
                            Div(
                                class_="w-4 h-4 rounded-full bg-blue-500"
                            ),
                            Div(
                                class_="h-full w-0.5 bg-gray-200"
                            ) if i < len(timeline_events) - 1 else "",
                            class_="flex flex-col items-center"
                        ),
                        Div(
                            Div(
                                P(
                                    event.get("event_type", "Event"),
                                    class_="text-md font-medium text-gray-900"
                                ),
                                P(
                                    event.get("timestamp", ""),
                                    class_="text-xs text-gray-500"
                                ),
                                class_="flex justify-between"
                            ),
                            P(
                                event.get("description", ""),
                                class_="mt-1 text-sm text-gray-600"
                            ),
                            Div(
                                Span(
                                    event.get("provider", "Unknown provider"),
                                    class_="text-xs font-medium text-gray-700"
                                ),
                                Span(
                                    event.get("location", "Unknown location"),
                                    class_="ml-2 text-xs text-gray-500"
                                ),
                                class_="mt-2 flex items-center"
                            ),
                            # Add EMR reference if available
                            Div(
                                P(
                                    Span("EMR Reference: ", class_="font-medium"),
                                    Span(event.get("emr_reference", "Not available")),
                                    class_="text-xs text-gray-500"
                                ),
                                A(
                                    "View in EMR",
                                    href=f"/emr/link/{event.get('emr_id', '')}",
                                    target="_blank",
                                    class_="text-xs text-blue-600 hover:text-blue-800 ml-2"
                                ) if event.get("emr_id") else "",
                                class_="mt-1"
                            ) if event.get("emr_reference") or event.get("emr_id") else "",
                            class_="ml-4 pb-6"
                        ),
                        class_="flex mb-2"
                    )
                    for i, event in enumerate(timeline_events or [])
                ],
                P(
                    "No timeline events available for this case.",
                    class_="text-gray-500 italic text-center p-4"
                ) if not timeline_events else "",
                class_="ml-4"
            ),
            class_="p-4 bg-white border border-gray-200 rounded-lg mb-6"
        ),
        
        # Action buttons
        Div(
            Button(
                "Add Event",
                id="add-event",
                class_="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
                **{
                    "hx-get": f"/api/v1/case_coordination/events/new?case_id={case_data.get('case_id', '')}",
                    "hx-target": "#event-modal",
                    "hx-trigger": "click"
                }
            ),
            Button(
                "Sync with EMR",
                id="sync-emr",
                class_="ml-3 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700",
                **{
                    "hx-post": f"/api/v1/case_coordination/sync?case_id={case_data.get('case_id', '')}",
                    "hx-target": "#sync-result",
                    "hx-trigger": "click",
                    "hx-indicator": "#sync-indicator"
                }
            ),
            class_="flex"
        ),
        
        # Loading indicator
        Div(
            Div(class_="w-5 h-5 border-t-2 border-green-500 border-r-2 rounded-full animate-spin"),
            Span("Syncing with EMR...", class_="ml-2"),
            id="sync-indicator",
            class_="htmx-indicator flex items-center mt-4"
        ),
        
        # Results container
        Div(
            id="sync-result",
            class_="mt-4"
        ),
        
        # Modal for adding events (would be shown/hidden with Alpine.js)
        Div(
            id="event-modal",
            class_="hidden fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_protocol_management_component(protocol_data: Dict[str, Any] = None, compliance_data: Dict[str, Any] = None):
    """
    Creates a protocol management component for tracking treatment protocol compliance
    Integrates with OpenClinica for protocol versioning
    """
    return Div(
        H3("Protocol Management", class_="text-xl font-semibold mb-4"),
        
        # Protocol selection
        Div(
            Form(
                Div(
                    Label("Select Protocol:", for_="protocol_select", class_="block text-sm font-medium text-gray-700"),
                    Select(
                        Option("Select a protocol", value="", disabled=True, selected=not protocol_data),
                        Option("ADCI Standard Protocol", value="adci_standard", selected=protocol_data and protocol_data.get("id") == "adci_standard"),
                        Option("Gastrectomy Workflow", value="gastrectomy", selected=protocol_data and protocol_data.get("id") == "gastrectomy"),
                        Option("FLOT Chemotherapy", value="flot", selected=protocol_data and protocol_data.get("id") == "flot"),
                        Option("Combined FLOT + Gastrectomy", value="flot_gastrectomy", selected=protocol_data and protocol_data.get("id") == "flot_gastrectomy"),
                        name="protocol_id",
                        id="protocol_select",
                        class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                    ),
                    class_="mb-4"
                ),
                Button(
                    "Load Protocol",
                    type_="submit",
                    class_="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                ),
                **{
                    "hx-get": "/api/v1/protocols/details",
                    "hx-target": "#protocol-details",
                    "hx-trigger": "submit",
                    "hx-include": "select[name='protocol_id']",
                    "hx-indicator": "#protocol-indicator"
                },
                class_="mb-6"
            ),
            class_="p-4 bg-white border border-gray-200 rounded-lg mb-6"
        ),
        
        # Protocol details
        Div(
            # Show protocol details if available
            Div(
                Div(
                    H4(protocol_data.get("name", ""), class_="text-lg font-medium"),
                    Div(
                        Span(
                            f"Version {protocol_data.get('version', '1.0')}",
                            class_="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
                        ),
                        Span(
                            f"Last updated: {protocol_data.get('last_updated', 'Unknown')}",
                            class_="ml-2 text-xs text-gray-500"
                        ),
                        class_="flex items-center mt-1"
                    ),
                    class_="mb-4"
                ),
                P(
                    protocol_data.get("description", ""),
                    class_="text-sm text-gray-600 mb-4"
                ),
                # Protocol steps
                Div(
                    H5("Protocol Steps", class_="text-md font-medium mb-2"),
                    Ol(
                        *[
                            Li(
                                Div(
                                    Div(
                                        P(
                                            step.get("name", ""),
                                            class_="font-medium"
                                        ),
                                        Div(
                                            Span(
                                                "Required",
                                                class_="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800 rounded-full"
                                            ) if step.get("required", False) else Span(
                                                "Optional",
                                                class_="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-800 rounded-full"
                                            ),
                                            Span(
                                                f"Timeline: {step.get('timeline', 'N/A')}",
                                                class_="ml-2 text-xs text-gray-500"
                                            ),
                                            class_="flex items-center"
                                        ),
                                        class_="flex justify-between items-center"
                                    ),
                                    P(
                                        step.get("description", ""),
                                        class_="mt-1 text-sm text-gray-600"
                                    ),
                                    class_="p-3 bg-gray-50 rounded-lg mb-2"
                                )
                            )
                            for step in protocol_data.get("steps", [])
                        ],
                        class_="list-decimal pl-5"
                    ),
                    class_="mb-4"
                ),
                # Compliance information
                Div(
                    H5("Compliance Status", class_="text-md font-medium mb-2"),
                    Div(
                        P(
                            "Overall Compliance: ",
                            Span(
                                f"{compliance_data.get('overall_compliance', 0) * 100:.1f}%",
                                class_=f"font-medium {'text-green-600' if compliance_data.get('overall_compliance', 0) >= 0.8 else 'text-yellow-600' if compliance_data.get('overall_compliance', 0) >= 0.6 else 'text-red-600'}"
                            ),
                            class_="text-sm"
                        ),
                        Div(
                            Div(
                                class_=f"h-2 rounded-full {'bg-green-500' if compliance_data.get('overall_compliance', 0) >= 0.8 else 'bg-yellow-500' if compliance_data.get('overall_compliance', 0) >= 0.6 else 'bg-red-500'}",
                                style=f"width: {compliance_data.get('overall_compliance', 0) * 100}%"
                            ),
                            class_="w-full bg-gray-200 rounded-full h-2 mt-1"
                        ),
                        class_="mb-4"
                    ),
                    # Compliance details by step
                    Ul(
                        *[
                            Li(
                                Div(
                                    Div(
                                        P(
                                            step_compliance.get("name", ""),
                                            class_="text-sm font-medium"
                                        ),
                                        P(
                                            f"{step_compliance.get('compliance', 0) * 100:.1f}%",
                                            class_=f"text-sm font-medium {'text-green-600' if step_compliance.get('compliance', 0) >= 0.8 else 'text-yellow-600' if step_compliance.get('compliance', 0) >= 0.6 else 'text-red-600'}"
                                        ),
                                        class_="flex justify-between"
                                    ),
                                    Div(
                                        Div(
                                            class_=f"h-2 rounded-full {'bg-green-500' if step_compliance.get('compliance', 0) >= 0.8 else 'bg-yellow-500' if step_compliance.get('compliance', 0) >= 0.6 else 'bg-red-500'}",
                                            style=f"width: {step_compliance.get('compliance', 0) * 100}%"
                                        ),
                                        class_="w-full bg-gray-200 rounded-full h-2 mt-1"
                                    ),
                                    class_="mb-2"
                                )
                            )
                            for step_compliance in compliance_data.get("steps", [])
                        ],
                        class_="space-y-2"
                    ) if compliance_data and "steps" in compliance_data else P(
                        "No compliance data available for this protocol.",
                        class_="text-gray-500 italic"
                    ),
                    class_="mt-2"
                ) if compliance_data else "",
                class_=""
            ) if protocol_data else Div(
                P("Select a protocol to view details.", class_="text-gray-500 italic text-center p-4"),
                class_="p-4 bg-gray-50 border border-gray-200 rounded-lg text-center"
            ),
            id="protocol-details"
        ),
        
        # Loading indicator
        Div(
            Div(class_="w-6 h-6 border-t-2 border-blue-500 border-r-2 rounded-full animate-spin mx-auto"),
            P("Loading protocol...", class_="text-center text-gray-700 mt-2"),
            id="protocol-indicator",
            class_="htmx-indicator py-4"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_care_plan_editor(plan_data: Dict[str, Any] = None, team_members: List[Dict[str, Any]] = None):
    """
    Creates a collaborative care plan editor with real-time sync via Gun.js
    Integrates with HAPI FHIR for care plan management
    """
    return Div(
        H3("Collaborative Care Plan", class_="text-xl font-semibold mb-4"),
        
        # Plan header
        Div(
            Div(
                H4(
                    plan_data.get("title", "New Care Plan"),
                    class_="text-lg font-medium"
                ),
                Div(
                    Span(
                        plan_data.get("status", "Draft"),
                        class_=f"px-2 py-1 text-xs font-medium {'bg-yellow-100 text-yellow-800' if plan_data.get('status') == 'Draft' else 'bg-green-100 text-green-800' if plan_data.get('status') == 'Active' else 'bg-gray-100 text-gray-800'} rounded-full"
                    ),
                    class_="flex items-center"
                ),
                class_="flex justify-between"
            ),
            P(
                f"Patient: {plan_data.get('patient_name', 'Unknown')} | Created: {plan_data.get('created_date', 'Unknown')}",
                class_="text-sm text-gray-600 mt-1"
            ),
            P(
                f"Care Team: {', '.join([m.get('name', '') for m in team_members or []])}",
                class_="text-xs text-gray-500 mt-1"
            ),
            class_="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg"
        ) if plan_data else "",
        
        # Care team members
        Div(
            H4("Care Team", class_="text-md font-medium mb-2"),
            Div(
                *[
                    Div(
                        Div(
                            Img(
                                src=member.get("avatar", "/static/avatars/default.png"),
                                alt=member.get("name", "Team member"),
                                class_="w-8 h-8 rounded-full"
                            ),
                            Div(
                                P(
                                    member.get("name", ""),
                                    class_="text-sm font-medium"
                                ),
                                P(
                                    member.get("role", ""),
                                    class_="text-xs text-gray-500"
                                ),
                                class_="ml-2"
                            ),
                            class_="flex items-center"
                        ),
                        Div(
                            Span(
                                "Online",
                                class_="flex items-center text-xs text-green-700"
                            ) if member.get("online", False) else Span(
                                "Offline",
                                class_="flex items-center text-xs text-gray-500"
                            ),
                            class_="flex items-center"
                        ),
                        class_="flex justify-between items-center p-2 hover:bg-gray-50 rounded"
                    )
                    for member in team_members or []
                ],
                P(
                    "No team members assigned to this care plan.",
                    class_="text-gray-500 italic text-center p-2"
                ) if not team_members else "",
                class_="divide-y divide-gray-100"
            ),
            class_="mb-6 p-4 bg-white border border-gray-200 rounded-lg"
        ),
        
        # Care plan editor
        Div(
            H4("Care Plan Details", class_="text-md font-medium mb-4"),
            Form(
                # Care plan sections
                *[
                    Div(
                        H5(
                            section.get("title", ""),
                            class_="text-md font-medium mb-2"
                        ),
                        P(
                            section.get("description", ""),
                            class_="text-sm text-gray-600 mb-2"
                        ),
                        Textarea(
                            section.get("content", ""),
                            name=f"section_{i}",
                            id=f"section_{i}",
                            placeholder=f"Enter {section.get('title', 'section')} details...",
                            rows=4,
                            class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                        ),
                        P(
                            Span("Last edited by ", class_="text-xs text-gray-500"),
                            Span(section.get("last_edited_by", "Unknown"), class_="text-xs font-medium text-gray-700"),
                            Span(f" on {section.get('last_edited_at', 'Unknown')}", class_="text-xs text-gray-500"),
                            class_="mt-1"
                        ) if section.get("last_edited_by") else "",
                        class_="mb-6"
                    )
                    for i, section in enumerate(plan_data.get("sections", []))
                ] if plan_data and "sections" in plan_data else [
                    Div(
                        H5("Goals", class_="text-md font-medium mb-2"),
                        P("Define treatment goals and expected outcomes.", class_="text-sm text-gray-600 mb-2"),
                        Textarea(
                            name="section_0",
                            id="section_0",
                            placeholder="Enter treatment goals...",
                            rows=4,
                            class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                        ),
                        class_="mb-6"
                    ),
                    Div(
                        H5("Interventions", class_="text-md font-medium mb-2"),
                        P("List planned interventions and treatments.", class_="text-sm text-gray-600 mb-2"),
                        Textarea(
                            name="section_1",
                            id="section_1",
                            placeholder="Enter planned interventions...",
                            rows=4,
                            class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                        ),
                        class_="mb-6"
                    ),
                    Div(
                        H5("Monitoring", class_="text-md font-medium mb-2"),
                        P("Describe monitoring and follow-up plan.", class_="text-sm text-gray-600 mb-2"),
                        Textarea(
                            name="section_2",
                            id="section_2",
                            placeholder="Enter monitoring plan...",
                            rows=4,
                            class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                        ),
                        class_="mb-6"
                    )
                ],
                
                # Form actions
                Div(
                    Button(
                        "Save Changes",
                        type_="submit",
                        class_="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    ),
                    Button(
                        "Export to FHIR",
                        type_="button",
                        class_="ml-3 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700",
                        **{
                            "hx-post": "/api/v1/collaboration/export-fhir",
                            "hx-target": "#export-result",
                            "hx-trigger": "click",
                            "hx-include": "form",
                            "hx-indicator": "#export-indicator"
                        }
                    ),
                    class_="flex justify-between"
                ),
                
                **{
                    "hx-post": "/api/v1/collaboration/save-plan",
                    "hx-target": "#save-result",
                    "hx-trigger": "submit",
                    "hx-indicator": "#save-indicator",
                    "gun-sync": "true",  # Custom attribute for Gun.js integration
                    "plan-id": plan_data.get("id", "") if plan_data else ""
                },
                class_=""
            ),
            class_="p-4 bg-white border border-gray-200 rounded-lg"
        ),
        
        # Loading indicators
        Div(
            Div(class_="w-5 h-5 border-t-2 border-blue-500 border-r-2 rounded-full animate-spin"),
            Span("Saving...", class_="ml-2"),
            id="save-indicator",
            class_="htmx-indicator flex items-center mt-4"
        ),
        Div(
            Div(class_="w-5 h-5 border-t-2 border-green-500 border-r-2 rounded-full animate-spin"),
            Span("Exporting to FHIR...", class_="ml-2"),
            id="export-indicator",
            class_="htmx-indicator flex items-center mt-4"
        ),
        
        # Results containers
        Div(id="save-result", class_="mt-4"),
        Div(id="export-result", class_="mt-4"),
        
        # Collaboration status
        Div(
            Div(
                Div(
                    Span(
                        "●",
                        class_="text-green-500"
                    ),
                    Span(
                        "Real-time collaboration active",
                        class_="ml-1 text-sm"
                    ),
                    class_="flex items-center"
                ),
                Div(
                    Span("2 users viewing", class_="text-xs text-gray-500"),
                    class_="ml-2"
                ),
                class_="flex items-center"
            ),
            class_="mt-4 p-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-700"
        ),
        
        # Gun.js integration script
        Script("""
            document.addEventListener('DOMContentLoaded', function() {
                // Initialize Gun.js for real-time collaboration
                const gun = Gun();
                const planId = document.querySelector('form[gun-sync]').getAttribute('plan-id');
                
                // Set up data sync for each text area
                document.querySelectorAll('textarea').forEach(textarea => {
                    const sectionId = textarea.id;
                    
                    // Subscribe to changes
                    gun.get('care_plans').get(planId).get(sectionId).on(data => {
                        if (data && textarea !== document.activeElement) {
                            textarea.value = data.content;
                        }
                    });
                    
                    // Publish changes on input
                    textarea.addEventListener('input', e => {
                        gun.get('care_plans').get(planId).get(sectionId).put({
                            content: textarea.value,
                            last_edited_by: 'Current User', // Would come from auth context
                            last_edited_at: new Date().toISOString()
                        });
                    });
                });
            });
        """),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )

def create_journal_entry_component(patient_data: Dict[str, Any], templates: List[Dict[str, Any]] = None):
    """
    Creates a clinical journal entry component for structured documentation
    Integrates with event logger for immutable record-keeping
    """
    return Div(
        H3("Clinical Journal", class_="text-xl font-semibold mb-4"),
        
        # Patient identifier
        Div(
            Span(
                f"Patient: {patient_data.get('patient_name', 'Unknown')} ({patient_data.get('patient_id', '')})",
                class_="text-lg font-medium"
            ),
            class_="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg"
        ),
        
        # Template selector
        Div(
            H4("New Journal Entry", class_="text-md font-medium mb-2"),
            Form(
                Div(
                    Label("Entry Template:", for_="template_select", class_="block text-sm font-medium text-gray-700"),
                    Select(
                        Option("Select a template", value="", disabled=True, selected=True),
                        *[
                            Option(
                                template.get("name", ""),
                                value=template.get("id", "")
                            )
                            for template in templates or []
                        ],
                        name="template_id",
                        id="template_select",
                        class_="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                    ),
                    class_="mb-4"
                ),
                Button(
                    "Load Template",
                    type_="submit",
                    class_="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                ),
                **{
                    "hx-get": "/api/v1/journal/template",
                    "hx-target": "#template-form",
                    "hx-trigger": "submit",
                    "hx-include": "select[name='template_id']",
                    "hx-indicator": "#template-indicator"
                },
                class_="mb-6"
            ),
            class_="p-4 bg-white border border-gray-200 rounded-lg mb-6"
        ),
        
        # Template form (populated via HTMX)
        Div(
            P("Select a template to create a journal entry.", class_="text-gray-500 italic text-center p-4"),
            id="template-form",
            class_="p-4 bg-white border border-gray-200 rounded-lg mb-6"
        ),
        
        # Recent entries
        Div(
            H4("Recent Journal Entries", class_="text-md font-medium mb-4"),
            P("Loading recent entries...", class_="text-gray-500 italic text-center p-4"),
            id="recent-entries",
            **{
                "hx-get": f"/api/v1/journal/entries?patient_id={patient_data.get('patient_id', '')}",
                "hx-trigger": "load",
                "hx-indicator": "#entries-indicator"
            },
            class_="p-4 bg-white border border-gray-200 rounded-lg"
        ),
        
        # Loading indicators
        Div(
            Div(class_="w-6 h-6 border-t-2 border-blue-500 border-r-2 rounded-full animate-spin mx-auto"),
            P("Loading template...", class_="text-center text-gray-700 mt-2"),
            id="template-indicator",
            class_="htmx-indicator py-4"
        ),
        Div(
            Div(class_="w-6 h-6 border-t-2 border-blue-500 border-r-2 rounded-full animate-spin mx-auto"),
            P("Loading entries...", class_="text-center text-gray-700 mt-2"),
            id="entries-indicator",
            class_="htmx-indicator py-4"
        ),
        
        class_="p-6 bg-white shadow-md rounded-lg"
    )
