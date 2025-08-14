# Operations Guide

## Overview

This document provides operational guidance for running, monitoring, and maintaining the YAZ Healthcare Platform in production environments.

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- PostgreSQL 14+ (for production database)
- Redis 6+ (for caching and sessions)
- HTTPS certificates (Let's Encrypt recommended)
- Minimum 4GB RAM, 2 CPU cores

### Environment Configuration

```bash
# Copy and customize environment file
cp .env.example .env.production

# Required production variables
export YAZ_ENV=production
export YAZ_SECRET_KEY="$(openssl rand -hex 32)"
export YAZ_DATABASE_URL="postgresql://user:pass@host:5432/yaz_prod"
export YAZ_REDIS_URL="redis://redis:6379/0"
export YAZ_LOG_LEVEL=INFO
```

### Deployment Steps

```bash
# 1. Build production image
make docker-build

# 2. Run database migrations
make db-migrate

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify health
make health-check
```

## Monitoring and Observability

### Health Checks

The platform exposes health check endpoints:

- `/health` - Basic application health
- `/health/db` - Database connectivity
- `/health/fhir` - FHIR backend status
- `/health/orthanc` - Orthanc PACS status

### Logging

Structured JSON logging is configured with:

- **INFO**: Normal operations, user actions
- **WARNING**: Recoverable errors, performance issues
- **ERROR**: Application errors, failed requests
- **CRITICAL**: System failures, security incidents

Log locations:
- Application: `/data/logs/application.log`
- Errors: `/data/logs/errors.log`
- Healthcare modules: `/data/logs/surgify.log`

### Metrics and Alerts

Key metrics to monitor:

1. **Application Metrics**
   - Request rate and latency
   - Error rates by endpoint
   - Database connection pool usage

2. **Healthcare Module Metrics**
   - FHIR proxy response times
   - Orthanc storage utilization
   - SMART on FHIR token refresh rates

3. **Infrastructure Metrics**
   - CPU and memory usage
   - Disk space utilization
   - Network connectivity

### Recommended Alerts

```yaml
# Example alert thresholds
alerts:
  - name: high_error_rate
    condition: error_rate > 5%
    severity: warning
  
  - name: fhir_backend_down
    condition: fhir_health_check = false
    severity: critical
  
  - name: disk_space_low
    condition: disk_usage > 85%
    severity: warning
```

## Backup and Recovery

### Database Backups

```bash
# Daily automated backup
0 2 * * * /scripts/backup_database.sh

# Manual backup
make db-backup

# Restore from backup
make db-restore BACKUP_FILE=backup_20240811.sql
```

### File System Backups

```bash
# Backup uploaded files and logs
tar -czf yaz_files_$(date +%Y%m%d).tar.gz \
  /data/uploads \
  /data/logs \
  /data/outputs
```

### Disaster Recovery

1. **RTO (Recovery Time Objective)**: 4 hours
2. **RPO (Recovery Point Objective)**: 1 hour
3. **Backup retention**: 30 days local, 90 days offsite

## Security Operations

### Certificate Management

```bash
# Renew SSL certificates (automated)
certbot renew --quiet

# Manual certificate renewal
certbot certonly --webroot -w /var/www/html -d yaz.example.com
```

### Security Monitoring

Monitor for:
- Failed authentication attempts
- Unusual API access patterns
- PHI access without audit trails
- Expired certificates and tokens

### Incident Response

1. **Immediate Response** (0-15 minutes)
   - Assess impact and scope
   - Notify stakeholders
   - Begin containment

2. **Containment** (15-60 minutes)
   - Isolate affected systems
   - Preserve evidence
   - Implement temporary fixes

3. **Recovery** (1-4 hours)
   - Restore services
   - Verify system integrity
   - Resume normal operations

4. **Post-Incident** (24-48 hours)
   - Document lessons learned
   - Update procedures
   - Implement preventive measures

## Maintenance Windows

### Scheduled Maintenance

- **Weekly**: Security updates (Sunday 02:00-04:00 UTC)
- **Monthly**: Feature deployments (First Saturday 01:00-05:00 UTC)
- **Quarterly**: Major upgrades (Planned 4 weeks in advance)

### Emergency Maintenance

Critical security or stability issues may require emergency maintenance with:
- 2-hour advance notice for non-critical systems
- Immediate action for security vulnerabilities

## Performance Optimization

### Database Optimization

```sql
-- Common performance queries
EXPLAIN ANALYZE SELECT * FROM patients WHERE status = 'active';

-- Index maintenance
REINDEX DATABASE yaz_prod;

-- Table statistics update
ANALYZE;
```

### Application Performance

- Enable Redis caching for frequently accessed data
- Configure connection pooling (min: 5, max: 20)
- Monitor slow query logs
- Implement request rate limiting

### Resource Scaling

```yaml
# Horizontal scaling thresholds
scale_up:
  cpu_usage: > 70%
  memory_usage: > 80%
  response_time: > 2s

scale_down:
  cpu_usage: < 30%
  memory_usage: < 50%
  response_time: < 500ms
```

## Troubleshooting

### Common Issues

1. **FHIR Backend Connectivity**
   ```bash
   # Check FHIR backend status
   curl -f ${FHIR_BASE_URL}/metadata
   
   # Verify network connectivity
   telnet fhir-server 8080
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connectivity
   psql $YAZ_DATABASE_URL -c "SELECT 1;"
   
   # Monitor connection pool
   make db-pool-status
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats yaz_web
   
   # Restart application
   docker-compose restart web
   ```

### Log Analysis

```bash
# Filter error logs
grep "ERROR" /data/logs/application.log | tail -100

# Monitor real-time logs
tail -f /data/logs/application.log | grep -E "(ERROR|WARNING)"

# Analyze performance
grep "slow_query" /data/logs/application.log | awk '{print $5}' | sort -n
```

## Contact Information

### Escalation Matrix

- **Level 1**: Platform team (response: 30 minutes)
- **Level 2**: Senior engineers (response: 1 hour)
- **Level 3**: Architecture team (response: 2 hours)
- **Emergency**: On-call engineer (response: 15 minutes)

### Key Contacts

- **Platform Team**: platform-team@organization.com
- **Security Team**: security@organization.com
- **On-call**: +1-555-ONCALL (1-555-662-2255)

---

For additional operational procedures, see:
- [Security Procedures](SECURITY.md)
- [Testing Guide](TESTING.md)
- [Architecture Overview](ARCHITECTURE.md)
