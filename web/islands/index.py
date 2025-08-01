"""
Index Island Component for Surgify
Handles dynamic content updates and interactions on the main dashboard
"""

from typing import Dict, List, Any
import asyncio
from datetime import datetime, timedelta

class IndexIsland:
    """Interactive component for the main dashboard"""
    
    def __init__(self):
        self.events = []
        self.cases = []
        self.quick_stats = {}
    
    async def load_upcoming_events(self) -> List[Dict[str, Any]]:
        """Load upcoming events for carousel"""
        # Mock data - replace with actual database queries
        events = [
            {
                "id": 1,
                "title": "International Gastric Surgery Symposium",
                "description": "Advanced techniques and latest research in gastric oncology",
                "date": datetime.now() + timedelta(days=14),
                "type": "Virtual Event",
                "image_url": "/static/images/events/symposium.jpg"
            },
            {
                "id": 2,
                "title": "Robotic Surgery Workshop",
                "description": "Hands-on training with latest robotic surgical systems",
                "date": datetime.now() + timedelta(days=21),
                "type": "In-Person",
                "image_url": "/static/images/events/workshop.jpg"
            },
            {
                "id": 3,
                "title": "FLOT Protocol Masterclass",
                "description": "Deep dive into perioperative chemotherapy protocols",
                "date": datetime.now() + timedelta(days=35),
                "type": "Hybrid",
                "image_url": "/static/images/events/masterclass.jpg"
            }
        ]
        self.events = events
        return events
    
    async def load_recent_cases(self) -> List[Dict[str, Any]]:
        """Load recent cases for horizontal scroll"""
        # Mock data - replace with actual database queries
        cases = [
            {
                "id": "JD001",
                "patient_id": "J.D.",
                "condition": "Stage III Gastric Cancer",
                "adci_score": 8.5,
                "recommendation": "FLOT Protocol Recommended",
                "status": "Active",
                "last_updated": "2h ago",
                "priority": "high"
            },
            {
                "id": "AS002",
                "patient_id": "A.S.",
                "condition": "Post-FLOT Assessment",
                "adci_score": 9.2,
                "recommendation": "Surgery Recommended",
                "status": "Review",
                "last_updated": "Yesterday",
                "priority": "medium"
            },
            {
                "id": "MR003",
                "patient_id": "M.R.",
                "condition": "Pre-surgical Planning",
                "adci_score": 7.8,
                "recommendation": "Further Analysis Needed",
                "status": "Pending",
                "last_updated": "3d ago",
                "priority": "low"
            }
        ]
        self.cases = cases
        return cases
    
    async def get_quick_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        stats = {
            "total_cases": 127,
            "active_cases": 23,
            "completed_this_month": 45,
            "avg_adci_score": 8.3,
            "upcoming_events": len(self.events),
            "system_alerts": 2
        }
        self.quick_stats = stats
        return stats
    
    async def handle_case_update(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Handle real-time case updates"""
        try:
            # Update case in database
            # Broadcast update to connected clients
            return True
        except Exception as e:
            print(f"Error updating case {case_id}: {e}")
            return False
    
    async def refresh_dashboard(self) -> Dict[str, Any]:
        """Refresh all dashboard components"""
        try:
            events = await self.load_upcoming_events()
            cases = await self.load_recent_cases()
            stats = await self.get_quick_stats()
            
            return {
                "events": events,
                "cases": cases,
                "stats": stats,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
            return {}

# Global instance
index_island = IndexIsland()
