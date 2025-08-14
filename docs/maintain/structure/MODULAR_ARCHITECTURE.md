 Yaz Platform Modular Architecture

## Overview

The Yaz platform has been refactored into a truly modular architecture where common functionality is shared across all apps, making each app reproducible and maintainable.

## Directory Structure

```
src/
├── shared/                 # Shared components for all apps
│   ├── core/              # Core shared functionality
│   │   ├── config.py      # Base configuration
│   │   ├── logger.py      # Centralized logging
│   │   ├── cache.py       # Cache management
│   │   ├── database.py    # Database management
│   │   └── exceptions.py  # Common exceptions
│   ├── models/            # Shared data models
│   │   └── __init__.py    # BaseYazModel and common models
│   ├── services/          # Shared services
│   │   ├── auth.py        # Authentication service
│   │   ├── notification.py # Notification service
│   │   └── audit.py       # Audit service
│   └── utils/             # Shared utilities
│       ├── pagination.py  # Pagination helpers
│       └── exceptions.py  # Exception utilities
├── surge/                 # Surgery Analytics App
│   ├── config.py          # Surge-specific config
│   ├── main.py            # Original main (legacy)
│   ├── main_modular.py    # New modular main
│   ├── api/               # Surge API endpoints
│   ├── ui/                # Surge web interface
│   └── models/            # Surge-specific models
├── move/                  # Logistics App
│   ├── config.py          # Move-specific config
│   ├── main.py            # Move main application
│   └── ...
├── insura/                # Insurance App
├── educa/                 # Education App
└── clinica/               # Clinical App
```

## Key Principles

### 1. Shared Foundation
- **Common Core**: All apps use the same core services (auth, cache, database, logging)
- **Consistent Models**: Base models and patterns shared across apps
- **Unified Configuration**: Apps extend a base configuration with app-specific settings

### 2. App Independence
- **Self-Contained**: Each app can run independently
- **Isolated Concerns**: App-specific logic stays within the app
- **Clean Interfaces**: Well-defined boundaries between shared and app-specific code

### 3. Reproducible Patterns
- **Standard Structure**: All apps follow the same structural pattern
- **Consistent APIs**: Similar endpoints and patterns across apps
- **Shared Tooling**: Common CLI tools and deployment scripts

## App Structure Pattern

Each app follows this pattern:

```python
# app/main.py
from shared.core import get_shared_config, setup_logging, CacheManager
from shared.services import AuthService
from .config import get_app_config

def create_app():
    config = get_app_config()
    setup_logging(app_name)
    
    app = FastAPI(...)
    app.state.config = config
    app.state.cache = CacheManager(app_name)
    app.state.auth = AuthService(app_name)
    
    return app
```

## Benefits

### For Developers
- **Faster Development**: Reuse common functionality
- **Consistent Patterns**: Same patterns across all apps
- **Easy Testing**: Shared test utilities and patterns
- **Clear Separation**: Know exactly where code belongs

### For Operations
- **Easier Deployment**: Consistent deployment patterns
- **Better Monitoring**: Unified logging and metrics
- **Simpler Configuration**: Standard configuration approach
- **Scalable Architecture**: Add new apps easily

### For Maintenance
- **Single Source of Truth**: Common functionality in one place
- **Easier Updates**: Update shared components once
- **Better Documentation**: Clear architectural boundaries
- **Reduced Duplication**: No repeated code across apps

## Usage Examples

### Starting Individual Apps

```bash
# Using the universal launcher
./tools/yaz-launcher surge                 # Start Surge app
./tools/yaz-launcher move --port 8001     # Start Move app
./tools/yaz-launcher --list               # List all apps

# Using app-specific methods
cd src/surge && python main_modular.py
cd src/move && python main.py
```

### Development Mode

```bash
# Start all apps for development
./tools/yaz-launcher --all

# Or start individual apps with reload
./tools/yaz-launcher surge --reload
```

### Configuration

Each app can override shared configuration:

```python
# surge/config.py
class SurgeConfig(BaseConfig):
    surgery_types_enabled: list = ["general", "cardiac"]
    ai_analysis_enabled: bool = True
```

### Adding New Apps

1. Create app directory: `src/newapp/`
2. Add configuration: `src/newapp/config.py`
3. Create main application: `src/newapp/main.py`
4. Add to launcher: Update `tools/yaz-launcher`

## Migration Path

### Phase 1: Shared Foundation ✅
- Move common utilities to `shared/`
- Create base configuration and services
- Update imports to use shared components

### Phase 2: App Modularization ✅
- Create modular versions of existing apps
- Implement universal launcher
- Update CLI tools to use shared patterns

### Phase 3: Complete Migration (Next)
- Migrate all apps to modular pattern
- Remove duplicate code
- Update deployment scripts

### Phase 4: Enhancement (Future)
- Add shared monitoring and metrics
- Implement cross-app communication
- Advanced deployment orchestration

## Best Practices

### Do's
- ✅ Use shared components for common functionality
- ✅ Keep app-specific logic in app directories
- ✅ Follow consistent naming conventions
- ✅ Document app-specific configurations
- ✅ Use the universal launcher for development

### Don'ts
- ❌ Don't duplicate shared functionality in apps
- ❌ Don't put app-specific code in shared/
- ❌ Don't create tight coupling between apps
- ❌ Don't ignore the standard patterns
- ❌ Don't skip configuration inheritance

## Testing

### Shared Component Tests
```bash
cd src/shared && python -m pytest tests/
```

### App-Specific Tests
```bash
cd src/surge && python -m pytest tests/
cd src/move && python -m pytest tests/
```

### Integration Tests
```bash
# Test all apps together
./tools/yaz-launcher --all &
python tests/integration/test_all_apps.py
```

## Future Enhancements

1. **Service Mesh**: Auto-discovery and communication between apps
2. **Shared UI Components**: Common web components across apps
3. **Unified API Gateway**: Single entry point for all apps
4. **Cross-App Analytics**: Shared metrics and monitoring
5. **Plugin System**: Dynamic app loading and management

This modular architecture ensures that the Yaz platform is maintainable, scalable, and developer-friendly while maintaining clear separation of concerns.
