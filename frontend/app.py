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
from .components.pwa import create_pwa_manifest, create_service_worker
from .static.js.pwa import dicom_viewer, webrtc_collab, ar_visualization, post_op_monitoring, ai_analytics, instrument_tracking

# Initialize FastHTML app
app = FastHTML(
    title="Gastric ADCI Platform",
    pico=False,  # We'll use our custom CSS
    hdrs=[
        Link(rel="stylesheet", href="/static/css/app.css"),
        Link(rel="stylesheet", href="/static/css/pwa.css"),
        Link(rel="manifest", href="/manifest.json"),
        Meta(name="theme-color", content="#2563eb"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Script(src="/static/js/app.js", defer=True),
        Script(src="/static/js/gun-integration.js", defer=True),
        Script(src="https://unpkg.com/htmx.org@1.9.10", defer=True),
        Script(src="https://kit.fontawesome.com/3e7c6b5f6c.js", crossorigin="anonymous", defer=True)
    ],
    static_path="frontend/static"
)

# Updated routes for new features
@app.get("/dicom-viewer")
def dicom_viewer_page():
    """DICOM MPR & 3D Visualization"""
    return dicom_viewer.render()

@app.get("/telemedicine")
def telemedicine_page():
    """Real-Time Telemedicine & Surgical Collaboration"""
    return webrtc_collab.render()

@app.get("/ar-visualization")
def ar_visualization_page():
    """WebXR AR/VR Integration"""
    return ar_visualization.render()

@app.get("/post-op-monitoring")
def post_op_monitoring_page():
    """Patient Monitoring Module"""
    return post_op_monitoring.render()

@app.get("/ai-analytics")
def ai_analytics_page():
    """AI Surgical Insight Engine"""
    return ai_analytics.render()

@app.get("/instrument-tracking")
def instrument_tracking_page():
    """Instrument Tracking & Intraoperative Logging"""
    return instrument_tracking.render()

# Updated PWA manifest and service worker routes
@app.get("/manifest.json")
def pwa_manifest():
    return create_pwa_manifest()

@app.get("/sw.js")
def service_worker():
    return create_service_worker()

# API Base URL configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
