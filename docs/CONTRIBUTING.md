# Contributing to Surgify Platform

Welcome to the Surgify Platform! This guide will help you contribute effectively to our advanced surgery analytics platform with AI-powered decision support.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Working with Live Production](#working-with-live-production)
- [Branch Management](#branch-management)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Code Quality Standards](#code-quality-standards)
- [Canary Deployment Process](#canary-deployment-process)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Node.js 18+ (for n8n workflows)
- Git
- kubectl (for Kubernetes deployments)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/surgify.git
   cd surgify
   ```

2. **Set up development environment**
   ```bash
   # Install Python dependencies
   pip install -e ".[dev]"
   
   # Set up git hooks
   ./scripts/setup-git-hooks.sh
   
   # Start development services
   make dev-setup
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Initialize database**
   ```bash
   alembic upgrade head
   python data/load_data.py --sample
   ```

5. **Start development server**
   ```bash
   make dev
   ```

### Development Container

For a consistent development environment, use the provided dev container:

```bash
# Using VS Code Dev Containers
code .  # Open in VS Code, then "Reopen in Container"

# Or using Docker directly
docker-compose -f docker-compose.dev.yml up
```

## Working with Live Production

### Safe Development Practices

**🚨 IMPORTANT**: Always ensure your development work doesn't impact the live production system.

1. **Use Local Development Database**
   ```bash
   # Never connect to production database directly
   export DATABASE_URL="postgresql://localhost:5432/surgify_dev"
   ```

2. **Separate API Keys and Credentials**
   ```bash
   # Use development-specific credentials
   export OPENAI_API_KEY="your-dev-api-key"
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/dev-channel"
   ```

3. **Development vs Production URLs**
   ```bash
   # Development
   SURGIFY_BASE_URL="http://localhost:8000"
   
   # Production (read-only for monitoring)
   PRODUCTION_API_URL="https://api.surgify.com"
   ```

### Production Monitoring

Monitor production health while developing:

```bash
# Check production status
make prod-status

# Monitor production logs (read-only)
make prod-logs

# Run production health checks
make prod-health-check
```

## Branch Management

### Branch Naming Convention

Follow this naming convention for all branches:

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical production fixes
- `release/version` - Release preparation
- `canary-YYYYMMDD-ID` - Canary deployments
- `docs/description` - Documentation updates
- `test/description` - Test improvements
- `refactor/description` - Code refactoring

### Examples

```bash
# Good branch names
git checkout -b feature/ai-summarization-api
git checkout -b bugfix/sync-conflict-resolution
git checkout -b hotfix/security-vulnerability-fix
git checkout -b canary-20250805-ai-improvements

# Avoid
git checkout -b fix-stuff
git checkout -b my-changes
git checkout -b temp-branch
```

### Branch Lifecycle

1. **Feature Branches**
   ```bash
   # Create from develop
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature
   
   # Work on feature
   git add .
   git commit -m "feat: implement new feature"
   
   # Push and create PR
   git push origin feature/new-feature
   ```

2. **Canary Branches**
   ```bash
   # Create canary from develop/main
   git checkout develop
   git checkout -b canary-$(date +%Y%m%d)-feature-name
   
   # Deploy to canary environment (automatic via CI/CD)
   git push origin canary-$(date +%Y%m%d)-feature-name
   ```

## Development Workflow

### 1. Daily Development

```bash
# Start your day
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature

# Make changes, write tests
# Run local tests
make test

# Commit with conventional format
git commit -m "feat(api): add new endpoint for case management"

# Push and create PR
git push origin feature/your-feature
```

### 2. Pre-commit Checks

Our git hooks automatically run:
- Code formatting (black)
- Linting (flake8)
- Type checking (mypy)
- Unit tests
- Security scans

```bash
# To run manually
make lint
make test
make security-check

# Format code
make format
```

### 3. Integration Testing

```bash
# Run all tests
make test-all

# Run specific test types
make test-unit
make test-integration
make test-canary

# Run tests with coverage
make test-cov
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/          # Unit tests for individual components
├── integration/   # Integration tests for workflows
├── canary/        # Canary deployment tests
├── fixtures/      # Test data and fixtures
└── conftest.py    # Pytest configuration
```

### Writing Tests

1. **Unit Tests**
   ```python
   # tests/unit/test_ai_service.py
   import pytest
   from src.surgify.api.v1.ai import SummarizeRequest
   
   def test_ai_summarization():
       request = SummarizeRequest(
           case_id="test-123",
           title="Test Case",
           description="Test description"
       )
       # Test implementation
   ```

2. **Integration Tests**
   ```python
   # tests/integration/test_case_workflow.py
   @pytest.mark.integration
   async def test_complete_case_workflow():
       # Test entire workflow from creation to completion
       pass
   ```

3. **Canary Tests**
   ```python
   # tests/canary/test_production_compatibility.py
   @pytest.mark.canary
   async def test_api_compatibility():
       # Test API compatibility with production
       pass
   ```

### Test Data Management

- Use fixtures for reusable test data
- Mock external services (OpenAI, Slack, etc.)
- Never use production data in tests
- Clean up test data after each test

```python
@pytest.fixture
def sample_case_data():
    return {
        "title": "Test Surgery Case",
        "patient_id": "TEST_PATIENT_001",
        "status": "scheduled"
    }
```

## Code Quality Standards

### Python Code Style

- **Formatter**: Black (line length: 88)
- **Linter**: Flake8 with custom rules
- **Type Checker**: MyPy
- **Import Sorter**: isort

```python
# Good Python code example
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..core.services import CaseService


class CaseRequest(BaseModel):
    """Request model for case creation."""
    
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    patient_id: str = Field(..., description="Patient identifier")


@router.post("/cases/", response_model=CaseResponse)
async def create_case(
    request: CaseRequest,
    service: CaseService = Depends(get_case_service)
) -> CaseResponse:
    """Create a new surgical case."""
    try:
        case = await service.create_case(request)
        return case
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **API Documentation**: Automatic via FastAPI and Pydantic
- **Code Comments**: Explain WHY, not WHAT

```python
def calculate_risk_score(patient_data: Dict[str, Any]) -> float:
    """
    Calculate surgical risk score based on patient data.
    
    Uses machine learning model to assess multiple risk factors
    including age, comorbidities, and surgical complexity.
    
    Args:
        patient_data: Dictionary containing patient information
        
    Returns:
        Risk score between 0.0 (low risk) and 1.0 (high risk)
        
    Raises:
        ValueError: If required patient data is missing
    """
    # Implementation here
```

### Error Handling

```python
# Good error handling
try:
    result = await external_service.call()
except ServiceUnavailableError as e:
    logger.warning(f"External service unavailable: {e}")
    # Implement fallback logic
    result = fallback_handler()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=500, 
        detail="Internal server error"
    )
```

## Canary Deployment Process

### Overview

Our canary deployment process allows safe testing of new features in production-like environment before full rollout.

### Canary Workflow

1. **Create Canary Branch**
   ```bash
   git checkout develop
   git checkout -b canary-$(date +%Y%m%d)-feature-name
   git push origin canary-$(date +%Y%m%d)-feature-name
   ```

2. **Automatic Canary Deployment**
   - CI/CD automatically deploys canary branches to canary environment
   - Runs comprehensive health checks
   - Executes canary-specific tests

3. **Canary Monitoring**
   ```bash
   # Monitor canary deployment
   make canary-status
   
   # View canary metrics
   make canary-metrics
   
   # Run manual canary tests
   make canary-test
   ```

4. **Promotion or Rollback**
   ```bash
   # Promote successful canary to production
   make canary-promote
   
   # Rollback failed canary
   make canary-rollback
   ```

### Canary Test Categories

1. **Health Checks** - Basic service health
2. **Functionality Tests** - Core feature validation
3. **Performance Tests** - Response time and throughput
4. **Compatibility Tests** - API compatibility with production
5. **Integration Tests** - External service integration

### Canary Metrics

Monitor these key metrics during canary deployment:

- **Response Time**: < 2000ms (95th percentile)
- **Error Rate**: < 1%
- **Success Rate**: > 99%
- **Database Performance**: Connection pool, query times
- **External Service Calls**: Success rates, timeouts

### Canary Decision Criteria

**Promote to Production** if:
- All canary tests pass
- Error rate < 1% for 30 minutes
- No critical alerts
- Performance within acceptable thresholds
- Manual review approval

**Rollback** if:
- Error rate > 5%
- Critical functionality broken
- Performance degradation > 50%
- External service integration failures

## API Documentation

### OpenAPI/Swagger

- API documentation is automatically generated
- Access at: `http://localhost:8000/docs`
- Production docs: `https://api.surgify.com/docs`

### Documentation Best Practices

1. **Endpoint Documentation**
   ```python
   @router.post(
       "/cases/",
       response_model=CaseResponse,
       summary="Create surgical case",
       description="Create a new surgical case with AI-powered analysis",
       tags=["Cases"],
       responses={
           201: {"description": "Case created successfully"},
           400: {"description": "Invalid case data"},
           500: {"description": "Internal server error"}
       }
   )
   ```

2. **Model Documentation**
   ```python
   class CaseRequest(BaseModel):
       """Request model for creating a surgical case."""
       
       title: str = Field(
           ..., 
           description="Case title",
           example="Emergency Appendectomy"
       )
       priority: CasePriority = Field(
           default=CasePriority.MEDIUM,
           description="Case priority level"
       )
   ```

### API Versioning

- Use path versioning: `/api/v1/`, `/api/v2/`
- Maintain backward compatibility for at least 2 versions
- Deprecation notices in headers and documentation

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database status
   make db-status
   
   # Reset database
   make db-reset
   
   # Run migrations
   alembic upgrade head
   ```

2. **Docker Issues**
   ```bash
   # Rebuild containers
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Test Failures**
   ```bash
   # Run tests with verbose output
   pytest -v --tb=long
   
   # Run specific test
   pytest tests/unit/test_specific.py::test_function -v
   
   # Debug test with pdb
   pytest --pdb
   ```

4. **Git Hook Issues**
   ```bash
   # Reinstall git hooks
   ./scripts/setup-git-hooks.sh
   
   # Bypass hooks (emergency only)
   git commit --no-verify
   ```

### Performance Debugging

```bash
# Profile application startup
python -m cProfile -o profile.stats src/surgify/main.py

# Memory profiling
memory_profiler python src/surgify/main.py

# Database query analysis
make db-query-analysis
```

### Getting Help

1. **Check Documentation**
   - API docs at `/docs`
   - Architecture docs in `docs/architecture/`
   - Component docs in `docs/components/`

2. **Search Issues**
   - Check GitHub issues for similar problems
   - Search team Slack channels

3. **Create Issue**
   - Use issue templates
   - Include environment details
   - Provide reproducible steps

4. **Ask for Help**
   - Team Slack: `#surgify-dev`
   - Code review: Tag relevant team members
   - Pair programming: Schedule session

## Code Review Guidelines

### Creating Pull Requests

1. **PR Title**: Use conventional commit format
   ```
   feat(api): add AI summarization endpoint
   fix(sync): resolve CRDT merge conflicts
   docs: update API documentation
   ```

2. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

3. **Review Requirements**
   - At least 2 approvals for production changes
   - 1 approval for feature branches
   - All CI checks must pass
   - No merge conflicts

### Review Checklist

**Code Quality**
- [ ] Code is readable and well-documented
- [ ] No code duplication
- [ ] Error handling is appropriate
- [ ] Performance considerations addressed

**Testing**
- [ ] Adequate test coverage
- [ ] Tests are meaningful and not brittle
- [ ] Edge cases considered

**Security**
- [ ] No sensitive data in code
- [ ] Input validation implemented
- [ ] Authentication/authorization correct

**Architecture**
- [ ] Follows established patterns
- [ ] Proper separation of concerns
- [ ] Database changes are backward compatible

## Release Process

### Version Management

- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Release Branches**: `release/v2.1.0`
- **Tags**: `v2.1.0`

### Release Checklist

1. **Pre-release**
   - [ ] All features complete and tested
   - [ ] Documentation updated
   - [ ] Canary deployment successful
   - [ ] Performance benchmarks pass

2. **Release**
   - [ ] Create release branch
   - [ ] Update version numbers
   - [ ] Generate changelog
   - [ ] Create release tag

3. **Post-release**
   - [ ] Deploy to production
   - [ ] Monitor production metrics
   - [ ] Update deployment documentation
   - [ ] Notify stakeholders

### Hotfix Process

For critical production issues:

1. **Create Hotfix Branch**
   ```bash
   git checkout main
   git checkout -b hotfix/critical-issue
   ```

2. **Fast-track Testing**
   - Minimal viable tests
   - Focus on regression prevention
   - Canary deployment optional

3. **Emergency Deployment**
   - Direct to production after approval
   - Monitor closely
   - Prepare rollback plan

---

## Quick Reference

### Useful Commands

```bash
# Development
make dev                    # Start development server
make test                   # Run all tests
make lint                   # Run linting
make format                 # Format code

# Database
make db-reset              # Reset database
make db-migrate            # Run migrations
make db-seed               # Seed test data

# Docker
make docker-build          # Build Docker image
make docker-run            # Run in Docker
make docker-logs           # View Docker logs

# Deployment
make canary-deploy         # Deploy to canary
make canary-status         # Check canary status
make prod-deploy           # Deploy to production
```

### Environment Variables

```bash
# Core
DATABASE_URL="postgresql://..."
REDIS_URL="redis://..."
SECRET_KEY="your-secret-key"

# AI Integration
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4"

# External Services
SLACK_WEBHOOK_URL="https://..."
SMTP_HOST="smtp.gmail.com"

# Development
DEBUG=true
LOG_LEVEL="DEBUG"
```

---

Thank you for contributing to the Surgify Platform! Your work helps improve surgical outcomes and saves lives. 🏥✨
