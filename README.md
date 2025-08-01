# Decision Precision in Surgery - Gastric ADCI Platform

A streamlined healthcare application for surgical decision support in gastric cancer treatment, featuring the ADCI (Adaptive Decision Confidence Index) framework and FLOT protocol analysis. Now enhanced with multi-environment deployment and peer-to-peer collaboration capabilities.

## Features

- **Decision Support Engine**: Evidence-based gastric cancer treatment recommendations
- **ADCI Framework**: Structured decision-making with confidence scoring
- **FLOT Protocol Analysis**: Assessment of perioperative chemotherapy effects
- **Statistical Analysis**: Survival analysis (Cox regression) and outcome prediction (Random Forest)
- **Modern Web Interface**: Redesigned Surgify interface with organized layout and functional navigation
- **Multi-Environment Support**: Local, P2P, and Multi-cloud deployment options
- **P2P Collaboration**: Real-time peer-to-peer data sharing and synchronization
- **Offline-First**: Works seamlessly with or without internet connectivity

## Web Interface (Surgify UI)

The web interface has been redesigned for better user experience:

### Layout Structure
- **Header**: Surgify logo and main navigation
- **Hero Section**: Welcome area with key information
- **Navigation Bar**: Horizontal navigation for main sections
- **Main Content**: Primary workspace area
- **Sidebar**: Functional menu for surgical systems
- **Footer**: Bottom navigation with workstation, add case, marketplace, and settings

### Features
- **Events Carousel**: Horizontally scrollable events display
- **Cases Overview**: Scrollable case management interface
- **Surgical Systems Menu**: Organized sidebar navigation for different surgical specialties
- **Responsive Design**: Works across desktop and mobile devices

### Logo Setup
To complete the Surgify branding:

1. Place your logo files in `/web/static/icons/` directory:
   - `logo.svg` or `logo.png` for the main logo
   - `favicon.ico` for browser favicon
   - `apple-touch-icon.png` for mobile app icon

2. See `/web/static/icons/README.md` for detailed logo specifications and requirements.

## Deployment Modes

### 🏠 Local Mode
Standalone operation on local machine for development and isolated use.

### 🔗 P2P Mode
Peer-to-peer decentralized collaboration with real-time data sync and WebRTC connectivity.

### ☁️ Multi-Cloud Mode
Enterprise deployment across AWS, GCP, Azure with auto-scaling and load balancing.

## Quick Start

### Prerequisites
- Python 3.10+
- Git
- Node.js (for P2P mode)

### Automated Setup

Choose your deployment mode and run the corresponding script:

```bash
# Local development
./scripts/setup_local.sh

# P2P collaboration
./scripts/setup_p2p.sh

# Multi-cloud deployment
./scripts/setup_multicloud.sh
```

### Manual Installation

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd yaz
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   ```

4. Set environment mode:
   ```bash
   export GASTRIC_ADCI_ENV=local  # or p2p, multicloud
   ```

5. Initialize database:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   # Development mode
   uvicorn asgi:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   python main.py
   ```

The application will be available at `http://localhost:8000`

### Web Interface Development

The Surgify web interface is built with modern web technologies:

**Frontend Structure:**
- Templates: Located in `/web/templates/` 
- Static assets: Located in `/web/static/`
- Islands: Interactive components in `/web/islands/`
- Components: Reusable UI elements in `/web/components/`

**Key Files:**
- `layout.html`: Main layout template with header, navigation, and footer
- `index.html`: Home page with hero section and case management
- `sidebar.html`: Surgical systems navigation menu
- `layout.css`: Main styling for the interface
- `sidebar-menu.js`: Interactive sidebar functionality

**Development Workflow:**
1. Templates use Jinja2 for server-side rendering
2. Islands provide interactive client-side functionality
3. Static assets are served directly
4. Sidebar menu dynamically loads surgical system content

### Validation

Run the comprehensive validation script to ensure everything is set up correctly:

```bash
python scripts/validate_platform.py
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
├── main.py                 # Application entry point with multi-env support
├── core/                   # Core functionality
│   ├── config/            # Multi-environment configuration
│   ├── models/            # Data models
│   ├── operators/         # System operators (reorganized)
│   │   ├── general_purpose/   # Cross-domain operators
│   │   └── specific_purpose/  # Domain-specific operators (includes P2P)
│   └── services/          # Core services
├── features/              # Feature modules
│   ├── analysis/          # Statistical analysis
│   ├── auth/              # Authentication
│   ├── decisions/         # Decision engines
│   └── protocols/         # Clinical protocols
├── api/                   # REST API endpoints
├── data/                  # Database and migrations
├── web/                   # Web interface (refactored)
│   ├── components/        # FastHTML dynamic components only
│   ├── templates/         # Static HTML templates and partials
│   ├── static/           # CSS, JS (including P2P connector)
│   └── router.py         # Web routing
├── scripts/              # Automation and validation scripts
└── tests/                # Test files
```

