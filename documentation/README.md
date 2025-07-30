# Decision Precision in Surgery: Gastric ADCI Surgery FLOT Impact

## Overview
The Decision Precision in Surgery platform provides clinicians with evidence-based decision support for gastric cancer treatment planning, with a specific focus on the impact of FLOT protocol on surgical outcomes. The platform includes a dedicated Precision Decision Engine for diffuse-type gastric cancer surgery that integrates FLOT protocol impact analysis, a multi-criteria decision analysis (MCDA) framework, and real-time confidence scoring using the ADCI (Adaptive Decision Confidence Index) methodology. It also features an Impact Analyzer tool that computes Kaplan–Meier survival curves, treatment effectiveness, quality-of-life assessments, and cost–effectiveness metrics. Previously based on Markov chain simulations, the platform now employs more robust statistical methods—including Cox regression, logistic regression, and Random Forest models—for improved prediction accuracy and clinical interpretability.

## Features

### Core Features
- **Adaptive Decision Confidence Index (ADCI)**: Structured decision framework with confidence scoring
- **FLOT Protocol Impact Assessment**: Comprehensive analysis of FLOT protocol impact on surgical outcomes
- **Statistical Analysis**: Both retrospective (Cox & Logistic Regression) and prospective (Random Forest, RL) models
- **Evidence Synthesis**: Automated literature review and protocol integration
- **HIPAA/GDPR Compliant**: End-to-end encryption and comprehensive audit logging

### Key Components
- **Decision Support Engine**: Evidence-based gastric cancer treatment recommendations
- **Precision Surgery Framework**: Patient-specific risk stratification for surgical outcomes
- **FLOT Impact Analysis**: Assessment of perioperative chemotherapy effects on surgical results
- **Statistical Analysis Module**: Advanced analytics for outcome prediction
- **Progressive Web App**: Healthcare-grade, offline-capable interface

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 4GB+ RAM for development environment

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gastric-adci-platform.git
   cd gastric-adci-platform
   ```

2. Start the development environment:
   ```bash
   docker-compose -f deploy/dev/docker-compose.yml up -d
   ```

3. Enter the development container:
   ```bash
   docker-compose -f deploy/dev/docker-compose.yml exec dev bash
   ```

4. Run tests within the container:
   ```bash
   python -m pytest tests/
   ```

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
```
gastric-adci-platform/
├── api/                  # API endpoints
│   └── v1/
│       ├── analysis_retrospective.py  # Retrospective analysis endpoints
│       ├── analysis_prospective.py    # Prospective analysis endpoints
│       └── decisions.py               # Decision support endpoints
├── core/                 # Core framework
│   ├── config/           # Configuration
│   ├── models/           # Shared data models
│   └── utils/            # Utilities
├── features/             # Business logic modules
│   ├── analysis/         # Statistical analysis
│   │   ├── retrospective.py  # Cox & Logistic Regression
│   │   ├── prospective.py    # Random Forest
│   │   └── rl_engine.py      # Reinforcement Learning stub
│   ├── auth/             # Authentication
│   ├── cohorts/          # Cohort management
│   └── decisions/        # Decision support
├── tests/                # Test suite
│   ├── integration/      # Integration tests
│   └── unit/             # Unit tests
└── web/                  # Web interface
    ├── components/       # Reusable UI components
    ├── pages/            # Page templates
    └── static/           # Static assets
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
