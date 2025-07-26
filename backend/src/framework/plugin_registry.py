"""
Plugin Registry and Service Manager for Domain-Agnostic Decision Framework
Manages registration, discovery, and lifecycle of decision modules across domains

Features:
- Dynamic module loading and registration
- Domain-specific service discovery
- Health monitoring and auto-recovery
- Plugin versioning and compatibility
- Configuration management per domain
"""

import asyncio
import importlib
import inspect
import json
import os
import time
from typing import Dict, List, Any, Optional, Type, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import structlog

from .decision_module import DecisionModule, DecisionModuleType, DecisionFramework

logger = structlog.get_logger(__name__)

@dataclass
class PluginManifest:
    """Plugin manifest containing metadata and configuration"""
    plugin_id: str
    name: str
    version: str
    domain: str
    module_type: DecisionModuleType
    author: str
    description: str
    dependencies: List[str]
    config_schema: Dict[str, Any]
    entry_point: str
    min_framework_version: str
    tags: List[str]
    
    @classmethod
    def from_file(cls, manifest_path: Path) -> 'PluginManifest':
        """Load plugin manifest from JSON file"""
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            plugin_id=data['plugin_id'],
            name=data['name'],
            version=data['version'],
            domain=data['domain'],
            module_type=DecisionModuleType(data['module_type']),
            author=data['author'],
            description=data['description'],
            dependencies=data.get('dependencies', []),
            config_schema=data.get('config_schema', {}),
            entry_point=data['entry_point'],
            min_framework_version=data.get('min_framework_version', '3.0.0'),
            tags=data.get('tags', [])
        )

@dataclass
class PluginHealth:
    """Plugin health status information"""
    plugin_id: str
    status: str  # healthy, unhealthy, disabled, error
    last_check: datetime
    response_time_ms: float
    error_count: int
    uptime_seconds: float
    memory_usage_mb: float
    
