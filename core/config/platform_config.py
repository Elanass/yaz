"""
Minimal configuration using environment variables for MVP Precision Decision Platform
"""
import os

class PlatformConfig:
    """Minimal configuration settings for MVP"""
    # Core settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # API configuration
    api_title: str = os.getenv("API_TITLE", "Precision Decision Platform")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    pwa_name: str = os.getenv("PWA_NAME", "Precision Decision Platform")
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "* ").split(",")
    allowed_hosts: list[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/gastric_adci")
    electricsql_url: str = os.getenv("ELECTRICSQL_URL", "http://localhost:5133")
    electricsql_token: str = os.getenv("ELECTRICSQL_TOKEN", "dev-token")
    electricsql_secure: bool = os.getenv("ELECTRICSQL_SECURE", "False").lower() == "true"
    electric_database_id: str = os.getenv("ELECTRIC_DATABASE_ID", "dev-database-id")
    electric_token: str = os.getenv("ELECTRIC_TOKEN", "dev-electric-token")
    sync_interval_ms: int = int(os.getenv("SYNC_INTERVAL_MS", "5000"))  # 5 seconds
    offline_storage_mb: int = int(os.getenv("OFFLINE_STORAGE_MB", "100"))  # 100 MB for offline storage
    
    # IPFS configuration
    ipfs_api_url: str = os.getenv("IPFS_API_URL", "http://localhost:5001/api/v0")
    ipfs_gateway_url: str = os.getenv("IPFS_GATEWAY_URL", "http://localhost:8080/ipfs")
    
    # Security and encryption settings
    secret_key: str = os.getenv("SECRET_KEY", "default-secret-key-for-development-only")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "dev-encryption-key-32-chars-long")
    token_expire_minutes: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
    file_encryption_enabled: bool = os.getenv("FILE_ENCRYPTION_ENABLED", "True").lower() == "true"
    patient_data_encryption: bool = os.getenv("PATIENT_DATA_ENCRYPTION", "True").lower() == "true"
    enable_audit_logging: bool = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() == "true"
    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # ~7 years for healthcare data
    enable_real_time_collaboration: bool = os.getenv("ENABLE_REAL_TIME_COLLABORATION", "True").lower() == "true"

# Singleton configuration instance
config = PlatformConfig()
