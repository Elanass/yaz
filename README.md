# Gastric ADCI Platform

## Overview
The Gastric ADCI (Adaptive Decision Confidence Index) Platform provides clinicians with evidence-based decision support for gastric cancer treatment planning. The platform uses advanced statistical analysis, precision medicine algorithms, and evidence synthesis to provide personalized treatment recommendations with confidence intervals. Previously based on Markov chain simulations, the platform now employs more robust statistical methods including Cox regression, logistic regression, and Random Forest models for improved prediction accuracy and clinical interpretability.

## Features

### Core Features
- **Adaptive Decision Confidence Index (ADCI)**: Structured decision framework with confidence scoring
- **Statistical Analysis**: Both retrospective (Cox & Logistic Regression) and prospective (Random Forest, RL) models
- **Evidence Synthesis**: Automated literature review and protocol integration
- **HIPAA/GDPR Compliant**: End-to-end encryption and comprehensive audit logging

### Key Components
- **Decision Support Engine**: Evidence-based gastric cancer treatment recommendations
- **Precision Medicine Framework**: Patient-specific risk stratification
- **Statistical Analysis Module**: Advanced analytics for outcome prediction
- **Progressive Web App**: Healthcare-grade, offline-capable interface

## Getting Started

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)
- PostgreSQL 14+ (production) or SQLite (development)

### Installation

#### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/gastric-adci-platform.git
cd gastric-adci-platform

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d
```

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

### Project Structure
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

## Statistical Analysis Module

### Retrospective Analysis
The retrospective analysis module provides tools for analyzing historical data:

- **Cox Proportional Hazards Regression**: For time-to-event outcomes (survival analysis)
  - Identifies prognostic factors and their effect sizes
  - Calculates hazard ratios with confidence intervals
  - Provides concordance and likelihood ratio tests

- **Logistic Regression**: For binary outcomes
  - Estimates probability of outcomes based on predictors
  - Calculates odds ratios with confidence intervals
  - Provides model performance metrics (AUC, accuracy)

### Prospective Analysis
The prospective analysis module provides predictive modeling for future outcomes:

- **Random Forest**: Ensemble machine learning for outcome prediction
  - Handles complex non-linear relationships
  - Provides feature importance rankings
  - Robust to noise and outliers

- **Reinforcement Learning**: Adaptive decision-making framework (experimental)
  - Learns optimal strategies from outcomes
  - Adapts to changing patient characteristics
  - Balances exploration and exploitation

## Recent Changes

### Version 2.0.0 (July 2025)
- **Removed Markov Chain Simulation**: Replaced with more robust statistical analysis modules
- **Added Retrospective Analysis**: Cox & Logistic Regression models with clinical interpretation
- **Added Prospective Analysis**: Random Forest models and RL framework stub
- **Enhanced User Interface**: Added new analysis pages with interactive forms
- **Improved API**: New endpoints for statistical analysis with comprehensive documentation
- **Extended Testing**: Added unit and integration tests for analysis modules

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

## License
This project is licensed under the AGPL-3.0 License - see the LICENSE file for details.

## Acknowledgements
- Gastric Oncology Research Consortium
- World Health Organization Guidelines
- Healthcare Interoperability Standards Organization
