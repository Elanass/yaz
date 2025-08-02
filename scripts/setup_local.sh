#!/bin/bash
"""
Local Development Setup and Run Script for Gastric ADCI Platform
Automated setup for standalone local development environment
"""

set -e

echo "🏥 Setting up Gastric ADCI Platform - Local Development Environment"

# Set environment variables for local mode
export GASTRIC_ADCI_ENV=local
export DEBUG=true
export LOG_LEVEL=INFO
export PORT=8000
export DATA_DIR=./data
export DATABASE_URL=sqlite:///./data/database/gastric_adci.db

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python version: $PYTHON_VERSION"
    
    # Check if running in virtual environment (recommended)
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Running in virtual environment: $VIRTUAL_ENV"
    else
        print_warning "Not running in a virtual environment. Consider using 'python -m venv venv && source venv/bin/activate'"
    fi
}

# Setup local directories
setup_directories() {
    print_status "Setting up local directories..."
    
    mkdir -p data/database
    mkdir -p data/uploads
    mkdir -p data/logs
    mkdir -p data/backups
    mkdir -p logs
    
    print_success "Local directories created"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    elif [ -f "config/requirements.txt" ]; then
        pip install -r config/requirements.txt
        print_success "Dependencies installed from config/requirements.txt"
    else
        print_warning "No requirements.txt found. Installing core dependencies..."
        pip install fastapi uvicorn sqlalchemy sqlite3 jinja2 python-multipart
    fi
}

# Initialize local database
initialize_database() {
    print_status "Initializing local SQLite database..."
    
    # Create database file if it doesn't exist
    if [ ! -f "data/database/gastric_adci.db" ]; then
        python3 -c "
import sqlite3
import os

os.makedirs('data/database', exist_ok=True)
conn = sqlite3.connect('data/database/gastric_adci.db')
print('Local database created')
conn.close()
"
        print_success "Local database initialized"
    else
        print_status "Database already exists"
    fi
}

# Create local configuration
create_local_config() {
    print_status "Creating local configuration..."
    
    mkdir -p config
    
    cat > config/local.env << EOF
# Local Development Configuration
GASTRIC_ADCI_ENV=local
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/database/gastric_adci.db

# File Storage
DATA_DIR=./data
FILE_STORAGE=./data/uploads

# Security (development only)
ENCRYPTION_ENABLED=true
AUTH_REQUIRED=false
SESSION_TIMEOUT=7200

# Features
REAL_TIME_UPDATES=true
OFFLINE_SUPPORT=true
COLLABORATION_FEATURES=false

# CORS (for local development)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173
EOF

    print_success "Local configuration created at config/local.env"
}

# Validate setup
validate_setup() {
    print_status "Validating setup..."
    
    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        print_error "main.py not found. Are you in the correct directory?"
        exit 1
    fi
    
    # Test import
    python3 -c "
try:
    from core.config.environment import get_environment_config
    config = get_environment_config()
    print(f'Environment: {config.get_mode().value}')
    print('Configuration validation passed')
except Exception as e:
    print(f'Configuration validation failed: {e}')
    exit(1)
"
    
    print_success "Setup validation passed"
}

# Start the application
start_application() {
    print_status "Starting Gastric ADCI Platform in local mode..."
    print_status "Access the application at: http://localhost:$PORT"
    print_status "API documentation: http://localhost:$PORT/docs"
    print_status ""
    print_status "Press Ctrl+C to stop the server"
    print_status ""
    
    # Source local environment if it exists
    if [ -f "config/local.env" ]; then
        export $(cat config/local.env | grep -v '^#' | xargs)
    fi
    
    # Start with hot reload for development
    python3 main.py
}

# Main execution
main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "🏥 Gastric ADCI Platform - Local Development Setup"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    check_prerequisites
    setup_directories
    install_dependencies
    initialize_database
    create_local_config
    validate_setup
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    print_success "Local development environment setup complete!"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    # Ask if user wants to start the application
    read -p "Start the application now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_application
    else
        echo ""
        print_status "To start the application later, run:"
        print_status "  source config/local.env && python3 main.py"
        print_status "  OR"
        print_status "  ./scripts/run_local.sh"
    fi
}

# Handle script arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "start")
        print_status "Starting application..."
        if [ -f "config/local.env" ]; then
            export $(cat config/local.env | grep -v '^#' | xargs)
        fi
        start_application
        ;;
    "validate")
        validate_setup
        ;;
    "clean")
        print_status "Cleaning local data..."
        rm -rf data/database/*.db
        rm -rf data/uploads/*
        rm -rf data/logs/*
        print_success "Local data cleaned"
        ;;
    *)
        echo "Usage: $0 {setup|start|validate|clean}"
        echo "  setup   - Full setup and optionally start"
        echo "  start   - Start the application"
        echo "  validate - Validate configuration"
        echo "  clean   - Clean local data"
        exit 1
        ;;
esac
