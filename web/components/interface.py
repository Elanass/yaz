"""
Dynamic FastHTML Interface Components for Gastric ADCI Platform
Pure dynamic components for real-time collaboration and multi-environment deployment
"""

from typing import Any, Dict, List, Optional
from fasthtml.common import (
    Div, H1, H2, H3, H4, P, Form, Input, Button, A, Br, Script, Table, Tr, Td, Th, 
    Span, Strong, Select, Option, Textarea, Label, Ul, Li, Pre, Code
)


def create_dynamic_layout(title: str, content: Any, environment: str = "local", 
                         breadcrumbs: Optional[List[Dict[str, str]]] = None) -> Div:
    """Create dynamic page layout that integrates with static templates"""
    
    layout_children = []
    
    # Add breadcrumbs if provided
    if breadcrumbs:
        breadcrumb_items = []
        for i, item in enumerate(breadcrumbs):
            if i > 0:
                breadcrumb_items.append(Span(" / ", cls="breadcrumb-separator"))
            
            if item.get("url"):
                breadcrumb_items.append(A(item["text"], href=item["url"], cls="breadcrumb-link"))
            else:
                breadcrumb_items.append(Span(item["text"], cls="breadcrumb-current"))
        
        layout_children.append(
            Div(*breadcrumb_items, cls="breadcrumb", id="dynamic-breadcrumb")
        )
    
    # Main content with environment-aware styling
    layout_children.extend([
        H1(title, cls=f"page-title environment-{environment}"),
        content if isinstance(content, (list, tuple)) else [content]
    ])
    
    return Div(
        *layout_children,
        cls="dynamic-page-content",
        data_environment=environment
    )


def collaboration_panel(mode: str = "local", active_users: List[Dict[str, Any]] = None) -> Div:
    """Dynamic collaboration panel for real-time features"""
    
    if mode == "local":
        return Div(
            P("Local Mode - No collaboration features", cls="collaboration-disabled"),
            cls="collaboration-panel local-mode"
        )
    
    panel_children = [
        H4("🤝 Active Collaboration", cls="collaboration-title")
    ]
    
    # Active users display
    if active_users:
        user_items = []
        for user in active_users:
            status_color = "online" if user.get("status") == "active" else "idle"
            user_items.append(
                Li(
                    Span("●", cls=f"user-status {status_color}"),
                    Span(user.get("name", "Anonymous"), cls="user-name"),
                    Span(user.get("role", "User"), cls="user-role"),
                    cls="user-item"
                )
            )
        panel_children.append(
            Div(
                Strong(f"{len(active_users)} active users"),
                Ul(*user_items, cls="user-list"),
                cls="active-users"
            )
        )
    else:
        panel_children.append(
            P("No other users currently active", cls="no-users")
        )
    
    # P2P specific features
    if mode == "p2p":
        panel_children.extend([
            Div(
                Strong("P2P Network Status"),
                Div(id="p2p-status-display", cls="network-status"),
                cls="p2p-status"
            ),
            Button(
                "Sync Data",
                onclick="gastricApp.shareData({type: 'manual_sync'})",
                cls="btn btn-sm btn-outline"
            )
        ])
    
    # Cloud collaboration features
    elif mode == "multicloud":
        panel_children.extend([
            Div(
                Strong("Cloud Sync Status"),
                Div(id="cloud-status-display", cls="network-status"),
                cls="cloud-status"
            ),
            Button(
                "Force Sync",
                onclick="gastricApp.syncToCloud({type: 'force_sync'})",
                cls="btn btn-sm btn-outline"
            )
        ])
    
    return Div(
        *panel_children,
        cls=f"collaboration-panel {mode}-mode",
        id="collaboration-panel"
    )


