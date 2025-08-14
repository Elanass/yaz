"""Configuration module for YAZ Healthcare Platform"""

import os
from pathlib import Path
from typing import Dict, List


class PlatformConfig:
    """Central configuration for the YAZ platform"""

    # Database settings
    DATABASE_PATH = os.getenv("YAZ_DB_PATH", "data/yaz.db")
    DATABASE_BACKUP_PATH = os.getenv("YAZ_DB_BACKUP_PATH", "data/backups")

    # Server settings
    HOST = os.getenv("YAZ_HOST", "0.0.0.0")
    PORT = int(os.getenv("YAZ_PORT", "8000"))
    DEBUG = os.getenv("YAZ_DEBUG", "false").lower() == "true"

    # Logging settings
    LOG_LEVEL = os.getenv("YAZ_LOG_LEVEL", "INFO")
    LOG_DIR = Path(os.getenv("YAZ_LOG_DIR", "logs"))

    # Application settings - Organized by service type
    APP_CONFIGS = {
        # External Services (Open APIs accessible via external interfaces)
        "surge": {
            "name": "Surgery Analytics Platform",
            "description": "Advanced surgical case management and analytics",
            "version": "1.0.0",
            "enabled": True,
            "type": "external",
            "api_access": "open",
            "features": ["case_management", "surgical_analytics", "outcome_tracking"],
        },
        "move": {
            "name": "Logistics Management Platform",
            "description": "Medical logistics and supply chain management",
            "version": "1.0.0",
            "enabled": True,
            "type": "external",
            "api_access": "open",
            "features": [
                "inventory_management",
                "supply_tracking",
                "delivery_coordination",
            ],
        },
        # Internal Services (Platform management and administration)
        "clinica": {
            "name": "Clinical Management System",
            "description": "Integrated clinical care and management platform",
            "version": "1.0.0",
            "enabled": True,
            "type": "internal",
            "api_access": "restricted",
            "features": [
                "patient_management",
                "clinical_workflows",
                "care_coordination",
            ],
        },
        "educa": {
            "name": "Medical Education Platform",
            "description": "Medical education and training management system",
            "version": "1.0.0",
            "enabled": True,
            "type": "internal",
            "api_access": "restricted",
            "features": ["course_management", "training_tracking", "certification"],
        },
        "insura": {
            "name": "Insurance Management System",
            "description": "Insurance claims and coverage management platform",
            "version": "1.0.0",
            "enabled": True,
            "type": "internal",
            "api_access": "restricted",
            "features": ["claims_processing", "coverage_verification", "billing"],
        },
    }

    # Security settings
    SECRET_KEY = os.getenv("YAZ_SECRET_KEY", "your-secret-key-change-in-production")
    CORS_ORIGINS = os.getenv("YAZ_CORS_ORIGINS", "*").split(",")

    # Feature flags
    FEATURES = {
        "dashboard_analytics": True,
        "real_time_updates": True,
        "audit_logging": True,
        "automated_backups": True,
        "api_rate_limiting": False,
        "user_authentication": False,
    }

    @classmethod
    def get_enabled_apps(cls) -> list[str]:
        """Get list of enabled applications"""
        return [
            app
            for app, config in cls.APP_CONFIGS.items()
            if config.get("enabled", True)
        ]

    @classmethod
    def get_external_apps(cls) -> list[str]:
        """Get list of external (open API) applications"""
        return [
            app
            for app, config in cls.APP_CONFIGS.items()
            if config.get("enabled", True) and config.get("type") == "external"
        ]

    @classmethod
    def get_internal_apps(cls) -> list[str]:
        """Get list of internal applications"""
        return [
            app
            for app, config in cls.APP_CONFIGS.items()
            if config.get("enabled", True) and config.get("type") == "internal"
        ]

    @classmethod
    def get_app_config(cls, app_name: str) -> dict:
        """Get configuration for a specific app"""
        return cls.APP_CONFIGS.get(app_name, {})

    @classmethod
    def get_apps_by_type(cls, app_type: str) -> list[str]:
        """Get apps by type (internal/external)"""
        return [
            app
            for app, config in cls.APP_CONFIGS.items()
            if config.get("enabled", True) and config.get("type") == app_type
        ]

    @classmethod
    def is_feature_enabled(cls, feature: str) -> bool:
        """Check if a feature is enabled"""
        return cls.FEATURES.get(feature, False)


# Global config instance
config = PlatformConfig()
