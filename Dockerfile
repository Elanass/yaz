# Dockerfile for Gastric ADCI Platform
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for scalability
ENV PYTHONUNBUFFERED=1
ENV WORKERS=4

# Expose application port
EXPOSE 8000

# Start application
CMD ["gunicorn", "main:app", "--workers", "${WORKERS}", "--bind", "0.0.0.0:8000"]
