"""
Domain Configuration Factory and Manager

This module provides a factory for creating domain-specific configurations
and a manager for handling domain adaptations.
"""

from typing import Dict, Any, List, Optional
import logging

from core.config.domains import DomainType, DomainConfiguration, ComponentType
from core.config.domains.healthcare import HealthcareDomainConfig
from core.config.domains.logistics import LogisticsDomainConfig
from core.config.domains.insurance import InsuranceDomainConfig
from core.config.domains.education import EducationDomainConfig
from core.config.platform_config import config


class DomainConfigurationFactory:
    """Factory for creating domain-specific configurations"""
    
    _domain_configs = {
        DomainType.HEALTHCARE: HealthcareDomainConfig,
        DomainType.LOGISTICS: LogisticsDomainConfig,
        DomainType.INSURANCE: InsuranceDomainConfig,
        DomainType.EDUCATION: EducationDomainConfig
    }
    
    @classmethod
    def create_domain_config(cls, domain_type: DomainType) -> DomainConfiguration:
        """Create a domain-specific configuration"""
        config_class = cls._domain_configs.get(domain_type)
        if not config_class:
            raise ValueError(f"Unsupported domain type: {domain_type}")
        
        return config_class()
    
    @classmethod
    def get_supported_domains(cls) -> List[DomainType]:
        """Get list of supported domain types"""
        return list(cls._domain_configs.keys())
    
    @classmethod
    def register_domain_config(cls, domain_type: DomainType, config_class: type):
        """Register a new domain configuration"""
        cls._domain_configs[domain_type] = config_class


