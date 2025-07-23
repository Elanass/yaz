# Gastric ADCI Platform - Deployment Guide

## Overview

This guide covers deploying the Gastric ADCI Platform to production environments, with focus on Google Cloud Platform (GCP) deployment using Cloud Run and supporting services.

---

## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Load Balancer │────│  Cloud Run   │────│   PostgreSQL    │
│   (Cloud LB)    │    │  (FastAPI)   │    │   (Cloud SQL)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                       ┌──────────────┐    ┌─────────────────┐
                       │   Frontend   │    │      IPFS       │
                       │  (FastHTML)  │    │  (Distributed   │
                       └──────────────┘    │   Storage)      │
                                           └─────────────────┘
                              │
                       ┌──────────────┐    ┌─────────────────┐
                       │    Redis     │    │   Gun.js Node   │
                       │   (Memory    │    │  (Real-time     │
                       │    Store)    │    │   Sync)         │
                       └──────────────┘    └─────────────────┘
```

---

## Prerequisites

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB minimum for database and file storage
- **Network**: HTTPS capability with valid SSL certificates

### Required Services
- **Database**: PostgreSQL 13+ (managed service recommended)
- **Cache**: Redis 6+ (for session management and caching)
- **File Storage**: IPFS node or cloud storage
- **Container Registry**: For Docker images

### Development Tools
- Docker and Docker Compose
- Google Cloud SDK (for GCP deployment)
- Node.js 18+ (for Gun.js server)
- Python 3.9+ (for local development)

---

## Local Development Setup

### Quick Start
```bash
# Clone repository
git clone https://github.com/your-org/gastric-adci-platform.git
cd gastric-adci-platform

# Start development environment
./scripts/start_platform.sh

# Platform available at:
# Frontend: http://localhost:8001
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup
```bash
# 1. Environment configuration
cp .env.example .env
# Edit .env with your settings

# 2. Database setup
docker-compose up -d postgres redis

# 3. Run migrations
python -m backend.src.db.migrations.001_create_cohort_tables

# 4. Start backend
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Start frontend
cd frontend
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

---

## Google Cloud Platform Deployment

### 1. Project Setup

```bash
# Create GCP project
gcloud projects create gastric-adci-platform --name="Gastric ADCI Platform"
gcloud config set project gastric-adci-platform

# Enable required APIs
gcloud services enable \
  cloudsql-admin.googleapis.com \
  container.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com
```

### 2. Database Setup (Cloud SQL)

```bash
# Create PostgreSQL instance
gcloud sql instances create gastric-adci-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=20GB \
  --backup-start-time=03:00

# Create database
gcloud sql databases create gastric_adci --instance=gastric-adci-db

# Create user
gcloud sql users create gastric_user \
  --instance=gastric-adci-db \
  --password=your-secure-password
```

### 3. Redis Setup (Memory Store)

```bash
# Create Redis instance
gcloud redis instances create gastric-adci-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_6_x
```

### 4. Secret Management

```bash
# Create secrets
echo -n "your-secret-key" | gcloud secrets create secret-key --data-file=-
echo -n "postgresql://user:pass@/db" | gcloud secrets create database-url --data-file=-
echo -n "redis://redis-ip:6379" | gcloud secrets create redis-url --data-file=-
echo -n "your-jwt-secret" | gcloud secrets create jwt-secret --data-file=-
```

### 5. Container Build and Deploy

#### Build Docker Images

```bash
# Build backend image
docker build -t gcr.io/gastric-adci-platform/backend:latest -f backend/Dockerfile .

# Build frontend image  
docker build -t gcr.io/gastric-adci-platform/frontend:latest -f frontend/Dockerfile .

# Push to Container Registry
docker push gcr.io/gastric-adci-platform/backend:latest
docker push gcr.io/gastric-adci-platform/frontend:latest
```

#### Deploy to Cloud Run

**Backend Service:**
```bash
gcloud run deploy gastric-adci-backend \
  --image gcr.io/gastric-adci-platform/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-secrets "SECRET_KEY=secret-key:latest" \
  --set-secrets "DATABASE_URL=database-url:latest" \
  --set-secrets "REDIS_URL=redis-url:latest" \
  --set-secrets "JWT_SECRET_KEY=jwt-secret:latest"
