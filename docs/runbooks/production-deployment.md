# Production Deployment Runbook

This runbook provides step-by-step instructions for deploying Surgify to production environments.

## Prerequisites Checklist

### Infrastructure Requirements
- [ ] **Production Server**: Linux server with 4+ CPU cores, 8GB+ RAM
- [ ] **Database**: PostgreSQL 13+ instance with backup strategy
- [ ] **Cache**: Redis 6+ instance for session and application caching
- [ ] **Load Balancer**: Nginx or cloud load balancer configured
- [ ] **SSL Certificate**: Valid SSL certificate for HTTPS
- [ ] **Domain**: Production domain name configured
- [ ] **Monitoring**: Prometheus/Grafana or cloud monitoring setup

### Security Requirements
- [ ] **Firewall**: Properly configured firewall rules
- [ ] **VPN/Bastion**: Secure access to production environment
- [ ] **Secrets Management**: Secure storage for API keys and credentials
- [ ] **Backup Strategy**: Database and file backup procedures
- [ ] **HTTPS Only**: Force HTTPS redirects configured
- [ ] **Security Headers**: CSP, HSTS, and other security headers

## Environment Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application user
sudo useradd -m -s /bin/bash surgify
sudo usermod -aG docker surgify

# Create application directories
sudo mkdir -p /opt/surgify/{data,logs,backups,uploads}
sudo chown -R surgify:surgify /opt/surgify
```

### 2. Application Deployment

```bash
# Switch to application user
sudo su - surgify
cd /opt/surgify

# Clone repository
git clone https://github.com/surgifyai/yaz.git .
git checkout main

# Setup production environment
cp .env.example .env.production
```

### 3. Environment Configuration

Edit `.env.production` with production values:

```bash
# Core application settings
YAZ_ENV=production
YAZ_SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE
YAZ_DEBUG=false
YAZ_HOST=0.0.0.0
YAZ_PORT=6379

# Database configuration
DATABASE_URL=postgresql://surgify_user:SECURE_PASSWORD@db:5432/surgify_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Cache configuration
REDIS_URL=redis://redis:6379/0
CACHE_DEFAULT_TTL=3600
CACHE_ENABLED=true

# Security settings
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
SESSION_TIMEOUT=3600
JWT_SECRET_KEY=DIFFERENT_SECRET_FOR_JWT
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Feature flags for production
FEATURE_AI_ANALYTICS=true
FEATURE_TEAM_NOTIFICATIONS=true
FEATURE_ADVANCED_CHARTS=true
FEATURE_FILE_UPLOADS=true
FEATURE_DEBUG_TOOLBAR=false

# File upload settings
MAX_UPLOAD_SIZE=50MB
UPLOAD_DIRECTORY=/opt/surgify/uploads

# Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/opt/surgify/logs/surgify.log
LOG_ROTATION=daily

# Email configuration (for notifications)
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=notifications@your-domain.com
SMTP_PASSWORD=SMTP_PASSWORD
SMTP_TLS=true

# Monitoring and health checks
HEALTH_CHECK_ENABLED=true
METRICS_ENABLED=true
METRICS_PATH=/metrics

# Backup configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
```

## Database Setup

### 1. PostgreSQL Configuration

```bash
# Create production database
sudo -u postgres psql << EOF
CREATE USER surgify_user WITH PASSWORD 'SECURE_PASSWORD';
CREATE DATABASE surgify_prod OWNER surgify_user;
GRANT ALL PRIVILEGES ON DATABASE surgify_prod TO surgify_user;
\q
EOF

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
```

Production PostgreSQL settings:
```
# Memory settings
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 64MB
maintenance_work_mem = 512MB

# Connection settings
max_connections = 200
listen_addresses = 'localhost'

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_min_duration_statement = 1000
```

### 2. Database Migration

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm web alembic upgrade head

# Verify migration
docker-compose -f docker-compose.prod.yml run --rm web python -c "
from src.surgify.database.connection import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    print(f'Database version: {result.fetchone()[0]}')
"
```

