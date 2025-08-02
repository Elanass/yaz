"""
Unified configuration system for the Gastric ADCI Platform
Provides a clean interface for accessing configuration values
"""
import os
import secrets
from typing import Any, Union, List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class PlatformConfig:
    """Production-ready configuration settings"""
    # Core settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug_mode: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    debug: bool = debug_mode  # Alias for compatibility
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # API configuration
    api_title: str = os.getenv("API_TITLE", "Precision Decision Platform")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    pwa_name: str = os.getenv("PWA_NAME", "Precision Decision Platform")
    
    # Security settings
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
    allowed_hosts: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Generate a secure secret key if not provided
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    encryption_key: str = os.getenv("ENCRYPTION_KEY", secrets.token_urlsafe(32))
    token_expire_minutes: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/database/gastric_adci.db")
    
    # Performance settings
    workers: int = int(os.getenv("WORKERS", "4"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Feature flags
    enable_swagger: bool = os.getenv("ENABLE_SWAGGER", "True").lower() in ("true", "1", "yes")
    enable_response_compression: bool = os.getenv("ENABLE_RESPONSE_COMPRESSION", "True").lower() in ("true", "1", "yes")
    enable_real_time_collaboration: bool = os.getenv("ENABLE_REAL_TIME_COLLABORATION", "True").lower() in ("true", "1", "yes")
    
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

# Singleton configuration instance
config = PlatformConfig()

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value from platform config or environment"""
    # First try to get from platform config object
    if hasattr(config, key.lower()):
        return getattr(config, key.lower())
    
    # Fallback to environment variable
    return os.getenv(key, default)

def is_development() -> bool:
    """Check if running in development mode"""
    return config.is_development

def is_production() -> bool:
    """Check if running in production mode"""
    return config.is_production

def get_settings() -> PlatformConfig:
    """Get the global configuration settings"""
    return config
