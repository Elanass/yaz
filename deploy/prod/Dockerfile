# Dockerfile for Gastric ADCI Platform
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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production-specific packages
RUN pip install --no-cache-dir \
    gunicorn \
    uvloop \
    httptools \
    redis \
    sentry-sdk \
    newrelic

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads logs web/static/icons

# Set permissions
RUN chmod +x scripts/run_prod.sh

# Expose ports
EXPOSE 8000 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command: start ASGI server with Uvicorn
CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--http", "httptools"]
