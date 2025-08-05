"""
Island Manager
Manages the lifecycle and integration of UI Island components
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class IslandManager:
    """
    Manages UI Island components like InteractionIsland, DiscussionIsland, etc.
    Provides a centralized way to register, load, and interact with islands.
    """

    def __init__(self):
        self.registered_islands: Dict[str, Dict] = {}
        self.active_islands: Dict[str, Any] = {}
        self._initialize_default_islands()

    def _initialize_default_islands(self):
        """Initialize default island configurations"""
        self.register_island(
            "interaction",
            {
                "name": "InteractionIsland",
                "title": "Feedback Hub",
                "component_path": "/static/js/InteractionIsland.js",
                "api_endpoint": "/api/feedback",
                "features": {
                    "submission": True,
                    "viewing": True,
                    "filtering": True,
                    "moderation": False,
                },
                "config": {
                    "max_entries": 50,
                    "allow_anonymous": True,
                    "require_moderation": False,
                    "feedback_types": [
                        "general",
                        "feature-request",
                        "bug-report",
                        "service-value",
                        "improvement",
                    ],
                },
            },
        )

        self.register_island(
            "discussion",
            {
                "name": "DiscussionIsland",
                "title": "Clinical Discussion",
                "component_path": "/static/js/DiscussionIsland.js",
                "api_endpoint": "/api/discussions",
                "features": {
                    "threaded_comments": True,
                    "case_references": True,
                    "expert_highlights": True,
                },
            },
        )

        self.register_island(
            "comparison",
            {
                "name": "ComparisonIsland",
                "title": "Treatment Comparison",
                "component_path": "/static/js/ComparisonIsland.js",
                "api_endpoint": "/api/comparisons",
                "features": {
                    "side_by_side": True,
                    "metrics_overlay": True,
                    "export_results": True,
                },
            },
        )

    def register_island(self, island_id: str, config: Dict):
        """Register a new island configuration"""
        self.registered_islands[island_id] = {
            **config,
            "registered_at": datetime.utcnow().isoformat(),
            "status": "registered",
        }
        logger.info(f"Registered island: {island_id}")

    def get_island_config(self, island_id: str) -> Optional[Dict]:
        """Get configuration for a specific island"""
        return self.registered_islands.get(island_id)

    def get_all_islands(self) -> Dict[str, Dict]:
        """Get all registered islands"""
        return self.registered_islands

    def get_island_html(
        self, island_id: str, container_id: str, options: Dict = None
    ) -> str:
        """Generate HTML for embedding an island component"""
        config = self.get_island_config(island_id)
        if not config:
            return f"<!-- Island '{island_id}' not found -->"

        options = options or {}
        merged_options = {**config.get("config", {}), **options}

        return f"""
        <div id="{container_id}" class="island-container" data-island-type="{island_id}">
            <div class="island-loading">
                <div class="flex items-center justify-center py-8">
                    <div class="flex items-center text-gray-500">
                        <i class="fas fa-spinner fa-spin mr-2"></i>
                        <span>Loading {config['title']}...</span>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (window.{config['name']}) {{
                const island = new {config['name']}('{container_id}', {json.dumps(merged_options)});
                island.render();
            }} else {{
                console.error('{config['name']} component not loaded');
            }}
        }});
        </script>
        """

    def get_island_script_tags(self, island_ids: List[str]) -> str:
        """Generate script tags for loading required island components"""
        script_tags = []
        loaded_paths = set()

        for island_id in island_ids:
            config = self.get_island_config(island_id)
            if config and config["component_path"] not in loaded_paths:
                script_tags.append(
                    f'<script src="{config["component_path"]}"></script>'
                )
                loaded_paths.add(config["component_path"])

        return "\n".join(script_tags)

    def create_feedback_island(self, container_id: str, options: Dict = None) -> str:
        """Convenience method to create a feedback/interaction island"""
        default_options = {
            "title": "Community Feedback Hub",
            "allowSubmission": True,
            "showExistingEntries": True,
            "placeholder": "Share your feedback, suggestions, or service values...",
        }

        if options:
            default_options.update(options)

        return self.get_island_html("interaction", container_id, default_options)

    def create_discussion_island(
        self, container_id: str, case_id: str = None, options: Dict = None
    ) -> str:
        """Convenience method to create a discussion island"""
        default_options = {
            "title": "Clinical Discussion",
            "case_id": case_id,
            "allow_case_references": True,
            "highlight_experts": True,
        }

        if options:
            default_options.update(options)

        return self.get_island_html("discussion", container_id, default_options)

    def get_island_styles(self) -> str:
        """Get CSS styles for island components"""
        return """
        <style>
        .island-container {
            margin: 1rem 0;
            border-radius: 0.75rem;
            border: 1px solid #e5e7eb;
            background: white;
            overflow: hidden;
        }
        
        .island-loading {
            padding: 2rem;
            text-align: center;
        }
        
        .island-error {
            padding: 2rem;
            text-align: center;
            color: #dc2626;
            background: #fef2f2;
        }
        
        .island-header {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e5e7eb;
            background: #f9fafb;
        }
        
        .island-content {
            padding: 1.5rem;
        }
        
        @media (max-width: 640px) {
            .island-container {
                margin: 0.5rem 0;
                border-radius: 0.5rem;
            }
            
            .island-content {
                padding: 1rem;
            }
        }
        </style>
        """


# Global instance
island_manager = IslandManager()


# Convenience functions for templates
def render_feedback_island(container_id: str, options: Dict = None) -> str:
    """Template function to render feedback island"""
    return island_manager.create_feedback_island(container_id, options)


def render_discussion_island(
    container_id: str, case_id: str = None, options: Dict = None
) -> str:
    """Template function to render discussion island"""
    return island_manager.create_discussion_island(container_id, case_id, options)


def get_required_scripts(island_types: List[str]) -> str:
    """Template function to get required script tags"""
    return island_manager.get_island_script_tags(island_types)


def get_island_styles() -> str:
    """Template function to get island CSS styles"""
    return island_manager.get_island_styles()
