"""
Feature flag middleware for toggling features per environment
"""
import os

def is_feature_enabled(feature: str) -> bool:
    # Example: Use env vars or config service
    return os.getenv(f"FEATURE_{feature.upper()}", "false").lower() == "true"
