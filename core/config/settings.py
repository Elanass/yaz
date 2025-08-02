"""
Settings module - compatibility layer for unified configuration
"""

from .unified_config import PlatformConfig

# Global config instance
config = PlatformConfig()

def get_settings() -> PlatformConfig:
    """Get platform settings"""
    return config

def get_feature_config() -> dict:
    """Get feature configuration"""
    return {
        'analysis': {
            'enabled': True,
            'max_cohort_size': 10000,
            'statistical_significance': 0.05
        },
        'decisions': {
            'enabled': True,
            'adci_threshold': 0.7,
            'confidence_intervals': True
        },
        'protocols': {
            'enabled': True,
            'flot_protocol': True,
            'neo_adjuvant': True
        },
        'auth': {
            'enabled': True,
            'session_timeout': 3600
        }
    }

def get_database_config() -> dict:
    """Get database configuration"""
    return {
        'url': config.database_url,
        'pool_size': 10,
        'echo': config.debug_mode
    }

def get_security_config() -> dict:
    """Get security configuration"""
    return {
        'secret_key': config.secret_key,
        'algorithm': 'HS256',
        'access_token_expire_minutes': 30
    }
