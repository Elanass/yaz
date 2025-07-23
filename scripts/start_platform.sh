#!/bin/bash

# Gastric ADCI Platform Startup Script
# This script starts both the backend and frontend servers

set -e

echo "🚀 Starting Gastric ADCI Platform..."
echo "======================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
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

echo "📦 Installing dependencies..."
pip install -r requirements.txt

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
