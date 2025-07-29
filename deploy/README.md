# Deployment Configurations

This directory contains Docker and deployment configurations for different environments.

## Directory Structure

- `dev/`: Development environment configurations
  - `Dockerfile`: Development Docker image with additional tools for development
  - `docker-compose.yml`: Docker Compose configuration for local development

- `test/`: Testing environment configurations
  - `Dockerfile`: Testing Docker image with testing dependencies
  - `docker-compose.yml`: Docker Compose configuration for running tests

- `prod/`: Production environment configurations
  - `Dockerfile`: Production Docker image optimized for performance
  - `docker-compose.yml`: Docker Compose configuration for production deployment

## Usage

### Development Environment

```bash
cd /workspaces/yaz
docker-compose -f deploy/dev/docker-compose.yml up -d
```

### Test Environment

```bash
cd /workspaces/yaz
docker-compose -f deploy/test/docker-compose.yml up
```

### Production Environment

```bash
cd /workspaces/yaz
docker-compose -f deploy/prod/docker-compose.yml up -d
```

## Configuration

Environment-specific configurations are contained in the respective docker-compose.yml files. For additional configuration, please refer to the main README.md file in the project root.