```

**Frontend Service:**
```bash
gcloud run deploy gastric-adci-frontend \
  --image gcr.io/gastric-adci-platform/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars "API_BASE_URL=https://gastric-adci-backend-url"
```

### 6. Load Balancer Setup

```yaml
# load-balancer.yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: gastric-adci-ssl-cert
spec:
  domains:
    - gastric-adci.your-domain.com
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gastric-adci-ingress
  annotations:
    kubernetes.io/ingress.global-static-ip-name: gastric-adci-ip
    networking.gke.io/managed-certificates: gastric-adci-ssl-cert
    kubernetes.io/ingress.class: "gce"
spec:
  rules:
  - host: gastric-adci.your-domain.com
    http:
      paths:
      - path: /api/*
        pathType: ImplementationSpecific
        backend:
          service:
            name: gastric-adci-backend
            port:
              number: 80
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: gastric-adci-frontend
            port:
              number: 80
```

---

## Environment Configuration

### Production Environment Variables

```bash
# Core Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis-host:6379/0
REDIS_POOL_SIZE=10

# Security
SECRET_KEY=your-256-bit-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=https://your-domain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=*

# File Storage
IPFS_API_URL=https://your-ipfs-node:5001
IPFS_GATEWAY_URL=https://your-ipfs-gateway:8080

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-new-relic-key

# Gun.js Server
GUNDB_PEERS=https://gun1.your-domain.com,https://gun2.your-domain.com
```

### Development Environment

```bash
# Development overrides
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql+asyncpg://localhost:5432/gastric_adci_dev
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8001
```

---

## Database Migrations

### Running Migrations

```bash
# Production migration
python -m backend.src.db.migrations.001_create_cohort_tables

# Check migration status
python -c "
import asyncio
from backend.src.db.database import get_async_session
from sqlalchemy import text

async def check_tables():
    async with get_async_session() as session:
        result = await session.execute(text('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\''))
        tables = [row[0] for row in result.fetchall()]
        print('Tables:', tables)

asyncio.run(check_tables())
"
```

### Migration Rollback (if needed)

```sql
-- Rollback cohort tables
DROP TABLE IF EXISTS cohort_hypotheses CASCADE;
DROP TABLE IF EXISTS cohort_export_tasks CASCADE;
DROP TABLE IF EXISTS patient_decision_results CASCADE;
DROP TABLE IF EXISTS inference_sessions CASCADE;
DROP TABLE IF EXISTS cohort_patients CASCADE;
DROP TABLE IF EXISTS cohort_studies CASCADE;

-- Drop enum types
DROP TYPE IF EXISTS cohort_upload_format;
DROP TYPE IF EXISTS cohort_status;
DROP TYPE IF EXISTS inference_status;
```

---

## Monitoring and Logging

### Application Logging

```python
# Configure structured logging
import structlog
import logging

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Health Checks

```python
# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    checks = {}
    
    # Database check
    try:
        async with get_async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Redis check
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if all(c == "healthy" for c in checks.values()) else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Monitoring Setup

```bash
# Install monitoring agents
pip install sentry-sdk[fastapi] newrelic

# Configure Sentry
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)

# Configure New Relic
export NEW_RELIC_LICENSE_KEY=your-license-key
export NEW_RELIC_APP_NAME=gastric-adci-platform
newrelic-admin run-program uvicorn src.main:app
```

---

## Security Configuration

### SSL/TLS Setup

```bash
# Create SSL certificate
gcloud compute ssl-certificates create gastric-adci-ssl \
  --domains gastric-adci.your-domain.com

# Configure HTTPS redirect
gcloud compute url-maps create gastric-adci-https-redirect \
  --default-service=gastric-adci-backend-service
```

### Security Headers

```python
# Add security middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["gastric-adci.your-domain.com", "*.your-domain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gastric-adci.your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Data Encryption

```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
```

---

## Backup and Recovery

### Database Backup

```bash
# Automated daily backups
gcloud sql backups create \
  --instance=gastric-adci-db \
  --description="Daily backup $(date +%Y%m%d)"

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --restore-instance=gastric-adci-db-restore \
  --backup-instance=gastric-adci-db
```

### File Storage Backup

```bash
# IPFS backup script
#!/bin/bash
BACKUP_DIR="/backups/ipfs/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Export IPFS data
ipfs repo gc
ipfs pin ls --type recursive > $BACKUP_DIR/pinned_hashes.txt
ipfs repo stat > $BACKUP_DIR/repo_stats.txt

# Backup to cloud storage
gsutil -m cp -r $BACKUP_DIR gs://gastric-adci-backups/ipfs/
```

### Application Data Export

```python
# Export cohort data
async def export_all_cohorts():
    async with get_async_session() as session:
        cohorts = await session.execute(
            select(CohortStudy).options(
                selectinload(CohortStudy.patients),
                selectinload(CohortStudy.sessions)
            )
        )
        
        export_data = []
        for cohort in cohorts.scalars():
            export_data.append({
                "study": cohort.to_dict(),
                "patients": [p.to_dict() for p in cohort.patients],
                "sessions": [s.to_dict() for s in cohort.sessions]
            })
        
        return export_data
```

---

## Performance Optimization

### Database Optimization

```sql
-- Optimize frequently used queries
CREATE INDEX CONCURRENTLY idx_cohort_patients_clinical_params_gin 
ON cohort_patients USING GIN (clinical_parameters);

CREATE INDEX CONCURRENTLY idx_patient_results_scores 
ON patient_decision_results (confidence_score, risk_score);

-- Update table statistics
ANALYZE cohort_studies;
ANALYZE cohort_patients;
ANALYZE patient_decision_results;
```

### Caching Strategy

```python
# Redis caching
import redis.asyncio as redis
from functools import wraps

redis_client = redis.from_url(settings.REDIS_URL)

def cache_result(timeout: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(timeout=600)
async def get_cohort_summary(cohort_id: str):
    # Expensive computation
    pass
```

### Load Testing

```bash
# Install Artillery
npm install -g artillery

# Load test configuration
# artillery.yml
config:
  target: 'https://gastric-adci.your-domain.com'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "API Load Test"
    flow:
      - get:
          url: "/api/v1/cohorts"
          headers:
            Authorization: "Bearer {{ token }}"

# Run load test
artillery run artillery.yml
```

---

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
gcloud sql instances describe gastric-adci-db
gcloud sql operations list --instance=gastric-adci-db

# Test connection
psql "postgresql://user:pass@host:5432/db" -c "SELECT version();"
```

#### Cloud Run Issues
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Check service status
gcloud run services describe gastric-adci-backend --region=us-central1

# Update service
gcloud run services update gastric-adci-backend \
  --region=us-central1 \
  --memory=4Gi
```

#### IPFS Issues
```bash
# Check IPFS node status
curl -X POST http://your-ipfs-node:5001/api/v0/id

# Restart IPFS
systemctl restart ipfs
```

### Performance Issues

#### Slow Queries
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
SELECT pg_reload_conf();

-- Analyze slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

#### Memory Issues
```bash
# Monitor memory usage
gcloud monitoring dashboards list
gcloud logging read "severity=ERROR" --limit=20

# Scale up if needed
gcloud run services update gastric-adci-backend \
  --memory=8Gi \
  --cpu=4
```

---

## Maintenance

### Regular Maintenance Tasks

```bash
#!/bin/bash
# Daily maintenance script

# 1. Database maintenance
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# 2. Clear old logs
find /var/log/gastric-adci -name "*.log" -mtime +7 -delete

# 3. IPFS garbage collection
ipfs repo gc

# 4. Check disk space
df -h

# 5. Update system packages (if applicable)
apt update && apt upgrade -y
```

### Scaling

```bash
# Scale Cloud Run services
gcloud run services update gastric-adci-backend \
  --min-instances=1 \
  --max-instances=10 \
  --concurrency=100

# Scale database
gcloud sql instances patch gastric-adci-db \
  --tier=db-n1-standard-2
```

---

## Support and Documentation

### Additional Resources
- **GCP Documentation**: https://cloud.google.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **PostgreSQL Documentation**: https://www.postgresql.org/docs
- **Redis Documentation**: https://redis.io/documentation

### Support Contacts
- **Technical Issues**: devops@gastric-adci.health
- **Security Issues**: security@gastric-adci.health
- **Emergency Contact**: +1-XXX-XXX-XXXX

---

This deployment guide provides a comprehensive foundation for deploying the Gastric ADCI Platform to production. Customize the configurations based on your specific requirements and infrastructure constraints.