def real_time_form(title: str, fields: List[Dict[str, Any]], action: str = "/api/v1/submit",
                  collaboration_enabled: bool = False) -> Div:
    """Dynamic form with real-time collaboration features"""
    
    form_fields = []
    
    for field in fields:
        field_type = field.get("type", "text")
        field_name = field.get("name", "")
        field_label = field.get("label", field_name.title())
        field_required = field.get("required", False)
        field_value = field.get("value", "")
        field_placeholder = field.get("placeholder", "")
        
        field_wrapper = Div(cls="form-field")
        field_elements = [
            Label(field_label, for_=field_name, cls="form-label")
        ]
        
        # Add real-time collaboration indicators
        if collaboration_enabled:
            field_elements.append(
                Span(cls=f"collaboration-indicator", id=f"collab-{field_name}")
            )
        
        # Create field based on type
        if field_type == "select":
            options = field.get("options", [])
            option_elements = [Option("Select...", value="")]
            for option in options:
                option_elements.append(
                    Option(
                        option.get("label", ""),
                        value=option.get("value", ""),
                        selected=(option.get("value") == field_value)
                    )
                )
            field_elements.append(
                Select(
                    *option_elements,
                    name=field_name,
                    id=field_name,
                    required=field_required,
                    cls="form-control",
                    onchange="gastricApp.handleFieldUpdate(this)" if collaboration_enabled else None
                )
            )
        elif field_type == "textarea":
            field_elements.append(
                Textarea(
                    field_value,
                    name=field_name,
                    id=field_name,
                    placeholder=field_placeholder,
                    required=field_required,
                    rows=field.get("rows", 4),
                    cls="form-control",
                    oninput="gastricApp.handleFieldUpdate(this)" if collaboration_enabled else None
                )
            )
        else:
            field_elements.append(
                Input(
                    type=field_type,
                    name=field_name,
                    id=field_name,
                    value=field_value,
                    placeholder=field_placeholder,
                    required=field_required,
                    cls="form-control",
                    oninput="gastricApp.handleFieldUpdate(this)" if collaboration_enabled else None
                )
            )
        
        field_wrapper.children = field_elements
        form_fields.append(field_wrapper)
    
    return Div(
        H3(title, cls="form-title"),
        Form(
            *form_fields,
            Div(
                Button("Submit", type="submit", cls="btn btn-primary"),
                Button("Save Draft", type="button", cls="btn btn-secondary", 
                      onclick="gastricApp.saveDraft(this.form)" if collaboration_enabled else None),
                cls="form-actions"
            ),
            action=action,
            method="post",
            cls="real-time-form ajax-form",
            onsubmit="return gastricApp.handleFormSubmit(this)"
        ),
        cls="dynamic-form-container"
    )


def data_visualization_card(title: str, data: Dict[str, Any], chart_type: str = "table") -> Div:
    """Dynamic data visualization component"""
    
    card_children = [
        Div(
            H4(title),
            Span(f"Updated: {data.get('last_updated', 'Unknown')}", cls="update-time"),
            cls="card-header"
        )
    ]
    
    if chart_type == "table" and data.get("rows"):
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        
        header_cells = [Th(header) for header in headers]
        table_rows = [Tr(*header_cells)]
        
        for row in rows:
            row_cells = [Td(cell) for cell in row]
            table_rows.append(Tr(*row_cells))
        
        card_children.append(
            Div(
                Table(*table_rows, cls="data-table"),
                cls="card-body"
            )
        )
    
    elif chart_type == "metrics" and data.get("metrics"):
        metrics = data.get("metrics", {})
        metric_items = []
        
        for metric_name, metric_value in metrics.items():
            metric_items.append(
                Div(
                    Strong(str(metric_value), cls="metric-value"),
                    P(metric_name.replace("_", " ").title(), cls="metric-label"),
                    cls="metric-item"
                )
            )
        
        card_children.append(
            Div(
                Div(*metric_items, cls="metrics-grid"),
                cls="card-body"
            )
        )
    
    elif chart_type == "chart":
        # Placeholder for chart integration
        card_children.append(
            Div(
                Div(cls="chart-placeholder", id=f"chart-{title.lower().replace(' ', '-')}"),
                Script(f"""
                    // Initialize chart for {title}
                    if (typeof Chart !== 'undefined') {{
                        // Chart.js integration would go here
                        console.log('Chart data:', {data});
                    }}
                """),
                cls="card-body"
            )
        )
    
    return Div(
        *card_children,
        cls="data-visualization-card card",
        data_chart_type=chart_type
    )


