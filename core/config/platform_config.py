"""
Minimal configuration using environment variables for MVP Precision Decision Platform
"""
import os

class PlatformConfig:
    """Minimal configuration settings for MVP"""
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/gastric_adci")
    api_title: str = os.getenv("API_TITLE", "Precision Decision Platform")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    pwa_name: str = os.getenv("PWA_NAME", "Precision Decision Platform")
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "* ").split(",")
    allowed_hosts: list[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Singleton configuration instance
config = PlatformConfig()
