#!/bin/bash
# Contabo Server Setup Script for Yaz & Surgify Platform
# This script sets up the production and staging servers on Contabo with Coolify

set -e

# Configuration
PYTHON_VERSION="3.11"
NODE_VERSION="18"
DOCKER_COMPOSE_VERSION="2.21.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi

log "🚀 Starting Contabo server setup for Yaz & Surgify Platform..."

# Update system
log "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
log "📦 Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    fail2ban \
    ufw \
    nginx \
    certbot \
    python3-certbot-nginx \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Configure firewall
log "🔥 Configuring UFW firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Surgify API
sudo ufw allow 3000/tcp  # Coolify
sudo ufw --force enable

# Configure fail2ban
log "🛡️ Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Install Docker
log "🐳 Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose standalone
log "🐳 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python
log "🐍 Installing Python ${PYTHON_VERSION}..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-pip python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev

# Install Node.js
log "📦 Installing Node.js ${NODE_VERSION}..."
curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
sudo apt install -y nodejs

# Install Coolify
log "🚀 Installing Coolify..."
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Wait for Coolify to be ready
log "⏳ Waiting for Coolify to be ready..."
sleep 30

# Create application directories
log "📁 Creating application directories..."
sudo mkdir -p /opt/yaz-surgify/{staging,production}
sudo chown -R $USER:$USER /opt/yaz-surgify

# Create environment files
log "⚙️ Creating environment configuration..."
cat > /opt/yaz-surgify/staging/.env << EOF
# Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=false
SECRET_KEY=staging-secret-key-$(openssl rand -hex 32)
JWT_SECRET=staging-jwt-secret-$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://surgify_staging:$(openssl rand -hex 16)@localhost:5432/surgify_staging

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=https://staging.surgify.com,https://staging.yaz.com

# SSL
SSL_ENABLED=true
EOF

cat > /opt/yaz-surgify/production/.env << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=production-secret-key-$(openssl rand -hex 32)
JWT_SECRET=production-jwt-secret-$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://surgify_prod:$(openssl rand -hex 16)@localhost:5432/surgify_production

# Redis
REDIS_URL=redis://localhost:6379/1

# Application
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=WARNING

# CORS
CORS_ORIGINS=https://surgify.com,https://yaz.com

# SSL
SSL_ENABLED=true
EOF

# Set proper permissions
chmod 600 /opt/yaz-surgify/staging/.env
chmod 600 /opt/yaz-surgify/production/.env

# Create Docker Compose file for services
log "🐳 Creating Docker Compose configuration..."
cat > /opt/yaz-surgify/docker-compose.services.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: surgify_production
      POSTGRES_USER: surgify_prod
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U surgify_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres_staging:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: surgify_staging
      POSTGRES_USER: surgify_staging
      POSTGRES_PASSWORD: \${POSTGRES_STAGING_PASSWORD}
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U surgify_staging"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - surgify_production
      - surgify_staging

volumes:
  postgres_data:
  postgres_staging_data:
  redis_data:
EOF

# Create nginx configuration
log "🌐 Creating Nginx configuration..."
sudo mkdir -p /opt/yaz-surgify/nginx/conf.d

cat > /opt/yaz-surgify/nginx/conf.d/surgify.conf << 'EOF'
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;

# Production server
server {
    listen 80;
    server_name surgify.com www.surgify.com yaz.com www.yaz.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name surgify.com www.surgify.com yaz.com www.yaz.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/surgify.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/surgify.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting
    limit_req zone=web burst=20 nodelay;

    # Main application
    location / {
        proxy_pass http://surgify_production:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # API endpoints with separate rate limiting
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://surgify_production:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://surgify_production:8000/health;
        access_log off;
    }
}

