# Contributing to YAZ Surgery Analytics Platform

Welcome to the YAZ Surgery Analytics Platform! This guide will help you contribute effectively to our healthcare technology project.

## 🏥 Project Overview

The YAZ Surgery Analytics Platform is a comprehensive healthcare solution for:
- **Surgery Analysis**: Gastric surgery outcome prediction and analysis
- **Insurance Integration**: Claims processing and risk assessment
- **Logistics Management**: Healthcare supply chain and resource optimization
- **Reproducible Research**: Ensuring scientific reproducibility in medical research

## 📋 Quick Start Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] Docker and Docker Compose
- [ ] Git configured with your name and email
- [ ] Code editor (VS Code recommended)

### First-Time Setup
```bash
# Clone the repository
git clone <repository-url>
cd yaz

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt

# Install development dependencies
pip install pytest flake8 black isort safety

# Set up pre-commit hooks
cp .git/hooks/pre-push.example .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Run initial setup
./scripts/clean_cache.sh
python3 -m core.utils.license_validator
```

## 🏗️ Development Workflow

### 1. Branch Management
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Create bugfix branch
git checkout -b bugfix/issue-description

# Create hotfix branch (for production issues)
git checkout -b hotfix/critical-fix
```

### 2. Code Development

#### Project Structure
```
├── api/v1/           # API endpoints
├── core/             # Core business logic
│   ├── operators/    # Domain-specific operators
│   ├── services/     # Shared services
│   └── utils/        # Utilities
├── features/         # Feature modules
├── web/              # Web interface
├── data/             # Data storage
├── docs/             # Documentation
└── tests/            # Test suites
```

#### Coding Standards
- **Python**: Follow PEP 8, max line length 120 characters
- **Documentation**: Include docstrings for all functions and classes
- **Type Hints**: Use type annotations for function parameters and returns
- **Error Handling**: Implement proper exception handling
- **Logging**: Use the centralized logging system

#### Example Code Structure
```python
"""
Module for surgery outcome analysis.

This module provides functionality for analyzing gastric surgery outcomes
and predicting patient recovery patterns.
"""
from typing import Dict, List, Optional
from datetime import datetime

from core.services.logger import get_logger
from core.models.surgery_models import SurgeryOutcome

logger = get_logger(__name__)


