"""
Template Coherence
Ensures consistent templates and layouts across Web, Desktop, and Mobile
"""

from typing import Dict, Any
from pathlib import Path


class TemplateManager:
    """Manages consistent templates across platforms"""
    
    def __init__(self):
        self.base_templates = self._load_base_templates()
    
    def _load_base_templates(self) -> Dict[str, str]:
        """Load base template structures"""
        return {
            "dashboard": self._dashboard_template(),
            "case_list": self._case_list_template(),
            "case_detail": self._case_detail_template(),
            "settings": self._settings_template(),
        }
    
    def _dashboard_template(self) -> str:
        """Dashboard template structure"""
        return """
        {
            "layout": "main",
            "sections": [
                {
                    "type": "header",
                    "content": {
                        "title": "Surgery Dashboard",
                        "actions": ["notifications", "settings"]
                    }
                },
                {
                    "type": "stats_grid",
                    "content": {
                        "columns": 4,
                        "widgets": [
                            {"type": "metric", "title": "Total Cases", "key": "total_cases"},
                            {"type": "metric", "title": "Today's Surgeries", "key": "today_surgeries"}, 
                            {"type": "metric", "title": "Success Rate", "key": "success_rate"},
                            {"type": "metric", "title": "Avg Duration", "key": "avg_duration"}
                        ]
                    }
                },
                {
                    "type": "recent_cases",
                    "content": {
                        "title": "Recent Cases",
                        "limit": 10,
                        "columns": ["patient", "procedure", "status", "date"]
                    }
                }
            ]
        }
        """
    
    def _case_list_template(self) -> str:
        """Case list template structure"""
        return """
        {
            "layout": "main",
            "sections": [
                {
                    "type": "header",
                    "content": {
                        "title": "Cases",
                        "actions": ["add_case", "filter", "search"]
                    }
                },
                {
                    "type": "filters",
                    "content": {
                        "filters": ["status", "surgeon", "procedure", "date_range"]
                    }
                },
                {
                    "type": "case_grid",
                    "content": {
                        "view": "grid",
                        "pagination": true,
                        "sorting": ["date", "status", "priority"]
                    }
                }
            ]
        }
        """
    
    def _case_detail_template(self) -> str:
        """Case detail template structure"""
        return """
        {
            "layout": "detail",
            "sections": [
                {
                    "type": "header",
                    "content": {
                        "title": "Case Details",
                        "actions": ["edit", "share", "print"]
                    }
                },
                {
                    "type": "patient_info",
                    "content": {
                        "fields": ["name", "age", "gender", "mrn", "allergies"]
                    }
                },
                {
                    "type": "procedure_info", 
                    "content": {
                        "fields": ["procedure", "surgeon", "date", "duration", "status"]
                    }
                },
                {
                    "type": "timeline",
                    "content": {
                        "events": ["scheduled", "prep", "surgery", "recovery", "discharge"]
                    }
                },
                {
                    "type": "notes",
                    "content": {
                        "types": ["pre_op", "intra_op", "post_op"]
                    }
                }
            ]
        }
        """
    
    def _settings_template(self) -> str:
        """Settings template structure"""
        return """
        {
            "layout": "settings",
            "sections": [
                {
                    "type": "header",
                    "content": {
                        "title": "Settings",
                        "actions": ["save", "reset"]
                    }
                },
                {
                    "type": "settings_groups",
                    "content": {
                        "groups": [
                            {
                                "title": "General",
                                "settings": ["language", "timezone", "notifications"]
                            },
                            {
                                "title": "Security",
                                "settings": ["password", "2fa", "session_timeout"]
                            },
                            {
                                "title": "Preferences",
                                "settings": ["theme", "dashboard_layout", "default_view"]
                            }
                        ]
                    }
                }
            ]
        }
        """
    
    def generate_web_template(self, template_name: str, data: Dict[str, Any] = None) -> str:
        """Generate HTML template for web platform"""
        if template_name == "dashboard":
            return self._generate_web_dashboard(data or {})
        elif template_name == "case_list":
            return self._generate_web_case_list(data or {})
        return ""
    
    def _generate_web_dashboard(self, data: Dict[str, Any]) -> str:
        """Generate web dashboard HTML"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Surgery Dashboard - Surge</title>
            <style>
                :root {{
                    --primary-color: #3b82f6;
                    --secondary-color: #64748b;
                    --success-color: #10b981;
                    --background-color: #f8fafc;
                    --surface-color: #ffffff;
                    --text-primary: #1e293b;
                    --border-radius: 8px;
                    --shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                
                body {{
                    font-family: system-ui, -apple-system, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: var(--background-color);
                    color: var(--text-primary);
                }}
                
                .header {{
                    background: var(--surface-color);
                    padding: 1rem 2rem;
                    border-bottom: 1px solid #e2e8f0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1rem;
                    padding: 2rem;
                }}
                
                .stat-card {{
                    background: var(--surface-color);
                    padding: 1.5rem;
                    border-radius: var(--border-radius);
                    box-shadow: var(--shadow);
                }}
                
                .stat-value {{
                    font-size: 2rem;
                    font-weight: bold;
                    color: var(--primary-color);
                }}
                
                .recent-cases {{
                    margin: 2rem;
                    background: var(--surface-color);
                    border-radius: var(--border-radius);
                    box-shadow: var(--shadow);
                }}
                
                .case-item {{
                    padding: 1rem;
                    border-bottom: 1px solid #e2e8f0;
                }}
            </style>
        </head>
        <body>
            <header class="header">
                <h1>🏥 Surgery Dashboard</h1>
                <div>
                    <button>🔔 Notifications</button>
                    <button>⚙️ Settings</button>
                </div>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Cases</h3>
                    <div class="stat-value">{data.get('total_cases', '156')}</div>
                </div>
                <div class="stat-card">
                    <h3>Today's Surgeries</h3>
                    <div class="stat-value">{data.get('today_surgeries', '8')}</div>
                </div>
                <div class="stat-card">
                    <h3>Success Rate</h3>
                    <div class="stat-value">{data.get('success_rate', '97.2%')}</div>
                </div>
                <div class="stat-card">
                    <h3>Avg Duration</h3>
                    <div class="stat-value">{data.get('avg_duration', '2.5h')}</div>
                </div>
            </div>
            
            <div class="recent-cases">
                <h2 style="padding: 1rem;">Recent Cases</h2>
                <div class="case-item">
                    <strong>John Doe</strong> - Gastric Surgery - <span style="color: var(--success-color);">Completed</span>
                </div>
                <div class="case-item">
                    <strong>Jane Smith</strong> - Cardiac Surgery - <span style="color: var(--primary-color);">In Progress</span>
                </div>
                <div class="case-item">
                    <strong>Bob Johnson</strong> - Orthopedic Surgery - <span style="color: var(--secondary-color);">Scheduled</span>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_web_case_list(self, data: Dict[str, Any]) -> str:
        """Generate web case list HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cases - Surge</title>
            <link rel="stylesheet" href="/surge/static/css/main.css">
        </head>
        <body>
            <header>
                <h1>Cases</h1>
                <div class="actions">
                    <button class="btn btn-primary">Add Case</button>
                    <button class="btn btn-secondary">Filter</button>
                </div>
            </header>
            
            <div class="case-grid">
                <!-- Cases will be loaded here -->
            </div>
        </body>
        </html>
        """


# Global template manager
template_manager = TemplateManager()
