#!/bin/bash

# Gastric ADCI Platform Startup Script
# This script starts both the backend and frontend servers

set -e

MODE=${1:-local} # Default mode is 'local'

echo "🚀 Starting Gastric ADCI Platform in $MODE mode..."
echo "======================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Docker is available for multicloud or P2P
if [[ "$MODE" != "local" ]] && ! command -v docker &> /dev/null; then
    echo "❌ Docker is required for $MODE mode but not installed."
    exit 1
fi

# Local mode setup
if [[ "$MODE" == "local" ]]; then
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        echo "❌ Please run this script from the project root directory."
        exit 1
    fi

    # Install dependencies if needed
    if [[ ! -d "venv" ]]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    echo "📦 Activating virtual environment..."
    source venv/bin/activate

    # Ensure poetry is accessible
    export PATH="$(pwd)/.venv/bin:$PATH"

    echo "📦 Installing dependencies with poetry..."
    poetry install

    # Create necessary directories
    echo "📁 Creating directories..."
    mkdir -p uploads/patients
    mkdir -p logs
    mkdir -p frontend/static/icons

    # Set environment variables
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export ENVIRONMENT="development"
    export DATABASE_URL="postgresql://adci_user:adci_pass@localhost/adci_db"
    export SECRET_KEY="your-secret-key-change-in-production"
    export API_BASE_URL="http://localhost:8000/api/v1"

    # Function to kill background processes on exit
    cleanup() {
        echo "🛑 Shutting down servers..."
        if [[ ! -z "$BACKEND_PID" ]]; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        if [[ ! -z "$FRONTEND_PID" ]]; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        exit 0
    }

    # Set trap to cleanup on script exit
    trap cleanup SIGINT SIGTERM EXIT

    # Start backend server
    echo "🔧 Starting backend server on port 8000..."
    python3 -m uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"

    # Wait a moment for backend to start
    sleep 3

    # Start frontend server
    echo "🎨 Starting frontend server on port 8001..."
    python3 -m uvicorn frontend.app:app --host 0.0.0.0 --port 8001 --reload &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"

    # Wait a moment for frontend to start
    sleep 3

    # Show status
    echo ""
    echo "✅ ADCI Platform is now running!"
    echo "======================================="
    echo "🔧 Backend API:  http://localhost:8000"
    echo "🔧 API Docs:     http://localhost:8000/docs"
    echo "🎨 Frontend:     http://localhost:8001"
    echo "📋 Protocols:    http://localhost:8001/protocols"
    echo "🧠 Decision:     http://localhost:8001/decision"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    echo "======================================="

    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID

# Multicloud or P2P setup
else
    echo "📦 Starting Docker containers for $MODE mode..."
    docker-compose up --build

    if [[ "$MODE" == "p2p" ]]; then
        echo "🔗 Initializing IPFS for P2P networking..."
        docker exec -it $(docker ps -qf "name=ipfs") ipfs swarm connect
    fi

    echo "✅ ADCI Platform is now running in $MODE mode!"
    echo "======================================="
    echo "Use 'docker-compose logs' to view logs."
    echo "======================================="
fi
