# Gastric ADCI Platform

A healthcare-grade Progressive Web App (PWA) for gastric oncology-surgery decision support using the Adaptive Decision Confidence Index (ADCI) framework.

## Overview

The Gastric ADCI Platform provides clinicians with evidence-based decision support for gastric cancer treatment planning. The platform uses advanced Markov modeling, precision medicine algorithms, and evidence synthesis to provide personalized treatment recommendations with confidence intervals.

## Key Features

- **Data Ingestion**: Support for retrospective and prospective clinical data
- **Precision Decision Engine**: Personalized treatment recommendations with confidence metrics
- **Markov Chain Simulation**: Advanced disease progression modeling
- **Evidence Synthesis**: Integration with clinical guidelines and research
- **Clinical Workflow Integration**: Seamless integration with clinical workflows
- **HIPAA & GDPR Compliance**: Built-in security and audit features
- **Responsive UI**: Offline-capable Progressive Web App

## Technology Stack

- **Backend**: FastAPI, PostgreSQL, ElectricsQL, IPFS
- **Frontend**: FastHTML, HTMX, Gun.js for reactive state
- **Deployment**: Google Cloud Run/GKE, Docker
- **Compliance**: HIPAA, GDPR with audit trails

## Architecture

The platform follows a modular architecture with the following components:

- **Core**: Base configuration, shared models, and utilities
- **Features**: Modular services for specific domain functionality
  - Data Ingestion Pipeline
  - Markov Simulation Engine
  - Precision Decision Engine
  - Evidence Synthesis Engine
  - Report Generation Service
- **API**: RESTful endpoints with proper validation and documentation
- **Web**: HTMX-powered user interface components
  - Clinical Platform Components
  - Decision Support Interface
  - Evidence Visualization Tools

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Node.js 18+ (for frontend build tools)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gastric-adci-platform.git
   cd gastric-adci-platform
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Build and start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   ```
   http://localhost:8000
   ```

## Development

### Running Tests

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run with coverage
pytest --cov=. tests/
```

### Code Structure

```
├── api/                 # API endpoints
│   └── v1/              # API version 1
├── core/                # Core functionality
│   ├── config/          # Configuration
│   ├── models/          # Shared data models
│   └── utils/           # Utility functions
├── features/            # Domain-specific features
│   ├── auth/            # Authentication & authorization
│   ├── data_ingestion/  # Data ingestion pipeline
│   ├── decisions/       # Decision support engine
│   ├── evidence/        # Evidence synthesis
│   ├── export/          # Report generation
│   └── markov/          # Markov simulation
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
└── web/                 # Web interface
    ├── components/      # Reusable UI components
    ├── pages/           # Page definitions
    └── static/          # Static assets
```

## Security & Compliance

The platform implements several security measures:

- **Authentication**: JWT-based authentication with role-based access control
- **Data Encryption**: Encryption for sensitive clinical data
- **Audit Logging**: Comprehensive audit trails for all data access
- **HIPAA/GDPR Compliance**: Built-in compliance features
- **Input Validation**: Strict validation for all user inputs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com).
