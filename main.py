#!/usr/bin/env python3
"""
YAZ Platform - Single ASGI Entrypoint
Modern healthcare platform with integrated applications
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import configuration and app registry
from infra.settings.config import settings
from apps.registry import get_all_apps, get_available_apps, get_app_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("yaz-platform")

# Initialize templates
templates = Jinja2Templates(directory="templates")


def create_app() -> FastAPI:
    """Create and configure the main YAZ platform application"""
    
    # Create main app
    app = FastAPI(
        title="YAZ Healthcare Platform",
        description="Unified healthcare platform with integrated applications",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    if Path("static").exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Build and mount all sub-apps
    sub_apps = get_all_apps()
    for app_name, sub_app in sub_apps.items():
        mount_path = f"{settings.apps_prefix}/{app_name}"
        app.mount(mount_path, sub_app, name=app_name)
        logger.info(f"Mounted app '{app_name}' at {mount_path}")
    
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Homepage with beautiful app listing using HTMX and Tailwind"""
        
        apps_info = []
        for app_name in get_available_apps():
            info = get_app_info(app_name)
            info["url"] = f"{settings.apps_prefix}/{app_name}"
            info["app_name"] = app_name
            apps_info.append(info)
        
        # Create beautiful HTML response with HTMX and Tailwind
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YAZ Healthcare Platform</title>
    
    <!-- Progressive Web App Meta Tags -->
    <meta name="theme-color" content="#2563eb">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="YAZ Healthcare">
    
    <!-- Core Styles -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#2563eb',
                        secondary: '#64748b'
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-lg border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <h1 class="text-2xl font-bold text-primary">
                            <i class="fas fa-heartbeat mr-2"></i>YAZ
                        </h1>
                    </div>
                    <nav class="hidden md:ml-8 md:flex md:space-x-8">
                        <a href="/docs" class="text-gray-500 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                            API Docs
                        </a>
                        <a href="/health" class="text-gray-500 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                            System Health
                        </a>
                    </nav>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="text-sm text-gray-500">v2.0.0</span>
                    <div class="h-2 w-2 bg-green-400 rounded-full animate-pulse" title="System Online"></div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Hero Section -->
        <div class="text-center mb-12">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
                Healthcare Platform Applications
            </h2>
            <p class="text-xl text-gray-600 max-w-3xl mx-auto">
                Access integrated healthcare applications designed for modern medical practice.
                Choose an application below to get started.
            </p>
        </div>

        <!-- Quick Access -->
        <div class="mb-8 flex justify-center">
            <a href="/entry" 
               class="bg-primary hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg shadow-lg transition-all duration-200 transform hover:scale-105">
                <i class="fas fa-rocket mr-2"></i>
                Launch Default App
            </a>
        </div>

        <!-- Domain Selector -->
        <div class="mb-12">
            <div class="max-w-4xl mx-auto">
                <h3 class="text-2xl font-bold text-gray-900 mb-6 text-center">Choose Your Playground</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {generate_domain_cards(apps_info)}
                </div>
            </div>
        </div>

        <!-- Applications Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {generate_app_cards(apps_info)}
        </div>

        <!-- System Information -->
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
                <i class="fas fa-info-circle mr-2 text-blue-500"></i>
                System Information
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-500">Environment</div>
                    <div class="text-lg font-semibold">{settings.environment.title()}</div>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-500">Applications</div>
                    <div class="text-lg font-semibold">{len(apps_info)} Active</div>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-500">Default App</div>
                    <div class="text-lg font-semibold">{settings.default_app.title()}</div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div class="text-center text-gray-500 text-sm">
                <p>&copy; 2025 YAZ Healthcare Platform. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        // Add some interactivity with HTMX
        document.addEventListener('htmx:afterRequest', function(event) {{
            if (event.detail.successful) {{
                console.log('Request successful');
            }}
        }});
        
        // Add hover effects
        document.querySelectorAll('.app-card').forEach(card => {{
            card.addEventListener('mouseenter', function() {{
                this.classList.add('transform', 'scale-105');
            }});
            card.addEventListener('mouseleave', function() {{
                this.classList.remove('transform', 'scale-105');
            }});
        }});
    </script>
