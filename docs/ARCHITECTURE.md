# YAZ Platform - Lean Architecture Overview

## System Structure

YAZ Platform follows a **lean, modular architecture** with clear separation of concerns and minimal overhead.

### Directory Structure

```
/workspaces/yaz/
├── apps/                    # Application modules
│   ├── core/               # Core platform services
│   │   ├── app.py         # FastAPI app builder
│   │   ├── routers/       # API routers (FHIR, forms, etc.)
│   │   ├── static/        # Static assets
│   │   └── templates/     # HTML templates
│   ├── surge/             # Surgery analytics
│   ├── move/              # Medical logistics
│   ├── clinica/           # Clinical operations
│   ├── educa/             # Medical education
│   ├── insura/            # Insurance management
│   └── registry.py        # App registration system
├── config/                # All configuration files
│   ├── alembic.ini       # Database migrations
│   ├── ruff.toml         # Code formatting
│   └── *.yaml            # Other configs
├── data/                  # Data storage
│   ├── logs/             # Application logs
│   ├── uploads/          # File uploads
│   └── *.db              # Databases
├── docs/                  # Documentation
├── infra/                 # Infrastructure utilities
│   ├── monitoring/       # System monitoring
│   ├── encryption.py     # Network security
│   └── *_client.py       # External integrations
├── scripts/               # Operational scripts
├── tests/                 # Test suites
├── main.py               # Platform entry point
├── unified_platform.py   # Unified platform logic
└── pyproject.toml        # Python project config
```

### Request Flow

```mermaid
graph TB
    %% Client Layer
    subgraph "Client Layer"
        PWA[PWA Shell + FastHTML]
        HTMX[HTMX Components]
        React[React Islands]
        Mobile[Mobile Apps]
    end

    %% API Gateway Layer
    subgraph "API Gateway"
        FastAPI[FastAPI Application]
        Middleware[CORS/Auth/Rate Limiting]
        Router[API Router]
    end

    %% Application Layer - Healthcare Domains
    subgraph "Healthcare Domains"
        Surge[Surge - Surgery Analytics]
        Clinica[Clinica - Clinical Ops]
        Educa[Educa - Medical Education]
        Insura[Insura - Insurance]
        Move[Move - Logistics]
    end

    %% Infrastructure Layer - Healthcare Integrations
    subgraph "Healthcare Infrastructure"
        FHIR[FHIR Client]
        Orthanc[Orthanc PACS]
        OHIF[OHIF Viewer]
        SMART[SMART on FHIR]
        Quest[Questionnaire Engine]
    end

    %% External Healthcare Services
    subgraph "External Services"
        Medplum[Medplum FHIR]
        HAPI[HAPI FHIR Server]
        DICOM[DICOM Storage]
        EHR[EHR Systems]
    end

    %% Data Layer
    subgraph "Data Layer"
        DB[(PostgreSQL)]
        Cache[(Redis Cache)]
        Files[(File Storage)]
        Migrations[Alembic Migrations]
    end

    %% Healthcare Applications
    subgraph "Healthcare Modules"
        Surge[Surgery Analytics]
        Clinica[Clinical Operations]
        Educa[Medical Education]
        Insura[Insurance Management]
        Move[Healthcare Logistics]
    end

    %% Flow connections
    PWA --> FastAPI
    HTMX --> FastAPI
    React --> FastAPI
    
    FastAPI --> Middleware
    Middleware --> Router
    Router --> UC
    
    UC --> Auth
    UC --> Validation
    UC --> Entities
    UC --> DomainServices
    
    DomainServices --> Repos
    Repos --> DB
    
    UC --> External
    UC --> Cache
    UC --> Queue
    
    Surge --> UC
    Clinica --> UC
    Educa --> UC
    Insura --> UC
    Move --> UC
```

## Module Dependencies

### Core Modules
- **Domain**: Pure business logic, no external dependencies
- **Application**: Orchestrates domain and infrastructure
- **Infrastructure**: External system adapters (DB, APIs, cache)
- **API**: HTTP interface layer
- **Client**: User interface components

### Healthcare Applications
Each healthcare module follows clean architecture:
- **Entities**: Core business objects
- **Use Cases**: Application-specific business rules
- **Adapters**: Interface implementations
- **Controllers**: HTTP/UI controllers

## Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant UseCase
    participant Domain
    participant Repository
    participant Database

    Client->>API: HTTP Request
    API->>API: Validate Input
    API->>UseCase: Execute Business Logic
    UseCase->>Domain: Apply Business Rules
    UseCase->>Repository: Persist/Fetch Data
    Repository->>Database: SQL Operations
    Database-->>Repository: Data
    Repository-->>UseCase: Domain Objects
    UseCase-->>API: Result
    API-->>Client: HTTP Response
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: ORM with database abstraction
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization
- **Redis**: Caching and session storage

### Frontend
- **FastHTML**: Server-side rendered HTML
- **HTMX**: Dynamic HTML over the wire
- **React**: Islands architecture for complex interactions
- **PWA**: Progressive Web App capabilities

