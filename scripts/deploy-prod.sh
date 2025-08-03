#!/bin/bash
# Production deployment script for Surgify Platform

set -e

echo "🚀 Deploying Surgify Platform to production..."

# Build Docker image
echo "🏗️  Building Docker image..."
docker build -t surgify:latest .

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker-compose -f docker-compose.yml down || true

# Start production containers
echo "▶️  Starting production containers..."
docker-compose -f docker-compose.yml up -d surgify-prod

# Wait for containers to be healthy
echo "⏳ Waiting for containers to be healthy..."
timeout 60 bash -c 'until docker-compose ps | grep healthy; do sleep 5; done'

echo "✅ Production deployment complete!"
echo "🌐 Application available at: http://localhost"
