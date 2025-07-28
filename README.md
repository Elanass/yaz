# Gastric ADCI Platform

A state-of-the-art Progressive Web App (PWA) for precision oncology decision support in gastric surgery, centered on the ADCI (Adaptive Decision Confidence Index) framework.

## 🎯 Overview

This platform serves clinical experts and patients in collaborative, evidence-based healthcare environments for gastric cancer treatment decisions.

## 🏗️ Architecture

### New Modular Structure
```
yaz/
├── core/                    # 🤖 Core platform functionality
│   ├── config/             # Central configuration system
│   ├── models/             # Shared data models
│   ├── services/           # Base services & utilities
│   └── utils/              # Helper functions
├── features/               # 🔧 Feature modules (add new features here)
│   ├── auth/              # Authentication & RBAC
│   ├── decisions/         # Decision engines (ADCI, Gastrectomy)
│   ├── insights/          # Insight generation (future)
│   └── cohorts/           # Cohort management (future)
├── api/                   # 🌐 Clean API layer
│   └── v1/               # API v1 endpoints
├── web/                  # 💻 Simple web interface
│   ├── components/       # Reusable UI components
│   └── pages/           # Page templates
├── data/                # 📊 Data layer (future)
│   ├── models/          # Database models
│   └── repositories/    # Data access layer
└── tests/               # ✅ Comprehensive tests
    ├── unit/           # Unit tests
    └── integration/    # End-to-end tests
```

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

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Start the platform:**
```bash
python app.py
```

## 🏗️ Migration Notes

This restructure focuses on:
- **DRY** (Don't Repeat Yourself) - Eliminated code duplication
- **MVP** (Minimum Viable Product) - Core functionality first
- **Reproducible** - Standardized patterns for feature development

Refer to the new modular structure above for details.

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
