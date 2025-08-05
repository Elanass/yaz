"""
Production-ready configuration using environment variables for Precision Decision Platform
"""
import os
import secrets
from typing import Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Extract environment variable parsing to a utility function
def parse_env_var(key: str, default: Any, cast_type: type = str) -> Any:
    value = os.getenv(key, default)
    try:
        return cast_type(value)
    except ValueError:
        return default

class PlatformConfig:
    """Production-ready configuration settings"""
    # Core settings
    environment: str = parse_env_var("ENVIRONMENT", "development")
    debug_mode: bool = parse_env_var("DEBUG", "False", bool)
    debug: bool = debug_mode  # Alias for compatibility
    host: str = parse_env_var("HOST", "0.0.0.0")
    port: int = parse_env_var("PORT", 8000, int)
    
    # API configuration
    api_title: str = os.getenv("API_TITLE", "Precision Decision Platform")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    pwa_name: str = os.getenv("PWA_NAME", "Precision Decision Platform")
    
    # Security settings
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
    allowed_hosts: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Generate a secure secret key if not provided
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    # Note: Ensure SECRET_KEY is set in the environment for production to avoid using a generated key.
    encryption_key: str = os.getenv("ENCRYPTION_KEY", secrets.token_urlsafe(32))
    token_expire_minutes: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "cockroachdb://root@localhost:26257/surgify?sslmode=disable")
    electricsql_url: str = os.getenv("ELECTRICSQL_URL", "http://localhost:5133")
    electricsql_token: str = os.getenv("ELECTRICSQL_TOKEN", "dev-token")
    electricsql_secure: bool = os.getenv("ELECTRICSQL_SECURE", "False").lower() in ("true", "1", "yes")
    electric_database_id: str = os.getenv("ELECTRIC_DATABASE_ID", "dev-database-id")
    electric_token: str = os.getenv("ELECTRIC_TOKEN", "dev-electric-token")
    
    # Performance settings
    workers: int = int(os.getenv("WORKERS", "4"))  # Number of Uvicorn workers
    sync_interval_ms: int = int(os.getenv("SYNC_INTERVAL_MS", "5000"))  # 5 seconds
    offline_storage_mb: int = int(os.getenv("OFFLINE_STORAGE_MB", "100"))  # 100 MB for offline storage
    max_request_size_mb: int = int(os.getenv("MAX_REQUEST_SIZE_MB", "50"))  # 50 MB max request size
    
    # IPFS configuration
    ipfs_api_url: str = os.getenv("IPFS_API_URL", "http://localhost:5001/api/v0")
    ipfs_gateway_url: str = os.getenv("IPFS_GATEWAY_URL", "http://localhost:8080/ipfs")
    
    # Security and compliance settings
    file_encryption_enabled: bool = os.getenv("FILE_ENCRYPTION_ENABLED", "True").lower() in ("true", "1", "yes")
    patient_data_encryption: bool = os.getenv("PATIENT_DATA_ENCRYPTION", "True").lower() in ("true", "1", "yes")
    enable_audit_logging: bool = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() in ("true", "1", "yes")
    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # ~7 years for healthcare data
    enable_real_time_collaboration: bool = os.getenv("ENABLE_REAL_TIME_COLLABORATION", "True").lower() in ("true", "1", "yes")
    
    # Cache and optimization settings
    enable_response_compression: bool = os.getenv("ENABLE_RESPONSE_COMPRESSION", "True").lower() in ("true", "1", "yes")
    static_files_max_age: int = parse_env_var("STATIC_FILES_MAX_AGE", 86400, int)  # 1 day in seconds
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_to_file: bool = os.getenv("LOG_TO_FILE", "False").lower() in ("true", "1", "yes")
    log_file_path: str = os.getenv("LOG_FILE_PATH", "logs/app.log")
    
    # Feature flags
    enable_swagger: bool = os.getenv("ENABLE_SWAGGER", "True").lower() in ("true", "1", "yes")
    
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