</body>
</html>"""
        
        return HTMLResponse(content=html_content)
    
    @app.get("/entry")
    async def entry_redirect():
        """Redirect to the default app"""
        default_url = f"{settings.apps_prefix}/{settings.default_app}"
        return RedirectResponse(url=default_url, status_code=302)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "ok": True,
            "apps": get_available_apps(),
            "environment": settings.environment,
            "version": "2.0.0",
            "timestamp": "2025-08-11T00:00:00Z"
        }
    
    return app


def generate_domain_cards(apps_info: List[Dict]) -> str:
    """Generate HTML for domain selector cards"""
    cards = []
    
    # Focus on key domains with specific actions
    domains = {
        "surge": {
            "name": "Surgery Platform",
            "icon": "fas fa-cut",
            "color": "red",
            "description": "Advanced surgical analytics and case management",
            "actions": [
                {"name": "Analytics", "url": "/apps/surge/analytics", "icon": "fas fa-chart-line"},
                {"name": "Start Surgery", "url": "/apps/surge/interact", "icon": "fas fa-play"}
            ]
        },
        "clinica": {
            "name": "Clinical Care",
            "icon": "fas fa-stethoscope", 
            "color": "purple",
            "description": "Integrated clinical workflows and patient management",
            "actions": [
                {"name": "Dashboard", "url": "/apps/clinica/dashboard", "icon": "fas fa-tachometer-alt"},
                {"name": "Patients", "url": "/apps/clinica/patients", "icon": "fas fa-user-md"}
            ]
        },
        "move": {
            "name": "Medical Logistics",
            "icon": "fas fa-truck",
            "color": "green", 
            "description": "Supply chain and medical equipment management",
            "actions": [
                {"name": "Inventory", "url": "/apps/move/inventory", "icon": "fas fa-boxes"},
                {"name": "Tracking", "url": "/apps/move/tracking", "icon": "fas fa-route"}
            ]
        }
    }
    
    for domain_key, domain in domains.items():
        # Check if this domain exists in available apps
        domain_app = next((app for app in apps_info if app["app_name"] == domain_key), None)
        if not domain_app:
            continue
            
        actions_html = ""
        for action in domain["actions"]:
            actions_html += f"""
            <a href="{action['url']}" 
               class="inline-flex items-center px-4 py-2 bg-{domain['color']}-600 hover:bg-{domain['color']}-700 text-white text-sm font-medium rounded-lg transition-colors duration-200">
                <i class="{action['icon']} mr-2"></i>
                {action['name']}
            </a>"""
        
        card_html = f"""
        <div class="bg-white rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl hover:scale-105">
            <div class="bg-gradient-to-r from-{domain['color']}-500 to-{domain['color']}-600 p-6">
                <div class="flex items-center text-white">
                    <div class="bg-white bg-opacity-20 p-3 rounded-lg mr-4">
                        <i class="{domain['icon']} text-2xl"></i>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold">{domain['name']}</h3>
                        <p class="text-{domain['color']}-100 text-sm">{domain['description']}</p>
                    </div>
                </div>
            </div>
            <div class="p-6">
                <div class="flex flex-col space-y-3">
                    {actions_html}
                </div>
            </div>
        </div>"""
        cards.append(card_html)
    
    return "\n".join(cards)


def generate_app_cards(apps_info: List[Dict]) -> str:
    """Generate HTML for app cards"""
    cards = []
    
    app_icons = {
        "core": "fas fa-cog",
        "surge": "fas fa-cut", 
        "move": "fas fa-truck",
        "clinica": "fas fa-stethoscope",
        "educa": "fas fa-graduation-cap",
        "insura": "fas fa-shield-alt"
    }
    
    app_colors = {
        "core": "blue",
        "surge": "red",
        "move": "green", 
        "clinica": "purple",
        "educa": "yellow",
        "insura": "indigo"
    }
    
    for app in apps_info:
        app_name = app["app_name"]
        icon = app_icons.get(app_name, "fas fa-cube")
        color = app_colors.get(app_name, "gray")
        
        card_html = f"""
        <div class="app-card bg-white rounded-lg shadow-lg overflow-hidden transition-all duration-200 hover:shadow-xl cursor-pointer"
             onclick="window.location.href='{app["url"]}'"
             hx-boost="true">
            <div class="p-6">
                <div class="flex items-center mb-4">
                    <div class="bg-{color}-100 p-3 rounded-lg mr-4">
                        <i class="{icon} text-{color}-600 text-xl"></i>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900">{app["name"]}</h3>
                        <span class="text-sm text-{color}-600 font-medium">{app["type"].title()}</span>
                    </div>
                </div>
                <p class="text-gray-600 text-sm mb-4">{app["description"]}</p>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500">v{app["version"]}</span>
                    <span class="text-{color}-600 font-medium text-sm">
                        Launch <i class="fas fa-arrow-right ml-1"></i>
                    </span>
                </div>
            </div>
        </div>"""
        cards.append(card_html)
    
    return "\n".join(cards)


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