def decision_support_interface(engine_type: str = "adci", patient_data: Optional[Dict] = None) -> Div:
    """Dynamic decision support interface"""
    
    interface_children = [
        H3(f"🧠 {engine_type.upper()} Decision Support", cls="decision-title")
    ]
    
    # Patient data summary
    if patient_data:
        summary_items = []
        for key, value in patient_data.items():
            summary_items.append(
                Div(
                    Strong(f"{key.replace('_', ' ').title()}:"),
                    Span(str(value)),
                    cls="patient-data-item"
                )
            )
        
        interface_children.append(
            Div(
                H4("Patient Summary"),
                Div(*summary_items, cls="patient-summary"),
                cls="patient-data-section"
            )
        )
    
    # Decision form
    decision_fields = [
        {
            "name": "patient_age",
            "label": "Patient Age",
            "type": "number",
            "required": True,
            "placeholder": "Enter patient age"
        },
        {
            "name": "tumor_stage",
            "label": "Tumor Stage",
            "type": "select",
            "required": True,
            "options": [
                {"value": "T1", "label": "T1 - Small tumor"},
                {"value": "T2", "label": "T2 - Medium tumor"},
                {"value": "T3", "label": "T3 - Large tumor"},
                {"value": "T4", "label": "T4 - Very large tumor"}
            ]
        },
        {
            "name": "clinical_notes",
            "label": "Clinical Notes",
            "type": "textarea",
            "placeholder": "Additional clinical observations",
            "rows": 4
        }
    ]
    
    interface_children.append(
        real_time_form(
            "Decision Analysis",
            decision_fields,
            action="/api/v1/decisions/analyze",
            collaboration_enabled=True
        )
    )
    
    # Results area
    interface_children.append(
        Div(
            H4("Analysis Results"),
            Div(id="decision-results", cls="results-container"),
            cls="results-section"
        )
    )
    
    return Div(
        *interface_children,
        cls="decision-support-interface",
        data_engine=engine_type
    )


def case_management_dashboard(cases: List[Dict[str, Any]] = None, mode: str = "local") -> Div:
    """Dynamic case management dashboard"""
    
    dashboard_children = [
        Div(
            H2("📋 Case Management", cls="dashboard-title"),
            collaboration_panel(mode),
            cls="dashboard-header"
        )
    ]
    
    # Cases summary
    if cases:
        case_cards = []
        for case in cases[:5]:  # Show recent 5 cases
            case_cards.append(
                Div(
                    H5(case.get("title", f"Case #{case.get('id', 'Unknown')}")),
                    P(case.get("status", "Unknown"), cls=f"case-status {case.get('status', '').lower()}"),
                    P(f"Last updated: {case.get('updated_at', 'Unknown')}", cls="case-date"),
                    A("View Details", href=f"/cases/{case.get('id')}", cls="btn btn-sm btn-outline"),
                    cls="case-card card"
                )
            )
        
        dashboard_children.extend([
            H3("Recent Cases"),
            Div(*case_cards, cls="cases-grid")
        ])
    else:
        dashboard_children.append(
            Div(
                P("No cases available", cls="no-cases"),
                Button("Create New Case", cls="btn btn-primary", 
                      onclick="window.location.href='/cases/new'"),
                cls="empty-state"
            )
        )
    
    # Quick actions
    dashboard_children.append(
        Div(
            H3("Quick Actions"),
            Div(
                Button("📝 New Case", onclick="window.location.href='/cases/new'", 
                      cls="btn btn-outline"),
                Button("🔍 Search Cases", onclick="gastricApp.showSearchModal()", 
                      cls="btn btn-outline"),
                Button("📊 Generate Report", onclick="window.location.href='/reports/new'", 
                      cls="btn btn-outline"),
                Button("📚 View Guidelines", onclick="window.location.href='/education'", 
                      cls="btn btn-outline"),
                cls="actions-grid"
            ),
            cls="quick-actions"
        )
    )
    
    return Div(
        *dashboard_children,
        cls="case-management-dashboard",
        data_mode=mode
    )


def notification_system() -> Div:
    """Dynamic notification system component"""
    return Div(
        # Notifications will be injected here dynamically
        cls="notification-system",
        id="dynamic-notifications"
    )


def status_indicator_component(status: str, label: str = "", real_time: bool = False) -> Span:
    """Dynamic status indicator with real-time updates"""
    classes = f"status-indicator status-{status}"
    if real_time:
        classes += " real-time"
    
    return Span(
        "●" if not label else f"● {label}",
        cls=classes,
        id=f"status-{status}" if real_time else None
    )


