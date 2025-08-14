"""Shared Configuration Module
Base configuration that can be extended by each app.
"""

from pathlib import Path


try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for older pydantic versions
        class BaseSettings:
            pass


from pydantic import Field


class BaseConfig(BaseSettings):
    """Base configuration for all Yaz platform apps."""

    # App identification
    app_name: str = Field(default="Yaz Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_environment: str = Field(default="development", env="APP_ENV")

    # Server configuration
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")

    # Database configuration
    database_url: str = Field(
        default="sqlite:///./data/local/yaz.db", env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # Cache configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")

    # Security configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")

    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    # Feature flags
    enable_docs: bool = Field(default=True, env="ENABLE_DOCS")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")

    # File storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB

    # Networking configuration
    mesh_enabled: bool = Field(default=False, env="MESH_ENABLED")
    mesh_port: int = Field(default=9000, env="MESH_PORT")
    enable_networking: bool = Field(default=True, env="ENABLE_NETWORKING")
    enable_p2p: bool = Field(default=True, env="ENABLE_P2P")
    enable_ble_mesh: bool = Field(default=False, env="ENABLE_BLE_MESH")
    enable_multi_vm: bool = Field(default=False, env="ENABLE_MULTI_VM")

    # Surgery-specific features
    surgery_types_enabled: list = Field(
        default=["general", "cardiac", "neuro", "orthopedic"], env="SURGERY_TYPES"
    )
    ai_analysis_enabled: bool = Field(default=True, env="AI_ANALYSIS_ENABLED")
    enable_3d_visualization: bool = Field(default=True, env="ENABLE_3D_VISUALIZATION")
    enable_real_time_monitoring: bool = Field(
        default=True, env="ENABLE_REAL_TIME_MONITORING"
    )
    enable_predictive_analytics: bool = Field(
        default=True, env="ENABLE_PREDICTIVE_ANALYTICS"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        return Path("./data") / self.app_environment

    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        return Path("./logs")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
_config: BaseConfig | None = None


def get_shared_config() -> BaseConfig:
    """Get shared configuration instance."""
    global _config
    if _config is None:
        _config = BaseConfig()
    return _config


def create_app_config(app_name: str, **overrides) -> BaseConfig:
    """Create app-specific configuration."""
    config_data = {"app_name": app_name, **overrides}
    return BaseConfig(**config_data)
