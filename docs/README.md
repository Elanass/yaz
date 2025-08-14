# Yaz - Targeted care platform

🏥 **Modern Healthcare Technology Platform** - Targeted care for surgery, clinical operations, education, insurance, and logistics

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

**Yaz** is a comprehensive healthcare technology ecosystem that brings together multiple specialized applications under one unified platform. Our mission is to streamline healthcare operations through cutting-edge technology, intuitive design, and seamless integration across all healthcare domains.

## 🚀 Platform Applications

### 🏥 **Surge** - Surgery Analytics & Decision Support
- **AI-Powered Analytics**: Advanced surgical outcome prediction and risk assessment
- **Case Management**: Comprehensive surgical case tracking and management
- **Decision Support**: Evidence-based clinical recommendations and insights
- **Real-time Monitoring**: Live surgical metrics and performance tracking

### 🏥 **Clinica** - Clinical Operations Management
- **Patient Care Coordination**: Streamlined clinical workflows
- **Resource Management**: Optimized clinical resource allocation
- **Quality Metrics**: Clinical performance monitoring and improvement

### 📚 **Educa** - Medical Education Platform
- **Training Programs**: Comprehensive medical education modules
- **Assessment Tools**: Skill evaluation and competency tracking
- **Knowledge Base**: Centralized medical learning resources

### 🛡️ **Insura** - Healthcare Insurance Management
- **Risk Assessment**: Advanced insurance risk modeling
- **Claims Processing**: Automated claims analysis and processing
- **Policy Management**: Comprehensive insurance policy administration

### 🚚 **Move** - Healthcare Logistics
- **Supply Chain Optimization**: Medical supply chain management
- **Resource Allocation**: Efficient healthcare resource distribution
- **Inventory Management**: Real-time medical inventory tracking

## ✨ Key Features

### � **Unified Platform Architecture**
- **Modular Design**: Independent applications with shared core services
- **Single Entry Point**: Unified platform access through main application
- **Shared Services**: Common authentication, database, and caching infrastructure
- **Cross-Application Integration**: Seamless data flow between applications

### 🔧 **Modern Technology Stack**
- **Backend**: FastAPI + SQLAlchemy + Alembic for robust API development
- **Frontend**: Modern web interfaces with responsive design
- **Database**: SQLite (development) → PostgreSQL (production)
- **Caching**: Redis-based caching with intelligent fallbacks
- **Authentication**: JWT-based security with role-based access control

### 🌐 **Multi-Platform Support**
- **Web Interface**: Responsive web applications for all platforms
- **Desktop Apps**: Native desktop applications for enhanced workflows
- **Mobile Ready**: Mobile-optimized interfaces for on-the-go access
- **API First**: Comprehensive RESTful APIs for all functionality

## 🏗️ Architecture

### Clean Directory Structure
```
/workspaces/yaz/
├── src/                              # Core platform source code
│   ├── surge/                        # Surgery analytics application
│   ├── shared/                       # Shared platform services
│   └── move/                         # Logistics application (minimal)
├── apps/                             # Modular application implementations
│   ├── clinica/                      # Clinical operations
│   ├── educa/                        # Education platform
│   ├── insura/                       # Insurance management
│   └── move/                         # Logistics coordination
├── data/                             # Application data and databases
├── config/                           # Configuration files
├── docs/                             # Documentation
│   └── maintain/                     # Maintenance documentation
├── scripts/                          # Utility and deployment scripts
├── tests/                            # Comprehensive testing suite
└── main.py                           # Unified platform entry point
```

### Core Services
- **Shared Configuration**: Unified configuration management across all apps
- **Database Management**: Centralized database connections and migrations
- **Authentication Service**: JWT-based authentication with role management
- **Cache Management**: Redis caching with intelligent fallback mechanisms
- **Logging Service**: Structured logging across all platform components

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis (for caching)
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd yaz
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**
   ```bash
   cd data && alembic upgrade head
   ```

4. **Start the Platform**
   ```bash
   # Full platform (all applications)
   python main.py

   # Specific application
   python main.py --app surge
   python main.py --app clinica
   ```

5. **Access Applications**
   - **Platform Dashboard**: http://localhost:8000
   - **Surge (Surgery)**: http://localhost:8000/surge
   - **Clinica (Clinical)**: http://localhost:8000/clinica
   - **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
```bash
# Application Settings
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./data/yaz.db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Application-Specific Configuration
Each application can be configured independently while sharing core platform services:

```python
# Example: Surge application configuration
from surge.config import get_surge_config

config = get_surge_config()
# Surgery-specific settings available
```

## 🧪 Testing

### Running Tests
```bash
# All tests
python -m pytest tests/

# Specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/api/
```

### Test Coverage
- **Unit Tests**: Core component functionality
- **Integration Tests**: Multi-component interactions
- **API Tests**: Endpoint validation and security
- **Compatibility Tests**: Cross-application compatibility

## 📊 Platform Monitoring

### Health Checks
```bash
# Platform health
GET /health

# Application-specific health
GET /surge/health
GET /clinica/health
```

### Metrics and Monitoring
- **Application Performance**: Request latency, error rates, throughput
- **Database Health**: Connection pooling, query performance
- **Cache Performance**: Hit rates, memory usage
- **Security Metrics**: Authentication success rates, access patterns

## 🔒 Security

### Authentication & Authorization
- **JWT-based Authentication**: Secure token-based authentication
- **Role-based Access Control**: Fine-grained permission management
- **Session Management**: Secure session handling across applications
- **API Security**: Rate limiting, input validation, CORS protection

### Data Protection
- **Encryption**: Data encryption at rest and in transit
- **Input Validation**: Comprehensive input sanitization
- **Audit Logging**: Complete audit trail for all operations
- **Privacy Compliance**: HIPAA-compliant data handling

## 🚀 Deployment

### Local Development
```bash
# Development server with hot reload
python main.py --reload

# Individual application development
python main.py --app surge --reload
```

### Production Deployment
```bash
# Using Docker
docker-compose up -d

# Direct deployment
ENVIRONMENT=production python main.py
```

### Cloud Deployment
- **Container Support**: Docker containerization ready
- **Cloud Native**: Kubernetes deployment configurations available
- **Infrastructure as Code**: Terraform modules for major cloud providers
- **CI/CD Integration**: GitHub Actions workflows for automated deployment

## 🤝 Contributing

We welcome contributions to the Yaz Platform! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- **Code Standards**: Python PEP 8, type hints, comprehensive testing
- **Architecture Principles**: Modular design, shared services, API-first
- **Testing Requirements**: Maintain comprehensive test coverage
- **Documentation**: Keep documentation updated with changes

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper tests
4. Ensure all tests pass (`python -m pytest`)
5. Submit a pull request

## 🗂️ Platform Evolution

### Recent Cleanup (August 2025)
- **✅ Codebase Optimization**: Removed duplicate directories and unnecessary files
- **✅ Architecture Simplification**: Consolidated modular application structure  
- **✅ Documentation Cleanup**: Organized documentation in maintain directory
- **✅ Dependency Cleanup**: Removed unused dependencies and bloated code
- **✅ Performance Optimization**: Streamlined application loading and resource usage

### Removed Components
- **Duplicate Surge Directories**: Consolidated `apps/surge` into `src/surge`
- **Unnecessary Platform Directories**: Removed `src/yaz_platform` (renamed directory)
- **Unrelated Projects**: Removed `network/bitchat` (separate project)
- **Enhanced/Modified Duplicates**: Removed "enhanced" versions of existing code
- **Build Artifacts**: Cleaned up cache directories and temporary files

### Future Roadmap
- **Enhanced Integration**: Deeper cross-application data sharing
- **Advanced Analytics**: Machine learning integration across all applications
- **Mobile Applications**: Native mobile apps for key workflows
- **Real-time Collaboration**: Live collaboration features across applications
- **International Support**: Multi-language and region-specific features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: Check the [docs/maintain/](docs/maintain/) directory
- **Issues**: Report bugs via GitHub Issues
- **Security**: Report security issues privately via email
- **Community**: Join our community discussions

---

**Yaz Platform** - *Unifying Healthcare Technology for Better Outcomes*

Built with ❤️ for healthcare professionals worldwide.

---

## 📋 Platform Status

**Current Version**: 2.1.0  
**Last Updated**: August 10, 2025  
**Status**: ✅ Production Ready  

### Application Status
- **🏥 Surge**: ✅ Fully Operational - Surgery analytics and decision support
- **🏥 Clinica**: ✅ Active Development - Clinical operations management
- **📚 Educa**: ✅ Active Development - Medical education platform
- **🛡️ Insura**: ✅ Active Development - Insurance management
- **🚚 Move**: ✅ Active Development - Healthcare logistics

### Core Infrastructure
- **⚡ Platform Core**: ✅ Stable - Shared services and configuration
- **🔐 Authentication**: ✅ Secure - JWT-based with role management
- **💾 Database**: ✅ Reliable - SQLAlchemy with Alembic migrations
- **🚀 API Layer**: ✅ Robust - FastAPI with comprehensive documentation
- **🎨 UI Framework**: ✅ Modern - Responsive design with accessibility features
