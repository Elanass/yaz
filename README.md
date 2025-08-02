# Gastric ADCI Platform - Surgery Decision Support

A **streamlined** healthcare application for surgical decision support in gastric cancer treatment, featuring the ADCI (Adaptive Decision Confidence Index) framework and FLOT protocol analysis.

## 🎯 Current Status: STREAMLINED & FUNCTIONAL

This codebase has been **completely streamlined** to eliminate complexity while maintaining core functionality:

### ✅ Streamlining Improvements
- **Single Entry Point**: One `app.py` file instead of multiple scattered Python files
- **Consolidated Configuration**: All config in one place - no complex folder structures
- **DRY Principle**: Eliminated code duplication and redundant files
- **Minimal Dependencies**: Only essential packages for core functionality
- **Clean Architecture**: Simple, maintainable, and understandable structure
- **Zero Complexity**: Removed over-engineered patterns and abstractions

### 🏗️ Clean Structure
```
/workspaces/yaz/
├── app.py              # Single application entry point
├── requirements.txt    # All dependencies 
├── README.md          # This file
├── .env               # Environment configuration
└── static/            # Static assets (if needed)
```

**Previous mess eliminated:**
- ❌ main.py, asgi.py, config.py (removed)
- ❌ Complex config/ folder structure (simplified)  
- ❌ Over-engineered core/ and feature/ hierarchies
- ❌ Unnecessary API routing complexity
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
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main application info |
| `GET /health` | System health check |
| `GET /api/features` | Available platform features |
| `GET /api/analysis` | Statistical analysis service |
| `GET /api/decisions` | ADCI decision support |
| `GET /api/cases` | Case management |

## 🏥 Core Features

- **Decision Support Engine**: Evidence-based gastric cancer treatment recommendations
- **ADCI Framework**: Structured decision-making with confidence scoring  
- **FLOT Protocol Analysis**: Assessment of perioperative chemotherapy effects
- **Statistical Analysis**: Survival analysis and outcome prediction
- **RESTful API**: Clean, documented endpoints for all functionality

## ⚙️ Configuration

## ⚙️ Configuration

All configuration is centralized in `app.py`:
- Environment variables via `.env` file
- Feature toggles for enabling/disabling modules  
- CORS and security settings
- Development vs production modes

## 🚀 Deployment

### Local Development
```bash
# Set environment variables
export DEBUG=true
export PORT=8000

# Run the application
python app.py
```

### Production
```bash
# Use environment variables for production config
export ENVIRONMENT=production
export DEBUG=false
export HOST=0.0.0.0
export PORT=80

# Run with production server
python app.py
```

## 📊 Technical Stack

- **Backend**: FastAPI (Python 3.10+)
- **API**: RESTful endpoints with automatic OpenAPI docs
- **Dependencies**: Minimal, production-ready packages
- **Deployment**: Single-file application, containerizable

## 🧪 Development

### Code Quality
- Clean, readable Python code
- Type hints throughout
- Comprehensive error handling
- Structured logging

### Testing
```bash
# Test the application
python -c "import app; print('✅ App imports successfully')"
```

---
