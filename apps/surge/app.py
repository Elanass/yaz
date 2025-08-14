"""
Surge App - Lean Surgery Platform
Cross-platform surgery management: Web, Desktop, Mobile
P2P collaboration, local-first, multi-VM deployment
"""

from fastapi import FastAPI, Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path
import json
import asyncio
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from shared.base_app import create_base_app
from shared.logging import get_logger
from shared.database import get_db
from shared.config import get_shared_config

# P2P networking (optional - handle import errors gracefully)
try:
    from apps.surge.network.p2p import initialize_p2p, get_p2p_node, shutdown_p2p
    P2P_AVAILABLE = True
except ImportError as e:
    P2P_AVAILABLE = False
    
    # Mock functions for when P2P is not available
    async def initialize_p2p(port: int = 8001):
        return None
    
    def get_p2p_node():
        return None
    
    async def shutdown_p2p():
        pass

logger = get_logger("apps.surge")
config = get_shared_config()

# In-memory storage for P2P collaboration (replace with Redis/DB for production)
active_connections: Dict[str, WebSocket] = {}
surgery_cases: List[Dict] = [
    {
        "id": "1",
        "patient_id": "PAT001",
        "procedure": "Laparoscopic Gastrectomy",
        "surgeon": "Dr. Smith",
        "status": "scheduled",
        "date": "2025-08-15",
        "time": "10:00",
        "duration": "3h",
        "platform": "web"
    },
    {
        "id": "2", 
        "patient_id": "PAT002",
        "procedure": "Cardiac Bypass",
        "surgeon": "Dr. Johnson",
        "status": "in-progress",
        "date": "2025-08-14",
        "time": "08:30",
        "duration": "5h",
        "platform": "desktop"
    }
]
collaborators: Dict[str, Dict] = {}


