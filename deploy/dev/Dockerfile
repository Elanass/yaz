# Development Dockerfile for Gastric ADCI Platform
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development extras
RUN pip install --no-cache-dir \
    black \
    isort \
    mypy \
    pylint \
    pytest \
    pytest-cov \
    pytest-asyncio \
    ipython \
    debugpy

# Create necessary directories
RUN mkdir -p data/uploads logs web/static/icons

# Create startup script
RUN echo '#!/bin/bash\necho "Development environment ready. Run your commands here."\necho "Example: python -m pytest tests/"\necho "Example: uvicorn main:app --host 0.0.0.0 --port 8001 --reload"\nexec /bin/bash' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Entry point
ENTRYPOINT ["/entrypoint.sh"]
