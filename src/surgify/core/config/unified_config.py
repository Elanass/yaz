"""
Unified configuration for Surgify - imports from main config
This file provides backward compatibility and imports from the main unified config
"""

# Import everything from the main unified config
from core.config.unified_config import (
    UnifiedConfig,
    get_settings,
    reload_settings,
    config,
    get_config_value,
    is_development,
    is_production,
    is_testing
)

# Alias for backward compatibility
SurgifyConfig = UnifiedConfig
