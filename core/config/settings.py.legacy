"""
Streamlined application settings
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # Basic config
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    # Application version
    version: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Server config
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/database/gastric_adci.db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()

# Legacy compatibility functions
def get_settings():
    return settings.__dict__

def get_feature_config(feature_name):
    return {}

def get_logging_config():
    return {"level": "INFO", "handlers": ["console"]}

def get_adapter_config(adapter_name):
    return {
        "url": "http://localhost:8080",
        "username": "admin", 
        "password": os.getenv("APP_PASSWORD", "default_password"),
        "timeout": 30
    }