## Application Deployment

### 1. Build Production Images

```bash
# Build production image
docker build -t surgify:production -f Dockerfile .

# Tag for registry (if using)
docker tag surgify:production your-registry.com/surgify:latest
docker push your-registry.com/surgify:latest
```

### 2. Deploy with Docker Compose

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
```

### 3. SSL/TLS Configuration

Nginx configuration (`/etc/nginx/sites-available/surgify`):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your-domain.crt;
    ssl_certificate_key /path/to/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # File upload size
    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:6379;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /opt/surgify/src/surgify/ui/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /opt/surgify/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
}
```

## Health Checks and Monitoring

### 1. Application Health Checks

```bash
# Basic health check
curl -f http://localhost:6379/health || exit 1

# Detailed health check
curl -f http://localhost:6379/health/ready || exit 1

# Database connectivity
curl -f http://localhost:6379/health/db || exit 1

# Cache connectivity
curl -f http://localhost:6379/health/cache || exit 1
```

### 2. Monitoring Setup

Create monitoring script (`/opt/surgify/scripts/monitor.sh`):

```bash
#!/bin/bash

# Health check endpoints
HEALTH_URL="http://localhost:6379/health"
READY_URL="http://localhost:6379/health/ready"
METRICS_URL="http://localhost:6379/metrics"

# Check application health
check_health() {
    if ! curl -f -s $HEALTH_URL > /dev/null; then
        echo "❌ Health check failed"
        return 1
    fi
    echo "✅ Health check passed"
    return 0
}

# Check application readiness
check_readiness() {
    if ! curl -f -s $READY_URL > /dev/null; then
        echo "❌ Readiness check failed"
        return 1
    fi
    echo "✅ Readiness check passed"
    return 0
}

# Check metrics endpoint
check_metrics() {
    if ! curl -f -s $METRICS_URL | grep -q "surgify_"; then
        echo "❌ Metrics check failed"
        return 1
    fi
    echo "✅ Metrics check passed"
    return 0
}

# Run all checks
echo "Running production health checks..."
check_health && check_readiness && check_metrics
```

Make it executable and add to crontab:
```bash
chmod +x /opt/surgify/scripts/monitor.sh

# Add to crontab for monitoring every 5 minutes
echo "*/5 * * * * /opt/surgify/scripts/monitor.sh >> /opt/surgify/logs/monitor.log 2>&1" | crontab -
```

## Backup and Recovery

### 1. Database Backup

Create backup script (`/opt/surgify/scripts/backup.sh`):

```bash
#!/bin/bash

BACKUP_DIR="/opt/surgify/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP="surgify_backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U surgify_user surgify_prod > "$BACKUP_DIR/$DB_BACKUP"

# Compress backup
gzip "$BACKUP_DIR/$DB_BACKUP"

# Remove backups older than 30 days
find $BACKUP_DIR -name "surgify_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DB_BACKUP.gz"
```

### 2. File Backup

```bash
#!/bin/bash

BACKUP_DIR="/opt/surgify/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILES_BACKUP="surgify_files_$DATE.tar.gz"

# Backup uploaded files
tar -czf "$BACKUP_DIR/$FILES_BACKUP" -C /opt/surgify uploads/

# Remove file backups older than 30 days
find $BACKUP_DIR -name "surgify_files_*.tar.gz" -mtime +30 -delete

echo "File backup completed: $FILES_BACKUP"
```

### 3. Automated Backup Schedule

Add to crontab:
```bash
# Daily database backup at 2 AM
0 2 * * * /opt/surgify/scripts/backup.sh >> /opt/surgify/logs/backup.log 2>&1

# Weekly file backup on Sundays at 3 AM
0 3 * * 0 /opt/surgify/scripts/backup_files.sh >> /opt/surgify/logs/backup.log 2>&1
```

## Disaster Recovery

