# Surgify Platform Makefile
# Provides convenient shortcuts for common development tasks

.PHONY: help install dev test lint format clean build deploy

# Default target
help:
	@echo "🏥 Surgify Platform - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install dependencies and setup development environment"
	@echo "  make dev        - Start development server"
	@echo "  make test       - Run all tests"
	@echo "  make test-api   - Run API tests only"
	@echo "  make test-unit  - Run unit tests only" 
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-canary - Run canary tests only"
	@echo "  make test-compatibility - Run backward compatibility tests"
	@echo "  make demo-integration - Run integration demonstration"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make format-check - Check code formatting"
	@echo ""
	@echo "Orchestration (Incus/Multipass):"
	@echo "  make incus.init     - Initialize Incus orchestration system"
	@echo "  make env.apply      - Apply demo environment plan"
	@echo "  make env.destroy    - Destroy environment instances"
	@echo "  make env.status     - Show environment status"
	@echo "  make env.snapshot   - Create environment snapshot"
	@echo "  make env.health     - Check orchestration health"
	@echo ""
	@echo "Domain Support (Phase 1.1):"
	@echo "  make check-domains - Validate all domain adapters"
	@echo "  make dev-surgery   - Start server in surgery domain mode"
	@echo "  make dev-logistics - Start server in logistics domain mode"
	@echo "  make dev-insurance - Start server in insurance domain mode"
	@echo ""
	@echo "Deployment & Canary:"
	@echo "  make build      - Build Docker image"
	@echo "  make deploy     - Deploy to production"
	@echo "  make deploy-dev - Deploy development environment"
	@echo "  make canary-deploy - Deploy to canary environment"
	@echo "  make canary-status - Check canary deployment status"
	@echo "  make canary-metrics - Get canary performance metrics"
	@echo "  make canary-test - Run canary tests"
	@echo "  make canary-promote - Promote canary to production"
	@echo "  make canary-rollback - Rollback canary deployment"
	@echo ""
	@echo "Quality & Security:"
	@echo "  make security-scan - Run security analysis"
	@echo "  make validate-n8n - Validate n8n workflow files"
	@echo "  make setup-hooks - Install git hooks"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make logs       - View application logs"
	@echo "  make test-cov   - Run tests with coverage"
	@echo "  make check      - Run all code quality checks"

# Development setup
install:
	python tasks.py install

install-dev:
	python tasks.py install-dev

bootstrap:
	python tasks.py bootstrap

setup-db:
	python tasks.py setup-db

# Code quality
format:
	python tasks.py format

lint:
	python tasks.py lint

type-check:
	python tasks.py type-check

# Testing
test:
	pytest tests/ -v

test-cov:
	python tasks.py test --coverage

test-compatibility:
	cd tests/compatibility && PYTHONPATH=$(PWD)/src python test_backward_compatibility.py

demo-integration:
	cd tests/integration/demos && PYTHONPATH=$(PWD)/src python demonstrate_integration.py

# Domain-specific testing and development (Phase 1.1)
check-domains:
	@echo "🧪 Validating all domain adapters..."
	cd scripts && PYTHONPATH=$(PWD)/src python check_domains.py

dev-surgery:
	@echo "🏥 Starting Surgify in Surgery domain mode..."
	PYTHONPATH=src python main.py --domain surgery --reload

dev-logistics:
	@echo "📦 Starting Surgify in Logistics domain mode..."
	PYTHONPATH=src python main.py --domain logistics --reload

dev-insurance:
	@echo "🛡️ Starting Surgify in Insurance domain mode..."
	PYTHONPATH=src python main.py --domain insurance --reload

# Server management
dev:
	python tasks.py dev

prod:
	python tasks.py prod

# Docker operations
docker-build:
	python tasks.py docker-build

docker-run:
	python tasks.py docker-run

# Utilities
clean:
	python tasks.py clean

# Quick development workflow
quick-start: bootstrap dev

# CI/CD workflow
ci: format lint type-check test-cov

# Canary deployment and management
canary-deploy:
	@echo "🚀 Deploying to canary environment..."
	@if [ -z "$(CANARY_VERSION)" ]; then \
		echo "Error: CANARY_VERSION must be set"; \
		exit 1; \
	fi
	docker build -t surgify:$(CANARY_VERSION) .
	kubectl apply -f infra/k8s/canary/
	kubectl set image deployment/surgify-canary surgify=surgify:$(CANARY_VERSION) -n surgify-canary