def loading_component(message: str = "Processing...", show_progress: bool = False) -> Div:
    """Dynamic loading component"""
    loading_children = [
        Div(cls="loading-spinner"),
        P(message, cls="loading-message")
    ]
    
    if show_progress:
        loading_children.append(
            Div(
                Div(cls="progress-bar", id="dynamic-progress"),
                cls="progress-container"
            )
        )
    
    return Div(
        *loading_children,
        cls="dynamic-loading",
        id="dynamic-loading"
    )


def environment_switcher(current_env: str, available_envs: List[str]) -> Div:
    """Dynamic environment switcher (if enabled)"""
    
    if len(available_envs) <= 1:
        return Div()  # No switcher needed
    
    env_options = []
    for env in available_envs:
        env_display = {
            'local': 'Local Development',
            'p2p': 'P2P Network',
            'multicloud': 'Multi-Cloud'
        }.get(env, env.title())
        
        env_options.append(
            Option(env_display, value=env, selected=(env == current_env))
        )
    
    return Div(
        Label("Environment:", for_="env-switcher"),
        Select(
            *env_options,
            id="env-switcher",
            onchange="gastricApp.switchEnvironment(this.value)",
            cls="env-switcher"
        ),
        cls="environment-switcher"
    )


def clinical_form(title: str, fields: List[Dict[str, Any]], action: str = "/", method: str = "post") -> Div:
    """Create a clinical form component using FastHTML"""
    form_fields = []
    
    for field in fields:
        field_type = field.get("type", "text")
        field_name = field.get("name", "")
        field_label = field.get("label", field_name.title())
        field_required = field.get("required", False)
        field_value = field.get("value", "")
        field_placeholder = field.get("placeholder", "")
        
        field_div = Div(cls="form-field")
        field_div.children = [
            Div(field_label, cls="form-label")
        ]
        
        if field_type == "select":
            options = field.get("options", [])
            option_elements = [Option("Select...", value="")]
            for option in options:
                option_elements.append(
                    Option(
                        option.get("label", ""),
                        value=option.get("value", ""),
                        selected=(option.get("value") == field_value)
                    )
                )
            field_div.children.append(
                Select(*option_elements, name=field_name, id=field_name, required=field_required)
            )
        elif field_type == "textarea":
            field_div.children.append(
                Textarea(
                    field_value,
                    name=field_name,
                    id=field_name,
                    placeholder=field_placeholder,
                    required=field_required,
                    rows=field.get("rows", 4)
                )
            )
        else:
            field_div.children.append(
                Input(
                    type=field_type,
                    name=field_name,
                    id=field_name,
                    value=field_value,
                    placeholder=field_placeholder,
                    required=field_required
                )
            )
        
        form_fields.append(field_div)
    
    return Div(
        H3(title, cls="form-title"),
        Form(
            *form_fields,
            Button("Submit", type="submit", cls="btn btn-primary"),
            action=action,
            method=method,
            cls="ajax-form"
        ),
        cls="clinical-form"
    )


def clinical_table(title: str, headers: List[str], rows: List[List[str]], actions: Optional[List[Dict[str, str]]] = None) -> Div:
    """Create a clinical data table component using FastHTML"""
    
    # Create header row
    header_cells = [Th(header) for header in headers]
    if actions:
        header_cells.append(Th("Actions"))
    
    # Create data rows
    table_rows = [Tr(*header_cells)]
    for row in rows:
        row_cells = [Td(cell) for cell in row]
        
        if actions:
            action_buttons = []
            for action in actions:
                action_buttons.append(
                    A(
                        action.get("label", "Action"),
                        href=action.get("url", "#"),
                        cls=f"btn btn-sm {action.get('class', 'btn-outline')}"
                    )
                )
            row_cells.append(Td(*action_buttons, cls="action-cell"))
        
        table_rows.append(Tr(*row_cells))
    
    return Div(
        H3(title, cls="table-title"),
        Table(*table_rows, cls="table"),
        cls="clinical-table"
    )


def clinical_card(title: str, content: Any, status: str = "info", actions: Optional[List[Dict[str, str]]] = None) -> Div:
    """Create a clinical information card component using FastHTML"""
    
    card_children = [
        Div(
            H4(title),
            cls="card-header"
        ),
        Div(
            content if isinstance(content, (list, tuple)) else [content],
            cls="card-body"
        )
    ]
    
    if actions:
        action_buttons = []
        for action in actions:
            action_buttons.append(
                A(
                    action.get("label", "Action"),
                    href=action.get("url", "#"),
                    cls=f"btn btn-sm {action.get('class', 'btn-outline')}"
                )
            )
        card_children.append(
            Div(*action_buttons, cls="card-actions")
        )
    
    return Div(
        *card_children,
        cls=f"clinical-card card card-{status}"
    )


