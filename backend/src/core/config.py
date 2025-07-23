"""
Core configuration management for Gastric ADCI Platform
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import BaseSettings, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str
    electricsql_url: str = "ws://localhost:5133"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Security
    secret_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    password_salt_rounds: int = 12
    
    # CORS
    cors_origins: List[str] = ["http://localhost:8000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600
    
    # IPFS
    ipfs_api_url: str = "http://localhost:5001"
    ipfs_gateway_url: str = "http://localhost:8080"
    
    # Clinical Decision Engines
    adci_engine_endpoint: str = "https://api.adci.health/v1"
    adci_api_key: Optional[str] = None
    clinical_data_encryption_key: str
    
    # Audit and Compliance
    audit_log_retention_days: int = 2555  # 7 years for HIPAA
    enable_audit_logging: bool = True
    gdpr_compliance_mode: bool = True
    hipaa_compliance_mode: bool = True
    
    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "noreply@gastric-adci.health"
    
    # Monitoring
    prometheus_metrics_port: int = 9090
    enable_metrics: bool = True
    sentry_dsn: Optional[str] = None
    
    # File Upload
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "dicom"]
    
    # PWA Configuration
    pwa_name: str = "Gastric ADCI Platform"
    pwa_short_name: str = "ADCI"
    pwa_description: str = "Gastric Oncology-Surgery Decision Support"
    pwa_theme_color: str = "#2563eb"
    pwa_background_color: str = "#ffffff"
    
    # Google Cloud
    google_cloud_project: Optional[str] = None
    google_cloud_region: str = "us-central1"
    cloud_sql_connection_name: Optional[str] = None
    
    # Clinical Settings
    default_confidence_threshold: float = 0.75
    enable_experimental_features: bool = False
    clinical_trial_mode: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @validator("default_confidence_threshold")
        def validate_confidence_threshold(cls, v):
            if not 0.0 <= v <= 1.0:
                raise ValueError("Confidence threshold must be between 0.0 and 1.0")
            return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()