class DomainManager:
    """Manager for domain-specific platform adaptations"""
    
    def __init__(self, domain_type: DomainType):
        self.domain_type = domain_type
        self.domain_config = DomainConfigurationFactory.create_domain_config(domain_type)
        self.logger = logging.getLogger(__name__)
        
        # Load domain-specific overrides from environment
        self._load_environment_overrides()
    
    def _load_environment_overrides(self):
        """Load domain-specific configuration overrides from environment"""
        domain_env_key = f"DOMAIN_{self.domain_type.value.upper()}_CONFIG"
        domain_overrides = getattr(config, domain_env_key.lower(), {})
        
        if domain_overrides:
            self.logger.info(f"Loading {self.domain_type} configuration overrides")
            # Apply overrides to domain configuration
            for component_type, override_config in domain_overrides.items():
                self.domain_config.update_component(
                    ComponentType(component_type), 
                    override_config
                )
    
    def get_component_config(self, component_type: ComponentType) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific component"""
        component = self.domain_config.get_component(component_type)
        return component.config if component else None
    
    def is_component_enabled(self, component_type: ComponentType) -> bool:
        """Check if a component is enabled for this domain"""
        component = self.domain_config.get_component(component_type)
        return component.enabled if component else False
    
    def get_authentication_config(self) -> Dict[str, Any]:
        """Get domain-specific authentication configuration"""
        return self.get_component_config(ComponentType.AUTHENTICATION) or {}
    
    def get_data_model_config(self) -> Dict[str, Any]:
        """Get domain-specific data model configuration"""
        return self.get_component_config(ComponentType.DATA_MODEL) or {}
    
    def get_compliance_config(self) -> Dict[str, Any]:
        """Get domain-specific compliance configuration"""
        return self.get_component_config(ComponentType.COMPLIANCE) or {}
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get domain-specific workflow configuration"""
        return self.get_component_config(ComponentType.WORKFLOW) or {}
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get domain-specific UI configuration"""
        return self.get_component_config(ComponentType.UI_COMPONENTS) or {}
    
    def get_integration_config(self) -> Dict[str, Any]:
        """Get domain-specific integration configuration"""
        return self.get_component_config(ComponentType.INTEGRATIONS) or {}
    
    def get_enabled_components(self) -> List[str]:
        """Get list of enabled component types"""
        enabled_components = self.domain_config.get_enabled_components()
        return [comp.component_type.value for comp in enabled_components]
    
    def adapt_middleware_stack(self) -> List[str]:
        """Get domain-specific middleware stack"""
        base_middleware = ["cors", "security_headers", "request_logging"]
        
        compliance_config = self.get_compliance_config()
        if compliance_config:
            if compliance_config.get("audit_all_access"):
                base_middleware.append("audit_middleware")
            if compliance_config.get("data_protection", {}).get("encryption_at_rest"):
                base_middleware.append("encryption_middleware")
            if self.domain_type == DomainType.HEALTHCARE:
                base_middleware.extend(["hipaa_middleware", "anonymization_middleware"])
            elif self.domain_type == DomainType.LOGISTICS:
                base_middleware.append("tracking_middleware")
            elif self.domain_type == DomainType.INSURANCE:
                base_middleware.append("fraud_detection_middleware")
            elif self.domain_type == DomainType.EDUCATION:
                base_middleware.append("ferpa_middleware")
        
        return base_middleware
    
    def get_required_dependencies(self) -> List[str]:
        """Get list of required dependencies for this domain"""
        dependencies = set()
        
        for component in self.domain_config.get_enabled_components():
            dependencies.update(component.dependencies)
        
        return list(dependencies)
    
    def validate_configuration(self) -> List[str]:
        """Validate domain configuration and return any issues"""
        issues = []
        
        # Check for missing required components
        required_components = [
            ComponentType.AUTHENTICATION,
            ComponentType.DATA_MODEL,
            ComponentType.COMPLIANCE
        ]
        
        for component_type in required_components:
            if not self.is_component_enabled(component_type):
                issues.append(f"Required component {component_type.value} is not enabled")
        
        # Domain-specific validations
        if self.domain_type == DomainType.HEALTHCARE:
            auth_config = self.get_authentication_config()
            if not auth_config.get("compliance_features", {}).get("hipaa_logging"):
                issues.append("HIPAA logging is required for healthcare domain")
        
        elif self.domain_type == DomainType.EDUCATION:
            auth_config = self.get_authentication_config()
            if not auth_config.get("privacy_protection", {}).get("ferpa_compliance"):
                issues.append("FERPA compliance is required for education domain")
        
        return issues
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete domain configuration"""
        return {
            "domain_type": self.domain_type.value,
            "enabled_components": self.get_enabled_components(),
            "component_configs": {
                comp.component_type.value: comp.config
                for comp in self.domain_config.get_enabled_components()
            },
            "middleware_stack": self.adapt_middleware_stack(),
            "required_dependencies": self.get_required_dependencies()
        }


# Global domain manager instance
_domain_manager: Optional[DomainManager] = None


def get_domain_manager(domain_type: Optional[DomainType] = None) -> DomainManager:
    """Get or create domain manager singleton"""
    global _domain_manager
    
    if not _domain_manager:
        # Determine domain type from configuration or default to healthcare
        if not domain_type:
            domain_env = getattr(config, 'domain_type', 'healthcare')
            domain_type = DomainType(domain_env)
        
        _domain_manager = DomainManager(domain_type)
    
    return _domain_manager


def initialize_domain(domain_type: DomainType) -> DomainManager:
    """Initialize the domain manager with specific domain type"""
    global _domain_manager
    _domain_manager = DomainManager(domain_type)
    return _domain_manager


def get_current_domain_type() -> DomainType:
    """Get the current domain type"""
    domain_manager = get_domain_manager()
    return domain_manager.domain_type


def is_healthcare_domain() -> bool:
    """Check if current domain is healthcare"""
    return get_current_domain_type() == DomainType.HEALTHCARE


def is_logistics_domain() -> bool:
    """Check if current domain is logistics"""
    return get_current_domain_type() == DomainType.LOGISTICS


def is_insurance_domain() -> bool:
    """Check if current domain is insurance"""
    return get_current_domain_type() == DomainType.INSURANCE


def is_education_domain() -> bool:
    """Check if current domain is education"""
    return get_current_domain_type() == DomainType.EDUCATION
