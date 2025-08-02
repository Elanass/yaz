# Gastric ADCI Platform - Medical Decision Support

A **professional** and **minimalist** healthcare application for medical decision support in gastric cancer treatment, featuring the ADCI (Adaptive Decision Confidence Index) framework, comprehensive surgery management, and integrated healthcare operations.

## 🎯 Current Status: CLEAN & PRODUCTION-READY

This platform has been **completely cleaned and modernized** with a professional, minimalist architecture:

### ✅ Clean Architecture
- **Streamlined Codebase**: No bloat - only essential files (py, html, css, md)
- **Complete API Integration**: All endpoints functional and tested
- **Professional UI/UX**: Minimalist medical-grade design with improved color scheme
- **Secure Authentication**: WebAuthn and traditional auth methods fully integrated
- **Enterprise Adapters**: Support for both open-source and closed-source integrations
- **Cohesive Database Integration**: All UI components connected to backend logic

### 🏗️ Clean Project Structure
```
/workspaces/yaz/
├── app.py                    # Main FastAPI application (single entry point)
├── api/v1/                   # Complete API endpoints
│   ├── auth.py              # Authentication & WebAuthn
│   ├── surgery.py           # Surgery management (NEW)
│   ├── insurance.py         # Insurance processing (NEW)
│   ├── logistics.py         # Healthcare logistics (NEW)
│   ├── reporter.py          # Analytics & reporting (NEW)
│   ├── analysis.py          # Medical analysis
│   ├── cases.py             # Case management
│   └── decisions.py         # Decision support
├── core/                     # Core business logic
│   ├── adapters/            # Integration adapters
│   │   ├── open_source/     # Open source integrations
│   │   └── closed_source/   # Enterprise integrations (NEW)
│   ├── services/            # Business services
│   └── models/              # Data models
├── web/                      # Professional web interface
│   ├── templates/           # Clean, cohesive templates
│   ├── static/              # Minimalist styling (updated)
│   └── components/          # Essential UI components only
└── data/                     # Data management & database
```

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Platform
- **Main Application**: http://localhost:8000
- **Surgify Dashboard**: http://localhost:8000/workstation
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Complete API v1**: http://localhost:8000/api/v1

## 🔧 Complete API Endpoints (v1)

### Core Platform
| Endpoint | Description |
|----------|-------------|
| `GET /` | Main Surgify interface |
| `GET /workstation` | Clinical workstation dashboard |
| `GET /api/health` | System health check |
| `GET /docs` | Interactive API documentation |

### Authentication & Security
| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | User authentication |
| `POST /api/v1/auth/logout` | User logout |
| `POST /api/v1/auth/register` | User registration |
| `POST /api/v1/auth/webauthn/register/begin` | Begin WebAuthn registration |
| `POST /api/v1/auth/webauthn/register/complete` | Complete WebAuthn registration |
| `POST /api/v1/auth/webauthn/authenticate/begin` | Begin WebAuthn authentication |
| `POST /api/v1/auth/webauthn/authenticate/complete` | Complete WebAuthn authentication |

### Medical Operations
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/surgery/procedures` | Available surgical procedures |
| `POST /api/v1/surgery/schedule` | Schedule surgery operations |
| `GET /api/v1/surgery/protocols` | Surgery protocols and guidelines |
| `POST /api/v1/surgery/optimize` | Optimize surgical workflow |
| `GET /api/v1/cases/` | Case management interface |
| `GET /api/v1/decisions/` | ADCI decision support engine |
| `GET /api/v1/analysis/` | Medical analysis and statistics |

### Healthcare Operations (NEW)
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/insurance/plans` | Insurance plan management |
| `POST /api/v1/insurance/verify` | Insurance verification |
| `POST /api/v1/insurance/claims` | Process insurance claims |
| `GET /api/v1/logistics/inventory` | Medical inventory management |
| `POST /api/v1/logistics/transport` | Patient transport coordination |
| `GET /api/v1/logistics/resources` | Resource allocation |
| `GET /api/v1/reporter/analytics` | Generate analytics reports |
| `POST /api/v1/reporter/export` | Export data reports |
| `GET /api/v1/reporter/dashboard` | Reporting dashboard |

## 🏥 Core Features
- **ADCI Framework**: Adaptive Decision Confidence Index for treatment recommendations
- **Surgery Management**: Complete surgical workflow and protocol management
- **Evidence-Based Decisions**: Statistical analysis and outcome prediction
- **Case Management**: Comprehensive patient case tracking