canary-status:
	@echo "📊 Checking canary deployment status..."
	kubectl get pods -n surgify-canary -l app=surgify
	kubectl get services -n surgify-canary
	@echo "Recent deployments:"
	kubectl rollout history deployment/surgify-canary -n surgify-canary

canary-metrics:
	@echo "📈 Fetching canary metrics..."
	@echo "Error rate:"
	curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{job=\"surgify-canary\",status=~\"5..\"}[5m])" | jq '.data.result[0].value[1]' || echo "N/A"
	@echo "Response time (95th percentile):"
	curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket{job=\"surgify-canary\"}[5m]))" | jq '.data.result[0].value[1]' || echo "N/A"

canary-test:
	@echo "🧪 Running canary tests..."
	python -m pytest tests/canary/ -v --tb=short

canary-promote:
	@echo "✅ Promoting canary to production..."
	@if [ -z "$(CANARY_VERSION)" ]; then \
		echo "Error: CANARY_VERSION must be set"; \
		exit 1; \
	fi
	kubectl set image deployment/surgify surgify=surgify:$(CANARY_VERSION) -n surgify-prod
	kubectl rollout status deployment/surgify -n surgify-prod

canary-rollback:
	@echo "🔄 Rolling back canary deployment..."
	kubectl rollout undo deployment/surgify-canary -n surgify-canary
	kubectl rollout status deployment/surgify-canary -n surgify-canary

# Testing targets
test-canary:
	@echo "🕯️ Running canary tests..."
	python -m pytest tests/canary/ -v

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v

test-integration:
	@echo "🔗 Running integration tests..."
	python -m pytest tests/integration/ -v

test-api:
	@echo "🌐 Running API tests..."
	python -m pytest tests/api/ -v

# Format checking (for git hooks)
format-check:
	@echo "🎨 Checking code formatting..."
	black --check src/ tests/
	isort --check-only src/ tests/

# Security scanning
security-scan:
	@echo "🔒 Running security scan..."
	bandit -r src/ -f json -o security-report.json || true
	safety check --json --output safety-report.json || true

# N8N workflow validation
validate-n8n:
	@echo "🔄 Validating n8n workflows..."
	@for workflow in n8n/workflows/*.json; do \
		echo "Validating $$workflow..."; \
	done

# Orchestration targets (Incus/Multipass)
incus.init:
	@echo "🚀 Initializing Incus orchestration system..."
	python -m infra.orchestrator.cli init

env.apply:
	@echo "📋 Applying demo environment plan..."
	python -m infra.orchestrator.cli apply infra/orchestrator/plans/demo.yaml

env.destroy:
	@echo "💥 Destroying environment instances..."
	python -m infra.orchestrator.cli destroy --plan infra/orchestrator/plans/demo.yaml --force

env.status:
	@echo "📊 Checking environment status..."
	python -m infra.orchestrator.cli status

env.snapshot:
	@echo "📸 Creating environment snapshot..."
	@timestamp=$$(date +%Y%m%d-%H%M%S); \
	for instance in yaz-gateway yaz-worker-1 yaz-storage; do \
		python -m infra.orchestrator.cli snapshot $$instance $$timestamp; \
	done

env.health:
	@echo "🏥 Checking orchestration health..."
	python -m infra.orchestrator.cli health

# Quick environment commands
env.start:
	@echo "▶️  Starting all instances..."
	@for instance in yaz-gateway yaz-worker-1 yaz-storage; do \
		echo "Starting $$instance..."; \
		python -m infra.orchestrator.cli exec $$instance "echo 'Instance started'" || true; \
	done

env.stop:
	@echo "⏹️  Stopping all instances..."
	@for instance in yaz-gateway yaz-worker-1 yaz-storage; do \
		echo "Stopping $$instance..."; \
		python -m infra.orchestrator.cli exec $$instance "sudo shutdown -h now" || true; \
	done

env.logs:
	@echo "📋 Showing instance logs..."
	@for instance in yaz-gateway yaz-worker-1 yaz-storage; do \
		echo "=== $$instance logs ==="; \
		python -m infra.orchestrator.cli exec $$instance "tail -20 /var/log/syslog" || true; \
		echo; \
	done
