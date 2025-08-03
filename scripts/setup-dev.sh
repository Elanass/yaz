#!/bin/bash
# Development setup script for Surgify Platform

set -e

echo "🏥 Setting up Surgify Platform for development..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/database
mkdir -p logs
mkdir -p data/uploads
mkdir -p data/backups

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
python -c "
import sys
sys.path.insert(0, 'src')
from surgify.core.database import create_tables
create_tables()
print('Database initialized successfully!')
"

echo "✅ Development environment setup complete!"
echo ""
echo "To start the development server:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
