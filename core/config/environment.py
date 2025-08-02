"""
Multi-Environment Configuration for Gastric ADCI Platform

Supports three operational environments:
- Local: Standalone operation on local machine  
- P2P: Peer-to-peer decentralized collaboration
- Multicloud: Deployable across AWS, GCP, Azure

Enhanced for collaborative subject study with real-time data sharing.
"""

import json
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path


class DeploymentMode(Enum):
    LOCAL = "local"
    P2P = "p2p" 
    MULTICLOUD = "multicloud"


class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    NONE = "none"


@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False
    # Enhanced for multi-environment
    backup_enabled: bool = True
    encryption_at_rest: bool = True
    connection_timeout: int = 30


@dataclass 
class P2PConfig:
    enabled: bool = False
    peer_discovery: str = "gun"  # gun, mdns, bootstrap
    bootstrap_nodes: List[str] = None
    port: int = 8765
    sync_interval: int = 30  # seconds
    # Enhanced collaboration features
    real_time_sync: bool = True
    conflict_resolution: str = "last_write_wins"
    data_types: List[str] = None  # ['cases', 'decisions', 'education']
    
    def __post_init__(self):
        if self.bootstrap_nodes is None:
            self.bootstrap_nodes = []
        if self.data_types is None:
            self.data_types = ['cases', 'decisions', 'education', 'feedback']


@dataclass
class CloudConfig:
    provider: CloudProvider = CloudProvider.NONE
    region: str = ""
    storage_bucket: str = ""
    database_url: str = ""
    redis_url: Optional[str] = None
    monitoring_enabled: bool = True
    # Enhanced cloud features
    auto_scaling: bool = True
    load_balancer: bool = True
    backup_retention_days: int = 30
    disaster_recovery: bool = True
    
    # Provider-specific configs
    aws_config: Dict[str, Any] = None
    gcp_config: Dict[str, Any] = None
    azure_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.aws_config is None:
            self.aws_config = {}
        if self.gcp_config is None:
            self.gcp_config = {}
        if self.azure_config is None:
            self.azure_config = {}


@dataclass
class SecurityConfig:
    """Enhanced security for healthcare data compliance"""
    encryption_enabled: bool = True
    auth_required: bool = True
    session_timeout: int = 3600
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: List[str] = None
    # Healthcare compliance
    hipaa_compliance: bool = True
    audit_logging: bool = True
    data_anonymization: bool = True
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.pdf', '.txt', '.json', '.csv', '.xlsx', '.dcm']


@dataclass
class CollaborationConfig:
    """Configuration for collaborative subject study features"""
    real_time_updates: bool = True
    data_sharing_enabled: bool = True
    feedback_collection: bool = True
    insight_sharing: bool = True
    automatic_sync: bool = True
    conflict_resolution: str = "merge"  # merge, overwrite, manual
    version_control: bool = True


