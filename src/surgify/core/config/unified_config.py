"""
Clean, unified configuration system for Surgify Platform
"""
import os
import secrets
from typing import List
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from surgify.core.feature_flags import is_feature_enabled

# Load environment variables
load_dotenv()


class SurgifyConfig(BaseModel):
    """Main configuration class for Surgify Platform"""

    # Core Application Settings
    app_name: str = "Surgify"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Security Settings
    secret_key: str = "surgify_dev_secret_key_2025"
    jwt_secret: str = "surgify_dev_jwt_secret_2025"
    token_expire_minutes: int = 1440

    # Database Settings
    database_url: str = os.getenv(
        "DATABASE_URL", "cockroachdb://root@localhost:26257/surgify?sslmode=disable"
    )

    # Redis Cache Settings
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # CORS Settings
    cors_origins: str = "http://localhost:8000,http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    # Feature Flags
    enable_docs: bool = True
    enable_metrics: bool = True

    def __init__(self, **kwargs):
        # Load from environment variables
        env_values = {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", "8000")),
            "workers": int(os.getenv("WORKERS", "4")),
            "secret_key": os.getenv("SECRET_KEY", "surgify_dev_secret_key_2025"),
            "jwt_secret": os.getenv("JWT_SECRET", "surgify_dev_jwt_secret_2025"),
            "token_expire_minutes": int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440")),
            "database_url": os.getenv(
                "DATABASE_URL",
                "cockroachdb://root@localhost:26257/surgify?sslmode=disable",
            ),
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
            "redis_db": int(os.getenv("REDIS_DB", "0")),
            "cors_origins": os.getenv(
                "CORS_ORIGINS", "http://localhost:8000,http://localhost:3000"
            ),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "enable_docs": os.getenv("ENABLE_DOCS", "true").lower()
            in ("true", "1", "yes"),
            "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower()
            in ("true", "1", "yes"),
        }

        # Override with any passed kwargs
        env_values.update(kwargs)
        super().__init__(**env_values)

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"

    @property
    def base_dir(self) -> Path:
        """Get base directory of the application"""
        return Path(__file__).parent.parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """Get data directory"""
        data_path = self.base_dir / "data"
        data_path.mkdir(exist_ok=True)
        return data_path

    @property
    def logs_dir(self) -> Path:
        """Get logs directory"""
        logs_path = self.base_dir / "logs"
        logs_path.mkdir(exist_ok=True)
        return logs_path


# Example usage in config:
if is_feature_enabled("COCKROACHDB"):
    database_url = os.getenv(
        "DATABASE_URL", "cockroachdb://root@localhost:26257/surgify?sslmode=disable"
    )
else:
    database_url = os.getenv("DATABASE_URL", "sqlite:///data/database/surgify.db")

# Global config instance
_config = None


def get_settings() -> SurgifyConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = SurgifyConfig()
    return _config


def reload_settings() -> SurgifyConfig:
    """Reload configuration (useful for testing)"""
    global _config
    _config = SurgifyConfig()
    return _config
