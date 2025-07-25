# Base image
FROM python:3.12-slim

# Multi-stage build for backend
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Install IPFS for P2P support
RUN apt-get update && apt-get install -y ipfs && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
