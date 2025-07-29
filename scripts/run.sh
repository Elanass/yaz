#!/bin/bash
# Launch script for Gastric ADCI Platform in development mode

# Setup colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Gastric ADCI Platform - Development Launcher${NC}"
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

# Check if requirements are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
pip3 install -q -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
  echo -e "${RED}Warning: .env file not found. Using default configuration.${NC}"
  echo -e "${YELLOW}Consider creating a .env file for proper configuration.${NC}"
fi

# Run database migrations if needed
echo -e "${YELLOW}Checking for database migrations...${NC}"
if [ -d "data/migrations" ]; then
  echo -e "${GREEN}Running database migrations...${NC}"
  alembic upgrade head
else
  echo -e "${YELLOW}No migrations directory found. Skipping migrations.${NC}"
fi

# Launch application with uvicorn
echo -e "${GREEN}Starting Gastric ADCI Platform...${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}Application will be available at:${NC}"
echo -e "${GREEN}http://localhost:8000${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

# Set environment variables for development
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=INFO

# Start application with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