## Web Architecture Refactoring

The web layer has been completely refactored for modularity and maintainability:

### 🔧 Separation of Concerns
- **`/web/components/`**: Pure FastHTML dynamic components (Python)
- **`/web/templates/`**: Static HTML templates and partials
- **`/web/static/`**: Client-side assets (CSS, JS, images)

### 🌐 P2P Integration
- **WebRTC connectivity** for real-time peer-to-peer communication
- **Gun.js integration** for decentralized data synchronization
- **Automatic peer discovery** and room management
- **Offline-first architecture** with conflict resolution

## Development

### Operator Architecture

The YAZ platform features a reorganized operator architecture that separates cross-domain functionality from domain-specific operations:

#### General Purpose Operators (`core/operators/general_purpose/`)
- **CoreOperationsOperator**: Essential system operations (logging, configuration, validation)
- **FinancialOperationsOperator**: Financial calculations, billing, cost analysis
- **CommunicationOperationsOperator**: Messaging, notifications, alerts
- **InfrastructureOperationsOperator**: System monitoring, health checks, resource management
- **SecurityOperationsOperator**: Authentication, authorization, encryption
- **MonitoringOperationsOperator**: Performance monitoring, analytics, reporting
- **IntegrationOperationsOperator**: External API integrations and data exchange
- **DataSyncOperationsOperator**: Data synchronization and consistency management

#### Specific Purpose Operators (`core/operators/specific_purpose/`)
- **HealthcareOperationsOperator**: General healthcare operations and standards
- **SurgeryOperationsOperator**: Surgery-specific workflows and protocols
- **PatientManagementOperationsOperator**: Patient lifecycle and care coordination
- **EducationOperationsOperator**: Medical education and training programs
- **HospitalityOperationsOperator**: Patient experience and accommodation services
- **InsuranceOperationsOperator**: Insurance verification and claims processing
- **LogisticsOperationsOperator**: Supply chain and resource logistics
- **P2pSignalingOperator**: WebSocket-based P2P signaling for real-time collaboration

See `core/operators/README.md` for detailed documentation and usage examples.

### Environment Configuration

The platform supports three operational environments:

```python
# Set environment mode
export GASTRIC_ADCI_ENV=local      # Standalone local development
export GASTRIC_ADCI_ENV=p2p        # P2P collaboration mode
export GASTRIC_ADCI_ENV=multicloud # Cloud deployment mode
```

Each environment has specific configurations for database, storage, networking, and features.

### P2P Development

When developing P2P features:

1. **Start P2P mode**: `./scripts/setup_p2p.sh`
2. **Check P2P status**: Visit `/health` endpoint
3. **Monitor peers**: View dashboard for peer connections
4. **Test sync**: Open multiple browser windows to test real-time sync

### Testing and Validation
### Testing and Validation

Run comprehensive platform validation:
```bash
python scripts/validate_platform.py
```

Run specific tests:
```bash
pytest tests/                    # All tests
pytest tests/integration/        # Integration tests only
python -m pytest tests/integration/test_api_endpoints.py -v  # API tests
```

### Code Formatting
```bash
black .
isort .
```

## License

This project is for medical research and educational purposes.

5. Start the development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

6. Access the application:
   - Web interface: http://localhost:8001
   - API documentation: http://localhost:8001/api/docs
   - Health check: http://localhost:8001/health

### Production Deployment

1. Configure environment variables for production:
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

2. Start the production stack:
   ```bash
   docker-compose -f deploy/prod/docker-compose.yml up -d
   ```

3. Access the production application:
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/api/docs (if enabled)

## Architecture

### Backend
- **FastAPI**: High-performance API framework
- **PostgreSQL**: Primary database
- **ElectricsQL**: Offline-first data synchronization
- **IPFS**: Immutable evidence storage

### Frontend
- **FastHTML**: Clean, lightweight templating
- **HTMX**: Modern, reactive UI with minimal JavaScript
- **Gun.js**: Reactive state management

### Deployment
- **Google Cloud Run/GKE**: Scalable, managed deployment
- **Docker**: Containerized for consistent environments

## Detailed Project Description
The Gastric ADCI Platform is a comprehensive decision-support system for gastric oncology surgery, designed to be modular, extensible, and compliant with healthcare regulations (HIPAA, GDPR). It brings together clinical data, advanced analytics, and a responsive PWA to deliver evidence-based recommendations with confidence intervals.