### Healthcare Operations  
- **Insurance Integration**: Automated insurance verification and processing
- **Logistics Coordination**: Medical supply and patient transport management
- **Analytics & Reporting**: Comprehensive reporting and data export capabilities
- **Multi-Modal Authentication**: Traditional and WebAuthn biometric authentication

### Technical Excellence
- **RESTful API**: Clean, versioned endpoints with comprehensive documentation
- **Extensible Architecture**: Support for both open-source and proprietary integrations
- **Professional UI**: Minimalist, medical-grade user interface design
- **Robust Security**: Multiple authentication methods and secure data handling

## ⚙️ Configuration

### Environment Setup
Configuration is managed through environment variables and centralized config files:
- Main configuration in `core/config/`
- Environment variables via `.env` file
- Feature toggles for enabling/disabling modules
- CORS and security settings
- Development vs production modes

### Adapters Configuration
- **Open Source Adapters**: `core/adapters/open_source/`
- **Closed Source Adapters**: `core/adapters/closed_source/`
- Extensible integration framework for external systems

## 🚀 Deployment

### Local Development
```bash
# Set environment variables
export DEBUG=true
export PORT=8000

# Run the application
python app.py
```

### Production Deployment
```bash
# Production configuration
export ENVIRONMENT=production
export DEBUG=false
export HOST=0.0.0.0
export PORT=80

# Run with production settings
python app.py
```

### Docker Deployment
```bash
# Development
docker-compose -f deploy/dev/docker-compose.yml up

# Production
docker-compose -f deploy/prod/docker-compose.yml up
```

## 📊 Technical Stack

### Backend Architecture
- **Framework**: FastAPI (Python 3.10+)
- **API Design**: RESTful with automatic OpenAPI documentation
- **Authentication**: WebAuthn + traditional auth methods
- **Database**: SQLite with SQLAlchemy ORM
- **Testing**: pytest with integration and unit tests

### Frontend & UI
- **Styling**: Minimalist, medical-grade CSS design
- **Templates**: Jinja2 with responsive layouts
- **Color Scheme**: Professional healthcare palette
- **Components**: Modular, reusable UI elements

### Integration & Extensions
- **Adapters**: Pluggable integration framework
- **Services**: Modular business logic services
- **Dependencies**: Dependency injection container
- **Logging**: Structured logging and monitoring

## 🧪 Development & Testing

### Code Quality
- Type hints throughout the codebase
- Comprehensive error handling and validation
- Clean architecture with separation of concerns
- Professional coding standards

## 🧹 Recent Improvements & Cleanup

### ✅ Codebase Cleanup (Latest)
- **Removed Bloat**: Eliminated all unnecessary files and redundant code
- **Single Entry Point**: Consolidated to single `app.py` main application
- **No Duplicate Files**: Removed redundant main files and conflicting endpoints
- **Cache Cleanup**: Removed all Python cache files and `__pycache__` directories
- **UI Refinement**: Removed unused components (ENP, asepsi references)
- **Professional Footer**: Improved footer design for minimalist, professional look

### ✅ UI/UX Enhancements
- **Color Scheme**: Updated to professional, minimalist healthcare palette
- **Template Cleanup**: Removed broken and unused templates
- **Cohesive Design**: All UI components now integrated with backend logic
- **Enhanced Footer**: Modern, clean footer with system status indicator
- **Responsive Design**: Mobile-first, professional medical interface

### ✅ API & Backend Integration
- **Complete API v1**: All new modules (surgery, insurance, logistics, reporter) fully integrated
- **WebAuthn Ready**: Secure authentication system fully functional
- **Database Connectivity**: All UI pages connected to backend logic and database
- **Error Handling**: Professional error handling throughout the application
- **Documentation**: Up-to-date API documentation and usage examples

### Testing Suite
```bash
# Run all tests
python -m pytest

# Run integration tests
python -m pytest test/integration/

# Run unit tests  
python -m pytest test/unit/

# Test API endpoints
pytest tests/integration/test_api_endpoints.py -v
```

### Development Tools
```bash
# Check application health
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login

# Explore API documentation
open http://localhost:8000/docs
```

## 🔐 Security Features

- **Multi-Factor Authentication**: WebAuthn biometric authentication
- **Secure API**: Token-based authentication with proper validation
- **Data Protection**: Encryption and secure data handling
- **Access Control**: Role-based permissions and authorization

## 📈 Analytics & Reporting

- **Medical Analytics**: Statistical analysis of treatment outcomes
- **Operational Reports**: Healthcare logistics and efficiency metrics
- **Data Export**: Multiple formats for external analysis
- **Real-time Dashboards**: Live monitoring and insights

---

**Ready for Production** | **Medical-Grade Quality** | **Extensible Architecture**
