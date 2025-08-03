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
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
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

test:
	python tasks.py test

test-cov:
	python tasks.py test --coverage

check:
	python tasks.py check

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
