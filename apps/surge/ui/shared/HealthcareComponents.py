"""
Shared Healthcare Components
Reusable components for Web, Desktop, and Mobile platforms
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .coherence import ui_coherence


@dataclass
class CaseData:
    """Shared case data structure"""
    id: str
    patient_name: str
    procedure: str
    status: str
    scheduled_date: str
    surgeon: str
    priority: str = "normal"
    notes: Optional[str] = None


@dataclass
class ComponentProps:
    """Base component properties"""
    id: str
    className: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    disabled: bool = False


class HealthcareComponents:
    """Shared healthcare component definitions"""
    
    @staticmethod
    def case_card_template(case: CaseData) -> Dict[str, Any]:
        """Template for case card component"""
        return {
            "type": "case_card",
            "data": {
                "id": case.id,
                "patient": case.patient_name,
                "procedure": case.procedure,
                "status": case.status,
                "scheduled": case.scheduled_date,
                "surgeon": case.surgeon,
                "priority": case.priority,
                "notes": case.notes,
            },
            "styling": {
                "backgroundColor": ui_coherence.theme.surface_color,
                "borderRadius": ui_coherence.theme.border_radius,
                "padding": ui_coherence.specs.card_padding,
                "shadow": ui_coherence.theme.shadow,
            }
        }
    
    @staticmethod
    def navigation_template() -> Dict[str, Any]:
        """Template for navigation component"""
        return {
            "type": "navigation",
            "config": ui_coherence.get_shared_components_config()["navigation"],
            "styling": {
                "backgroundColor": ui_coherence.theme.surface_color,
                "height": ui_coherence.specs.header_height,
                "borderBottom": f"1px solid {ui_coherence.theme.secondary_color}",
            }
        }
    
    @staticmethod
    def button_template(label: str, variant: str = "primary", onClick: str = "") -> Dict[str, Any]:
        """Template for button component"""
        colors = {
            "primary": ui_coherence.theme.primary_color,
            "secondary": ui_coherence.theme.secondary_color,
            "success": ui_coherence.theme.success_color,
            "warning": ui_coherence.theme.warning_color,
            "error": ui_coherence.theme.error_color,
        }
        
        return {
            "type": "button",
            "data": {
                "label": label,
                "variant": variant,
                "onClick": onClick,
            },
            "styling": {
                "backgroundColor": colors.get(variant, colors["primary"]),
                "color": "white",
                "height": ui_coherence.specs.button_height,
                "borderRadius": ui_coherence.theme.border_radius,
                "border": "none",
                "padding": "0 1rem",
                "cursor": "pointer",
            }
        }
    
    @staticmethod
    def dashboard_grid_template() -> Dict[str, Any]:
        """Template for dashboard grid layout"""
        return {
            "type": "dashboard_grid",
            "layout": {
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                "gap": ui_coherence.specs.grid_gap,
                "padding": ui_coherence.specs.card_padding,
            },
            "widgets": [
                {"type": "stats_card", "title": "Total Cases", "value": "156", "icon": "cases"},
                {"type": "stats_card", "title": "Today's Surgeries", "value": "8", "icon": "surgery"},
                {"type": "stats_card", "title": "Success Rate", "value": "97.2%", "icon": "success"},
                {"type": "stats_card", "title": "Avg Duration", "value": "2.5h", "icon": "time"},
            ]
        }
    
    @staticmethod
    def generate_web_html(component: Dict[str, Any]) -> str:
        """Generate HTML for web platform"""
        if component["type"] == "case_card":
            data = component["data"]
            style = component["styling"]
            return f"""
            <div class="case-card" style="background-color: {style['backgroundColor']}; 
                                          border-radius: {style['borderRadius']}; 
                                          padding: {style['padding']}; 
                                          box-shadow: {style['shadow']};">
                <h3>{data['patient']}</h3>
                <p><strong>Procedure:</strong> {data['procedure']}</p>
                <p><strong>Status:</strong> <span class="status-{data['status']}">{data['status']}</span></p>
                <p><strong>Date:</strong> {data['scheduled']}</p>
                <p><strong>Surgeon:</strong> {data['surgeon']}</p>
            </div>
            """
        elif component["type"] == "button":
            data = component["data"]
            style = component["styling"]
            return f"""
            <button class="btn btn-{data['variant']}" 
                    onclick="{data['onClick']}"
                    style="background-color: {style['backgroundColor']}; 
                           color: {style['color']}; 
                           height: {style['height']}; 
                           border-radius: {style['borderRadius']}; 
                           border: {style['border']}; 
                           padding: {style['padding']}; 
                           cursor: {style['cursor']};">
                {data['label']}
            </button>
            """
        return ""
    
    @staticmethod
    def generate_react_tsx(component: Dict[str, Any]) -> str:
        """Generate React TSX for desktop/mobile platforms"""
        if component["type"] == "case_card":
            data = component["data"]
            return f"""
            <View style={{{{
                backgroundColor: '{component["styling"]["backgroundColor"]}',
                borderRadius: {component["styling"]["borderRadius"].replace('px', '')},
                padding: {component["styling"]["padding"].replace('rem', '') * 16},
                marginBottom: 16,
                shadowColor: '#000',
                shadowOffset: {{ width: 0, height: 2 }},
                shadowOpacity: 0.1,
                shadowRadius: 3,
                elevation: 3,
            }}}}>
                <Text style={{{{ fontSize: 18, fontWeight: 'bold', marginBottom: 8 }}}}>{data['patient']}</Text>
                <Text style={{{{ marginBottom: 4 }}}}>Procedure: {data['procedure']}</Text>
                <Text style={{{{ marginBottom: 4 }}}}>Status: {data['status']}</Text>
                <Text style={{{{ marginBottom: 4 }}}}>Date: {data['scheduled']}</Text>
                <Text>Surgeon: {data['surgeon']}</Text>
            </View>
            """
        elif component["type"] == "button":
            data = component["data"]
            style = component["styling"]
            return f"""
            <TouchableOpacity 
                style={{{{
                    backgroundColor: '{style["backgroundColor"]}',
                    borderRadius: {style["borderRadius"].replace('px', '')},
                    paddingHorizontal: 16,
                    paddingVertical: 12,
                    alignItems: 'center',
                    justifyContent: 'center',
                }}}}
                onPress={{() => {data['onClick']}}}>
                <Text style={{{{ color: '{style["color"]}', fontWeight: 'bold' }}}}>{data['label']}</Text>
            </TouchableOpacity>
            """
        return ""


# Global components instance
healthcare_components = HealthcareComponents()