def create_lean_surgery_router() -> APIRouter:
    """Lean surgery management with real-time collaboration"""
    router = APIRouter(tags=["surgery"])
    
    @router.get("/", response_class=HTMLResponse)
    async def surge_dashboard(request: Request):
        """Main surgery dashboard with coherent navigation"""
        platform = request.headers.get("User-Agent", "").lower()
        
        # Detect platform for adaptive UI
        is_mobile = any(x in platform for x in ["mobile", "android", "iphone", "ipad"])
        is_desktop = "electron" in platform or "desktop" in platform
        detected_platform = "mobile" if is_mobile else "desktop" if is_desktop else "web"
        
        return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Surge - Surgery Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#dc2626',
                        secondary: '#64748b',
                        yaz: '#2563eb'
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Coherent Navigation Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-3">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <!-- Platform Breadcrumb -->
                    <a href="/" class="flex items-center space-x-2 text-yaz hover:text-blue-700 transition-colors">
                        <i class="fas fa-heartbeat"></i>
                        <span class="font-semibold">YAZ</span>
                    </a>
                    <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
                    <div class="flex items-center space-x-2">
                        <div class="w-6 h-6 bg-red-500 rounded flex items-center justify-center">
                            <i class="fas fa-cut text-white text-xs"></i>
                        </div>
                        <h1 class="text-lg font-bold text-gray-900">Surge Dashboard</h1>
                    </div>
                    <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {detected_platform.title()}
                    </span>
                </div>
                
                <!-- Navigation Actions -->
                <div class="flex items-center space-x-3">
                    <a href="/apps/surge/interact" 
                       class="bg-primary hover:bg-red-700 text-white px-3 py-1.5 rounded text-sm font-medium transition-colors">
                        <i class="fas fa-users mr-1"></i>
                        Interact
                    </a>
                    <div class="flex items-center space-x-2 text-sm text-gray-600">
                        <i class="fas fa-users"></i>
                        <span id="collaborator-count">{len(collaborators)}</span>
                        <span class="text-xs">online</span>
                    </div>
                    <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse" title="Connected"></div>
                </div>
            </div>
        </div>
    </header>

    <!-- Dashboard Content -->
    <main class="max-w-7xl mx-auto px-4 py-6">
        <!-- Quick Actions -->
        <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-900">Quick Actions</h2>
                <span class="text-sm text-gray-500">Surgery Management Hub</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                <button class="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 text-left transition-colors"
                        onclick="window.location.href='/apps/surge/cases/new'">
                    <i class="fas fa-plus text-blue-600 mb-2"></i>
                    <div class="font-medium text-blue-900">New Case</div>
                    <div class="text-xs text-blue-700">Schedule surgery</div>
                </button>
                
                <button class="bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-3 text-left transition-colors"
                        onclick="window.location.href='/apps/surge/interact'">
                    <i class="fas fa-users text-green-600 mb-2"></i>
                    <div class="font-medium text-green-900">Collaborate</div>
                    <div class="text-xs text-green-700">Join team</div>
                </button>
                
                <button class="bg-yellow-50 hover:bg-yellow-100 border border-yellow-200 rounded-lg p-3 text-left transition-colors"
                        onclick="window.location.href='/apps/surge/analytics'">
                    <i class="fas fa-chart-bar text-yellow-600 mb-2"></i>
                    <div class="font-medium text-yellow-900">Analytics</div>
                    <div class="text-xs text-yellow-700">View insights</div>
                </button>
                
                <button class="bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg p-3 text-left transition-colors"
                        onclick="window.location.href='/apps/surge/mobile'">
                    <i class="fas fa-mobile text-purple-600 mb-2"></i>
                    <div class="font-medium text-purple-900">Mobile</div>
                    <div class="text-xs text-purple-700">Go mobile</div>
                </button>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-white p-4 rounded-lg shadow-sm">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                        <i class="fas fa-clipboard-list text-blue-600"></i>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Active Cases</p>
                        <p class="text-xl font-semibold" id="active-cases">{len([c for c in surgery_cases if c['status'] in ['scheduled', 'in-progress']])}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-4 rounded-lg shadow-sm">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                        <i class="fas fa-user-md text-green-600"></i>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Online Surgeons</p>
                        <p class="text-xl font-semibold" id="online-surgeons">{len(collaborators)}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-4 rounded-lg shadow-sm">
                <div class="flex items-center">
                    <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                        <i class="fas fa-network-wired text-purple-600"></i>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">P2P Nodes</p>
                        <p class="text-xl font-semibold" id="p2p-nodes">{'1' if P2P_AVAILABLE else '0'}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Surgery Cases Table -->
        <div class="bg-white rounded-lg shadow-sm">
            <div class="p-4 border-b border-gray-200">
                <div class="flex items-center justify-between">
                    <h2 class="text-lg font-semibold text-gray-900">Surgery Cases</h2>
                    <div class="flex items-center space-x-2">
                        <input type="text" placeholder="Search cases..." 
                               class="px-3 py-1 border border-gray-300 rounded text-sm">
                        <button class="bg-primary hover:bg-red-700 text-white px-3 py-1 rounded text-sm">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Procedure</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Surgeon</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        {''.join([f'''
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3 text-sm text-gray-900">{case["patient_id"]}</td>
                            <td class="px-4 py-3 text-sm text-gray-900">{case["procedure"]}</td>
                            <td class="px-4 py-3 text-sm text-gray-900">{case["surgeon"]}</td>
                            <td class="px-4 py-3">
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full 
                                           {"bg-green-100 text-green-800" if case["status"] == "completed" 
                                            else "bg-yellow-100 text-yellow-800" if case["status"] == "in-progress"
                                            else "bg-blue-100 text-blue-800"}">
                                    {case["status"].title()}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-900">{case["date"]} {case["time"]}</td>
                            <td class="px-4 py-3 text-sm">
                                <div class="flex items-center space-x-2">
                                    <button class="text-blue-600 hover:text-blue-800" title="View">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="text-green-600 hover:text-green-800" title="Edit">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="text-red-600 hover:text-red-800" title="Join">
                                        <i class="fas fa-users"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        ''' for case in surgery_cases])}
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- Real-time Updates -->
    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:8000/apps/surge/ws');
        
        ws.onopen = function(event) {{
            console.log('Connected to Surge real-time updates');
            ws.send(JSON.stringify({{
                type: 'join',
                user: 'surgeon_' + Math.random().toString(36).substr(2, 9),
                platform: '{detected_platform}'
            }}));
        }};
        
        ws.onmessage = function(event) {{
            const data = JSON.parse(event.data);
            if (data.type === 'collaborator_update') {{
                document.getElementById('collaborator-count').textContent = data.count;
            }}
        }};
        
        // Auto-refresh stats every 30 seconds
        setInterval(function() {{
            fetch('/apps/surge/api/stats')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('active-cases').textContent = data.active_cases;
                    document.getElementById('online-surgeons').textContent = data.online_surgeons;
                    document.getElementById('p2p-nodes').textContent = data.p2p_nodes;
                }});
        }}, 30000);
    </script>
