# YAZ Documentation

## Overview
YAZ is a decision precision platform for surgical procedures, focusing on gastric cancer treatment with ADCI (Adaptive Decision Confidence Index) framework.

## Features

### 1. Analysis Feature
Provides statistical modeling and decision support capabilities.

**Location**: `feature/analysis/`
**Modules**:
- `analysis.py` - Core analysis engine
- `analysis_engine.py` - Advanced analysis processing
- `impact_metrics.py` - Impact calculation utilities
- `surgery_analyzer.py` - Surgery-specific analysis

**Tests**: `test/unit/analysis/` and `test/integration/`
**Documentation**: [Analysis Feature Guide](features/analysis.md)

### 2. Authentication Feature
Handles user authentication and authorization.

**Location**: `feature/auth/`
**Modules**:
- `service.py` - Authentication service

**Tests**: `test/unit/auth/`
**Documentation**: [Authentication Guide](features/auth.md)

### 3. Decisions Feature
Implements decision engines for surgical recommendations.

**Location**: `feature/decisions/`
**Modules**:
- `service.py` - Decision service
- `base_decision_engine.py` - Base decision engine
- `adci_engine.py` - ADCI decision engine
- `precision_engine.py` - Precision decision engine

**Tests**: `test/unit/decisions/`
**Documentation**: [Decisions Guide](features/decisions.md)

### 4. Protocols Feature
Manages clinical protocols and compliance tracking.

**Location**: `feature/protocols/`
**Modules**:
- `service.py` - Protocol service
- `flot_analyzer.py` - FLOT protocol analyzer

**Tests**: `test/unit/protocols/`
**Documentation**: [Protocols Guide](features/protocols.md)

## Architecture

### Directory Structure
```
yaz/
├── feature/           # Feature modules
├── core/             # Core utilities and services
├── api/              # API endpoints
├── test/             # Test suites
├── doc/              # Documentation
├── data/             # Data and models
└── web/              # Web interface
```

### Design Patterns
- **Dependency Injection**: Clean dependency management
- **Repository Pattern**: Data access abstraction
- **Strategy Pattern**: Configurable algorithms
- **Observer Pattern**: Event-driven architecture

## Development

### Prerequisites
- Python 3.10+
- FastAPI
- SQLAlchemy
- Pytest

### Setup
1. Install dependencies: `pip install -r config/requirements.txt`
2. Run tests: `pytest test/`
3. Start development server: `python main.py`

### Testing Strategy
- **Unit Tests**: Individual module testing
- **Integration Tests**: Feature integration testing
- **End-to-End Tests**: Complete workflow testing

## API Documentation
Auto-generated at `/docs` when running the application.

## Contributing
1. Follow the established architecture patterns
2. Write comprehensive tests
3. Update documentation
4. Ensure all imports are properly organized
