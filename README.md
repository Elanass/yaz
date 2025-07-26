# Gastric ADCI Platform

## Overview
The Gastric ADCI Platform is a healthcare-grade Progressive Web App (PWA) designed to support gastric oncology-surgery decision-making using the Adaptive Decision Confidence Index (ADCI) framework. It integrates advanced clinical decision engines, real-time collaboration tools, and compliance with healthcare standards like HIPAA and GDPR.

## Current State of the Codebase

### Backend
- **Framework**: FastAPI for building RESTful APIs.
- **Database**: PostgreSQL with ElectricsQL for real-time synchronization.
- **Decision Engines**:
  - **ADCI Engine**: Provides confidence-scored treatment recommendations.
  - **Gastrectomy Engine**: Suggests surgical approaches based on clinical data.
  - **FLOT Engine**: Optimizes perioperative chemotherapy protocols.
- **Security**:
  - Role-Based Access Control (RBAC).
  - Audit logging for all data access and modifications.
  - Encryption for sensitive clinical data.
- **Compliance**:
  - Fully adheres to HIPAA and GDPR standards.
  - Implements audit trails for all clinical workflows.

### Frontend
- **Framework**: FastHTML and HTMX for lightweight, reactive UI components.
- **State Management**: Gun.js for real-time collaboration and offline-first functionality.
- **Features**:
  - Responsive, mobile-first design.
  - Advanced analytics dashboards with export options (PDF, CSV, JSON).
  - Real-time notifications and updates.
  - Accessibility compliant with WCAG 2.1 AA standards.

### Deployment
- **Containerization**: Dockerized services for consistent deployment.
- **Cloud**: Google Cloud Run/GKE for scalable hosting.
- **CI/CD**: Automated pipelines for testing and deployment.

### Testing
- Comprehensive unit tests for decision engines.
- Integration tests for clinical workflows.
- Performance tests ensuring sub-200ms API response times.
- Offline functionality and sync scenarios validated.

## State-of-the-Art Features
1. **Adaptive Decision Confidence Index (ADCI)**:
   - Provides confidence intervals and uncertainty measures for clinical decisions.
   - Integrates evidence-based scoring and recommendations.

2. **Real-Time Collaboration**:
   - Supports collaborative protocol editing and case discussions.
   - Real-time synchronization of decisions and evidence.

3. **Offline-First Functionality**:
   - Ensures seamless operation during network outages.
   - Automatic synchronization when connectivity is restored.

4. **Advanced Analytics**:
   - Interactive dashboards for cohort analysis and protocol optimization.
   - Exportable reports with clinical explanations and evidence citations.

5. **Compliance and Security**:
   - End-to-end encryption for sensitive data.
   - Comprehensive audit trails for all actions.

## Getting Started

### Prerequisites
- Python 3.11 or higher.
- Docker and Docker Compose.
- Node.js (for frontend builds).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/gastric-adci-platform.git
   cd gastric-adci-platform
   ```
2. Set up the Python environment:
   ```bash
   poetry install
   ```
3. Start the platform:
   ```bash
   ./scripts/start_platform.sh
   ```

### Troubleshooting
- Ensure Python 3.11+ is installed and set as the default interpreter.
- Check Docker and Node.js installations for compatibility.

## Contributing
We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
