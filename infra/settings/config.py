"""Configuration settings for YAZ Platform"""

import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from pydantic import Field


class Settings(BaseSettings):
    """Application settings for YAZ Platform"""
    
    # App identification
    app_name: str = Field(default="YAZ Healthcare Platform", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="HOST") 
    port: int = Field(default=8000, env="PORT")
    
    # App routing settings
    default_app: str = Field(default="core", env="DEFAULT_APP")
    apps_prefix: str = Field(default="/apps", env="APPS_PREFIX")
    
    # Security
    secret_key: str = Field(default="yaz_dev_secret_key_2025", env="SECRET_KEY")
    jwt_secret: str = Field(default="yaz_dev_jwt_secret_2025", env="JWT_SECRET")
    token_expire_minutes: int = Field(default=1440, env="TOKEN_EXPIRE_MINUTES")
    
    # Database
    database_url: str = Field(default="sqlite:///data/yaz.db", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_path: str = Field(default="data/yaz.db", env="YAZ_DB_PATH")
    database_backup_path: str = Field(default="data/backups", env="YAZ_DB_BACKUP_PATH")
    
    # Cache configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_dir: Path = Field(default=Path("logs"), env="LOG_DIR")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:8000",
            "http://localhost:3000", 
            "http://127.0.0.1:8000"
        ],
        env="CORS_ORIGINS"
    )
    
    # Application configurations
    app_configs: Dict = Field(default_factory=lambda: {
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
            "name": "Integrated Clinical Care",
            "description": "Comprehensive clinical care experience",
            "version": "1.0.0",
            "enabled": True,
            "type": "internal",
            "api_access": "restricted",
            "features": [
                "patient_management",
                "clinical_workflows",
                "integrated_services",
            ],
        },
        "educa": {
            "name": "Medical Education Platform",
            "description": "Medical education and training platform",
            "version": "1.0.0",
            "enabled": True,
            "type": "internal",
            "api_access": "restricted",
            "features": [
                "course_management",
                "assessment_tools",
                "certification_tracking",
            ],
        },
        "insura": {
            "name": "Insurance Management Platform",
            "description": "Healthcare insurance and billing management",
            "version": "1.0.0",
            "enabled": True,
            "type": "internal",
            "api_access": "restricted",
            "features": [
                "claims_processing",
                "billing_management",
                "coverage_verification",
            ],
        },
        "core": {
            "name": "Core Platform",
            "description": "Core YAZ platform services and management",
            "version": "2.0.0",
            "enabled": True,
            "type": "core",
            "api_access": "internal",
            "features": [
                "platform_management",
                "user_authentication",
                "system_monitoring",
            ],
        }
    })
    
    class Config:
        env_file = ".env"
        env_prefix = "YAZ_"
        case_sensitive = False


# Global settings instance
settings = Settings()
