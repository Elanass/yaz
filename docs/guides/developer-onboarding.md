# Developer Onboarding Guide

Welcome to the Surgify development team! This guide will help you get up and running with the codebase and development environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Codebase Overview](#codebase-overview)
4. [Development Workflow](#development-workflow)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Quality Standards](#code-quality-standards)
7. [API Development](#api-development)
8. [Frontend Development](#frontend-development)
9. [Database Development](#database-development)
10. [Deployment Process](#deployment-process)
11. [Resources and Support](#resources-and-support)

## Prerequisites

### Required Software
- **Python 3.11+**: Primary development language
- **Node.js 18+**: For frontend tooling
- **Git**: Version control
- **Docker & Docker Compose**: Container development
- **PostgreSQL**: Database (can use Docker)
- **Redis**: Caching (can use Docker)
- **VS Code**: Recommended IDE with extensions

### Recommended VS Code Extensions
```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension ms-python.mypy-type-checker
code --install-extension ms-toolsai.jupyter
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
```

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **CPU**: 4 cores recommended

## Development Environment Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/surgifyai/yaz.git
cd yaz

# Set up your Git configuration
git config user.name "Your Name"
git config user.email "your.email@company.com"
```

### 2. Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
make setup

# Copy environment template
cp .env.example .env

# Install pre-commit hooks
make install-hooks
```

### 3. Environment Configuration

Edit `.env` file for development:

```bash
# Development settings
YAZ_ENV=development
YAZ_DEBUG=true
YAZ_SECRET_KEY=dev-secret-key-change-in-production
YAZ_HOST=localhost
YAZ_PORT=6379

# Database (using Docker)
DATABASE_URL=postgresql://surgify:surgify@localhost:5432/surgify_dev

# Cache (using Docker)
REDIS_URL=redis://localhost:6379/0

# Feature flags for development
FEATURE_AI_ANALYTICS=true
FEATURE_TEAM_NOTIFICATIONS=true
FEATURE_ADVANCED_CHARTS=true
FEATURE_FILE_UPLOADS=true
FEATURE_DEBUG_TOOLBAR=true

# Development logging
LOG_LEVEL=DEBUG
LOG_FORMAT=human

# API Keys (get from team lead)
OPENAI_API_KEY=your-openai-key-here
```

### 4. Start Development Environment

```bash
# Option 1: Use Docker for services only
make docker-services  # Starts PostgreSQL and Redis only
make dev              # Starts the application locally

# Option 2: Full Docker development
make docker-dev       # Starts all services in Docker

# Option 3: Local development
make db-init          # Initialize local database
make dev              # Start development server
```

### 5. Verify Setup

```bash
# Run tests to verify everything works
make test

# Check code quality
make lint
make typecheck

# Verify the application is running
curl http://localhost:6379/health
```

## Codebase Overview

### Project Structure

```
src/surgify/
├── api/                    # FastAPI API endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── cases.py           # Case management endpoints
│   ├── analytics.py       # Analytics and metrics endpoints
│   └── team.py            # Team and collaboration endpoints
├── core/                   # Core business logic
│   ├── config/            # Configuration management
│   ├── services/          # Business services
│   └── middleware.py      # Custom middleware
├── domain/                 # Domain models and entities
│   ├── models.py          # Pydantic models
│   └── entities.py        # Business entities
├── services/               # Application services
│   ├── case_service.py    # Case management service
│   ├── analytics_service.py # Analytics service
│   ├── notification_service.py # Notification service
│   └── auth_service.py    # Authentication service
├── database/               # Database layer
│   ├── models/            # SQLAlchemy models
│   ├── repositories/      # Repository pattern
│   └── migrations/        # Alembic migrations
├── utils/                  # Shared utilities
│   ├── cache.py           # Caching utilities
│   ├── exceptions.py      # Custom exceptions
│   └── pagination.py     # Pagination helpers
└── ui/web/                # Web interface
    ├── templates/         # Jinja2 templates
    ├── static/           # CSS, JS, images
    └── components/       # Reusable components
```

### Architecture Patterns

#### Clean Architecture
- **Domain Layer**: Core business entities and rules
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: External services and frameworks
- **Interface Layer**: API endpoints and UI components

#### Repository Pattern
```python
# Example repository usage
from src.surgify.database.repositories import CaseRepository

async def get_cases_by_status(status: str):
    repo = CaseRepository()
    return await repo.find_by_status(status)
```

#### Service Layer Pattern
```python
# Example service usage
from src.surgify.services import CaseService

async def create_case(case_data: dict):
    service = CaseService()
    return await service.create_case(case_data)
```

## Development Workflow

### 1. Branch Strategy

We follow **Git Flow** with the following branches:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/`: New features (`feature/case-management`)
- `hotfix/`: Critical production fixes (`hotfix/security-patch`)
- `release/`: Release preparation (`release/v2.1.0`)

### 2. Feature Development Workflow

```bash
# 1. Start with latest develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/new-feature-name

# 3. Make your changes
# ... code changes ...

# 4. Run tests and quality checks
make test
make lint
make typecheck
make security

# 5. Commit your changes
git add .
git commit -m "feat: add new feature description"

# 6. Push and create PR
git push origin feature/new-feature-name
# Create pull request via GitHub
```

### 3. Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

# Types:
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: adding or updating tests
chore: maintenance tasks

# Examples:
git commit -m "feat(api): add case export endpoint"
git commit -m "fix(auth): resolve JWT token expiration issue"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(cases): add integration tests for case creation"
```

### 4. Pull Request Guidelines

#### PR Template Checklist
- [ ] **Clear Description**: What does this PR do and why?
- [ ] **Tests Added**: All new functionality has tests
- [ ] **Tests Passing**: All existing tests still pass
- [ ] **Code Quality**: Linting and type checking pass
- [ ] **Security**: Security scan passes
- [ ] **Documentation**: Updated relevant documentation
- [ ] **Breaking Changes**: None or clearly documented
- [ ] **Database Changes**: Migration scripts included if needed

#### PR Review Process
1. **Automated Checks**: CI pipeline must pass
2. **Code Review**: At least one team member review
3. **Testing**: Manual testing for UI changes
4. **Security Review**: For security-related changes
5. **Approval**: Required before merging

## Testing Guidelines

### Testing Strategy

We maintain comprehensive test coverage across multiple levels:

- **Unit Tests**: Individual functions and classes
- **Integration Tests**: Multiple components working together
- **API Tests**: Endpoint behavior and contracts
- **End-to-End Tests**: Complete user workflows

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-api          # API endpoint tests only

# Run tests with coverage
make test-coverage

# Run specific test file
pytest tests/api/test_cases.py -v

# Run specific test function
pytest tests/api/test_cases.py::test_create_case -v
```

### Writing Tests

#### Unit Test Example
```python
# tests/unit/test_case_service.py
import pytest
from src.surgify.services.case_service import CaseService
from src.surgify.domain.models import CaseCreate

@pytest.mark.asyncio
async def test_create_case():
    """Test case creation service."""
    service = CaseService()
    case_data = CaseCreate(
        title="Test Case",
        patient_id="P001",
        status="planned"
    )
    
    case = await service.create_case(case_data)
    
    assert case.title == "Test Case"
    assert case.patient_id == "P001"
    assert case.status == "planned"
```

#### API Test Example
```python
# tests/api/test_cases.py
import pytest
from fastapi.testclient import TestClient
from src.surgify.app import app

client = TestClient(app)

def test_create_case_endpoint():
    """Test case creation endpoint."""
    case_data = {
        "title": "Test Case",
        "patient_id": "P001",
        "status": "planned"
    }
    
    response = client.post("/api/v1/cases/", json=case_data)
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Case"
```

#### Integration Test Example
```python
# tests/integration/test_case_workflow.py
import pytest
from tests.helpers import create_test_user, create_test_case

@pytest.mark.asyncio
async def test_complete_case_workflow():
    """Test complete case management workflow."""
    # Create user
    user = await create_test_user()
    
    # Create case
    case = await create_test_case(user_id=user.id)
    assert case.status == "planned"
    
    # Update case status
    updated_case = await case_service.update_status(case.id, "active")
    assert updated_case.status == "active"
    
    # Complete case
    completed_case = await case_service.complete_case(case.id)
    assert completed_case.status == "completed"
```

### Test Data and Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.surgify.database.models import User, Case

@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # ... setup test database
    yield session
    # ... cleanup

@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    return user
```

## Code Quality Standards

### Code Formatting and Linting

```bash
# Format code with Black and isort
make format

# Run linting checks
make lint

# Type checking with MyPy
make typecheck

# Security scanning with Bandit
make security

# Run all quality checks
make quality
```

### Code Style Guidelines

#### Python Style
- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Google-style docstrings
- **Line Length**: 88 characters (Black default)
- **Imports**: Organized with isort

```python
from typing import List, Optional
from datetime import datetime

async def get_cases_by_status(
    status: str,
    limit: int = 10,
    offset: int = 0
) -> List[Case]:
    """Get cases filtered by status.
    
    Args:
        status: Case status to filter by
        limit: Maximum number of cases to return
        offset: Number of cases to skip
        
    Returns:
        List of cases matching the status
        
    Raises:
        ValueError: If status is invalid
    """
    if status not in ["planned", "active", "completed"]:
        raise ValueError(f"Invalid status: {status}")
    
    # Implementation here
    return cases
```

#### Error Handling
```python
from src.surgify.utils.exceptions import CaseNotFoundError, ValidationError

async def get_case_by_id(case_id: int) -> Case:
    """Get case by ID with proper error handling."""
    try:
        case = await case_repository.find_by_id(case_id)
        if not case:
            raise CaseNotFoundError(f"Case with ID {case_id} not found")
        return case
    except DatabaseError as e:
        logger.error(f"Database error getting case {case_id}: {e}")
        raise ServiceError("Failed to retrieve case")
```

#### Logging
```python
import logging
from src.surgify.core.logging import get_logger

logger = get_logger(__name__)

async def process_case(case_id: int) -> None:
    """Process case with proper logging."""
    logger.info(f"Starting case processing for case {case_id}")
    
    try:
        case = await get_case_by_id(case_id)
        logger.debug(f"Retrieved case: {case.title}")
        
        # Process case
        await case_service.process(case)
        
        logger.info(f"Successfully processed case {case_id}")
    except Exception as e:
        logger.error(f"Failed to process case {case_id}: {e}", exc_info=True)
        raise
```

## API Development

### FastAPI Best Practices

#### Endpoint Structure
```python
from fastapi import APIRouter, Depends, HTTPException, status
from src.surgify.domain.models import CaseResponse, CaseCreate
from src.surgify.services.case_service import CaseService
from src.surgify.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    current_user: User = Depends(get_current_user),
    case_service: CaseService = Depends()
) -> CaseResponse:
    """Create a new case."""
    try:
        case = await case_service.create_case(case_data, user_id=current_user.id)
        return CaseResponse.from_orm(case)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

#### Pydantic Models
```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class CaseBase(BaseModel):
    """Base case model."""
    title: str = Field(..., min_length=1, max_length=200)
    patient_id: str = Field(..., regex=r"^P\d{6}$")
    description: Optional[str] = Field(None, max_length=1000)

class CaseCreate(CaseBase):
    """Case creation model."""
    status: str = Field(default="planned")
    
    @validator("status")
    def validate_status(cls, v):
        if v not in ["planned", "active", "completed", "cancelled"]:
            raise ValueError("Invalid status")
        return v

class CaseResponse(CaseBase):
    """Case response model."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

#### Authentication and Authorization
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from src.surgify.services.auth_service import AuthService

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    auth_service: AuthService = Depends()
) -> User:
    """Get current authenticated user."""
    try:
        user = await auth_service.get_user_from_token(token.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### API Documentation

- **Swagger UI**: Available at `/docs` in development
- **ReDoc**: Available at `/redoc` in development
- **OpenAPI Schema**: Available at `/openapi.json`

#### Documenting Endpoints
```python
@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Get case by ID",
    description="Retrieve a specific case by its ID",
    responses={
        200: {"description": "Case found and returned"},
        404: {"description": "Case not found"},
        403: {"description": "Access denied"}
    }
)
async def get_case(case_id: int) -> CaseResponse:
    """Get a specific case by ID.
    
    This endpoint retrieves a case by its unique identifier.
    The user must have permission to view the case.
    """
    # Implementation here
```

## Frontend Development

### Technology Stack
- **htmx**: For dynamic HTML interactions
- **Tailwind CSS**: Utility-first CSS framework
- **Alpine.js**: Lightweight JavaScript framework
- **Vanilla JavaScript**: For custom interactions

### Template Structure
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Surgify{% endblock %}</title>
    <link href="{{ url_for('static', path='/css/main.css') }}" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="h-full bg-gray-50">
    <div id="app" class="h-full">
        {% include "components/navbar.html" %}
        
        <main class="flex-1">
            {% block content %}{% endblock %}
        </main>
        
        {% include "components/footer.html" %}
    </div>
    
    <script src="{{ url_for('static', path='/js/app.js') }}"></script>
</body>
</html>
```

### htmx Patterns
```html
<!-- Dynamic form submission -->
<form hx-post="/api/v1/cases/" 
      hx-target="#case-list" 
      hx-swap="afterbegin"
      class="space-y-4">
    <input type="text" name="title" placeholder="Case title" required>
    <button type="submit" class="btn btn-primary">Create Case</button>
</form>

<!-- Live search -->
<input type="search" 
       name="q" 
       hx-get="/api/v1/cases/search" 
       hx-target="#search-results"
       hx-trigger="keyup changed delay:300ms"
       placeholder="Search cases...">

<!-- Infinite scroll -->
<div hx-get="/api/v1/cases?page=2" 
     hx-trigger="revealed" 
     hx-swap="afterend">
    Loading more cases...
</div>
```

### JavaScript Organization
```javascript
// static/js/app.js
class SurgifyApp {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeComponents();
    }
    
    setupEventListeners() {
        // htmx event listeners
        document.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.successful) {
                this.showSuccessMessage('Operation completed successfully');
            }
        });
    }
    
    showSuccessMessage(message) {
        // Toast notification implementation
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SurgifyApp();
});
```

## Database Development

### Database Schema

We use SQLAlchemy for ORM and Alembic for migrations.

#### Model Definition
```python
# src/surgify/database/models/case.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.surgify.database.base import Base

class Case(Base):
    """Case model."""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    patient_id = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="planned", index=True)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cases")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
```

#### Repository Pattern
```python
# src/surgify/database/repositories/case_repository.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.surgify.database.models import Case
from src.surgify.database.repositories.base import BaseRepository

class CaseRepository(BaseRepository[Case]):
    """Case repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Case, session)
    
    async def find_by_status(self, status: str, limit: int = 10) -> List[Case]:
        """Find cases by status."""
        stmt = select(Case).where(Case.status == status).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_user_and_status(
        self, 
        user_id: int, 
        status: str
    ) -> List[Case]:
        """Find cases by user and status."""
        stmt = select(Case).where(
            and_(Case.user_id == user_id, Case.status == status)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

### Database Migrations

#### Creating Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add case notes table"

# Review the generated migration file
# Edit if necessary

# Apply migration
alembic upgrade head
```

#### Migration Example
```python
# migrations/versions/001_add_case_notes.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add case notes table."""
    op.create_table(
        'case_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_case_notes_case_id', 'case_notes', ['case_id'])

def downgrade():
    """Remove case notes table."""
    op.drop_index('ix_case_notes_case_id', table_name='case_notes')
    op.drop_table('case_notes')
```

## Deployment Process

### Development Deployment
```bash
# Deploy to development environment
make deploy-dev

# Check deployment status
make status-dev

# View logs
make logs-dev
```

### Staging Deployment
```bash
# Deploy to staging
git checkout develop
git pull origin develop
make deploy-staging

# Run smoke tests
make test-staging

# Check metrics
make metrics-staging
```

### Production Deployment
```bash
# Create release branch
git checkout -b release/v2.1.0
git push origin release/v2.1.0

# Create pull request to main
# After approval and merge:

git checkout main
git pull origin main
make deploy-prod

# Monitor deployment
make monitor-prod
```

## Resources and Support

### Documentation
- **API Documentation**: `/docs` endpoint
- **Architecture Documentation**: `docs/architecture/`
- **Deployment Guide**: `docs/deployment/`
- **Troubleshooting**: `docs/troubleshooting/`

### Development Tools
- **Database GUI**: pgAdmin or DBeaver for PostgreSQL
- **API Testing**: Postman or Thunder Client (VS Code)
- **Redis GUI**: RedisInsight for cache inspection
- **Log Aggregation**: Local ELK stack for log analysis

### Learning Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **htmx Documentation**: https://htmx.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs

### Team Communication
- **Slack Channels**:
  - `#development`: General development discussions
  - `#code-review`: Code review discussions
  - `#deployment`: Deployment notifications
  - `#help`: Technical help and questions

### Support Contacts
- **Tech Lead**: tech-lead@surgifyai.com
- **DevOps Team**: devops@surgifyai.com
- **Product Manager**: product@surgifyai.com

### Getting Help

1. **Check Documentation**: Start with this guide and API docs
2. **Search Existing Issues**: GitHub issues and internal wiki
3. **Ask the Team**: Slack channels or team meetings
4. **Create an Issue**: For bugs or feature requests
5. **Pair Programming**: Schedule time with senior developers

### First Week Tasks

#### Days 1-2: Environment Setup
- [ ] Set up development environment
- [ ] Run all tests successfully
- [ ] Deploy to local development
- [ ] Complete codebase walkthrough

#### Days 3-4: Small Contributions
- [ ] Fix a documentation issue
- [ ] Write a small test
- [ ] Review team member's PR
- [ ] Attend team standup and planning

#### Day 5: First Feature
- [ ] Pick up a small feature ticket
- [ ] Implement with tests
- [ ] Create pull request
- [ ] Address code review feedback

### Code Review Guidelines

#### As a Reviewer
- **Be Kind**: Constructive feedback only
- **Be Specific**: Point out exact issues and suggest solutions
- **Check Tests**: Ensure adequate test coverage
- **Verify Security**: Look for security implications
- **Consider Performance**: Check for performance impacts

#### As an Author
- **Small PRs**: Keep changes focused and small
- **Clear Description**: Explain what and why
- **Test Coverage**: Include comprehensive tests
- **Documentation**: Update relevant documentation
- **Respond Quickly**: Address feedback promptly

---

**Welcome to the Team!** 🎉

We're excited to have you join the Surgify development team. This platform is making a real impact in healthcare, and your contributions will help improve patient outcomes worldwide.

If you have any questions or need help getting started, don't hesitate to reach out to the team. We're here to support you!

---

**Last Updated**: December 2024  
**Version**: 2.0  
**Maintained By**: Development Team
