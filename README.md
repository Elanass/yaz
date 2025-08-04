# Surgify - Advanced Surgical Platform

🏥 Empowering Healthcare Professionals with AI-Powered Decision Support

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Surgify is a comprehensive surgical decision support platform that empowers healthcare professionals with AI-powered insights, comprehensive case management, and evidence-based clinical tools. Our mission is to enhance surgical outcomes through cutting-edge technology and intuitive design.

## 🌟 Key Features

### ✨ **Modern UI/UX**
- **Responsive Design**: Beautiful, mobile-first interface that works seamlessly across all devices
- **Interactive Elements**: Smooth animations, hover effects, and intuitive navigation
- **Dark/Light Theme**: Toggle between themes with persistent preference storage
- **Smart Search**: Global search functionality for cases, patients, and procedures
- **Interactive Auth**: Stylish authentication modal with gradient buttons

### 🏥 **Core Functionality**
- **Case Management**: Complete CRUD operations for surgical cases with status tracking
- **Analytics Dashboard**: Real-time metrics, trends, and performance indicators
- **AI Decision Support**: Risk assessment, outcome prediction, and clinical recommendations
- **User Management**: Role-based access control with secure JWT authentication
- **API Integration**: RESTful API with comprehensive documentation

### 🎨 **Enhanced User Experience**
- **No Sidebar Clutter**: Clean header-focused navigation without overwhelming side panels
- **Gradient Logo**: Stylish branding with modern gradient effects
- **Quick Actions**: Easy access to common tasks from the homepage
- **Interactive Cards**: Hover effects and animations on feature cards
- **Mobile Optimized**: Dedicated mobile search bar and touch-friendly controls

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
│   ├── desktop/          # Desktop application (Electron)
│   │   ├── src/main/     # Main process (Node.js)
│   │   ├── src/renderer/ # Renderer process (Web)
│   │   └── assets/       # Icons and resources
│   └── mobile/           # Mobile applications
│       ├── ios/          # iOS app (Swift/SwiftUI)
│       └── android/      # Android app (Kotlin)
├── modules/              # Feature modules
│   ├── analytics/        # Analytics engine
│   └── surgery/          # Surgery-specific logic
└── main.py              # Application entry point
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package installer)

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd yaz
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   ```bash
   cd data && alembic upgrade head
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or with uvicorn directly:
   ```bash
   PYTHONPATH=src uvicorn surgify.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application:**
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/api/docs
   - **Interactive API**: http://localhost:8000/api/redoc

### 🎯 What's New in This Version

- ✅ **Removed sidebar menu** - Clean, header-focused navigation
- ✅ **Enhanced auth button** - Wider, more stylish gradient design
- ✅ **Added logo to header** - Beautiful gradient Surgify branding
- ✅ **Integrated search bar** - Global search functionality in header
- ✅ **Theme toggle** - Dark/light mode with sun/moon icons
- ✅ **Removed "Make Your Way"** - Cleaner hero section messaging
- ✅ **Mobile optimizations** - Dedicated mobile search and responsive design
- ✅ **Interactive elements** - Hover effects, animations, and smooth transitions

## 🎨 **Recent UI Updates:**

### Modern Hero Section
- **Eye-Catching Design**: New gradient backgrounds with animated elements
- **Glassmorphism Effects**: Modern backdrop blur and transparency effects  
- **Interactive Animations**: Smooth hover effects and transitions
- **Mobile Responsive**: Optimized for all device sizes

### Simplified Authentication
- **Single Auth Element**: Replaced login/signup buttons with elegant auth logo
- **Gradient Design**: Modern gradient-based UI elements
- **Clean Interface**: Removed brand logo clutter for cleaner look

### Enhanced Visual Appeal
- **Modern Gradients**: Purple-to-blue gradient themes throughout
- **Animated Backgrounds**: Floating particle effects in hero section
- **Typography**: Improved font choices and text gradient effects
- **Micro-interactions**: Subtle animations for better user experience

---

### ✅ **Completed Features:**

1. **Core Authentication System** 🔐
   - JWT-based authentication with refresh tokens
   - User registration and login endpoints (`/api/v1/auth/`)
   - Password hashing with bcrypt
   - Role-based access control structure

2. **Multi-Platform App Downloads** 📱
   - Desktop app download system (`/api/v1/downloads/download/desktop`)
   - iOS App Store integration (`/api/v1/downloads/download/ios`)
   - Android Play Store integration (`/api/v1/downloads/download/android`)
   - Interactive download modal with platform detection
   - Cross-platform sync capabilities

