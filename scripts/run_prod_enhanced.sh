#!/bin/bash

# Enhanced Production Deployment Script for YAZ Surgery Analytics Platform
# Handles environment setup, license validation, cleanup, and monitoring

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_ROOT}/logs/deployment.log"
ENV_FILE="${PROJECT_ROOT}/.env"
COMPOSE_FILE="${PROJECT_ROOT}/deploy/prod/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; echo -e "${BLUE}ℹ${NC} $*"; }
log_warn() { log "WARN" "$@"; echo -e "${YELLOW}⚠${NC} $*"; }
log_error() { log "ERROR" "$@"; echo -e "${RED}✗${NC} $*"; }
log_success() { log "SUCCESS" "$@"; echo -e "${GREEN}✓${NC} $*"; }

# Error handler
error_exit() {
    log_error "Deployment failed: $1"
    cleanup_on_error
    exit 1
}

# Cleanup function
cleanup_on_error() {
    log_warn "Performing emergency cleanup..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
}

# Prerequisites check
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "python3" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error_exit "Required command not found: $cmd"
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error_exit "Docker daemon is not running"
    fi
    
    # Check Python environment
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        error_exit "Python 3.8+ is required"
    fi
    
    log_success "Prerequisites check passed"
}

# License validation
validate_licenses() {
    log_info "Validating license compliance..."
    
    # Run license validator
    if [ -f "${PROJECT_ROOT}/core/utils/license_validator.py" ]; then
        cd "$PROJECT_ROOT"
        python3 -m core.utils.license_validator --format summary > /tmp/license_report.txt 2>&1
        
        # Check for compliance issues
        if grep -q "incompatible\|unknown\|failed" /tmp/license_report.txt; then
            log_warn "License compliance issues detected:"
            cat /tmp/license_report.txt
            read -p "Continue deployment despite license issues? [y/N]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                error_exit "Deployment cancelled due to license compliance issues"
            fi
        else
            log_success "License compliance validated"
        fi
        rm -f /tmp/license_report.txt
    else
        log_warn "License validator not found, skipping license check"
    fi
}

# Environment setup
setup_environment() {
    log_info "Setting up production environment..."
    
    # Create logs directory
    mkdir -p "${PROJECT_ROOT}/logs"
    
    # Check for .env file
    if [ ! -f "$ENV_FILE" ]; then
        log_info "Creating .env file from template..."
        cat > "$ENV_FILE" << EOF
# Production Environment Configuration
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 16)
API_BASE_URL=https://$(hostname)/api/v1
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_SWAGGER=false
PATIENT_DATA_ENCRYPTION=true
ENABLE_AUDIT_LOGGING=true
APP_REPLICAS=2
WORKER_REPLICAS=2
API_WORKERS=4
MAX_REQUESTS=1000
EOF
        log_success "Environment file created"
    else
        log_info "Using existing environment file"
    fi
    
    # Source environment
    set -a
    source "$ENV_FILE"
    set +a
}

# Cache cleanup
cleanup_cache() {
    log_info "Cleaning up cache and temporary files..."
    
    # Run the cache cleanup script if it exists
    if [ -f "${PROJECT_ROOT}/scripts/clean_cache.sh" ]; then
        bash "${PROJECT_ROOT}/scripts/clean_cache.sh"
    else
        # Fallback cleanup
        find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
        find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
        find "$PROJECT_ROOT" -type f -name "*~" -delete 2>/dev/null || true
    fi
    
    log_success "Cache cleanup completed"
}

# Build and test
build_and_test() {
    log_info "Building application..."
    
    cd "$PROJECT_ROOT"
    
    # Build Docker images
    if ! docker-compose -f "$COMPOSE_FILE" build --no-cache; then
        error_exit "Docker build failed"
    fi
    
    # Run quick health check
    log_info "Running application health check..."
    
    # Start services temporarily for testing
    docker-compose -f "$COMPOSE_FILE" up -d db redis
    
    # Wait for services to be ready
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U adci_user -d adci_db; then
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error_exit "Database failed to start within timeout"
    fi
    
    # Stop temporary services
    docker-compose -f "$COMPOSE_FILE" down
    
    log_success "Build and health check completed"
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Start services
    if ! docker-compose -f "$COMPOSE_FILE" up -d; then
        error_exit "Failed to start services"
    fi
    
    # Wait for application to be ready
    log_info "Waiting for application to be ready..."
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            break
        fi
        attempt=$((attempt + 1))
        sleep 5
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error_exit "Application failed to start within timeout"
    fi
    
    log_success "Application deployed successfully"
}

