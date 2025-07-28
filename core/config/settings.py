"""
Core Configuration System
Centralized configuration management for the Gastric ADCI Platform
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pydantic import ConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    model_config = ConfigDict(env_prefix="DB_")
    
    url: str = Field(default="sqlite:///./yaz.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)


class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    model_config = ConfigDict(env_prefix="SECURITY_")
    
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    password_min_length: int = Field(default=8)
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"])
    cors_methods: List[str] = Field(default=["*"])
    cors_headers: List[str] = Field(default=["*"])


class ApplicationConfig(BaseSettings):
    """Application configuration settings"""
    model_config = ConfigDict(env_prefix="APP_")
    
    name: str = Field(default="Gastric ADCI Platform")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Features
    enable_swagger: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
    enable_audit: bool = Field(default=True)


class ClinicalConfig(BaseSettings):
    """Clinical decision engine configuration"""
    model_config = ConfigDict(env_prefix="CLINICAL_")
    
    # Decision engine settings
    confidence_threshold: float = Field(default=0.7)
    max_batch_size: int = Field(default=100)
    
    # ADCI engine
    adci_model_version: str = Field(default="1.0")
    adci_cache_ttl: int = Field(default=3600)
    
    # FLOT protocol
    flot_eligibility_strict: bool = Field(default=True)
    
    # Surgery engine
    surgery_risk_threshold: float = Field(default=0.8)


class Settings(BaseSettings):
    """Main settings class combining all configuration sections"""
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        extra="ignore"  # Ignore extra fields from .env
    )
    
    # Core configs
    app: ApplicationConfig = ApplicationConfig()
    db: DatabaseConfig = DatabaseConfig()
    security: SecurityConfig = SecurityConfig()
    clinical: ClinicalConfig = ClinicalConfig()
    
    # Environment
    environment: str = Field(default="development")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"



@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Common environment variables for features
def get_feature_config(feature_name: str) -> Dict[str, Any]:
    """Get configuration for a specific feature"""
    settings = get_settings()
    
    base_config = {
        "debug": settings.app.debug,
        "environment": settings.environment,
        "database_url": settings.db.url,
    }
    
    # Feature-specific configurations
    if feature_name == "auth":
        base_config.update({
            "secret_key": settings.security.secret_key,
            "algorithm": settings.security.algorithm,
            "token_expire_minutes": settings.security.access_token_expire_minutes,
        })
    elif feature_name == "decisions":
        base_config.update({
            "confidence_threshold": settings.clinical.confidence_threshold,
            "cache_ttl": settings.clinical.adci_cache_ttl,
            "max_batch_size": settings.clinical.max_batch_size,
        })
    elif feature_name == "insights":
        base_config.update({
            "batch_size": settings.clinical.max_batch_size,
            "confidence_threshold": settings.clinical.confidence_threshold,
        })
    
    return base_config
