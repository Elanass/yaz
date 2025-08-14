"""Dashboard API endpoints for unified YAZ platform
"""

from datetime import datetime

from fastapi import APIRouter


router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    # Mock data - replace with real database queries
    return {
        "active_patients": 1234,
        "procedures_today": 45,
        "success_rate": 95.2,
        "avg_duration": 2.5,
        "total_apps": 5,
        "active_apps": 5,
    }


@router.get("/activity")
async def get_recent_activity():
    """Get recent platform activity"""
    # Mock data - replace with real activity tracking
    return [
        {
            "id": 1,
            "icon": "fas fa-user-plus",
            "description": "New patient registered: Sarah Johnson",
            "timestamp": "2 minutes ago",
            "app": "clinica",
        },
        {
            "id": 2,
            "icon": "fas fa-calendar-check",
            "description": "Gastric surgery scheduled for tomorrow",
            "timestamp": "15 minutes ago",
            "app": "surge",
        },
        {
            "id": 3,
            "icon": "fas fa-graduation-cap",
            "description": "Training module completed by Dr. Smith",
            "timestamp": "32 minutes ago",
            "app": "educa",
        },
        {
            "id": 4,
            "icon": "fas fa-shield-alt",
            "description": "Insurance claim processed: $15,000",
            "timestamp": "1 hour ago",
            "app": "insura",
        },
        {
            "id": 5,
            "icon": "fas fa-truck",
            "description": "Medical supplies delivered to Ward B",
            "timestamp": "1.5 hours ago",
            "app": "move",
        },
    ]


@router.get("/apps/status")
async def get_apps_status():
    """Get status of all healthcare apps"""
    return {
        "surge": {
            "name": "Surge",
            "description": "Surgery Analytics Platform",
            "status": "active",
            "health": "healthy",
            "users": 156,
            "uptime": "99.9%",
        },
        "clinica": {
            "name": "Clinica",
            "description": "Clinical Management System",
            "status": "active",
            "health": "healthy",
            "users": 234,
            "uptime": "99.8%",
        },
        "educa": {
            "name": "Educa",
            "description": "Medical Education Platform",
            "status": "active",
            "health": "healthy",
            "users": 89,
            "uptime": "99.9%",
        },
        "insura": {
            "name": "Insura",
            "description": "Insurance Management System",
            "status": "active",
            "health": "healthy",
            "users": 67,
            "uptime": "99.7%",
        },
        "move": {
            "name": "Move",
            "description": "Logistics Management Platform",
            "status": "active",
            "health": "healthy",
            "users": 45,
            "uptime": "99.9%",
        },
    }


@router.get("/metrics/weekly")
async def get_weekly_metrics():
    """Get weekly performance metrics"""
    return {
        "procedures": [120, 135, 145, 160, 155, 170, 165],
        "patients": [450, 467, 489, 501, 523, 545, 567],
        "success_rate": [94.2, 95.1, 94.8, 95.5, 95.2, 96.1, 95.8],
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    }


@router.get("/alerts")
async def get_system_alerts():
    """Get system alerts and notifications"""
    return [
        {
            "id": 1,
            "type": "warning",
            "title": "High Volume Alert",
            "message": "Surgery bookings are 20% above normal for tomorrow",
            "timestamp": datetime.now().isoformat(),
            "priority": "medium",
        },
        {
            "id": 2,
            "type": "info",
            "title": "System Update",
            "message": "Scheduled maintenance window: Sunday 2AM-4AM",
            "timestamp": datetime.now().isoformat(),
            "priority": "low",
        },
    ]