# Post-deployment verification
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check all services are running
    local services=("db" "redis" "app" "worker")
    for service in "${services[@]}"; do
        if ! docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            error_exit "Service $service is not running"
        fi
    done
    
    # Test API endpoints
    local endpoints=("/health" "/api/v1/results" "/api/v1/reproducibility/report")
    for endpoint in "${endpoints[@]}"; do
        if ! curl -f -s "http://localhost:8000$endpoint" > /dev/null; then
            log_warn "Endpoint $endpoint is not responding"
        fi
    done
    
    # Check logs for errors
    if docker-compose -f "$COMPOSE_FILE" logs app | grep -qi "error\|exception\|failed"; then
        log_warn "Errors detected in application logs"
        docker-compose -f "$COMPOSE_FILE" logs --tail=20 app
    fi
    
    log_success "Deployment verification completed"
}

# Generate deployment report
generate_report() {
    log_info "Generating deployment report..."
    
    local report_file="${PROJECT_ROOT}/logs/deployment_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "deployment": {
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "status": "success",
        "version": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
        "environment": "production"
    },
    "services": $(docker-compose -f "$COMPOSE_FILE" ps --format json 2>/dev/null || echo '[]'),
    "system": {
        "hostname": "$(hostname)",
        "uptime": "$(uptime)",
        "disk_usage": "$(df -h / | tail -1)",
        "memory_usage": "$(free -h | grep Mem)"
    }
}
EOF
    
    log_success "Deployment report saved to: $report_file"
}

# Monitoring setup
setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Check if monitoring services are configured
    if docker-compose -f "$COMPOSE_FILE" ps prometheus grafana | grep -q "Up"; then
        log_info "Monitoring services are running"
        log_info "Grafana dashboard: http://localhost:3000"
        log_info "Prometheus metrics: http://localhost:9090"
    else
        log_warn "Monitoring services not configured"
    fi
    
    # Setup log rotation
    if command -v logrotate &> /dev/null; then
        cat > /etc/logrotate.d/yaz-surgery-analytics << EOF
${PROJECT_ROOT}/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
        log_success "Log rotation configured"
    fi
}

# Display deployment info
show_deployment_info() {
    echo
    echo "======================================"
    echo "🏥 YAZ Surgery Analytics Platform"
    echo "======================================"
    echo
    echo "✅ Deployment Status: SUCCESS"
    echo "🌐 Application URL: http://localhost:8000"
    echo "📊 Dashboard: http://localhost:8000/dashboard"
    echo "📋 API Documentation: http://localhost:8000/docs"
    echo "📈 Monitoring: http://localhost:3000 (Grafana)"
    echo "📝 Logs: ${PROJECT_ROOT}/logs/"
    echo
    echo "🔧 Management Commands:"
    echo "  View logs:     docker-compose -f $COMPOSE_FILE logs -f"
    echo "  Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "  Restart:       docker-compose -f $COMPOSE_FILE restart"
    echo "  Scale up:      docker-compose -f $COMPOSE_FILE up -d --scale app=3"
    echo
    echo "📚 Documentation: ${PROJECT_ROOT}/docs/"
    echo "⚖️  License Info: ${PROJECT_ROOT}/docs/legal/"
    echo
}

# Main execution
main() {
    log_info "Starting YAZ Surgery Analytics Platform deployment..."
    log_info "Project root: $PROJECT_ROOT"
    
    check_prerequisites
    validate_licenses
    setup_environment
    cleanup_cache
    build_and_test
    deploy_application
    verify_deployment
    setup_monitoring
    generate_report
    
    log_success "Deployment completed successfully!"
    show_deployment_info
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "YAZ Surgery Analytics Platform - Production Deployment"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Clean deployment (remove volumes)"
        echo "  --logs         Show application logs"
        echo "  --status       Show deployment status"
        echo
        exit 0
        ;;
    --clean)
        log_info "Performing clean deployment..."
        docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
        docker system prune -f
        ;;
    --logs)
        docker-compose -f "$COMPOSE_FILE" logs -f
        exit 0
        ;;
    --status)
        docker-compose -f "$COMPOSE_FILE" ps
        exit 0
        ;;
esac

# Run main deployment
main "$@"
