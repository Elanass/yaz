#!/bin/bash
# Production launch script for Gastric ADCI Platform

# Setup colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Gastric ADCI Platform - Production Launcher${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if Python is installed
if ! [ -x "$(command -v python3)" ]; then
  echo -e "${RED}Error: Python3 is not installed.${NC}" >&2
  exit 1
fi

# Create directories if they don't exist
echo -e "${YELLOW}Setting up required directories...${NC}"
mkdir -p logs
mkdir -p data/uploads
mkdir -p web/static/uploads

# Ensure proper permissions
chmod -R 755 web/static

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python -m alembic -c config/alembic.ini upgrade head

# Check for required environment variables
if [ -z "$SECRET_KEY" ]; then
  echo -e "${YELLOW}WARNING: SECRET_KEY environment variable not set. Using a randomly generated key.${NC}"
  echo -e "${YELLOW}This is not recommended for production deployments.${NC}"
fi

# Start the server with production settings
echo -e "${GREEN}Starting Gastric ADCI Platform...${NC}"
echo -e "${BLUE}========================================${NC}"

# Use Gunicorn with Uvicorn workers for production
exec gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --log-level info \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
echo -e "${YELLOW}Running database migrations...${NC}"
alembic upgrade head

# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=WARNING
export WORKERS=4  # Adjust based on available CPU cores

# Launch application with gunicorn (if available) or uvicorn
echo -e "${GREEN}Starting Gastric ADCI Platform in production mode...${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

if [ -x "$(command -v gunicorn)" ]; then
  echo -e "${GREEN}Using Gunicorn ASGI server...${NC}"
  gunicorn main:app -w $WORKERS -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
  echo -e "${YELLOW}Gunicorn not found, using Uvicorn...${NC}"
  uvicorn main:app --host 0.0.0.0 --port 8000 --workers $WORKERS --no-reload
fi
