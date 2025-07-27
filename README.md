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

## Multi-Cloud & Self-Host Deployment

Use the following options to deploy the Gastric ADCI PWA on any VM or PaaS (Oracle Free Tier, Hostinger VPS, self-hosted servers, or multi-cloud setups) with Docker, Dokku, or Coolify.

### 1. Docker Compose on Your VM
1. SSH into your VM (Oracle Cloud VM, Hostinger VPS, etc.).
2. Clone the repo and switch to the main branch:
   ```bash
   git clone https://github.com/Elanass/yaz.git
   cd yaz
   git checkout main
   ```
3. Copy the production environment file:
   ```bash
   cp infra/config/production.env .env
   ```
4. Build and start services in detached mode:
   ```bash
   docker-compose up --build -d
   ```
5. Verify:
   - Frontend: http://<VM_PUBLIC_IP>
   - Backend API: http://<VM_PUBLIC_IP>:8000

### 2. Dokku Deployment
1. Add your Dokku remote and set as a Git remote:
   ```bash
   git remote add dokku dokku@<YOUR_DOKKU_HOST>:gastric-adci-platform
   ```
2. Push to Dokku:
   ```bash
   git push dokku main
   ```
3. GitHub Actions pipeline in `.github/workflows/deploy.yml` will also auto-deploy on each push to `main`.

### 3. Coolify Deployment
1. Create a new app in Coolify and link this GitHub repo.
2. Add environment variables from `infra/config/production.env`.
3. Configure build steps:
   - **Backend**: `docker build -t backend ./backend && docker run --env-file production.env backend`
   - **Frontend**: `docker build -t frontend ./frontend && docker run -p 80:80 frontend`
4. Deploy and monitor via Coolify dashboard.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
