"""
Core Shared Configuration
Minimal, DRY configuration management
"""

import os
from typing import Dict, Any, Optional


class SharedConfig:
    """Shared configuration for all YAZ applications"""
    
    def __init__(self):
        # Core settings
        self.app_name = "YAZ Healthcare Platform"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./data/yaz.db")
        
        # Server
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_dir = os.getenv("LOG_DIR", "logs")
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "dev-key-change-in-production")


# Global shared config instance
shared_config = SharedConfig()


def get_shared_config() -> SharedConfig:
    """Get shared configuration instance"""
    return shared_config


def get_app_config(app_name: str) -> Dict[str, Any]:
    """Get app-specific configuration"""
    return {
        "name": app_name,
        "version": shared_config.version,
        "debug": shared_config.debug,
        "database_url": shared_config.database_url,
        "log_level": shared_config.log_level,
    }
