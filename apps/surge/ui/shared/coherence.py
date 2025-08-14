"""
UI Coherence Module
Ensures consistent design and behavior across Web, Desktop, and Mobile platforms
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class UITheme:
    """Shared UI theme configuration"""
    primary_color: str = "#3b82f6"
    secondary_color: str = "#64748b"
    success_color: str = "#10b981"
    warning_color: str = "#f59e0b"
    error_color: str = "#ef4444"
    background_color: str = "#f8fafc"
    surface_color: str = "#ffffff"
    text_primary: str = "#1e293b"
    text_secondary: str = "#64748b"
    border_radius: str = "8px"
    shadow: str = "0 1px 3px rgba(0,0,0,0.1)"


@dataclass
class ComponentSpecs:
    """Shared component specifications"""
    button_height: str = "40px"
    input_height: str = "40px"
    card_padding: str = "1.5rem"
    grid_gap: str = "1rem"
    header_height: str = "60px"
    sidebar_width: str = "280px"


class UICoherence:
    """Manages UI coherence across platforms"""
    
    def __init__(self):
        self.theme = UITheme()
        self.specs = ComponentSpecs()
    
    def get_css_variables(self) -> str:
        """Generate CSS custom properties for web platform"""
        return f"""
        :root {{
            --primary-color: {self.theme.primary_color};
            --secondary-color: {self.theme.secondary_color};
            --success-color: {self.theme.success_color};
            --warning-color: {self.theme.warning_color};
            --error-color: {self.theme.error_color};
            --background-color: {self.theme.background_color};
            --surface-color: {self.theme.surface_color};
            --text-primary: {self.theme.text_primary};
            --text-secondary: {self.theme.text_secondary};
            --border-radius: {self.theme.border_radius};
            --shadow: {self.theme.shadow};
            --button-height: {self.specs.button_height};
            --input-height: {self.specs.input_height};
            --card-padding: {self.specs.card_padding};
            --grid-gap: {self.specs.grid_gap};
            --header-height: {self.specs.header_height};
            --sidebar-width: {self.specs.sidebar_width};
        }}
        """
    
    def get_react_native_theme(self) -> Dict[str, Any]:
        """Generate theme object for React Native (mobile)"""
        return {
            "colors": {
                "primary": self.theme.primary_color,
                "secondary": self.theme.secondary_color,
                "success": self.theme.success_color,
                "warning": self.theme.warning_color,
                "error": self.theme.error_color,
                "background": self.theme.background_color,
                "surface": self.theme.surface_color,
                "textPrimary": self.theme.text_primary,
                "textSecondary": self.theme.text_secondary,
            },
            "spacing": {
                "xs": 4,
                "sm": 8,
                "md": 16,
                "lg": 24,
                "xl": 32,
            },
            "borderRadius": {
                "sm": 4,
                "md": 8,
                "lg": 12,
            }
        }
    
    def get_electron_theme(self) -> Dict[str, Any]:
        """Generate theme object for Electron (desktop)"""
        return {
            "primary": self.theme.primary_color,
            "secondary": self.theme.secondary_color,
            "success": self.theme.success_color,
            "warning": self.theme.warning_color,
            "error": self.theme.error_color,
            "background": self.theme.background_color,
            "surface": self.theme.surface_color,
            "textPrimary": self.theme.text_primary,
            "textSecondary": self.theme.text_secondary,
            "borderRadius": self.theme.border_radius,
            "shadow": self.theme.shadow,
            "headerHeight": self.specs.header_height,
            "sidebarWidth": self.specs.sidebar_width,
        }
    
    def get_shared_components_config(self) -> Dict[str, Any]:
        """Get configuration for shared components across platforms"""
        return {
            "navigation": {
                "items": [
                    {"label": "Dashboard", "icon": "dashboard", "route": "/"},
                    {"label": "Cases", "icon": "cases", "route": "/cases"},
                    {"label": "Analytics", "icon": "analytics", "route": "/analytics"},
                    {"label": "Settings", "icon": "settings", "route": "/settings"},
                ]
            },
            "forms": {
                "validationRules": {
                    "required": "This field is required",
                    "email": "Please enter a valid email",
                    "minLength": "Minimum {min} characters required",
                }
            },
            "data": {
                "syncInterval": 30000,  # 30 seconds
                "offlineTimeout": 5000,  # 5 seconds
                "retryAttempts": 3,
            }
        }


# Global coherence instance
ui_coherence = UICoherence()