### Precision Decision Engine for Diffuse Gastric Cancer Surgery
- Built on `features/decisions/precision_engine.py`, this engine analyzes patient-specific risk factors for diffuse-type gastric cancer surgeries.
- Integrates the FLOT protocol impact analysis (5-FU, Leucovorin, Oxaliplatin, Docetaxel) from `features/protocols/flot_analyzer.py` to adjust surgical risk and perioperative planning.
- Applies Multi-Criteria Decision Analysis (MCDA) combining adjusted risk scores and confidence intervals to generate `mcda_score` and `confidence_interval` per treatment option.
- Provides real-time confidence scoring algorithms and statistical prediction models (e.g., Random Forest outputs, logistic regression baselines).

### Impact Analyzer Tool
- Implemented in `features/analysis/impact_metrics.py`, the ImpactMetricsAnalyzer computes:
  - Kaplan–Meier survival curves using the `lifelines` library for cohort outcome tracking.
  - Treatment effectiveness metrics (response rates, pre/post comparisons).
  - Quality of Life (QoL) impact assessments from patient survey data.
  - Cost–effectiveness analysis for clinical and economic decision support.

## Security & Compliance

### HIPAA/GDPR Features
- **Encryption**: End-to-end encryption for PHI using industry-standard cryptography
- **Audit Logging**: Comprehensive audit trails for all data access and modifications
- **Access Control**: Role-based access control (RBAC) with fine-grained permissions
- **Data Retention**: Configurable data retention policies
- **Secure Communication**: TLS/SSL for all data transmission

### Security Testing
Run the security test suite:
```bash
python -m pytest tests/security/
```

## Project Structure

The codebase follows a modular architecture with clear separation of concerns:

```
gastric-adci-platform/
├── api/               # API endpoints and routes
│   └── v1/            # API version 1
├── apps/              # Application modules
│   ├── generalservices/  # General utility services
│   ├── parent/        # Parent supervision services
│   ├── specificapps/  # Domain-specific applications
│   └── visioner/      # Vision processing services
├── core/              # Core framework components
│   ├── adapters/      # Integration adapters
│   ├── config/        # Configuration settings
│   ├── managers/      # System managers
│   ├── medical/       # Medical domain logic
│   ├── middleware/    # Request middleware
│   ├── models/        # Data models
│   ├── operators/     # System operators (reorganized architecture)
│   │   ├── general_purpose/   # Cross-domain operators
│   │   │   ├── core_operations.py
│   │   │   ├── financial_operations.py
│   │   │   ├── communication_operations.py
│   │   │   ├── infrastructure_operations.py
│   │   │   ├── security_operations.py
│   │   │   ├── monitoring_operations.py
│   │   │   ├── integration_operations.py
│   │   │   └── data_sync_operations.py
│   │   └── specific_purpose/  # Domain-specific operators
│   │       ├── healthcare_operations.py
│   │       ├── surgery_operations.py
│   │       ├── patient_management_operations.py
│   │       ├── education_operations.py
│   │       ├── hospitality_operations.py
│   │       ├── insurance_operations.py
│   │       └── logistics_operations.py
│   ├── services/      # Core services
│   └── utils/         # Utility functions
├── data/              # Data management
│   ├── database/      # Database scripts
│   ├── migrations/    # Database migrations
│   ├── models/        # Data models
│   ├── repositories/  # Data repositories
│   └── uploads/       # User uploads
├── deploy/            # Deployment configurations
├── documentation/     # Documentation files
├── features/          # Feature modules
│   ├── analysis/      # Data analysis
│   ├── auth/          # Authentication
│   ├── decisions/     # Decision support
│   └── ...            # Other feature modules
├── orchestrator/      # System orchestration
├── scripts/           # Utility scripts
├── tests/             # Test suite
└── web/               # Web interface
    ├── components/    # UI components
    ├── islands/       # Island architecture components
    ├── pages/         # Page templates
    ├── static/        # Static assets
    └── templates/     # HTML templates
```

## API Documentation

### Authentication
```
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### Decision Support
```
POST /api/v1/decisions/analyze
GET /api/v1/decisions/{decision_id}
GET /api/v1/decisions/history
```

### Analysis
```
# Retrospective Analysis
POST /api/v1/analysis/retrospective/cox        # Cox Proportional Hazards Regression
POST /api/v1/analysis/retrospective/logistic   # Logistic Regression

# Prospective Analysis
POST /api/v1/analysis/prospective/random-forest # Train Random Forest model
POST /api/v1/analysis/prospective/predict      # Predict outcomes for a patient
```

## Contributing

### Development Workflow
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `python -m pytest tests/`
4. Format code: `black .` and `isort .`
5. Submit a pull request

### Coding Standards
- Follow PEP 8 style guide
- Write comprehensive docstrings
- Include unit tests for new features
- Maintain minimum 95% test coverage

## License
This project is licensed under the AGPL-3.0 License - see the LICENSE file for details.

## Acknowledgements
- Gastric Oncology Research Consortium
- World Health Organization Guidelines
- Healthcare Interoperability Standards Organization