</body>
</html>
        """)
    
    @router.get("/cases-list")
    async def get_cases_list():
        """Get cases list for dynamic updates"""
        return HTMLResponse(generate_cases_html())
    
    @router.get("/cases")
    async def get_cases():
        """Get all cases as JSON"""
        return JSONResponse({
            "cases": surgery_cases,
            "total": len(surgery_cases),
            "platform_distribution": get_platform_distribution()
        })
    
    @router.post("/new-case")
    async def create_new_case(request: Request):
        """Create a new surgery case"""
        new_case = {
            "id": str(uuid.uuid4()),
            "patient_id": f"PAT{str(len(surgery_cases) + 1).zfill(3)}",
            "procedure": "New Surgery Case",
            "surgeon": "Dr. Unknown",
            "status": "planned",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "duration": "2h",
            "platform": "web"
        }
        surgery_cases.insert(0, new_case)
        
        # Broadcast to all connected clients
        await broadcast_update({
            "type": "case_update",
            "total_cases": len(surgery_cases),
            "new_case": new_case
        })
        
        return HTMLResponse(generate_case_html(new_case))
    
    @router.get("/web")
    async def web_platform(request: Request):
        """Web platform specific view"""
        return HTMLResponse("""
        <div class="p-6">
            <h2 class="text-2xl font-bold mb-4">🌐 Web Platform</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Features</h3>
                    <ul class="space-y-1 text-sm">
                        <li>• Real-time collaboration</li>
                        <li>• Cross-browser compatibility</li>
                        <li>• Progressive Web App</li>
                        <li>• Offline capability</li>
                    </ul>
                </div>
                <div class="bg-green-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Technology</h3>
                    <ul class="space-y-1 text-sm">
                        <li>• HTMX for dynamic updates</li>
                        <li>• WebSocket for real-time</li>
                        <li>• Tailwind CSS</li>
                        <li>• Service Worker</li>
                    </ul>
                </div>
            </div>
        </div>
        """)
    
    @router.get("/desktop")
    async def desktop_platform(request: Request):
        """Desktop platform specific view"""
        return HTMLResponse("""
        <div class="p-6">
            <h2 class="text-2xl font-bold mb-4">💻 Desktop Platform</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Native Features</h3>
                    <ul class="space-y-1 text-sm">
                        <li>• File system access</li>
                        <li>• System notifications</li>
                        <li>• Keyboard shortcuts</li>
                        <li>• Offline-first</li>
                    </ul>
                </div>
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Platforms</h3>
                    <ul class="space-y-1 text-sm">
                        <li>• Windows 10/11</li>
                        <li>• macOS 10.14+</li>
                        <li>• Linux (Ubuntu, Fedora)</li>
                        <li>• Electron-based</li>
                    </ul>
                </div>
            </div>
        </div>
        """)
    
    @router.get("/mobile")
    async def mobile_platform(request: Request):
        """Mobile platform specific view"""
        return HTMLResponse("""
        <div class="p-6">
            <h2 class="text-2xl font-bold mb-4">📱 Mobile Platform</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-green-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">iOS Features</h3>
                    <ul class="space-y-1 text-sm">
                        <li>• Face ID / Touch ID</li>
                        <li>• Native camera access</li>
                        <li>• Push notifications</li>
                        <li>• Secure enclave storage</li>
                    </ul>
                </div>
                <div class="bg-purple-50 p-4 rounded-lg">
                    <h3 class="font-semibold mb-2">Android Features</h3>
                    <ul class="space-y-1 text-sm">
                        <li>• Biometric authentication</li>
                        <li>• Advanced camera APIs</li>
                        <li>• Background sync</li>
                        <li>• Hardware keystore</li>
                    </ul>
                </div>
            </div>
        </div>
        """)
    
    @router.get("/analytics")
    async def analytics_view(request: Request):
        """Analytics dashboard"""
        return HTMLResponse(f"""
        <div class="p-6">
            <h2 class="text-2xl font-bold mb-4">📊 Surgery Analytics</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-blue-50 p-4 rounded-lg text-center">
                    <div class="text-2xl font-bold text-blue-600">{len(surgery_cases)}</div>
                    <div class="text-sm text-gray-600">Total Cases</div>
                </div>
                <div class="bg-green-50 p-4 rounded-lg text-center">
                    <div class="text-2xl font-bold text-green-600">{len([c for c in surgery_cases if c['status'] == 'completed'])}</div>
                    <div class="text-sm text-gray-600">Completed</div>
                </div>
                <div class="bg-yellow-50 p-4 rounded-lg text-center">
                    <div class="text-2xl font-bold text-yellow-600">{len([c for c in surgery_cases if c['status'] == 'in-progress'])}</div>
                    <div class="text-sm text-gray-600">In Progress</div>
                </div>
            </div>
            <div class="bg-white rounded-lg p-4">
                <h3 class="font-semibold mb-3">Platform Distribution</h3>
                <div class="space-y-2">
                    {generate_platform_chart()}
                </div>
            </div>
        </div>
        """)
    
    
    @router.websocket("/ws/surge")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time collaboration"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        active_connections[connection_id] = websocket
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "join":
                    collaborators[connection_id] = {
                        "platform": message.get("platform", "unknown"),
                        "user_id": message.get("user_id", "anonymous"),
                        "joined_at": datetime.now().isoformat()
                    }
                    
                    # Broadcast collaborator update
                    await broadcast_update({
                        "type": "collaborator_update",
                        "active_collaborators": len(collaborators)
                    })
                    
                elif message["type"] == "join_collaboration":
                    collaborators[connection_id].update({
                        "name": message.get("name", "Anonymous"),
                        "platform": message.get("platform", "unknown")
                    })
                    
                    # Broadcast collaborator update
                    await broadcast_update({
                        "type": "collaborator_update", 
                        "active_collaborators": len(collaborators),
                        "new_collaborator": collaborators[connection_id]
                    })
                    
        except WebSocketDisconnect:
            if connection_id in active_connections:
                del active_connections[connection_id]
            if connection_id in collaborators:
                del collaborators[connection_id]
                
            # Broadcast collaborator update
            await broadcast_update({
                "type": "collaborator_update",
                "active_collaborators": len(collaborators)
            })
    
    @router.get("/interact", response_class=HTMLResponse)
    async def interact_interface(request: Request):
        """Real-time collaboration interface"""
        return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Surge - Collaborate</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#dc2626',
                        secondary: '#64748b',
                        yaz: '#2563eb'
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Coherent Navigation Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-3">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <!-- Platform Breadcrumb -->
                    <a href="/" class="flex items-center space-x-2 text-yaz hover:text-blue-700 transition-colors">
                        <i class="fas fa-heartbeat"></i>
                        <span class="font-semibold">YAZ</span>
                    </a>
                    <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
                    <a href="/apps/surge" class="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors">
                        <div class="w-5 h-5 bg-red-500 rounded flex items-center justify-center">
                            <i class="fas fa-cut text-white text-xs"></i>
                        </div>
                        <span class="font-medium">Surge</span>
                    </a>
                    <i class="fas fa-chevron-right text-gray-400 text-xs"></i>
                    <h1 class="text-lg font-bold text-gray-900">Collaborate</h1>
                </div>
                
                <!-- Navigation Actions -->
                <div class="flex items-center space-x-3">
                    <a href="/apps/surge" 
                       class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded text-sm font-medium transition-colors">
                        <i class="fas fa-arrow-left mr-1"></i>
                        Dashboard
                    </a>
                    <div class="flex items-center space-x-2 text-sm text-green-600">
                        <i class="fas fa-circle text-xs animate-pulse"></i>
                        <span class="font-medium">Live</span>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Collaboration Interface -->
    <main class="max-w-7xl mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main Collaboration Area -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Active Surgery Case -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="p-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <h2 class="text-lg font-semibold text-gray-900">Active Surgery Case</h2>
                            <div class="flex items-center space-x-2">
                                <span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                                    <i class="fas fa-circle text-xs mr-1"></i>
                                    Live
                                </span>
                                <span class="text-sm text-gray-500">Case #PAT002</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="p-6">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 class="font-medium text-gray-900 mb-3">Patient Information</h3>
                                <div class="space-y-2 text-sm">
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Patient ID:</span>
                                        <span class="font-medium">PAT002</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Procedure:</span>
                                        <span class="font-medium">Cardiac Bypass</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Lead Surgeon:</span>
                                        <span class="font-medium">Dr. Johnson</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="text-gray-600">Duration:</span>
                                        <span class="font-medium text-green-600">2h 15m elapsed</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div>
                                <h3 class="font-medium text-gray-900 mb-3">Current Status</h3>
                                <div class="space-y-3">
                                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                        <div class="flex items-center space-x-2">
                                            <i class="fas fa-heartbeat text-blue-600"></i>
                                            <span class="text-sm font-medium text-blue-900">Vitals Stable</span>
                                        </div>
                                        <p class="text-xs text-blue-700 mt-1">All parameters normal</p>
                                    </div>
                                    
                                    <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                                        <div class="flex items-center space-x-2">
                                            <i class="fas fa-check-circle text-green-600"></i>
                                            <span class="text-sm font-medium text-green-900">Phase 2/3 Complete</span>
                                        </div>
                                        <p class="text-xs text-green-700 mt-1">Bypass graft successful</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Real-time Chat -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="p-4 border-b border-gray-200">
                        <h3 class="font-semibold text-gray-900">Team Communication</h3>
                    </div>
                    
                    <div class="h-64 overflow-y-auto p-4 space-y-3" id="chat-messages">
                        <div class="flex items-start space-x-3">
                            <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                <span class="text-white text-xs font-medium">DJ</span>
                            </div>
                            <div class="flex-1">
                                <div class="bg-gray-100 rounded-lg p-3">
                                    <p class="text-sm">Bypass graft completed successfully. Moving to closure.</p>
                                </div>
                                <span class="text-xs text-gray-500">Dr. Johnson • 2 min ago</span>
                            </div>
                        </div>
                        
                        <div class="flex items-start space-x-3">
                            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                <span class="text-white text-xs font-medium">AN</span>
                            </div>
                            <div class="flex-1">
                                <div class="bg-gray-100 rounded-lg p-3">
                                    <p class="text-sm">Anesthesia levels optimal. Patient stable.</p>
                                </div>
                                <span class="text-xs text-gray-500">Anesthesiologist • 1 min ago</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="p-4 border-t border-gray-200">
                        <div class="flex space-x-2">
                            <input type="text" id="chat-input" placeholder="Type a message..." 
                                   class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm">
                            <button onclick="sendMessage()" 
                                    class="bg-primary hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Online Team -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="p-4 border-b border-gray-200">
                        <h3 class="font-semibold text-gray-900">Online Team</h3>
                    </div>
                    
                    <div class="p-4 space-y-3" id="online-team">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                <span class="text-white text-xs font-medium">DJ</span>
                            </div>
                            <div class="flex-1">
                                <p class="text-sm font-medium text-gray-900">Dr. Johnson</p>
                                <p class="text-xs text-gray-500">Lead Surgeon</p>
                            </div>
                            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                        </div>
                        
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                <span class="text-white text-xs font-medium">AN</span>
                            </div>
                            <div class="flex-1">
                                <p class="text-sm font-medium text-gray-900">Anesthesiologist</p>
                                <p class="text-xs text-gray-500">Anesthesia Team</p>
                            </div>
                            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                        </div>
                        
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                <span class="text-white text-xs font-medium">RN</span>
                            </div>
                            <div class="flex-1">
                                <p class="text-sm font-medium text-gray-900">Scrub Nurse</p>
                                <p class="text-xs text-gray-500">OR Team</p>
                            </div>
                            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="p-4 border-b border-gray-200">
                        <h3 class="font-semibold text-gray-900">Quick Actions</h3>
                    </div>
                    
                    <div class="p-4 space-y-2">
                        <button class="w-full bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg p-3 text-left transition-colors">
                            <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
                            <span class="text-sm font-medium text-red-900">Emergency Alert</span>
                        </button>
                        
                        <button class="w-full bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 text-left transition-colors">
                            <i class="fas fa-file-medical text-blue-600 mr-2"></i>
                            <span class="text-sm font-medium text-blue-900">Update Notes</span>
                        </button>
                        
                        <button class="w-full bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-3 text-left transition-colors">
                            <i class="fas fa-phone text-green-600 mr-2"></i>
                            <span class="text-sm font-medium text-green-900">Call Consultant</span>
                        </button>
                        
                        <button class="w-full bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg p-3 text-left transition-colors">
                            <i class="fas fa-share text-purple-600 mr-2"></i>
                            <span class="text-sm font-medium text-purple-900">Share Screen</span>
                        </button>
                    </div>
                </div>

                <!-- P2P Status -->
                <div class="bg-white rounded-lg shadow-sm">
                    <div class="p-4 border-b border-gray-200">
                        <h3 class="font-semibold text-gray-900">Network Status</h3>
                    </div>
                    
                    <div class="p-4 space-y-3">
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600">P2P Network</span>
                            <span class="text-xs font-medium {'text-green-600' if P2P_AVAILABLE else 'text-red-600'}">
                                {'Connected' if P2P_AVAILABLE else 'Offline'}
                            </span>
                        </div>
                        
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600">Connected Peers</span>
                            <span class="text-xs font-medium text-gray-900">
                                {len(collaborators)}
                            </span>
                        </div>
                        
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600">Data Sync</span>
                            <span class="text-xs font-medium text-green-600">Real-time</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Real-time WebSocket Connection -->
    <script>
        const ws = new WebSocket('ws://localhost:8000/apps/surge/ws');
        
        ws.onopen = function(event) {{
            console.log('Connected to Surgery Collaboration');
            ws.send(JSON.stringify({{
                type: 'join_surgery',
                user: 'colleague_' + Math.random().toString(36).substr(2, 9),
                case_id: 'PAT002'
            }}));
        }};
        
        ws.onmessage = function(event) {{
            const data = JSON.parse(event.data);
            console.log('Received:', data);
            
            if (data.type === 'chat_message') {{
                addChatMessage(data.user, data.message, data.timestamp);
            }} else if (data.type === 'team_update') {{
                updateOnlineTeam(data.team);
            }}
        }};
        
        function sendMessage() {{
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (message) {{
                ws.send(JSON.stringify({{
                    type: 'chat_message',
                    message: message,
                    case_id: 'PAT002'
                }}));
                input.value = '';
            }}
        }}
        
        function addChatMessage(user, message, timestamp) {{
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'flex items-start space-x-3';
            messageDiv.innerHTML = `
                <div class="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center">
                    <span class="text-white text-xs font-medium">${{user.substring(0, 2).toUpperCase()}}</span>
                </div>
                <div class="flex-1">
                    <div class="bg-blue-50 rounded-lg p-3">
                        <p class="text-sm">${{message}}</p>
                    </div>
                    <span class="text-xs text-gray-500">${{user}} • just now</span>
                </div>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
        
        // Handle Enter key in chat input
        document.getElementById('chat-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sendMessage();
            }}
        }});
    </script>
</body>
</html>
        """)
    
    @router.get("/api/stats")
    async def get_stats():
        """API endpoint for real-time stats"""
        return {
            "active_cases": len([c for c in surgery_cases if c['status'] in ['scheduled', 'in-progress']]),
            "online_surgeons": len(collaborators),
            "p2p_nodes": 1 if P2P_AVAILABLE else 0,
            "total_cases": len(surgery_cases),
            "completed_cases": len([c for c in surgery_cases if c['status'] == 'completed']),
            "timestamp": datetime.now().isoformat()
        }
    
    @router.post("/api/chat")
    async def send_chat_message(message: dict):
        """Send chat message to all connected peers"""
        chat_data = {
            "type": "chat_message",
            "user": message.get("user", "anonymous"),
            "message": message.get("message", ""),
            "case_id": message.get("case_id", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to all connected WebSocket clients
        for connection in active_connections.values():
            try:
                await connection.send_text(json.dumps(chat_data))
            except:
                pass
        
        return {"status": "sent", "message": chat_data}
    
    @router.get("/api/team")
    async def get_online_team():
        """Get currently online team members"""
        return {
            "team": list(collaborators.values()),
            "count": len(collaborators),
            "timestamp": datetime.now().isoformat()
        }
    
    return router


async def broadcast_update(message: dict):
    """Broadcast message to all connected clients"""
    if active_connections:
        disconnected = []
        for connection_id, websocket in active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            if connection_id in active_connections:
                del active_connections[connection_id]
            if connection_id in collaborators:
                del collaborators[connection_id]


def generate_cases_html() -> str:
    """Generate HTML for cases list"""
    if not surgery_cases:
        return """
        <div class="p-4 text-center text-gray-500">
            <i class="fas fa-clipboard-list text-3xl mb-2"></i>
            <p>No cases yet. Create your first surgery case.</p>
        </div>
        """
    
    html = ""
    for case in surgery_cases:
        html += generate_case_html(case)
    return html


def generate_case_html(case: dict) -> str:
    """Generate HTML for a single case"""
    status_colors = {
        "scheduled": "bg-blue-100 text-blue-800",
        "in-progress": "bg-yellow-100 text-yellow-800", 
        "completed": "bg-green-100 text-green-800",
        "planned": "bg-gray-100 text-gray-800"
    }
    
    status_color = status_colors.get(case["status"], "bg-gray-100 text-gray-800")
    
    return f"""
    <div class="p-4 border-b hover:bg-gray-50 transition-colors">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <i class="fas fa-user-injured text-red-600"></i>
                </div>
                <div>
                    <div class="font-semibold">{case["patient_id"]} - {case["procedure"]}</div>
                    <div class="text-sm text-gray-500">
                        {case["surgeon"]} • {case["date"]} at {case["time"]} • {case["duration"]}
                    </div>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <span class="px-2 py-1 text-xs font-medium rounded-full {status_color}">
                    {case["status"].replace('-', ' ').title()}
                </span>
                <button class="text-gray-400 hover:text-gray-600" title="Edit case">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
        </div>
    </div>
    """


def generate_platform_chart() -> str:
    """Generate platform distribution chart"""
    platform_counts = {}
    for case in surgery_cases:
        platform = case.get("platform", "unknown")
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    html = ""
    total = len(surgery_cases) if surgery_cases else 1
    
    for platform, count in platform_counts.items():
        percentage = (count / total) * 100
        html += f"""
        <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium">{platform.title()}</span>
            <span class="text-sm text-gray-500">{count} ({percentage:.1f}%)</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 mb-3">
            <div class="bg-blue-600 h-2 rounded-full" style="width: {percentage}%"></div>
        </div>
        """
    
    return html


def get_platform_distribution() -> dict:
    """Get platform distribution data"""
    platform_counts = {}
    for case in surgery_cases:
        platform = case.get("platform", "unknown")
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    return platform_counts


def build_app() -> FastAPI:
    """Build the lean Surge application"""
    
    # Create base app
    app = create_base_app(
        app_name="surge",
        routers=[create_lean_surgery_router()]
    )
    
    # Add CORS for cross-platform communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files for UI assets
    static_path = Path("apps/surge/static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # P2P network endpoints
    @app.get("/p2p/status")
    async def p2p_status():
        """Get P2P network status"""
        if not P2P_AVAILABLE:
            return {"status": "not_available", "reason": "P2P module not loaded"}
        
        node = get_p2p_node()
        if node:
            return node.get_network_status()
        return {"status": "not_initialized"}
    
    @app.post("/p2p/start")
    async def start_p2p(port: int = 8001):
        """Start P2P networking"""
        if not P2P_AVAILABLE:
            return {"status": "error", "message": "P2P not available"}
        
        try:
            node = await initialize_p2p(port)
            return {"status": "started", "node_id": node.node_id if node else None, "port": port}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @app.post("/p2p/stop")
    async def stop_p2p():
        """Stop P2P networking"""
        if not P2P_AVAILABLE:
            return {"status": "error", "message": "P2P not available"}
        
        try:
            await shutdown_p2p()
            return {"status": "stopped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # Startup event to initialize P2P
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        if P2P_AVAILABLE:
            try:
                # Start P2P networking
                await initialize_p2p(port=8001)
                logger.info("P2P networking initialized")
            except Exception as e:
                logger.error(f"Failed to initialize P2P: {e}")
        else:
            logger.info("P2P networking disabled (module not available)")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        if P2P_AVAILABLE:
            try:
                await shutdown_p2p()
                logger.info("P2P networking shutdown")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
    
    # Health check specific to surge
    @app.get("/health")
    async def surge_health():
        """Surge-specific health check"""
        p2p_status = "disabled"
        p2p_peers = 0
        
        if P2P_AVAILABLE:
            node = get_p2p_node()
            if node:
                p2p_status = "active"
                p2p_peers = len(node.peers)
            else:
                p2p_status = "available_not_started"
        
        return {
            "app": "surge",
            "status": "healthy",
            "version": "1.0.0",
            "cases": len(surgery_cases),
            "collaborators": len(collaborators),
            "platforms": list(get_platform_distribution().keys()),
            "p2p": {
                "available": P2P_AVAILABLE,
                "status": p2p_status,
                "peers": p2p_peers
            },
            "features": [
                "cross_platform_ui",
                "real_time_collaboration",
                "p2p_networking" if P2P_AVAILABLE else "p2p_disabled",
                "local_first",
                "multi_vm_deployment"
            ]
        }
    
    logger.info("Lean Surge Surgery Platform created successfully")
    return app


# For direct import compatibility
app = build_app()
