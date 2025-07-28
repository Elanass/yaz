"""
Domain Configuration System

This module provides domain-specific configurations for adapting the platform
to different industries: Healthcare, Logistics, Insurance, Education.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DomainType(str, Enum):
    """Supported domain types"""
    HEALTHCARE = "healthcare"
    LOGISTICS = "logistics"
    INSURANCE = "insurance"
    EDUCATION = "education"


class ComponentType(str, Enum):
    """Platform component types"""
    AUTHENTICATION = "authentication"
    DATA_MODEL = "data_model"
    WORKFLOW = "workflow"
    DECISION_ENGINE = "decision_engine"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"
    UI_COMPONENTS = "ui_components"
    INTEGRATIONS = "integrations"


class DomainComponent(BaseModel):
    """Base configuration for domain-specific components"""
    
    component_type: ComponentType
    enabled: bool = True
    priority: int = Field(default=1, ge=1, le=10)
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DomainConfiguration(ABC):
    """Abstract base class for domain configurations"""
    
    def __init__(self, domain_type: DomainType):
        self.domain_type = domain_type
        self.components: Dict[str, DomainComponent] = {}
        self._initialize_components()
    
    @abstractmethod
    def _initialize_components(self):
        """Initialize domain-specific components"""
        pass
    
    def get_component(self, component_type: ComponentType) -> Optional[DomainComponent]:
        """Get a specific component configuration"""
        return self.components.get(component_type.value)
    
    def get_enabled_components(self) -> List[DomainComponent]:
        """Get all enabled components sorted by priority"""
        enabled = [comp for comp in self.components.values() if comp.enabled]
        return sorted(enabled, key=lambda x: x.priority)
    
    def update_component(self, component_type: ComponentType, config: Dict[str, Any]):
        """Update component configuration"""
        if component_type.value in self.components:
            self.components[component_type.value].config.update(config)
    
    def disable_component(self, component_type: ComponentType):
        """Disable a component"""
        if component_type.value in self.components:
            self.components[component_type.value].enabled = False
    
    def enable_component(self, component_type: ComponentType):
        """Enable a component"""
        if component_type.value in self.components:
            self.components[component_type.value].enabled = True
