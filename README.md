# Gastric ADCI Oncology-Surgery Decision Support Platform

A state-of-the-art Progressive Web App (PWA) for precision oncology decision support in gastric surgery, centered on the ADCI (Adaptive Decision Confidence Index) framework.

## 🎯 Overview

This platform serves clinical experts and patients in collaborative, evidence-based healthcare environments for gastric cancer treatment decisions.

## 🏗️ Architecture

### Frontend (PWA)
- **FastHTML** + **HTMX** for reactive UI
- **Gun.js** for real-time distributed state
- **ElectricsQL** for offline-first PostgreSQL sync
- **Service Worker** for offline capabilities
- **Web App Manifest** for PWA installation

### Backend (FastAPI)
- **FastAPI** with async support
- **PostgreSQL** with ElectricsQL compatibility
- **IPFS** for immutable evidence storage
- **RBAC** (Role-Based Access Control)
- **Decision Engine** with ADCI, Gastrectomy, FLOT protocols

### Key Features
- 🔒 **HIPAA/GDPR Compliant** with audit trails
- 📱 **Mobile-first** responsive design
- 🔄 **Offline-first** with background sync
- 🧠 **AI-powered** decision support
- 👥 **Multi-role** support (Patients, Practitioners, Researchers)
- 📊 **Evidence visualization** and analysis
- 🔍 **Advanced filtering** and search
- 📤 **Data export** (CSV/JSON)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (optional - SQLite used for development)
- Redis 7+ (optional - for production caching)

### Development Setup

1. **Clone and setup the project:**
```bash
git clone <your-repo-url>
cd yaz
```

2. **Start the platform:**
```bash
# Simple startup (both backend and frontend)
./start_platform.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn backend.src.main:app --port 8000 --reload &
python3 -m uvicorn frontend.app:app --port 8001 --reload &
```

3. **Access the application:**
- 🎨 **Frontend**: http://localhost:8001
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 📋 **Clinical Protocols**: http://localhost:8001/protocols
- 🧠 **Decision Engine**: http://localhost:8001/decision

### Production Deployment

#### Using Docker Compose (Recommended)
```bash
# Start all services (app, database, redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Scale the application
docker-compose up -d --scale app=3
```

#### Manual Production Setup
```bash
# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/adci_db"
export SECRET_KEY="your-secret-key"
export ENVIRONMENT="production"

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python3 -m alembic upgrade head

# Start services
gunicorn backend.src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &
gunicorn frontend.app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 &
```

### Testing

Run the comprehensive test suite:
```bash
# Install test dependencies
pip install -r requirements.txt

# Run platform tests
python3 test_platform.py

# Run unit tests (when implemented)
pytest tests/

# Run integration tests
pytest tests/integration/
```

### Original Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py

# Run development server
python main.py
```

### Environment Variables

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/gastric_adci
ELECTRICSQL_URL=ws://localhost:5133

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# IPFS
IPFS_API_URL=http://localhost:5001

# Clinical Settings
ADCI_ENGINE_ENDPOINT=https://api.adci.health/v1
CLINICAL_DATA_ENCRYPTION_KEY=your-encryption-key

# Deployment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 📂 Project Structure

```
gastric-adci-platform/
├── backend/
│   ├── src/
│   │   ├── api/           # FastAPI routes
│   │   ├── core/          # Configuration, security
│   │   ├── db/            # Database models, migrations
│   │   ├── services/      # Business logic
│   │   └── engines/       # Decision engines
│   ├── tests/
│   └── alembic/
├── frontend/
│   ├── static/            # CSS, JS, images
│   ├── templates/         # FastHTML templates
│   ├── components/        # Reusable components
│   └── islands/           # Page islands
├── scripts/               # Deployment, setup scripts
├── docs/                  # Documentation
└── docker/                # Docker configurations
```

## 🔬 Clinical Decision Engines

### ADCI (Adaptive Decision Confidence Index)
- Real-time confidence scoring
- Evidence-based recommendations
- Uncertainty quantification

### Gastrectomy Protocol Engine
- Surgical approach recommendations
- Risk stratification
- Recovery predictions

### FLOT (Fluorouracil, Leucovorin, Oxaliplatin, Docetaxel)
- Chemotherapy protocol optimization
- Side effect prediction
- Dosage recommendations

## 👥 User Roles

- **Patients**: View treatment options, track progress
- **Practitioners**: Access decision tools, update protocols
- **Researchers**: Contribute evidence, analyze outcomes

## 🛡️ Security & Compliance

- End-to-end encryption for clinical data
- Audit logging for all access and modifications
- RBAC with fine-grained permissions
- HIPAA-compliant data handling
- GDPR-compliant data processing

## 🌐 Deployment

### Google Cloud Platform
- **Cloud Run** for scalable container deployment
- **Cloud SQL** for managed PostgreSQL
- **Cloud Storage** for static assets
- **Cloud CDN** for global distribution

### Monitoring
- **Prometheus** metrics collection
- **Grafana** dashboards
- **Cloud Logging** for centralized logs
- **Error Reporting** for issue tracking

## 📊 Performance Targets

- API response time: < 200ms (95th percentile)
- PWA load time: < 3s on 3G
- Offline functionality: Full feature parity
- Uptime: 99.9% SLA

## 🤝 Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

- **Clinical Decision Logic**: Proprietary/Licensed
- **EMR Integration Modules**: Open Source (MIT)

## 📞 Support

For clinical support: [clinical-support@gastric-adci.health](mailto:clinical-support@gastric-adci.health)
For technical support: [tech-support@gastric-adci.health](mailto:tech-support@gastric-adci.health)

---

**⚠️ Important**: This is a medical decision support tool. Always consult with qualified healthcare professionals before making clinical decisions.