class SurgeryAnalyzer:
    """Analyzes surgery outcomes and predicts recovery patterns."""
    
    def __init__(self, model_config: Dict[str, Any]):
        """Initialize the surgery analyzer.
        
        Args:
            model_config: Configuration for the analysis model
        """
        self.config = model_config
        logger.info("Surgery analyzer initialized")
    
    def analyze_outcome(self, patient_data: Dict[str, Any]) -> SurgeryOutcome:
        """Analyze surgery outcome for a patient.
        
        Args:
            patient_data: Patient medical data and surgery details
            
        Returns:
            SurgeryOutcome object with analysis results
            
        Raises:
            ValueError: If patient data is invalid
            AnalysisError: If analysis fails
        """
        try:
            # Implementation here
            logger.info(f"Analyzing outcome for patient {patient_data.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
```

### 3. Testing

#### Test Structure
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── fixtures/          # Test data
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=core --cov=features --cov-report=html

# Run specific test file
pytest tests/unit/test_surgery_analyzer.py -v
```

#### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch

from core.operators.specific_purpose.surgery_operations import SurgeryOperationsOperator
from core.models.surgery_models import SurgeryOutcome


class TestSurgeryAnalyzer:
    """Test suite for SurgeryAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        config = {"model_type": "test", "threshold": 0.5}
        return SurgeryAnalyzer(config)
    
    @pytest.fixture
    def sample_patient_data(self):
        """Sample patient data for testing."""
        return {
            "id": "patient_123",
            "age": 45,
            "bmi": 35.2,
            "procedure": "gastric_bypass",
            "comorbidities": ["diabetes", "hypertension"]
        }
    
    def test_analyze_outcome_success(self, analyzer, sample_patient_data):
        """Test successful outcome analysis."""
        result = analyzer.analyze_outcome(sample_patient_data)
        
        assert isinstance(result, SurgeryOutcome)
        assert result.patient_id == "patient_123"
        assert result.risk_score >= 0.0
        assert result.risk_score <= 1.0
    
    def test_analyze_outcome_invalid_data(self, analyzer):
        """Test analysis with invalid patient data."""
        invalid_data = {"invalid": "data"}
        
        with pytest.raises(ValueError):
            analyzer.analyze_outcome(invalid_data)
    
    @patch('core.operators.healthcare.external_api_call')
    def test_analyze_outcome_with_mock(self, mock_api, analyzer, sample_patient_data):
        """Test analysis with mocked external dependencies."""
        mock_api.return_value = {"score": 0.3}
        
        result = analyzer.analyze_outcome(sample_patient_data)
        
        mock_api.assert_called_once()
        assert result.risk_score == 0.3
```

### 4. Documentation

#### Code Documentation
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include comprehensive type annotations
- **Comments**: Explain complex business logic
- **README Updates**: Update README.md for significant changes

#### API Documentation
- **OpenAPI/Swagger**: Automatically generated from FastAPI
- **Examples**: Include request/response examples
- **Error Codes**: Document all possible error responses

### 5. License Compliance

#### Before Adding Dependencies
```bash
# Check license compatibility
python3 -m core.utils.license_validator

# Add to requirements.txt
echo "new-package==1.0.0" >> config/requirements.txt

# Re-validate licenses
python3 -m core.utils.license_validator
```

#### Updating License Documentation
- Update `docs/legal/LICENSE_COMPLIANCE.md`
- Add attributions to `docs/legal/ATTRIBUTIONS.md`
- Ensure compatibility with project license

## 🚀 Deployment Process

### Development Environment
```bash
# Start development server
python3 main.py

# Start with Docker
docker-compose -f deploy/dev/docker-compose.yml up
```

### Production Deployment
```bash
# Clean deployment
./scripts/run_prod_enhanced.sh --clean

# Standard deployment
./scripts/run_prod_enhanced.sh

# Check deployment status
./scripts/run_prod_enhanced.sh --status
```

### Pre-Push Validation
The Git pre-push hook automatically runs:
1. License compliance check
2. Code quality validation
3. Test execution
4. Cache cleanup
5. Security scanning
6. Documentation verification

## 🔧 Operators System

### Adding New Operators

The operators are now organized into two main categories:
- **General Purpose**: Cross-domain operators in `core/operators/general_purpose/`
- **Specific Purpose**: Domain-specific operators in `core/operators/specific_purpose/`

#### Specific Purpose Operators (`core/operators/specific_purpose/`)
```python
class NewSurgeryOperationsOperator:
    """Operator for specific surgery-related functionality."""
    
    def process_surgery_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process surgery data."""
        # Implementation
        pass
```

#### General Purpose Operators (`core/operators/general_purpose/`)
```python
class NewCoreOperationsOperator:
    """Operator for general cross-domain business logic."""
    
    def execute_operation(self, context: Dict[str, Any]) -> Any:
        """Execute business operation."""
        # Implementation
        pass
```

### Operator Registration
Add operators to the appropriate `__init__.py` files:

For specific purpose operators (`core/operators/specific_purpose/__init__.py`):
```python
from .new_surgery_operations import NewSurgeryOperationsOperator

__all__ = [
    'NewSurgeryOperationsOperator',
    # ... other specific operators
]
```

For general purpose operators (`core/operators/general_purpose/__init__.py`):
```python
from .new_core_operations import NewCoreOperationsOperator

__all__ = [
    'NewCoreOperationsOperator',
    # ... other general operators
]
```

Then update the main `core/operators/__init__.py` to import from the new structure.

## 📊 Reproducibility Guidelines

### Dataset Management
```python
from core.reproducibility.manager import ReproducibilityManager

# Register dataset version
manager = ReproducibilityManager()
version = manager.register_dataset_version(
    dataset_name="cohort_2025_q1",
    data=patient_data,
    metadata={
        "source": "hospital_system",
        "collection_date": "2025-01-15",
        "quality_score": 0.95
    }
)

# Record analysis run
run_id = manager.record_analysis_run(
    input_data=patient_data,
    configuration=analysis_config,
    results=analysis_results,
    analyst_id="researcher_001"
)
```

### Configuration Management
- Use consistent configuration schemas
- Version configuration files
- Document parameter changes
- Include environment information

## 🔒 Security Guidelines

### Data Protection
- **Encryption**: All patient data must be encrypted
- **Access Control**: Implement role-based access
- **Audit Logging**: Log all data access
- **Data Minimization**: Only collect necessary data

### Secret Management
```bash
# Never commit secrets to Git
echo "SECRET_KEY=actual_secret" >> .env.local

# Use environment variables
export DB_PASSWORD=$(openssl rand -base64 32)

# Validate before commit
./scripts/security_check.sh
```

## 📈 Performance Guidelines

### Database Optimization
- Use appropriate indexes
- Implement query pagination
- Monitor query performance
- Use connection pooling

### Caching Strategy
- Cache frequently accessed data
- Implement cache invalidation
- Use Redis for session data
- Monitor cache hit rates

### API Performance
- Implement rate limiting
- Use async/await patterns
- Optimize serialization
- Monitor response times

## 🐛 Issue Reporting

### Bug Reports
When reporting bugs, include:
1. **Environment**: OS, Python version, deployment method
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Logs**: Relevant log entries
6. **Screenshots**: If applicable

### Feature Requests
When requesting features:
1. **Use Case**: Why is this needed?
2. **Acceptance Criteria**: How to validate completion
3. **Dependencies**: Any related requirements
4. **Priority**: Business importance

## 📚 Additional Resources

### Documentation
- [API Reference](docs/architecture/API_REFERENCE.md)
- [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT.md)
- [License Compliance](docs/legal/LICENSE_COMPLIANCE.md)

### Tools and Extensions
- **VS Code Extensions**: Python, Docker, GitLens
- **Development Tools**: pytest, black, flake8, mypy
- **Monitoring**: Prometheus, Grafana, LogTail

### Communication
- **Code Reviews**: All PRs require review
- **Documentation**: Update docs with code changes
- **Questions**: Use issue tracker for questions

---

## 🎯 Quality Standards

### Definition of Done
- [ ] Code follows style guidelines
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] License compliance verified
- [ ] Security review completed
- [ ] Performance impact assessed
- [ ] Peer review approved

### Review Checklist
- [ ] Code is readable and maintainable
- [ ] Error handling is appropriate
- [ ] Tests cover edge cases
- [ ] Documentation is accurate
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Backwards compatibility maintained

---

**Thank you for contributing to the YAZ Surgery Analytics Platform!** Your contributions help improve healthcare outcomes through better technology. 🏥✨
