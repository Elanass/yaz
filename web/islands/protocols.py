"""
Protocol List Island - Display and filter available protocols.
"""

import json
from typing import Dict, List, Optional

from fasthtml.common import *


def ProtocolCard(protocol: Dict) -> Div:
    """Individual protocol card component."""
    stage_badges = []
    for stage in protocol.get("applicable_stages", []):
        stage_badges.append(
            Span(stage, cls="badge badge-outline badge-sm mr-1")
        )
    
    evidence_color = {
        "1": "badge-success",
        "2": "badge-info", 
        "3": "badge-warning",
        "4": "badge-error",
        "5": "badge-neutral"
    }.get(protocol.get("evidence_level", "5"), "badge-neutral")
    
    return Div(
        cls="card bg-base-100 shadow-md hover:shadow-lg transition-shadow duration-200",
        children=[
            Div(
                cls="card-body p-4",
                children=[
                    # Header with title and category
                    Div(
                        cls="flex justify-between items-start mb-3",
                        children=[
                            H3(
                                protocol.get("name", "Unknown Protocol"),
                                cls="card-title text-lg font-semibold text-primary"
                            ),
                            Div(
                                cls="flex gap-2",
                                children=[
                                    Span(
                                        protocol.get("category", "").replace("_", " ").title(),
                                        cls="badge badge-primary badge-sm"
                                    ),
                                    Span(
                                        f"Level {protocol.get('evidence_level', '5')}",
                                        cls=f"badge {evidence_color} badge-sm"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Description
                    P(
                        protocol.get("description", "No description available")[:150] + 
                        ("..." if len(protocol.get("description", "")) > 150 else ""),
                        cls="text-sm text-base-content/70 mb-3"
                    ),
                    
                    # Applicable stages
                    Div(
                        cls="mb-3",
                        children=[
                            Span("Stages: ", cls="text-xs font-medium text-base-content/60"),
                            Div(
                                cls="flex flex-wrap gap-1 mt-1",
                                children=stage_badges if stage_badges else [
                                    Span("All stages", cls="badge badge-outline badge-xs")
                                ]
                            )
                        ]
                    ),
                    
                    # Statistics
                    Div(
                        cls="stats stats-horizontal w-full mb-3",
                        children=[
                            Div(
                                cls="stat p-2",
                                children=[
                                    Div("Patients", cls="stat-title text-xs"),
                                    Div(
                                        protocol.get("total_patients_treated", 0),
                                        cls="stat-value text-sm"
                                    )
                                ]
                            ),
                            Div(
                                cls="stat p-2",
                                children=[
                                    Div("Success Rate", cls="stat-title text-xs"),
                                    Div(
                                        f"{protocol.get('success_rate', 0):.1f}%" if protocol.get('success_rate') else "N/A",
                                        cls="stat-value text-sm"
                                    )
                                ]
                            ),
                            Div(
                                cls="stat p-2",
                                children=[
                                    Div("Updated", cls="stat-title text-xs"),
                                    Div(
                                        protocol.get("updated_at", "")[:10] if protocol.get("updated_at") else "N/A",
                                        cls="stat-value text-xs"
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Actions
                    Div(
                        cls="card-actions justify-end",
                        children=[
                            Button(
                                "View Details",
                                cls="btn btn-outline btn-sm",
                                hx_get=f"/protocols/{protocol.get('id')}",
                                hx_target="#protocol-detail-modal .modal-box",
                                hx_trigger="click",
                                onclick="document.getElementById('protocol-detail-modal').showModal()"
                            ),
                            Button(
                                "Use Protocol",
                                cls="btn btn-primary btn-sm",
                                hx_get=f"/decision/new?protocol_id={protocol.get('id')}",
                                hx_target="#main-content",
                                hx_push_url="true"
                            )
                        ]
                    )
                ]
            )
        ]
    )

def ProtocolFilters(current_filters: Dict = None) -> Div:
    """Protocol filtering sidebar."""
    if current_filters is None:
        current_filters = {}
    
    return Div(
        cls="bg-base-200 p-4 rounded-lg",
        children=[
            H4("Filters", cls="font-semibold mb-4"),
            
            # Search
            Div(
                cls="form-control mb-4",
                children=[
                    Label("Search", cls="label label-text font-medium"),
                    Input(
                        type="text",
                        placeholder="Search protocols...",
                        cls="input input-bordered input-sm",
                        value=current_filters.get("search", ""),
                        name="search",
                        hx_get="/protocols",
                        hx_target="#protocol-list",
                        hx_trigger="keyup changed delay:300ms",
                        hx_include="[name='category'], [name='status'], [name='stage'], [name='evidence_level']"
                    )
                ]
            ),
            
            # Category filter
            Div(
                cls="form-control mb-4",
                children=[
                    Label("Category", cls="label label-text font-medium"),
                    Select(
                        name="category",
                        cls="select select-bordered select-sm",
                        hx_get="/protocols",
                        hx_target="#protocol-list",
                        hx_trigger="change",
                        hx_include="[name='search'], [name='status'], [name='stage'], [name='evidence_level']",
                        children=[
                            Option("All Categories", value="", 
                                  selected="" == current_filters.get("category", "")),
                            Option("Surgical", value="surgical",
                                  selected="surgical" == current_filters.get("category")),
                            Option("Chemotherapy", value="chemotherapy",
                                  selected="chemotherapy" == current_filters.get("category")),
                            Option("Radiation", value="radiation",
                                  selected="radiation" == current_filters.get("category")),
                            Option("Immunotherapy", value="immunotherapy",
                                  selected="immunotherapy" == current_filters.get("category")),
                            Option("Targeted Therapy", value="targeted_therapy",
                                  selected="targeted_therapy" == current_filters.get("category")),
                            Option("Palliative", value="palliative",
                                  selected="palliative" == current_filters.get("category")),
                            Option("Diagnostic", value="diagnostic",
                                  selected="diagnostic" == current_filters.get("category")),
                            Option("Monitoring", value="monitoring",
                                  selected="monitoring" == current_filters.get("category"))
                        ]
                    )
                ]
            ),
            
            # Status filter
            Div(
                cls="form-control mb-4",
                children=[
                    Label("Status", cls="label label-text font-medium"),
                    Select(
                        name="status",
                        cls="select select-bordered select-sm",
                        hx_get="/protocols",
                        hx_target="#protocol-list",
                        hx_trigger="change",
                        hx_include="[name='search'], [name='category'], [name='stage'], [name='evidence_level']",
                        children=[
                            Option("All Status", value="",
                                  selected="" == current_filters.get("status", "")),
                            Option("Active", value="active",
                                  selected="active" == current_filters.get("status")),
                            Option("Draft", value="draft",
                                  selected="draft" == current_filters.get("status")),
                            Option("Deprecated", value="deprecated",
                                  selected="deprecated" == current_filters.get("status"))
                        ]
                    )
                ]
            ),
            
            # Stage filter
            Div(
                cls="form-control mb-4",
                children=[
                    Label("Cancer Stage", cls="label label-text font-medium"),
                    Select(
                        name="stage",
                        cls="select select-bordered select-sm",
                        hx_get="/protocols",
                        hx_target="#protocol-list",
                        hx_trigger="change",
                        hx_include="[name='search'], [name='category'], [name='status'], [name='evidence_level']",
                        children=[
                            Option("All Stages", value="",
                                  selected="" == current_filters.get("stage", "")),
                            Option("Stage 0", value="0",
                                  selected="0" == current_filters.get("stage")),
                            Option("Stage I", value="I",
                                  selected="I" == current_filters.get("stage")),
                            Option("Stage II", value="II",
                                  selected="II" == current_filters.get("stage")),
                            Option("Stage III", value="III",
                                  selected="III" == current_filters.get("stage")),
                            Option("Stage IV", value="IV",
                                  selected="IV" == current_filters.get("stage"))
                        ]
                    )
                ]
            ),
            
            # Evidence level filter
            Div(
                cls="form-control mb-4",
                children=[
                    Label("Evidence Level", cls="label label-text font-medium"),
                    Select(
                        name="evidence_level",
                        cls="select select-bordered select-sm",
                        hx_get="/protocols",
                        hx_target="#protocol-list",
                        hx_trigger="change",
                        hx_include="[name='search'], [name='category'], [name='status'], [name='stage']",
                        children=[
                            Option("All Levels", value="",
                                  selected="" == current_filters.get("evidence_level", "")),
                            Option("Level 1 (High RCT)", value="1",
                                  selected="1" == current_filters.get("evidence_level")),
                            Option("Level 2 (Lower RCT)", value="2",
                                  selected="2" == current_filters.get("evidence_level")),
                            Option("Level 3 (Cohort)", value="3",
                                  selected="3" == current_filters.get("evidence_level")),
                            Option("Level 4 (Case series)", value="4",
                                  selected="4" == current_filters.get("evidence_level")),
                            Option("Level 5 (Expert opinion)", value="5",
                                  selected="5" == current_filters.get("evidence_level"))
                        ]
                    )
                ]
            ),
            
            # Clear filters
            Button(
                "Clear All Filters",
                cls="btn btn-outline btn-sm w-full",
                onclick="window.location.href='/protocols'"
            )
        ]
    )

def ProtocolList(protocols: List[Dict], total: int, current_page: int = 1, 
                 filters: Dict = None) -> Div:
    """Main protocol list component."""
    if filters is None:
        filters = {}
    
    # Calculate pagination
    per_page = 12
    total_pages = (total + per_page - 1) // per_page
    
    protocol_cards = []
    for protocol in protocols:
        protocol_cards.append(ProtocolCard(protocol))
    
    # Pagination component
    pagination = Div(
        cls="flex justify-center mt-8",
        children=[
            Div(
                cls="join",
                children=[
                    Button(
                        "«",
                        cls="join-item btn btn-sm" + (" btn-disabled" if current_page <= 1 else ""),
                        hx_get=f"/protocols?page={current_page - 1}",
                        hx_target="#protocol-list",
                        hx_include="[name='search'], [name='category'], [name='status'], [name='stage'], [name='evidence_level']"
                        if current_page > 1 else None
                    ),
                    Span(
                        f"Page {current_page} of {total_pages}",
                        cls="join-item btn btn-sm btn-disabled"
                    ),
                    Button(
                        "»",
                        cls="join-item btn btn-sm" + (" btn-disabled" if current_page >= total_pages else ""),
                        hx_get=f"/protocols?page={current_page + 1}",
                        hx_target="#protocol-list",
                        hx_include="[name='search'], [name='category'], [name='status'], [name='stage'], [name='evidence_level']"
                        if current_page < total_pages else None
                    )
                ]
            )
        ]
    ) if total_pages > 1 else Div()
    
    return Div(
        id="protocol-list",
        children=[
            # Results summary
            Div(
                cls="flex justify-between items-center mb-6",
                children=[
                    H2(
                        f"Clinical Protocols ({total} results)",
                        cls="text-2xl font-bold text-primary"
                    ),
                    Div(
                        cls="text-sm text-base-content/60",
                        children=[
                            f"Showing {len(protocols)} of {total} protocols"
                        ]
                    )
                ]
            ),
            
            # Protocol grid
            Div(
                cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                children=protocol_cards if protocol_cards else [
                    Div(
                        cls="col-span-full text-center py-12",
                        children=[
                            Div("🔍", cls="text-6xl mb-4"),
                            H3("No protocols found", cls="text-xl font-semibold mb-2"),
                            P("Try adjusting your search criteria or filters.", 
                              cls="text-base-content/60")
                        ]
                    )
                ]
            ),
            
            pagination
        ]
    )

def ProtocolDetailModal() -> Dialog:
    """Modal for displaying protocol details."""
    return Dialog(
        id="protocol-detail-modal",
        cls="modal",
        children=[
            Div(
                cls="modal-box w-11/12 max-w-4xl",
                children=[
                    # Content will be loaded via HTMX
                    Div("Loading...", cls="loading loading-spinner")
                ]
            ),
            Form(
                method="dialog",
                cls="modal-backdrop",
                children=[Button("close")]
            )
        ]
    )

def ProtocolsIsland(protocols: List[Dict] = None, total: int = 0, 
                   current_page: int = 1, filters: Dict = None) -> Div:
    """Complete protocols island with filters and list."""
    if protocols is None:
        protocols = []
    if filters is None:
        filters = {}
    
    return Div(
        cls="container mx-auto px-4 py-8",
        children=[
            # Page header
            Div(
                cls="hero bg-gradient-to-r from-primary/10 to-secondary/10 rounded-lg mb-8",
                children=[
                    Div(
                        cls="hero-content text-center py-12",
                        children=[
                            Div(
                                cls="max-w-md",
                                children=[
                                    H1("Clinical Protocols", cls="text-4xl font-bold text-primary mb-4"),
                                    P("Evidence-based treatment protocols for gastric oncology and surgery.",
                                      cls="text-lg text-base-content/80")
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Layout: Filters + Content
            Div(
                cls="grid grid-cols-1 lg:grid-cols-4 gap-6",
                children=[
                    # Filters sidebar
                    Div(
                        cls="lg:col-span-1",
                        children=[ProtocolFilters(filters)]
                    ),
                    
                    # Main content
                    Div(
                        cls="lg:col-span-3",
                        children=[ProtocolList(protocols, total, current_page, filters)]
                    )
                ]
            ),
            
            # Protocol detail modal
            ProtocolDetailModal()
        ]
    )
