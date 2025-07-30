"""
Licensing Manager Module

This module consolidates licensing-related functionality for the Gastric ADCI Platform.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from core.config.platform_config import config
from core.services.logger import get_logger

logger = get_logger("licensing_manager")

class LicensingManager:
    """Handles licensing for components and services"""

    def __init__(self):
        """Initialize the licensing manager"""
        self.licenses = {}
        self.license_file = os.getenv("LICENSE_FILE", "config/licenses.json")
        self.is_initialized = False

    def load_licenses(self):
        """Load licenses from configuration or license file"""
        try:
            # First try to load from environment/config
            self.licenses = config.get("licenses", {})
            
            # If no licenses found, try to load from file
            if not self.licenses and os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    self.licenses = json.load(f)
            
            # Set initialization flag
            self.is_initialized = True
            
            # Log license status
            valid_components = [name for name, details in self.licenses.items() 
                               if self._is_license_valid(details)]
            logger.info(f"Loaded licenses for {len(valid_components)} components")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load licenses: {str(e)}")
            return False
            
    def validate_license(self, component_name: str) -> bool:
        """
        Validate license for a specific component
        
        Args:
            component_name: The name of the component to validate
            
        Returns:
            bool: Whether the component has a valid license
        """
        # If not in production, allow all
        if not config.is_production:
            return True
            
        # If not initialized, try to load licenses
        if not self.is_initialized:
            self.load_licenses()
            
        # Check if component has a license
        if component_name not in self.licenses:
            logger.warning(f"No license found for component: {component_name}")
            return False
            
        # Validate the license
        license_details = self.licenses[component_name]
        is_valid = self._is_license_valid(license_details)
        
        if not is_valid:
            logger.warning(f"Invalid license for component: {component_name}")
            
        return is_valid
        
    def _is_license_valid(self, license_details: Dict[str, Any]) -> bool:
        """
        Check if a license is valid
        
        Args:
            license_details: The license details to check
            
        Returns:
            bool: Whether the license is valid
        """
        # Check if license has required fields
        if not all(key in license_details for key in ['key', 'expiry']):
            return False
            
        # Check if license has expired
        try:
            expiry_date = datetime.fromisoformat(license_details['expiry'])
            if expiry_date < datetime.now():
                return False
        except:
            return False
            
        # Add additional validation as needed
        
        return True

# Create a singleton instance
licensing_manager = LicensingManager()
        logger.info("Licenses loaded: %s", self.licenses)

    def validate_license(self, component: str) -> bool:
        """Validate the license for a given component."""
        license_key = self.licenses.get(component)
        if not license_key:
            logger.error("No license found for component: %s", component)
            return False
        # Add actual validation logic here
        return True

licensing_manager = LicensingManager()
