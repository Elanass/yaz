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
	@echo "  make test-compatibility - Run backward compatibility tests"
	@echo "  make demo-integration - Run integration demonstration"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo ""
	@echo "Domain Support (Phase 1.1):"
	@echo "  make check-domains - Validate all domain adapters"
	@echo "  make dev-surgery   - Start server in surgery domain mode"
	@echo "  make dev-logistics - Start server in logistics domain mode"
	@echo "  make dev-insurance - Start server in insurance domain mode"
	@echo ""
	@echo "Deployment:"
	@echo "  make build      - Build Docker image"
	@echo "  make deploy     - Deploy to production"
	@echo "  make deploy-dev - Deploy development environment"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make logs       - View application logs"
	@echo "  test-cov       Run tests with coverage"
	@echo "  check          Run all code quality checks"
	@echo ""
	@echo "Server:"
	@echo "  dev            Run development server"
	@echo "  prod           Run production server"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          Clean build artifacts"

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

test-api:
	pytest tests/api/ -v

test-integration:
	pytest tests/integration/ -v

test-unit:
	pytest tests/unit/ -v

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
