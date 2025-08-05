"""
Unified configuration for Surgify - imports from main config
This file provides backward compatibility and uses its own configuration
"""

from typing import List
from pathlib import Path
from pydantic import BaseSettings, Field
from dotenv import load_dotenv
import os
import secrets

# Load environment variables
load_dotenv()

class UnifiedConfig(BaseSettings):
    """Unified configuration settings for the entire platform"""
    
    # ===============================
    # Core Application Settings
    # ===============================
    app_name: str = Field(default="YAZ Surgify Platform", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug_mode: bool = Field(default=False, env="DEBUG")
    debug: bool = debug_mode  # Alias for compatibility
    
    # ===============================
    # Server Settings
    # ===============================
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=6379, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # ===============================
    # API Configuration
    # ===============================
    api_title: str = Field(default="Precision Decision Platform", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    pwa_name: str = Field(default="Precision Decision Platform", env="PWA_NAME")
    
    # ===============================
    # Security Settings
    # ===============================
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32), env="SECRET_KEY")
    jwt_secret: str = Field(default_factory=lambda: secrets.token_hex(32), env="JWT_SECRET")
    encryption_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="ENCRYPTION_KEY")
    token_expire_minutes: int = Field(default=1440, env="TOKEN_EXPIRE_MINUTES")  # 24 hours
    
    # ===============================
    # Database Configuration
    # ===============================
    database_url: str = Field(
        default="sqlite+aiosqlite:///data/database/gastric_adci.db",
        env="DATABASE_URL"
    )
    
    # ===============================
    # Redis Cache Settings
    # ===============================
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # ===============================
    # Feature Flags
    # ===============================
    enable_swagger: bool = Field(default=True, env="ENABLE_SWAGGER")
    enable_docs: bool = Field(default=True, env="ENABLE_DOCS")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    
    # ===============================
    # Properties for convenience
    # ===============================
    @property
    def base_dir(self) -> Path:
        """Base directory of the application"""
        return Path(__file__).parent.parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        """Data directory"""
        data_path = self.base_dir / "data"
        data_path.mkdir(exist_ok=True)
        return data_path
    
    @property
    def logs_dir(self) -> Path:
        """Logs directory"""
        logs_path = self.base_dir / "logs" 
        logs_path.mkdir(exist_ok=True)
        return logs_path
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.environment.lower() == "testing"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:6379,http://localhost:8000,http://localhost:3000")
        return [origin.strip() for origin in cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields

# ===============================
# Global Configuration Instance
# ===============================
_config_instance = None

def get_settings() -> UnifiedConfig:
    """Get the global configuration instance (singleton pattern)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = UnifiedConfig()
    return _config_instance

def reload_settings() -> UnifiedConfig:
    """Reload configuration (useful for testing)"""
    global _config_instance
    _config_instance = UnifiedConfig()
    return _config_instance

# Alias for backward compatibility
SurgifyConfig = UnifiedConfig
