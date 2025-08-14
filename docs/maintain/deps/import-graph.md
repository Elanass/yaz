# Import Graph & Dependency Analysis

**Generated on:** August 10, 2025  
**Total Python files with imports:** 230

## 🔍 Analysis Summary

Based on Ruff and dependency analysis, we have identified several areas for cleanup:

### Critical Issues Found

1. **Import Organization**: Multiple files have module-level imports not at the top
2. **Line Length**: Some files exceed the 88-character limit
3. **Duplicate Structure**: Similar patterns across apps (surgify, surge, move, etc.)

## 🧹 Cleanup Plan

### Phase 1: Import Standardization
- Fix module-level import order issues
- Standardize import groupings (stdlib, third-party, local)
- Remove unused imports

### Phase 2: Shared Module Extraction
- Move common patterns to `src/shared/`
- Create canonical app structure
- Update all imports to use shared components

### Phase 3: Code Quality
- Fix line length issues
- Apply consistent formatting
- Add type hints

## 🏗️ Proposed Canonical Structure

```
src/
├── shared/           # Shared components for all apps
│   ├── core/        # Core functionality (config, logging, cache, db)
│   ├── schemas/     # Pydantic models
│   ├── services/    # Cross-app services
│   ├── http/        # HTTP utilities, error handlers
│   └── ui/          # HTMX partials and components
├── surge/           # Surgery app (canonical structure)
├── move/            # Logistics app
├── insura/          # Insurance app
├── clinica/         # Clinical app
└── educa/           # Education app
```

## 🔧 Next Steps

1. Run formatting fixes with Ruff
2. Create shared module structure
3. Migrate common code to shared/
4. Update imports across all apps
5. Validate and test changes