2. **Case Management System** 📋
   - CRUD operations for surgical cases (`/api/v1/cases/`)
   - Case status tracking (Planned, Active, Completed, Cancelled)
   - Patient information management
   - Pre/post-operative notes handling

3. **Analytics Dashboard** 📊
   - Real-time metrics endpoint (`/api/v1/dashboard/metrics`)
   - Time-based analytics (daily, weekly, monthly trends)
   - Export functionality for reports
   - Performance indicators tracking

4. **Decision Support Engine** 🤖
   - Risk assessment algorithms (`/api/v1/recommendations/risk`)
   - Evidence-based recommendations (`/api/v1/recommendations/`)
   - Outcome prediction models (`/api/v1/recommendations/outcome`)
   - Alert system for high-risk cases (`/api/v1/recommendations/alerts`)

5. **Database Architecture** 🗄️
   - SQLAlchemy models for User and Case entities
   - Database connection and session management
   - Alembic migration system setup
   - Initial migration scripts

6. **API Infrastructure** 🔌
   - RESTful API design with FastAPI
   - Comprehensive API utilities
   - Input validation and error handling
   - Complete testing suite for all endpoints

7. **Modern Web Interface** 🖥️
   - Landing page with "Start" and "Doc" buttons
   - Fixed bottom navigation component
   - Tailwind CSS styling framework setup
   - Mobile-responsive design structure

### 🔄 **API Endpoints Available:**

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

#### Case Management
- `GET /api/v1/cases/cases` - List all cases
- `POST /api/v1/cases/cases` - Create new case
- `GET /api/v1/cases/cases/{id}` - Get specific case
- `PUT /api/v1/cases/cases/{id}` - Update case
- `DELETE /api/v1/cases/cases/{id}` - Delete case

#### Analytics Dashboard
- `GET /api/v1/dashboard/dashboard/metrics` - Get metrics
- `GET /api/v1/dashboard/dashboard/trends` - Get trends
- `GET /api/v1/dashboard/dashboard/export` - Export report

#### Decision Support
- `POST /api/v1/recommendations/recommendations/risk` - Assess risk
- `POST /api/v1/recommendations/recommendations` - Get recommendations
- `POST /api/v1/recommendations/recommendations/outcome` - Predict outcome
- `POST /api/v1/recommendations/recommendations/alerts` - Generate alerts

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# API tests
pytest tests/api/

# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/
```

### Test Coverage
```bash
pytest --cov=src/surgify --cov-report=html
```

## 🚀 Deployment

### Production Deployment
```bash
# Using Gunicorn
gunicorn surgify.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t surgify .
docker run -p 8000:8000 surgify
```

### Environment Variables
Create a `.env` file:
```env
DATABASE_URL=sqlite:///./surgify.db
SECRET_KEY=your-secret-key-here
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

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

### Desktop
- **Electron**: Cross-platform desktop application framework
- **TypeScript**: Type-safe development
- **React**: Component-based UI library
- **Webpack**: Module bundling and optimization
- **Forge**: Application packaging and distribution

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

### Desktop Application Setup

1. **Navigate to desktop directory**
```bash
cd src/surgify/ui/desktop
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development mode**
```bash
npm run dev
```

4. **Build for production**
```bash
npm run build
npm run package  # Create distributable package
```

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

# Test desktop application
cd src/surgify/ui/desktop
npm test                   # Desktop app tests
```

## 🖥️ Desktop Application

The Surgify Desktop Application provides a native desktop experience using Electron, offering enhanced performance, offline capabilities, and better system integration.

### Features
- **Native Performance**: Optimized for desktop environments
- **Offline Mode**: Continue working without internet connectivity
- **Security**: Enhanced security with certificate validation
- **Auto-updates**: Automatic application updates
- **Cross-platform**: Windows, macOS, and Linux support

### Installation
```bash
cd src/surgify/ui/desktop
npm install
npm run build
npm run package
```

For detailed desktop setup instructions, see: [Desktop README](src/surgify/ui/desktop/README.md)

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

## Mobile App Setup

### iOS
1. Install Xcode and development tools.
2. Run `setup-ios.sh` to initialize the environment.
3. Open the project in Xcode and build.

### Android
1. Install Android Studio and SDK tools.
2. Run `setup-android.sh` to initialize the environment.
3. Open the project in Android Studio and build.

### Troubleshooting
- Ensure all dependencies are installed.
- Check `.env` for missing configuration values.

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
- ✅ Desktop application (Electron wrapper)

### Phase 2 (Q2 2025)
- 🔄 Mobile app development
- 🔄 Advanced analytics
- 🔄 AI-powered recommendations
- 🔄 Real-time collaboration
- 🔄 Desktop app store distribution

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
