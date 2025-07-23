# Gastric ADCI Platform Deployment Configuration

## Overview
This directory contains deployment configurations for various environments:
- Development (local)
- Staging
- Production
- Cloud platforms (Google Cloud Run/GKE, AWS, Azure)

## Deployment Strategies

### 1. Local Development
```bash
# Using Poetry
poetry install
poetry run python -m uvicorn backend.src.main:app --reload

# Using Docker
docker-compose -f deployment/docker/docker-compose.dev.yml up
```

### 2. Staging Environment
```bash
# Deploy to staging
cd deployment/staging
./deploy.sh
```

### 3. Production Deployment
```bash
# Production deployment with monitoring
cd deployment/production
./deploy.sh
```

### 4. Cloud Deployment
```bash
# Google Cloud Run
cd deployment/gcp
./deploy-cloud-run.sh

# Kubernetes (GKE/EKS/AKS)
cd deployment/k8s
kubectl apply -f .
```

## Security Considerations

- All secrets are managed via environment variables
- Database connections use SSL/TLS
- Application runs as non-root user
- Container images are scanned for vulnerabilities
- HIPAA-compliant logging and audit trails

## Monitoring & Observability

- Prometheus metrics collection
- Grafana dashboards
- Sentry error tracking
- Structured logging with ELK stack
- Health checks and readiness probes

## Backup & Recovery

- Automated database backups
- Point-in-time recovery capability
- Disaster recovery procedures
- Data retention policies (GDPR/HIPAA compliant)