# Staging server
server {
    listen 80;
    server_name staging.surgify.com staging.yaz.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name staging.surgify.com staging.yaz.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/staging.surgify.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.surgify.com/privkey.pem;

    # Basic auth for staging
    auth_basic "Staging Environment";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://surgify_staging:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Create SSL certificates
log "🔐 Setting up SSL certificates..."
sudo certbot --nginx -d surgify.com -d www.surgify.com -d yaz.com -d www.yaz.com --non-interactive --agree-tos --email admin@surgify.com
sudo certbot --nginx -d staging.surgify.com -d staging.yaz.com --non-interactive --agree-tos --email admin@surgify.com

# Create monitoring setup
log "📊 Setting up monitoring..."
cat > /opt/yaz-surgify/docker-compose.monitoring.yml << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123!
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
EOF

# Create backup script
log "💾 Creating backup script..."
cat > /opt/yaz-surgify/backup.sh << 'EOF'
#!/bin/bash
# Backup script for Yaz & Surgify Platform

BACKUP_DIR="/opt/yaz-surgify/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker exec postgres pg_dump -U surgify_prod surgify_production | gzip > $BACKUP_DIR/db_production_$DATE.sql.gz
docker exec postgres_staging pg_dump -U surgify_staging surgify_staging | gzip > $BACKUP_DIR/db_staging_$DATE.sql.gz

# Application data backup
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz /opt/yaz-surgify/production/data /opt/yaz-surgify/staging/data

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/yaz-surgify/backup.sh

# Create systemd service for backups
sudo tee /etc/systemd/system/yaz-surgify-backup.service << EOF
[Unit]
Description=Yaz & Surgify Backup Service
After=docker.service

[Service]
Type=oneshot
ExecStart=/opt/yaz-surgify/backup.sh
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/yaz-surgify-backup.timer << EOF
[Unit]
Description=Run Yaz & Surgify backup daily
Requires=yaz-surgify-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl enable yaz-surgify-backup.timer
sudo systemctl start yaz-surgify-backup.timer

# Create health check script
log "🏥 Creating health check script..."
cat > /opt/yaz-surgify/health-check.sh << 'EOF'
#!/bin/bash
# Health check script for Yaz & Surgify Platform

PRODUCTION_URL="https://surgify.com"
STAGING_URL="https://staging.surgify.com"

check_endpoint() {
    local url=$1
    local name=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url/health")
    if [ "$response" = "200" ]; then
        echo "✅ $name is healthy"
        return 0
    else
        echo "❌ $name is unhealthy (HTTP $response)"
        return 1
    fi
}

# Check production
check_endpoint "$PRODUCTION_URL" "Production"
production_status=$?

# Check staging
check_endpoint "$STAGING_URL" "Staging"
staging_status=$?

# Check database connectivity
docker exec postgres pg_isready -U surgify_prod > /dev/null 2>&1
db_status=$?

if [ $db_status -eq 0 ]; then
    echo "✅ Database is healthy"
else
    echo "❌ Database is unhealthy"
fi

# Overall status
if [ $production_status -eq 0 ] && [ $staging_status -eq 0 ] && [ $db_status -eq 0 ]; then
    echo "🎉 All systems healthy"
    exit 0
else
    echo "⚠️ Some systems are unhealthy"
    exit 1
fi
EOF

chmod +x /opt/yaz-surgify/health-check.sh

# Start services
log "🚀 Starting infrastructure services..."
cd /opt/yaz-surgify
docker-compose -f docker-compose.services.yml up -d

# Wait for services to be ready
log "⏳ Waiting for services to be ready..."
sleep 60

# Run health check
log "🏥 Running initial health check..."
./health-check.sh

# Final steps
log "✅ Server setup completed successfully!"
warn "Please remember to:"
warn "1. Configure your DNS to point to this server"
warn "2. Update the environment variables in /opt/yaz-surgify/staging/.env and /opt/yaz-surgify/production/.env"
warn "3. Deploy your application using Coolify"
warn "4. Set up monitoring alerts"

log "🎉 Yaz & Surgify platform infrastructure is ready!"
log "🌐 Coolify dashboard: http://$(curl -s ifconfig.me):3000"
log "📊 Monitoring: http://$(curl -s ifconfig.me):3001"
log "🏥 Health check: /opt/yaz-surgify/health-check.sh"
log "💾 Backup service: systemctl status yaz-surgify-backup.timer"
EOF