def create_dashboard() -> Div:
    """Create dashboard with real-time components"""
    return Div(
        H2("Surgery Analytics Dashboard", cls="dashboard-title"),
        
        # Status cards
        Div(
            clinical_card(
                "System Status",
                Div(
                    P("All systems operational", cls="status-text"),
                    Span("●", cls="status-indicator status-success")
                ),
                "success"
            ),
            clinical_card(
                "Active Cases",
                Div(
                    Strong("12", cls="metric-value"),
                    P("cases in progress", cls="metric-label")
                ),
                "info"
            ),
            clinical_card(
                "Recent Reports",
                Div(
                    Strong("8", cls="metric-value"),
                    P("generated today", cls="metric-label")
                ),
                "info"
            ),
            cls="dashboard-cards"
        ),
        
        # Recent activity
        Div(
            clinical_table(
                "Recent Activity",
                ["Time", "User", "Action", "Status"],
                [
                    ["10:30 AM", "Dr. Smith", "Created case", "Success"],
                    ["10:15 AM", "Dr. Johnson", "Generated report", "Success"],
                    ["09:45 AM", "Dr. Davis", "Updated protocol", "Success"]
                ]
            ),
            cls="recent-activity"
        ),
        
        cls="dashboard"
    )


def create_decision_form() -> Div:
    """Create decision support form"""
    return clinical_form(
        "Clinical Decision Support",
        [
            {
                "name": "patient_age",
                "label": "Patient Age",
                "type": "number",
                "required": True,
                "placeholder": "Enter patient age"
            },
            {
                "name": "tumor_stage",
                "label": "Tumor Stage",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "T1", "label": "T1 - Small tumor"},
                    {"value": "T2", "label": "T2 - Medium tumor"},
                    {"value": "T3", "label": "T3 - Large tumor"},
                    {"value": "T4", "label": "T4 - Very large tumor"}
                ]
            },
            {
                "name": "comorbidities",
                "label": "Comorbidities",
                "type": "textarea",
                "placeholder": "List any relevant comorbidities",
                "rows": 3
            }
        ],
        action="/api/v1/decisions/analyze",
        method="post"
    )


def status_indicator(status: str, label: str = "") -> Span:
    """Create a status indicator component"""
    return Span(
        "●" if not label else f"● {label}",
        cls=f"status status-{status}"
    )


def loading_spinner(text: str = "Loading...") -> Div:
    """Create a loading spinner component"""
    return Div(
        Div(cls="loading"),
        Span(text, cls="loading-text"),
        cls="loading-container"
    )


def notification(message: str, type: str = "info") -> Div:
    """Create a notification component"""
    return Div(
        Span(message),
        Button("×", onclick="this.parentElement.remove()", cls="btn btn-sm"),
        cls=f"notification status-{type}",
        style="position: fixed; top: 1rem; right: 1rem; z-index: 1000;"
    )


def breadcrumb(items: List[Dict[str, str]]) -> Div:
    """Create a breadcrumb navigation component"""
    breadcrumb_items = []
    for i, item in enumerate(items):
        if i > 0:
            breadcrumb_items.append(Span(" / ", cls="breadcrumb-separator"))
        
        if item.get("url"):
            breadcrumb_items.append(A(item["label"], href=item["url"], cls="breadcrumb-link"))
        else:
            breadcrumb_items.append(Span(item["label"], cls="breadcrumb-current"))
    
    return Div(*breadcrumb_items, cls="breadcrumb")


def data_grid(data: List[Dict[str, Any]], columns: List[Dict[str, str]]) -> Div:
    """Create a data grid with sorting and filtering"""
    headers = [Th(col["label"], data_sort=col["key"]) for col in columns]
    
    rows = []
    for item in data:
        cells = []
        for col in columns:
            value = item.get(col["key"], "")
            if col.get("format") == "date":
                # Format date if needed
                value = str(value)  # Simplified for now
            cells.append(Td(value))
        rows.append(Tr(*cells))
    
    return Div(
        Table(
            Tr(*headers),
            *rows,
            cls="table sortable"
        ),
        cls="data-grid"
    )

# End of FastHTML dynamic components
