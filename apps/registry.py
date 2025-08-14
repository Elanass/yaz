"""
App Registry for YAZ Platform
Maps app names to their build functions and provides centralized app management.
"""

from typing import Dict, Callable, List
from fastapi import FastAPI
import importlib


# Registry mapping app name -> module:function
APPS = {
    "core": "apps.core.app:build_app",
    "surge": "apps.surge.app:build_app", 
    "move": "apps.move.app:build_app",
    "clinica": "apps.clinica.app:build_app",
    "educa": "apps.educa.app:build_app",
    "insura": "apps.insura.app:build_app",
}


def get_available_apps() -> List[str]:
    """Get list of available app names"""
    return list(APPS.keys())


def get_app_info(app_name: str) -> Dict[str, str]:
    """Get information about an app"""
    app_configs = {
        "core": {
            "name": "Core Platform",
            "description": "Core YAZ platform services and management",
            "version": "2.0.0",
            "type": "internal"
        },
        "surge": {
            "name": "Surgery Analytics",
            "description": "Advanced surgical case management and analytics",
            "version": "1.0.0", 
            "type": "external"
        },
        "move": {
            "name": "Logistics Management",
            "description": "Medical logistics and supply chain management",
            "version": "1.0.0",
            "type": "external"
        },
        "clinica": {
            "name": "Integrated Clinical Care",
            "description": "Comprehensive clinical care experience",
            "version": "1.0.0",
            "type": "internal"
        },
        "educa": {
            "name": "Medical Education",
            "description": "Medical education and training platform",
            "version": "1.0.0",
            "type": "internal"
        },
        "insura": {
            "name": "Insurance Management", 
            "description": "Healthcare insurance and billing management",
            "version": "1.0.0",
            "type": "internal"
        }
    }
    return app_configs.get(app_name, {
        "name": app_name.title(),
        "description": f"{app_name.title()} application",
        "version": "1.0.0",
        "type": "unknown"
    })


def build_app(app_name: str) -> FastAPI:
    """
    Build and return a FastAPI app instance for the given app name.
    
    Args:
        app_name: Name of the app to build
        
    Returns:
        FastAPI instance for the app
        
    Raises:
        ValueError: If app_name is not registered
        ImportError: If app module cannot be imported
    """
    if app_name not in APPS:
        raise ValueError(f"App '{app_name}' not found in registry. Available apps: {list(APPS.keys())}")
    
    module_path = APPS[app_name]
    module_name, function_name = module_path.split(":")
    
    try:
        module = importlib.import_module(module_name)
        build_function = getattr(module, function_name)
        return build_function()
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}' for app '{app_name}': {e}")
    except AttributeError as e:
        raise ImportError(f"Function '{function_name}' not found in module '{module_name}' for app '{app_name}': {e}")


def get_all_apps() -> Dict[str, FastAPI]:
    """
    Build all available apps and return them as a dictionary.
    
    Returns:
        Dictionary mapping app names to FastAPI instances
    """
    apps = {}
    for app_name in APPS.keys():
        try:
            apps[app_name] = build_app(app_name)
        except Exception as e:
            print(f"Warning: Could not build app '{app_name}': {e}")
            # Create a minimal fallback app
            fallback_app = FastAPI(title=f"{app_name} (Fallback)", version="1.0.0")
            
            @fallback_app.get("/")
            async def fallback_root():
                return {
                    "app": app_name,
                    "status": "error",
                    "message": f"App failed to load: {str(e)}"
                }
            
            apps[app_name] = fallback_app
    
    return apps
