"""
Hero Island Component for Surgify
Handles dynamic hero section content and call-to-action tracking
"""

from typing import Dict, List, Any
import asyncio
from datetime import datetime

class HeroIsland:
    """Interactive component for the hero section"""
    
    def __init__(self):
        self.hero_content = {}
        self.cta_stats = {}
        self.announcements = []
    
    async def get_hero_content(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get personalized hero content based on user context"""
        base_content = {
            "title": "Welcome to Surgify",
            "subtitle": "Advanced Decision Support for Surgical Excellence",
            "primary_cta": {
                "text": "Start Analyzing Cases",
                "url": "/workstation",
                "icon": "chart-bar"
            },
            "secondary_cta": {
                "text": "Explore Marketplace",
                "url": "/marketplace",
                "icon": "shopping-bag"
            }
        }
        
        # Personalize based on user context
        if user_context:
            user_role = user_context.get("role", "surgeon")
            if user_role == "researcher":
                base_content.update({
                    "title": "Welcome back, Researcher",
                    "subtitle": "Discover insights from the latest surgical data",
                    "primary_cta": {
                        "text": "View Research Hub",
                        "url": "/research",
                        "icon": "academic-cap"
                    }
                })
            elif user_role == "admin":
                base_content.update({
                    "title": "Admin Dashboard",
                    "subtitle": "Manage your Surgify platform",
                    "primary_cta": {
                        "text": "View Admin Panel",
                        "url": "/admin",
                        "icon": "cog"
                    }
                })
        
        self.hero_content = base_content
        return base_content
    
    async def get_announcements(self) -> List[Dict[str, Any]]:
        """Get active announcements for hero banner"""
        announcements = [
            {
                "id": 1,
                "type": "update",
                "title": "New FLOT Protocol Guidelines Available",
                "message": "Updated treatment protocols based on latest research",
                "url": "/protocols/flot-2024",
                "expires": datetime(2025, 8, 30),
                "priority": "high"
            },
            {
                "id": 2,
                "type": "event",
                "title": "Join our Virtual Symposium",
                "message": "International Gastric Surgery Symposium - Aug 15",
                "url": "/events/symposium-2025",
                "expires": datetime(2025, 8, 15),
                "priority": "medium"
            }
        ]
        
        # Filter active announcements
        active_announcements = [
            ann for ann in announcements 
            if ann["expires"] > datetime.now()
        ]
        
        self.announcements = active_announcements
        return active_announcements
    
    async def track_cta_click(self, cta_type: str, user_id: str = None) -> bool:
        """Track call-to-action clicks for analytics"""
        try:
            click_data = {
                "cta_type": cta_type,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "page": "hero"
            }
            
            # Update click statistics
            if cta_type not in self.cta_stats:
                self.cta_stats[cta_type] = 0
            self.cta_stats[cta_type] += 1
            
            # Log to analytics system
            print(f"CTA Click tracked: {click_data}")
            return True
            
        except Exception as e:
            print(f"Error tracking CTA click: {e}")
            return False
    
    async def get_cta_stats(self) -> Dict[str, Any]:
        """Get call-to-action click statistics"""
        return {
            "total_clicks": sum(self.cta_stats.values()),
            "clicks_by_type": self.cta_stats,
            "conversion_data": {
                "primary_cta_rate": self.cta_stats.get("primary", 0) * 0.1,
                "secondary_cta_rate": self.cta_stats.get("secondary", 0) * 0.05
            }
        }
    
    async def update_hero_message(self, message_type: str, content: Dict[str, Any]) -> bool:
        """Update hero message dynamically"""
        try:
            if message_type == "announcement":
                self.announcements.append({
                    "id": len(self.announcements) + 1,
                    "type": content.get("type", "info"),
                    "title": content["title"],
                    "message": content["message"],
                    "url": content.get("url"),
                    "expires": datetime.now() + timedelta(days=content.get("duration_days", 7)),
                    "priority": content.get("priority", "medium")
                })
            
            return True
            
        except Exception as e:
            print(f"Error updating hero message: {e}")
            return False

# Global instance
hero_island = HeroIsland()