### 1. Database Recovery

```bash
# Stop application
docker-compose -f docker-compose.prod.yml down

# Restore database from backup
gunzip -c /opt/surgify/backups/surgify_backup_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T db psql -U surgify_user surgify_prod

# Start application
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Complete System Recovery

```bash
# Restore from backup server
rsync -av backup-server:/backups/surgify/ /opt/surgify/backups/

# Restore files
tar -xzf /opt/surgify/backups/surgify_files_LATEST.tar.gz -C /opt/surgify/

# Restore database (see above)

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_cases_status ON cases(status);
CREATE INDEX CONCURRENTLY idx_cases_created_at ON cases(created_at);
CREATE INDEX CONCURRENTLY idx_cases_user_id ON cases(user_id);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Update statistics
ANALYZE;
```

### 2. Application Optimization

```bash
# Increase worker processes
# In docker-compose.prod.yml, set:
# command: gunicorn src.surgify.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:6379

# Enable Redis caching
# Verify Redis is running and accessible
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## Security Hardening

### 1. Application Security

```bash
# Set secure file permissions
chmod 600 .env.production
chmod 700 /opt/surgify/backups
chmod 755 /opt/surgify/uploads

# Regular security updates
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs web

# Check database connection
docker-compose -f docker-compose.prod.yml exec web python -c "
from src.surgify.database.connection import get_engine
engine = get_engine()
print('Database connection successful')
"

# Check environment variables
docker-compose -f docker-compose.prod.yml exec web env | grep YAZ_
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
docker-compose -f docker-compose.prod.yml exec db psql -U surgify_user -d surgify_prod -c "SELECT 1;"

# Reset database connection pool
docker-compose -f docker-compose.prod.yml restart web
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check database performance
docker-compose -f docker-compose.prod.yml exec db psql -U surgify_user -d surgify_prod -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"

# Check Redis performance
docker-compose -f docker-compose.prod.yml exec redis redis-cli info stats
```

## Maintenance Procedures

### 1. Regular Maintenance

```bash
# Weekly maintenance script
#!/bin/bash

echo "Starting weekly maintenance..."

# Update application
cd /opt/surgify
git pull origin main
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Database maintenance
docker-compose -f docker-compose.prod.yml exec db psql -U surgify_user -d surgify_prod -c "VACUUM ANALYZE;"

# Clear old logs
find /opt/surgify/logs -name "*.log" -mtime +7 -delete

# Check disk space
df -h

echo "Weekly maintenance completed"
```

### 2. Security Updates

```bash
# Monthly security updates
sudo apt update && sudo apt upgrade -y
docker system prune -f
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Rollback Procedures

### 1. Application Rollback

```bash
# Rollback to previous version
cd /opt/surgify
git log --oneline -n 10  # Find previous commit
git checkout PREVIOUS_COMMIT_HASH

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Database Rollback

```bash
# Rollback database migration
docker-compose -f docker-compose.prod.yml run --rm web alembic downgrade -1

# Or restore from backup if needed
# (See Disaster Recovery section)
```

## Support and Escalation

### Contact Information
- **Primary Contact**: DevOps Team <devops@surgifyai.com>
- **Secondary Contact**: Development Team <dev@surgifyai.com>
- **Emergency Contact**: CTO <cto@surgifyai.com>

### Escalation Matrix
1. **Level 1**: DevOps Engineer (Response: 15 minutes)
2. **Level 2**: Senior DevOps Engineer (Response: 30 minutes)
3. **Level 3**: Engineering Manager (Response: 1 hour)
4. **Level 4**: CTO (Response: 2 hours)

### Documentation
- **Internal Wiki**: [Confluence Link]
- **Monitoring Dashboard**: [Grafana Link]
- **Incident Management**: [PagerDuty Link]
- **Code Repository**: https://github.com/surgifyai/yaz

---

**Last Updated**: December 2024  
**Version**: 2.0  
**Reviewed By**: DevOps Team
