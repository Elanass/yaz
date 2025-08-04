# Surgify - Make Your Way

🏥 Advanced Decision Support Platform for Surgical Excellence

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Surgify is a comprehensive surgical decision support platform that empowers healthcare professionals with AI-powered insights, comprehensive case management, and evidence-based clinical tools. Our mission is to enhance surgical outcomes through cutting-edge technology and intuitive design.

**Tagline:** *Make your way* - Empowering surgeons to navigate complex clinical decisions with confidence.

## 🏗️ Architecture

```
src/surgify/
├── api/                    # Backend API endpoints
│   ├── v1/                # API version 1
│   │   ├── auth.py       # Authentication
│   │   ├── cases.py      # Case management
│   │   ├── dashboard.py  # Dashboard APIs
│   │   ├── mobile.py     # Mobile app support
│   │   ├── feedback.py   # User feedback
│   │   └── ...
├── core/                  # Core business logic
│   ├── config/           # Configuration management
│   ├── models/           # Data models
│   ├── services/         # Business services
│   └── utils/            # Utilities
├── ui/                   # User Interface
│   ├── web/              # Web application
│   │   ├── templates/    # HTML templates
│   │   ├── static/       # CSS, JS, images
│   │   ├── pages/        # Page controllers
│   │   └── components/   # Reusable components
│   └── mobile/           # Mobile applications
│       ├── ios/          # iOS app (Swift/SwiftUI)
│       └── android/      # Android app (Kotlin)
├── modules/              # Feature modules
│   ├── analytics/        # Analytics engine
│   └── surgery/          # Surgery-specific logic
└── main.py              # Application entry point
```

## 🚀 Features

### Web Platform
- **Clinical Workstation**: Comprehensive case management and surgical planning
- **Decision Support**: AI-powered recommendations and risk assessment
- **Analytics Dashboard**: Real-time metrics and performance insights
- **Collaboration Tools**: Team communication and knowledge sharing

### Mobile Apps (Coming Soon)
- **iOS App**: Native iPhone & iPad experience
- **Android App**: Native Android interface
- **Cross-platform Sync**: Seamless data synchronization
- **Offline Access**: Work without internet connectivity

### Core Capabilities
- ✅ Case management and tracking
- ✅ Evidence-based decision support
- ✅ Real-time analytics and reporting
- ✅ Multi-user collaboration
- ✅ Secure data handling
- ✅ Responsive web design
- 🔄 Mobile applications (in development)
- 🔄 AI-powered insights (expanding)

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: Core programming language
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and serialization
- **JWT**: Authentication and authorization

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: Reactive frontend logic
- **Jinja2**: Template engine

### Mobile (Planned)
- **iOS**: Swift/SwiftUI
- **Android**: Kotlin/Jetpack Compose
- **React Native**: Cross-platform alternative

### Infrastructure
- **Docker**: Containerization
- **PostgreSQL/SQLite**: Database systems
- **Redis**: Caching and sessions
- **GitHub Actions**: CI/CD pipeline

## 📱 User Interface

### Landing Page
- **Start Button**: Quick access to clinical workstation
- **Doc Button**: Direct link to API documentation
- **Surgify Logo**: Brand identity with tagline "Make your way"
- **Footer Navigation**: Partners, About, and Feedback sections

### Clinical Workstation
- **Fixed Bottom Navigation**: Always-accessible tools for active workflows
- **Case Dashboard**: Overview of active, planned, and completed cases
- **Quick Actions**: Streamlined access to common tasks
- **Real-time Notifications**: Updates on case status and system alerts

### Get App Page
- **Mobile Downloads**: iOS and Android app information
- **Device Mockups**: Visual preview of mobile experience
- **Feature Highlights**: Mobile-specific capabilities
- **Email Notifications**: Subscribe for app release updates

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Docker (optional, for containerized development)
- Node.js (for frontend tooling)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/surgify.git
cd surgify
```

2. **Set up Python environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database**
```bash
python -m surgify.core.database init
```

5. **Start the application**
```bash
# Development server
python main.py

# Or using uvicorn directly
uvicorn src.surgify.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the application**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Get App Page: http://localhost:8000/get-app

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access services
# Web: http://localhost:8000
# API: http://localhost:8000/api/docs
```

## 📖 API Documentation

The Surgify API provides comprehensive endpoints for:

- **Authentication**: User login, registration, and session management
- **Cases**: Create, read, update, and delete surgical cases
- **Dashboard**: Analytics and summary data
- **Mobile**: App status and user subscriptions
- **Feedback**: User feedback and feature requests

Access interactive API documentation at: `/api/docs`

### Key Endpoints

```
GET  /                    # Landing page
GET  /get-app            # Mobile app downloads
GET  /workstation        # Clinical workstation
GET  /api/v1/cases       # Case management
POST /api/v1/feedback    # Submit feedback
GET  /api/v1/mobile/app-status/{platform}  # App availability
```

## 🔧 Configuration

### Environment Variables

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///./data/surgify.db

# API
API_V1_STR=/api/v1
CORS_ORIGINS=["http://localhost:3000"]

# Mobile
IOS_APP_URL=https://apps.apple.com/app/surgify
ANDROID_APP_URL=https://play.google.com/store/apps/details?id=com.surgify.app
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/surgify

# Run specific test categories
pytest tests/api/          # API tests
pytest tests/ui/           # UI tests
pytest tests/integration/  # Integration tests
```

## 📱 Mobile Development

### iOS App Setup (Planned)
```bash
cd src/surgify/ui/mobile/ios
# iOS-specific setup instructions will be added
```

### Android App Setup (Planned)
```bash
cd src/surgify/ui/mobile/android
# Android-specific setup instructions will be added
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure mobile-responsive design for UI changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core web platform
- ✅ API infrastructure
- ✅ Basic case management
- ✅ User authentication

### Phase 2 (Q2 2025)
- 🔄 Mobile app development
- 🔄 Advanced analytics
- 🔄 AI-powered recommendations
- 🔄 Real-time collaboration

### Phase 3 (Q3 2025)
- 📋 Integration with hospital systems
- 📋 Advanced reporting
- 📋 Multi-tenant architecture
- 📋 Enterprise features

## 💬 Support

- 📧 Email: support@surgify.com
- 💬 Feedback: Use the in-app feedback system
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/surgify/issues)
- 📚 Documentation: [docs.surgify.com](https://docs.surgify.com)

---

**Surgify** - *Make your way* through surgical excellence.

Built with ❤️ for healthcare professionals worldwide.