class PluginRegistry:
    """
    Plugin Registry for Domain-Agnostic Decision Framework
    
    Manages:
    - Plugin discovery and loading
    - Service registration and health monitoring
    - Configuration management
    - Dependency resolution
    - Auto-recovery and failover
    """
    
    def __init__(self, framework: DecisionFramework, plugin_dirs: List[Path] = None):
        self.framework = framework
        self.plugin_dirs = plugin_dirs or [Path("plugins"), Path("modules")]
        self.registered_plugins: Dict[str, PluginManifest] = {}
        self.loaded_modules: Dict[str, DecisionModule] = {}
        self.plugin_health: Dict[str, PluginHealth] = {}
        self.domain_configs: Dict[str, Dict[str, Any]] = {}
        self._health_check_interval = 300  # 5 minutes
        self._health_check_task = None
        self._startup_time = time.time()
        
    async def start(self):
        """Start the plugin registry and load plugins"""
        logger.info("Starting Plugin Registry...")
        
        # Discover and load plugins
        await self._discover_plugins()
        await self._load_plugins()
        
        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"Plugin Registry started with {len(self.loaded_modules)} modules")
    
    async def stop(self):
        """Stop the plugin registry and cleanup"""
        logger.info("Stopping Plugin Registry...")
        
        # Stop health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Unload all plugins
        for plugin_id in list(self.loaded_modules.keys()):
            await self._unload_plugin(plugin_id)
        
        logger.info("Plugin Registry stopped")
    
    async def _discover_plugins(self):
        """Discover available plugins in plugin directories"""
        logger.info("Discovering plugins...")
        
        discovered_count = 0
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            # Look for plugin manifests
            for manifest_file in plugin_dir.rglob("plugin.json"):
                try:
                    manifest = PluginManifest.from_file(manifest_file)
                    
                    # Validate manifest
                    if self._validate_manifest(manifest):
                        self.registered_plugins[manifest.plugin_id] = manifest
                        discovered_count += 1
                        logger.info(f"Discovered plugin: {manifest.plugin_id}")
                    else:
                        logger.warning(f"Invalid manifest: {manifest_file}")
                        
                except Exception as e:
                    logger.error(f"Error loading manifest {manifest_file}: {e}")
        
        logger.info(f"Discovered {discovered_count} plugins")
    
    async def _load_plugins(self):
        """Load discovered plugins with dependency resolution"""
        logger.info("Loading plugins...")
        
        # Sort plugins by dependencies
        load_order = self._resolve_dependencies()
        
        loaded_count = 0
        failed_count = 0
        
        for plugin_id in load_order:
            try:
                await self._load_plugin(plugin_id)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
                failed_count += 1
        
        logger.info(f"Loaded {loaded_count} plugins, {failed_count} failed")
    
    async def _load_plugin(self, plugin_id: str):
        """Load a specific plugin"""
        manifest = self.registered_plugins[plugin_id]
        
        logger.info(f"Loading plugin: {plugin_id}")
        
        # Import the module
        try:
            module_path = manifest.entry_point
            module = importlib.import_module(module_path)
            
            # Find the DecisionModule class
            module_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, DecisionModule) and 
                    obj != DecisionModule):
                    module_class = obj
                    break
            
            if not module_class:
                raise ValueError(f"No DecisionModule class found in {module_path}")
            
            # Load domain configuration
            domain_config = self.domain_configs.get(manifest.domain, {})
            
            # Instantiate the module
            if self._requires_config(module_class):
                instance = module_class(config=domain_config)
            else:
                instance = module_class()
            
            # Register with framework
            self.framework.register_module(instance)
            self.loaded_modules[plugin_id] = instance
            
            # Initialize health tracking
            self.plugin_health[plugin_id] = PluginHealth(
                plugin_id=plugin_id,
                status="healthy",
                last_check=datetime.now(),
                response_time_ms=0.0,
                error_count=0,
                uptime_seconds=0.0,
                memory_usage_mb=0.0
            )
            
            logger.info(f"Successfully loaded plugin: {plugin_id}")
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            raise
    
    async def _unload_plugin(self, plugin_id: str):
        """Unload a specific plugin"""
        if plugin_id in self.loaded_modules:
            module = self.loaded_modules[plugin_id]
            
            # Unregister from framework
            self.framework.unregister_module(module.module_id)
            
            # Cleanup
            del self.loaded_modules[plugin_id]
            if plugin_id in self.plugin_health:
                del self.plugin_health[plugin_id]
            
            logger.info(f"Unloaded plugin: {plugin_id}")
    
    def _validate_manifest(self, manifest: PluginManifest) -> bool:
        """Validate plugin manifest"""
        
        # Check required fields
        required_fields = ['plugin_id', 'name', 'version', 'domain', 'entry_point']
        for field in required_fields:
            if not getattr(manifest, field):
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check framework version compatibility
        # TODO: Implement version comparison
        
        # Check for conflicts
        if manifest.plugin_id in self.registered_plugins:
            existing = self.registered_plugins[manifest.plugin_id]
            if existing.version != manifest.version:
                logger.warning(f"Version conflict for {manifest.plugin_id}: {existing.version} vs {manifest.version}")
        
        return True
    
    def _resolve_dependencies(self) -> List[str]:
        """Resolve plugin dependencies and return load order"""
        
        # Simple topological sort for dependency resolution
        load_order = []
        remaining = set(self.registered_plugins.keys())
        
        while remaining:
            # Find plugins with no unresolved dependencies
            ready = []
            for plugin_id in remaining:
                manifest = self.registered_plugins[plugin_id]
                deps_satisfied = all(
                    dep in load_order or dep not in self.registered_plugins
                    for dep in manifest.dependencies
                )
                if deps_satisfied:
                    ready.append(plugin_id)
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning(f"Circular or missing dependencies for: {remaining}")
                ready = list(remaining)  # Load remaining anyway
            
            for plugin_id in ready:
                load_order.append(plugin_id)
                remaining.remove(plugin_id)
        
        return load_order
    
    def _requires_config(self, module_class: Type[DecisionModule]) -> bool:
        """Check if module class requires configuration in constructor"""
        signature = inspect.signature(module_class.__init__)
        return 'config' in signature.parameters
    
    async def _health_check_loop(self):
        """Continuous health monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all loaded plugins"""
        
        for plugin_id, module in self.loaded_modules.items():
            try:
                health = await self._check_plugin_health(plugin_id, module)
                self.plugin_health[plugin_id] = health
                
                # Auto-recovery for unhealthy plugins
                if health.status == "unhealthy" and health.error_count > 5:
                    logger.warning(f"Plugin {plugin_id} unhealthy, attempting reload...")
                    await self._reload_plugin(plugin_id)
                    
            except Exception as e:
                logger.error(f"Health check failed for {plugin_id}: {e}")
                
                # Mark as error status
                if plugin_id in self.plugin_health:
                    self.plugin_health[plugin_id].status = "error"
                    self.plugin_health[plugin_id].error_count += 1
    
    async def _check_plugin_health(self, plugin_id: str, module: DecisionModule) -> PluginHealth:
        """Check health of a specific plugin"""
        
        start_time = time.perf_counter()
        current_time = datetime.now()
        
        try:
            # Test basic functionality with minimal request
            test_params = {"test": True}
            test_context = type('Context', (), {
                'user_id': 'health_check',
                'organization_id': 'system',
                'domain': module.domain,
                'timestamp': current_time
            })()
            
            # Validate parameters (should not throw for test params)
            validation_errors = module.validate_parameters(test_params)
            
            response_time = (time.perf_counter() - start_time) * 1000
            uptime = time.time() - self._startup_time
            
            # Get existing health or create new
            existing_health = self.plugin_health.get(plugin_id)
            error_count = existing_health.error_count if existing_health else 0
            
            status = "healthy"
            if response_time > 1000:  # 1 second threshold
                status = "unhealthy"
            elif len(validation_errors) > 10:  # Too many validation errors
                status = "unhealthy"
            
            return PluginHealth(
                plugin_id=plugin_id,
                status=status,
                last_check=current_time,
                response_time_ms=response_time,
                error_count=error_count,
                uptime_seconds=uptime,
                memory_usage_mb=0.0  # TODO: Implement memory monitoring
            )
            
        except Exception as e:
            logger.error(f"Health check error for {plugin_id}: {e}")
            
            existing_health = self.plugin_health.get(plugin_id)
            error_count = (existing_health.error_count if existing_health else 0) + 1
            
            return PluginHealth(
                plugin_id=plugin_id,
                status="unhealthy",
                last_check=current_time,
                response_time_ms=(time.perf_counter() - start_time) * 1000,
                error_count=error_count,
                uptime_seconds=time.time() - self._startup_time,
                memory_usage_mb=0.0
            )
    
    async def _reload_plugin(self, plugin_id: str):
        """Reload a plugin (unload and load again)"""
        try:
            logger.info(f"Reloading plugin: {plugin_id}")
            
            # Unload
            await self._unload_plugin(plugin_id)
            
            # Small delay
            await asyncio.sleep(1)
            
            # Reload
            await self._load_plugin(plugin_id)
            
            logger.info(f"Successfully reloaded plugin: {plugin_id}")
            
        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_id}: {e}")
    
    # Public API methods
    
    def list_plugins(self, domain: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List plugins with optional filtering"""
        
        plugins = []
        
        for plugin_id, manifest in self.registered_plugins.items():
            if domain and manifest.domain != domain:
                continue
            
            health = self.plugin_health.get(plugin_id)
            if status and health and health.status != status:
                continue
            
            plugin_info = {
                "plugin_id": plugin_id,
                "name": manifest.name,
                "version": manifest.version,
                "domain": manifest.domain,
                "module_type": manifest.module_type.value,
                "author": manifest.author,
                "description": manifest.description,
                "tags": manifest.tags,
                "loaded": plugin_id in self.loaded_modules,
                "health": health.__dict__ if health else None
            }
            
            plugins.append(plugin_info)
        
        return plugins
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific plugin"""
        
        if plugin_id not in self.registered_plugins:
            return None
        
        manifest = self.registered_plugins[plugin_id]
        health = self.plugin_health.get(plugin_id)
        module = self.loaded_modules.get(plugin_id)
        
        return {
            "manifest": manifest.__dict__,
            "health": health.__dict__ if health else None,
            "loaded": plugin_id in self.loaded_modules,
            "module_info": module.get_performance_metrics() if module else None
        }
    
    def get_domain_plugins(self, domain: str) -> List[str]:
        """Get all plugin IDs for a specific domain"""
        return [
            plugin_id for plugin_id, manifest in self.registered_plugins.items()
            if manifest.domain == domain
        ]
    
    def get_healthy_plugins(self) -> List[str]:
        """Get all healthy plugin IDs"""
        return [
            plugin_id for plugin_id, health in self.plugin_health.items()
            if health.status == "healthy"
        ]
    
    async def reload_domain(self, domain: str):
        """Reload all plugins for a specific domain"""
        domain_plugins = self.get_domain_plugins(domain)
        
        for plugin_id in domain_plugins:
            if plugin_id in self.loaded_modules:
                await self._reload_plugin(plugin_id)
    
    def set_domain_config(self, domain: str, config: Dict[str, Any]):
        """Set configuration for a domain"""
        self.domain_configs[domain] = config
        logger.info(f"Updated configuration for domain: {domain}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        
        total_plugins = len(self.registered_plugins)
        loaded_plugins = len(self.loaded_modules)
        healthy_plugins = len([h for h in self.plugin_health.values() if h.status == "healthy"])
        
        domains = set(m.domain for m in self.registered_plugins.values())
        
        return {
            "total_plugins": total_plugins,
            "loaded_plugins": loaded_plugins,
            "healthy_plugins": healthy_plugins,
            "unhealthy_plugins": loaded_plugins - healthy_plugins,
            "load_success_rate": loaded_plugins / max(total_plugins, 1),
            "health_success_rate": healthy_plugins / max(loaded_plugins, 1),
            "domains": list(domains),
            "uptime_seconds": time.time() - self._startup_time,
            "last_health_check": max(
                (h.last_check for h in self.plugin_health.values()),
                default=datetime.now()
            ).isoformat()
        }

class ServiceDiscovery:
    """
    Service Discovery for cross-domain module integration
    Enables modules to find and interact with services from other domains
    """
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.service_cache: Dict[str, List[str]] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = 0
    
    def find_services(
        self, 
        module_type: DecisionModuleType, 
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """Find services matching criteria"""
        
        self._refresh_cache_if_needed()
        
        matching_plugins = []
        
        for plugin_id, manifest in self.registry.registered_plugins.items():
            # Check if loaded and healthy
            if (plugin_id not in self.registry.loaded_modules or
                plugin_id not in self.registry.plugin_health or
                self.registry.plugin_health[plugin_id].status != "healthy"):
                continue
            
            # Check module type
            if manifest.module_type != module_type:
                continue
            
            # Check domain
            if domain and manifest.domain != domain:
                continue
            
            # Check tags
            if tags and not any(tag in manifest.tags for tag in tags):
                continue
            
            matching_plugins.append(plugin_id)
        
        return matching_plugins
    
    def find_diagnostic_services(self, domain: Optional[str] = None) -> List[str]:
        """Find diagnostic services"""
        return self.find_services(DecisionModuleType.DIAGNOSTIC, domain)
    
    def find_therapeutic_services(self, domain: Optional[str] = None) -> List[str]:
        """Find therapeutic services"""
        return self.find_services(DecisionModuleType.THERAPEUTIC, domain)
    
    def find_procedural_services(self, domain: Optional[str] = None) -> List[str]:
        """Find procedural services"""
        return self.find_services(DecisionModuleType.PROCEDURAL, domain)
    
    def get_service_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get service information"""
        return self.registry.get_plugin_info(plugin_id)
    
    def _refresh_cache_if_needed(self):
        """Refresh service cache if TTL expired"""
        current_time = time.time()
        if current_time - self.last_cache_update > self.cache_ttl:
            self.service_cache.clear()
            self.last_cache_update = current_time

# Global registry instance (will be initialized by main application)
plugin_registry: Optional[PluginRegistry] = None
