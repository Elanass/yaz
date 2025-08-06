"""
Domain-Agnostic Core Module for Surgify Platform

This module provides a unified interface for handling different domains
(surgery, logistics, insurance) by dynamically wiring the appropriate
parsers, models, and deliverable templates.
"""

import importlib
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)


class Domain(str, Enum):
    """Supported domain types"""

    SURGERY = "surgery"
    LOGISTICS = "logistics"
    INSURANCE = "insurance"


class DomainConfig:
    """Configuration for a specific domain"""

    def __init__(self, domain: Domain):
        self.domain = domain
        self.parser_module = f"surgify.core.parsers.{domain.value}_parser"
        self.model_module = f"surgify.core.models.{domain.value}"
        self.template_path = f"templates/{domain.value}"

    def get_parser_class(self):
        """Dynamically import and return the parser class for this domain"""
        try:
            module = importlib.import_module(self.parser_module)
            parser_class_name = f"{self.domain.value.title()}Parser"
            return getattr(module, parser_class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Parser for domain {self.domain} not found: {e}")
            return None

    def get_model_class(self):
        """Dynamically import and return the model class for this domain"""
        try:
            module = importlib.import_module(self.model_module)
            model_class_name = f"{self.domain.value.title()}Model"
            return getattr(module, model_class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Model for domain {self.domain} not found: {e}")
            return None

    def get_template_path(self) -> Path:
        """Return the template path for this domain"""
        return Path(self.template_path)


class DomainAdapter:
    """
    Central adapter that manages domain-specific functionality
    """

    def __init__(self, domain: Domain):
        self.domain = domain
        self.config = DomainConfig(domain)
        self._parser = None
        self._model = None

    @property
    def parser(self):
        """Lazy-load the domain parser"""
        if self._parser is None:
            parser_class = self.config.get_parser_class()
            if parser_class:
                self._parser = parser_class()
            else:
                logger.error(f"No parser available for domain: {self.domain}")
        return self._parser

    @property
    def model(self):
        """Lazy-load the domain model"""
        if self._model is None:
            self._model = self.config.get_model_class()
        return self._model

    def process_data(self, data: Any) -> Dict[str, Any]:
        """Process data using the domain-specific parser"""
        if not self.parser:
            return {"error": f"No parser available for domain: {self.domain}"}

        try:
            return self.parser.parse(data)
        except Exception as e:
            logger.error(f"Error processing data for domain {self.domain}: {e}")
            return {"error": str(e)}

    def generate_deliverable(
        self, data: Dict[str, Any], template_name: str = "default"
    ) -> Dict[str, Any]:
        """Generate a deliverable using domain-specific templates"""
        template_path = self.config.get_template_path() / f"{template_name}.md"

        return {
            "domain": self.domain.value,
            "template_path": str(template_path),
            "data": data,
            "status": "generated",
        }

    def hello_world(self) -> Dict[str, Any]:
        """Simple hello world test for domain verification"""
        return {
            "domain": self.domain.value,
            "message": f"Hello from {self.domain.value} domain!",
            "parser_available": self.parser is not None,
            "model_available": self.model is not None,
            "template_path": str(self.config.get_template_path()),
            "status": "operational",
        }


class DomainRegistry:
    """Registry for managing multiple domain adapters"""

    def __init__(self):
        self._adapters: Dict[Domain, DomainAdapter] = {}
        self._current_domain: Optional[Domain] = None

    def register_domain(self, domain: Domain) -> DomainAdapter:
        """Register a domain adapter"""
        if domain not in self._adapters:
            self._adapters[domain] = DomainAdapter(domain)
            logger.info(f"Registered domain adapter: {domain}")
        return self._adapters[domain]

    def set_current_domain(self, domain: Domain):
        """Set the current active domain"""
        self._current_domain = domain
        if domain not in self._adapters:
            self.register_domain(domain)
        logger.info(f"Set current domain to: {domain}")

    def get_current_adapter(self) -> Optional[DomainAdapter]:
        """Get the adapter for the current domain"""
        if self._current_domain:
            return self._adapters.get(self._current_domain)
        return None

    def get_adapter(self, domain: Domain) -> DomainAdapter:
        """Get a specific domain adapter"""
        if domain not in self._adapters:
            self.register_domain(domain)
        return self._adapters[domain]

    def list_domains(self) -> list[str]:
        """List all registered domains"""
        return [domain.value for domain in self._adapters.keys()]

    def validate_all_domains(self) -> Dict[str, Dict[str, Any]]:
        """Validate all registered domains with hello world test"""
        results = {}
        for domain in Domain:
            adapter = self.get_adapter(domain)
            results[domain.value] = adapter.hello_world()
        return results


# Global domain registry instance
domain_registry = DomainRegistry()

# Initialize all domains by default
for domain in Domain:
    domain_registry.register_domain(domain)


def get_domain_config(domain_name: str) -> Optional[DomainConfig]:
    """Get domain configuration by domain name"""
    try:
        domain = Domain(domain_name.lower())
        return DomainConfig(domain)
    except ValueError:
        logger.error(f"Invalid domain: {domain_name}")
        return None
