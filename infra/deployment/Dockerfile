# Multi-stage build for Surge Platform - Production Ready
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.txt ./
COPY src/surge/__init__.py src/surge/

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install -e .

# Production stage
FROM python:3.11-slim as production

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    WORKERS=4 \
    HOST=0.0.0.0 \
    PORT=8000

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && groupadd -r surge \
    && useradd -r -g surge -d /app -s /bin/bash surge

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set work directory and copy application
WORKDIR /app
COPY --chown=surge:surge . .

# Create necessary directories with proper permissions
RUN mkdir -p \
    data/database \
    data/uploads \
    logs \
    model_cache \
    outputs \
    && chown -R surge:surge /app \
    && chmod -R 755 /app

# Copy environment configuration
COPY --chown=surge:surge .env.example .env

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Switch to non-root user
USER surge

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Default command with proper signal handling
CMD ["sh", "-c", "exec uvicorn src.surge.main:app --host ${HOST} --port ${PORT} --workers ${WORKERS} --access-log --loop uvloop --http httptools"]