class EnvironmentConfig:
    """Enhanced environment configuration manager for multi-deployment support"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("./config/environment.json")
        self.mode = self._detect_mode()
        self.config = self._load_config()
        
        # Initialize configuration objects
        self.database = self._init_database_config()
        self.p2p = self._init_p2p_config()
        self.cloud = self._init_cloud_config()
        self.security = self._init_security_config()
        self.collaboration = self._init_collaboration_config()
    
    def _detect_mode(self) -> DeploymentMode:
        """Auto-detect deployment mode with enhanced logic"""
        # Check explicit environment variable
        env_mode = os.getenv("GASTRIC_ADCI_ENV", "").lower()
        if env_mode in ["local", "p2p", "multicloud"]:
            return DeploymentMode(env_mode)
        
        # Check for cloud provider indicators
        cloud_indicators = [
            "AWS_REGION", "AWS_ACCESS_KEY_ID",
            "GCP_PROJECT", "GOOGLE_APPLICATION_CREDENTIALS", 
            "AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID"
        ]
        if any(os.getenv(var) for var in cloud_indicators):
            return DeploymentMode.MULTICLOUD
        
        # Check for P2P indicators
        p2p_indicators = [
            os.getenv("P2P_ENABLED", "").lower() == "true",
            os.path.exists("./p2p.config"),
            os.getenv("GASTRIC_P2P_PORT")
        ]
        if any(p2p_indicators):
            return DeploymentMode.P2P
        
        # Default to local development
        return DeploymentMode.LOCAL
    
    def _load_config(self) -> Dict[str, Any]:
        """Load comprehensive configuration based on deployment mode"""
        base_config = {
            "app_name": "Gastric ADCI Platform",
            "version": "2.0.0",
            "environment": self.mode.value,
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", "8000")),
            "api_prefix": "/api/v1",
            "docs_url": "/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
            
            # Enhanced features
            "real_time_updates": True,
            "offline_support": True,
            "data_export": True,
            "analytics_enabled": self.mode == DeploymentMode.MULTICLOUD,
            "ml_insights": self.mode == DeploymentMode.MULTICLOUD,
            "collaboration_features": self.mode in [DeploymentMode.P2P, DeploymentMode.MULTICLOUD]
        }
        
        # Load environment-specific config
        if self.mode == DeploymentMode.LOCAL:
            base_config.update(self._get_local_config())
        elif self.mode == DeploymentMode.P2P:
            base_config.update(self._get_p2p_config())
        elif self.mode == DeploymentMode.MULTICLOUD:
            base_config.update(self._get_cloud_config())
        
        # Load from config file if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    base_config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return base_config
    
    def _get_local_config(self) -> Dict[str, Any]:
        """Configuration for local development"""
        return {
            "data_dir": os.getenv("DATA_DIR", "./data"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "hot_reload": True,
            "cors_origins": ["http://localhost:3000", "http://localhost:8080"],
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./data/database/gastric_adci.db"),
            "file_storage": "./data/uploads",
            "backup_enabled": False,
            "monitoring": False
        }
    
    def _get_p2p_config(self) -> Dict[str, Any]:
        """Configuration for P2P deployment"""
        return {
            "data_dir": os.getenv("DATA_DIR", "./data/p2p"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "p2p_port": int(os.getenv("P2P_PORT", "8765")),
            "peer_discovery": os.getenv("PEER_DISCOVERY", "gun"),
            "sync_interval": int(os.getenv("SYNC_INTERVAL", "30")),
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./data/p2p/gastric_adci.db"),
            "file_storage": "./data/p2p/uploads",
            "backup_enabled": True,
            "monitoring": True,
            "real_time_collaboration": True
        }
    
    def _get_cloud_config(self) -> Dict[str, Any]:
        """Configuration for cloud deployment"""
        provider = self._detect_cloud_provider()
        
        config = {
            "data_dir": os.getenv("DATA_DIR", "/app/data"),
            "log_level": os.getenv("LOG_LEVEL", "WARNING"),
            "cloud_provider": provider.value,
            "region": os.getenv("CLOUD_REGION", ""),
            "database_url": os.getenv("DATABASE_URL", ""),
            "redis_url": os.getenv("REDIS_URL", ""),
            "file_storage": os.getenv("STORAGE_BUCKET", ""),
            "backup_enabled": True,
            "monitoring": True,
            "auto_scaling": True,
            "load_balancer": True,
            "cdn_enabled": True,
            "ml_services": True,
            "advanced_analytics": True
        }
        
        # Add provider-specific configuration
        if provider == CloudProvider.AWS:
            config.update(self._get_aws_config())
        elif provider == CloudProvider.GCP:
            config.update(self._get_gcp_config())
        elif provider == CloudProvider.AZURE:
            config.update(self._get_azure_config())
        
        return config
    
    def _detect_cloud_provider(self) -> CloudProvider:
        """Detect which cloud provider is being used"""
        if os.getenv("AWS_REGION") or os.getenv("AWS_ACCESS_KEY_ID"):
            return CloudProvider.AWS
        elif os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return CloudProvider.GCP
        elif os.getenv("AZURE_SUBSCRIPTION_ID") or os.getenv("AZURE_TENANT_ID"):
            return CloudProvider.AZURE
        return CloudProvider.NONE
    
    def _get_aws_config(self) -> Dict[str, Any]:
        """AWS-specific configuration"""
        return {
            "aws_region": os.getenv("AWS_REGION", "us-west-2"),
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "aws_s3_bucket": os.getenv("AWS_S3_BUCKET", ""),
            "aws_rds_endpoint": os.getenv("AWS_RDS_ENDPOINT", ""),
            "aws_elasticache_endpoint": os.getenv("AWS_ELASTICACHE_ENDPOINT", ""),
            "aws_lambda_functions": True,
            "aws_cloudwatch": True,
            "aws_cognito": True
        }
    
    def _get_gcp_config(self) -> Dict[str, Any]:
        """GCP-specific configuration"""
        return {
            "gcp_project": os.getenv("GCP_PROJECT", ""),
            "gcp_region": os.getenv("GCP_REGION", "us-central1"),
            "gcp_service_account": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
            "gcp_storage_bucket": os.getenv("GCP_STORAGE_BUCKET", ""),
            "gcp_sql_instance": os.getenv("GCP_SQL_INSTANCE", ""),
            "gcp_redis_instance": os.getenv("GCP_REDIS_INSTANCE", ""),
            "gcp_cloud_functions": True,
            "gcp_monitoring": True,
            "gcp_iam": True
        }
    
    def _get_azure_config(self) -> Dict[str, Any]:
        """Azure-specific configuration"""
        return {
            "azure_subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID", ""),
            "azure_tenant_id": os.getenv("AZURE_TENANT_ID", ""),
            "azure_client_id": os.getenv("AZURE_CLIENT_ID", ""),
            "azure_client_secret": os.getenv("AZURE_CLIENT_SECRET", ""),
            "azure_resource_group": os.getenv("AZURE_RESOURCE_GROUP", ""),
            "azure_location": os.getenv("AZURE_LOCATION", "westus2"),
            "azure_storage_account": os.getenv("AZURE_STORAGE_ACCOUNT", ""),
            "azure_sql_server": os.getenv("AZURE_SQL_SERVER", ""),
            "azure_redis_cache": os.getenv("AZURE_REDIS_CACHE", ""),
            "azure_functions": True,
            "azure_monitor": True,
            "azure_ad": True
        }
    
    def _init_database_config(self) -> DatabaseConfig:
        """Initialize database configuration"""
        return DatabaseConfig(
            url=self.config.get("database_url", "sqlite:///./data/gastric_adci.db"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            echo=self.config.get("debug", False),
            backup_enabled=self.config.get("backup_enabled", True),
            encryption_at_rest=True,
            connection_timeout=int(os.getenv("DB_TIMEOUT", "30"))
        )
    
    def _init_p2p_config(self) -> P2PConfig:
        """Initialize P2P configuration"""
        return P2PConfig(
            enabled=self.mode == DeploymentMode.P2P,
            peer_discovery=os.getenv("PEER_DISCOVERY", "gun"),
            bootstrap_nodes=os.getenv("BOOTSTRAP_NODES", "").split(",") if os.getenv("BOOTSTRAP_NODES") else [],
            port=int(os.getenv("P2P_PORT", "8765")),
            sync_interval=int(os.getenv("SYNC_INTERVAL", "30")),
            real_time_sync=True,
            conflict_resolution=os.getenv("CONFLICT_RESOLUTION", "last_write_wins"),
            data_types=['cases', 'decisions', 'education', 'feedback', 'insights']
        )
    
    def _init_cloud_config(self) -> CloudConfig:
        """Initialize cloud configuration"""
        provider = self._detect_cloud_provider()
        
        config = CloudConfig(
            provider=provider,
            region=os.getenv("CLOUD_REGION", ""),
            storage_bucket=os.getenv("STORAGE_BUCKET", ""),
            database_url=self.config.get("database_url", ""),
            redis_url=self.config.get("redis_url"),
            monitoring_enabled=True,
            auto_scaling=True,
            load_balancer=True,
            backup_retention_days=int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
            disaster_recovery=True
        )
        
        # Set provider-specific configs
        if provider == CloudProvider.AWS:
            config.aws_config = {k: v for k, v in self.config.items() if k.startswith('aws_')}
        elif provider == CloudProvider.GCP:
            config.gcp_config = {k: v for k, v in self.config.items() if k.startswith('gcp_')}
        elif provider == CloudProvider.AZURE:
            config.azure_config = {k: v for k, v in self.config.items() if k.startswith('azure_')}
        
        return config
    
    def _init_security_config(self) -> SecurityConfig:
        """Initialize security configuration"""
        return SecurityConfig(
            encryption_enabled=os.getenv("ENCRYPTION_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("AUTH_REQUIRED", "true").lower() == "true",
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024))),
            allowed_file_types=['.pdf', '.txt', '.json', '.csv', '.xlsx', '.dcm', '.dicom'],
            hipaa_compliance=True,
            audit_logging=True,
            data_anonymization=True
        )
    
    def _init_collaboration_config(self) -> CollaborationConfig:
        """Initialize collaboration configuration"""
        return CollaborationConfig(
            real_time_updates=self.config.get("real_time_updates", True),
            data_sharing_enabled=self.config.get("collaboration_features", False),
            feedback_collection=True,
            insight_sharing=True,
            automatic_sync=self.mode in [DeploymentMode.P2P, DeploymentMode.MULTICLOUD],
            conflict_resolution=os.getenv("CONFLICT_RESOLUTION", "merge"),
            version_control=True
        )
    
    # Public API Methods
    def get_config(self) -> Dict[str, Any]:
        """Get complete configuration"""
        return self.config
    
    def get_mode(self) -> DeploymentMode:
        """Get current deployment mode"""
        return self.mode
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get configuration for web frontend"""
        return {
            'environment': self.mode.value,
            'environment_display': self._get_environment_display_name(),
            'api_base_url': self._get_api_base_url(),
            'p2p_enabled': self.p2p.enabled,
            'cloud_provider': self.cloud.provider.value,
            'features': {
                'real_time_updates': self.collaboration.real_time_updates,
                'data_sharing': self.collaboration.data_sharing_enabled,
                'feedback_collection': self.collaboration.feedback_collection,
                'insight_sharing': self.collaboration.insight_sharing,
                'offline_support': self.config.get('offline_support', True),
                'analytics': self.config.get('analytics_enabled', False),
                'ml_insights': self.config.get('ml_insights', False),
                'collaboration': self.config.get('collaboration_features', False)
            }
        }
    
    def _get_environment_display_name(self) -> str:
        """Get display name for current environment"""
        if self.mode == DeploymentMode.LOCAL:
            return "Local Development"
        elif self.mode == DeploymentMode.P2P:
            return "P2P Collaborative Network"
        else:  # MULTICLOUD
            provider = self.cloud.provider.value
            return f"Cloud ({provider.upper()})" if provider != 'none' else "Multi-Cloud"
    
    def _get_api_base_url(self) -> str:
        """Get API base URL for current environment"""
        if self.mode == DeploymentMode.LOCAL:
            port = self.config['port']
            return f"http://localhost:{port}/api/v1"
        elif self.mode == DeploymentMode.P2P:
            return "/api/v1"  # Relative URL for P2P
        else:  # MULTICLOUD
            return os.getenv('API_BASE_URL', '/api/v1')
    
    def save_config(self, file_path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        path = Path(file_path) if file_path else self.config_path
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare config for serialization
        serializable_config = {
            'mode': self.mode.value,
            'config': self.config,
            'database': {
                'url': self.database.url,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
                'echo': self.database.echo,
                'backup_enabled': self.database.backup_enabled,
                'encryption_at_rest': self.database.encryption_at_rest,
                'connection_timeout': self.database.connection_timeout
            },
            'p2p': {
                'enabled': self.p2p.enabled,
                'peer_discovery': self.p2p.peer_discovery,
                'bootstrap_nodes': self.p2p.bootstrap_nodes,
                'port': self.p2p.port,
                'sync_interval': self.p2p.sync_interval,
                'real_time_sync': self.p2p.real_time_sync,
                'conflict_resolution': self.p2p.conflict_resolution,
                'data_types': self.p2p.data_types
            },
            'cloud': {
                'provider': self.cloud.provider.value,
                'region': self.cloud.region,
                'storage_bucket': self.cloud.storage_bucket,
                'database_url': self.cloud.database_url,
                'redis_url': self.cloud.redis_url,
                'monitoring_enabled': self.cloud.monitoring_enabled,
                'auto_scaling': self.cloud.auto_scaling,
                'load_balancer': self.cloud.load_balancer,
                'backup_retention_days': self.cloud.backup_retention_days,
                'disaster_recovery': self.cloud.disaster_recovery
            }
        }
        
        with open(path, 'w') as f:
            json.dump(serializable_config, f, indent=2)
    
    def validate_config(self) -> List[str]:
        """Validate current configuration and return any issues"""
        issues = []
        
        # Validate based on deployment mode
        if self.mode == DeploymentMode.P2P:
            if not self.p2p.enabled:
                issues.append("P2P mode selected but P2P is not enabled")
            if not self.p2p.bootstrap_nodes and self.p2p.peer_discovery != "gun":
                issues.append("P2P mode requires bootstrap nodes or GUN discovery")
        
        elif self.mode == DeploymentMode.MULTICLOUD:
            if self.cloud.provider == CloudProvider.NONE:
                issues.append("Multicloud mode selected but no cloud provider configured")
            if not self.cloud.database_url:
                issues.append("Cloud mode requires database URL")
        
        # Validate security settings
        if self.security.auth_required and not self.security.encryption_enabled:
            issues.append("Authentication is required but encryption is disabled")
        
        # Validate database configuration
        if not self.database.url:
            issues.append("Database URL is required")
        
        return issues
    
    def update_mode(self, new_mode: DeploymentMode) -> None:
        """Update deployment mode and reconfigure"""
        self.mode = new_mode
        self.config = self._load_config()
        
        # Reinitialize components
        self.database = self._init_database_config()
        self.p2p = self._init_p2p_config()
        self.cloud = self._init_cloud_config()
        self.security = self._init_security_config()
        self.collaboration = self._init_collaboration_config()
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.mode == DeploymentMode.LOCAL and self.config.get('debug', False)
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.mode == DeploymentMode.MULTICLOUD
    
    def supports_collaboration(self) -> bool:
        """Check if current mode supports collaboration features"""
        return self.mode in [DeploymentMode.P2P, DeploymentMode.MULTICLOUD]
    
    def supports_real_time(self) -> bool:
        """Check if current mode supports real-time features"""
        return self.collaboration.real_time_updates and self.supports_collaboration()
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information for monitoring and debugging"""
        return {
            'mode': self.mode.value,
            'environment_display': self._get_environment_display_name(),
            'version': self.config.get('version', 'unknown'),
            'debug': self.config.get('debug', False),
            'features': {
                'p2p_enabled': self.p2p.enabled,
                'cloud_provider': self.cloud.provider.value,
                'collaboration': self.supports_collaboration(),
                'real_time': self.supports_real_time(),
                'monitoring': self.cloud.monitoring_enabled if self.mode == DeploymentMode.MULTICLOUD else False
            },
            'validation_issues': self.validate_config()
        }


# Global configuration instance
_environment_config = None


def get_environment_config(config_path: Optional[str] = None) -> EnvironmentConfig:
    """Get global environment configuration instance"""
    global _environment_config
    if _environment_config is None:
        _environment_config = EnvironmentConfig(config_path)
    return _environment_config


def reset_environment_config():
    """Reset global configuration instance for testing purposes"""
    global _environment_config
    _environment_config = None


def get_current_mode() -> DeploymentMode:
    """Get current deployment mode"""
    return get_environment_config().get_mode()


def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    return get_environment_config().get_config()


def get_web_config() -> Dict[str, Any]:
    """Get configuration for web frontend"""
    return get_environment_config().get_web_config()


def is_local_mode() -> bool:
    """Check if running in local mode"""
    return get_current_mode() == DeploymentMode.LOCAL


def is_p2p_mode() -> bool:
    """Check if running in P2P mode"""
    return get_current_mode() == DeploymentMode.P2P


def is_cloud_mode() -> bool:
    """Check if running in cloud mode"""
    return get_current_mode() == DeploymentMode.MULTICLOUD