### Database
- **PostgreSQL/CockroachDB**: Primary database
- **SQLite**: Development and testing

### DevOps
- **Podman**: Containerization
- **GitHub Actions**: CI/CD
- **Pre-commit**: Code quality hooks

## Security Architecture

```mermaid
graph LR
    Request[HTTP Request] --> RateLimit[Rate Limiting]
    RateLimit --> CORS[CORS Validation]
    CORS --> Auth[Authentication]
    Auth --> Authz[Authorization]
    Authz --> Validation[Input Validation]
    Validation --> Business[Business Logic]
```

## Data Flow Architecture

```mermaid
graph TD
    Input[User Input] --> Validation[Input Validation]
    Validation --> Command[Command/Query]
    Command --> UseCase[Use Case Layer]
    UseCase --> Domain[Domain Layer]
    Domain --> Events[Domain Events]
    Events --> Handlers[Event Handlers]
    UseCase --> Repository[Repository Layer]
    Repository --> Database[(Database)]
    
    UseCase --> Cache[Cache Layer]
    UseCase --> External[External APIs]
    
    Database --> Repository
    Repository --> UseCase
    UseCase --> Response[Response]
    Response --> Output[User Output]
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance 3]
        DB[(Primary DB)]
        Cache[(Redis Cache)]
        Queue[(Task Queue)]
    end
    
    subgraph "Staging Environment"
        StagingAPI[Staging API]
        StagingDB[(Staging DB)]
        StagingCache[(Staging Cache)]
    end
    
    subgraph "Development Environment"
        DevAPI[Dev API]
        DevDB[(Dev DB)]
        DevCache[(Dev Cache)]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> DB
    API2 --> DB
    API3 --> DB
    
    API1 --> Cache
    API2 --> Cache
    API3 --> Cache
```

## Performance Considerations

### Caching Strategy
- **Application Level**: Redis for session data and frequently accessed objects
- **Database Level**: Query result caching
- **CDN Level**: Static asset caching

### Scalability
- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Database Scaling**: Read replicas for read-heavy operations
- **Async Processing**: Background tasks for heavy operations

### Monitoring
- **Health Checks**: Application and dependency health endpoints
- **Metrics**: Performance metrics collection
- **Logging**: Structured logging with correlation IDs
- **Tracing**: Request tracing for debugging

## Security Measures

### Authentication & Authorization
- JWT tokens for API authentication
- Role-based access control (RBAC)
- Session management

### Data Protection
- Input validation and sanitization
- SQL injection prevention through ORM
- XSS protection
- CSRF protection for forms

### Infrastructure Security
- Container security scanning
- Dependency vulnerability scanning
- Secret management
- Network security (TLS, firewall rules)

## Development Workflow

```mermaid
graph LR
    Dev[Development] --> Commit[Commit]
    Commit --> PreCommit[Pre-commit Hooks]
    PreCommit --> Test[Automated Tests]
    Test --> Build[Build Image]
    Build --> Security[Security Scan]
    Security --> Deploy[Deploy to Staging]
    Deploy --> E2E[E2E Tests]
    E2E --> Prod[Production Deploy]
```

## Quality Gates

### Code Quality
- Type checking with mypy
- Linting with ruff/flake8
- Code formatting with black
- Import sorting with isort

### Security
- Static code analysis with bandit
- Container scanning with trivy
- Dependency scanning with pip-audit
- Secret scanning with gitleaks

### Testing
- Unit tests (>80% coverage)
- Integration tests
- E2E tests
- Performance tests

## Migration Strategy

### Phase 1: Safety Net
- Add comprehensive testing
- Set up CI/CD pipeline
- Add monitoring and logging

### Phase 2: Clean Architecture
- Refactor to layered architecture
- Extract domain logic
- Implement repository pattern

### Phase 3: Performance & Scale
- Add caching layer
- Optimize database queries
- Implement background processing

### Phase 4: Advanced Features
- Add PWA capabilities
- Implement real-time features
- Add advanced monitoring

## Key Architectural Decisions

### ADR-001: Clean Architecture
**Decision**: Adopt clean architecture with clear separation of concerns
**Rationale**: Maintainability, testability, and independence from frameworks
**Consequences**: More complex initially but better long-term maintainability

### ADR-002: FastAPI + FastHTML
**Decision**: Use FastAPI for APIs and FastHTML for server-side rendering
**Rationale**: Type safety, performance, and modern Python ecosystem
**Consequences**: Learning curve but better developer experience

### ADR-003: Repository Pattern
**Decision**: Implement repository pattern for data access
**Rationale**: Database independence and easier testing
**Consequences**: Additional abstraction layer but improved testability

### ADR-004: Event-Driven Architecture
**Decision**: Use domain events for cross-cutting concerns
**Rationale**: Loose coupling and extensibility
**Consequences**: More complex event handling but better modularity
