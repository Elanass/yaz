# Test environment Dockerfile for Gastric ADCI Platform
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=test

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Test-specific dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    pytest-mock \
    black \
    coverage

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads logs web/static/icons

# Default command: run tests
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=."]
