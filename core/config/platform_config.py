"""
Platform Configuration
Consolidated environment settings for Gastric ADCI Platform
"""

import os
from pydantic import BaseSettings, Field

class PlatformConfig(BaseSettings):
    """Consolidated configuration settings"""
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    debug: bool = Field(default=os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

    # Database
    database_url: str = Field(default=os.getenv("DATABASE_URL"))
    electricsql_url: str = Field(default=os.getenv("ELECTRICSQL_URL"))

    # Security
    secret_key: str = Field(default=os.getenv("SECRET_KEY"))
    jwt_secret: str = Field(default=os.getenv("JWT_SECRET"))
    clinical_data_encryption_key: str = Field(default=os.getenv("CLINICAL_DATA_ENCRYPTION_KEY"))

    # CORS
    cors_origins: list = Field(default=os.getenv("CORS_ORIGINS", "[]"))
    allowed_hosts: list = Field(default=os.getenv("ALLOWED_HOSTS", "[]"))

    # Redis
    redis_url: str = Field(default=os.getenv("REDIS_URL"))

    # IPFS
    ipfs_api_url: str = Field(default=os.getenv("IPFS_API_URL"))
    ipfs_gateway_url: str = Field(default=os.getenv("IPFS_GATEWAY_URL"))

    # API Settings
    api_base_url: str = Field(default=os.getenv("API_BASE_URL"))
    default_confidence_threshold: float = Field(default=float(os.getenv("DEFAULT_CONFIDENCE_THRESHOLD", 0.75)))

    # Clinical Settings
    enable_clinical_validation: bool = Field(default=os.getenv("ENABLE_CLINICAL_VALIDATION", "true").lower() == "true")
    clinical_trial_mode: bool = Field(default=os.getenv("CLINICAL_TRIAL_MODE", "false").lower() == "true")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
