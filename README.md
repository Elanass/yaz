# Decision Precision in Surgery - Gastric ADCI Platform

A streamlined healthcare application for surgical decision support in gastric cancer treatment, featuring the ADCI (Adaptive Decision Confidence Index) framework and FLOT protocol analysis.

## Features

- **Decision Support Engine**: Evidence-based gastric cancer treatment recommendations
- **ADCI Framework**: Structured decision-making with confidence scoring
- **FLOT Protocol Analysis**: Assessment of perioperative chemotherapy effects
- **Statistical Analysis**: Survival analysis (Cox regression) and outcome prediction (Random Forest)
- **Modern Web Interface**: Clean, responsive design for clinical use

## Quick Start

### Prerequisites
- Python 3.10+
- Git

### Installation

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

4. Initialize database:
   ```bash
   alembic upgrade head
   ```

5. Start the application:
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:8000`

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
├── main.py                 # Application entry point
├── core/                   # Core functionality
│   ├── config/            # Configuration
│   ├── models/            # Data models
│   └── services/          # Core services
├── features/              # Feature modules
│   ├── analysis/          # Statistical analysis
│   ├── auth/              # Authentication
│   ├── decisions/         # Decision engines
│   └── protocols/         # Clinical protocols
├── api/                   # REST API endpoints
├── data/                  # Database and migrations
├── web/                   # Web interface
└── tests/                 # Test files
```

## Development

### Running Tests
```bash
pytest tests/
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
   cp .env.example .env.prod
   # Edit .env.prod with your production settings
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
│   ├── operators/     # System operators
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
