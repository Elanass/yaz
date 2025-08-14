#!/bin/bash
"""
Multi-VM Deployment Script for Surge
Deploy and manage Surge instances across multiple VMs/containers
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List

def create_docker_compose(instances: int = 3):
    """Create docker-compose.yml for multi-instance deployment"""
    
    services = {}
    
    for i in range(instances):
        port = 8000 + i
        p2p_port = 8001 + i
        
        services[f"surge-{i}"] = {
            "build": ".",
            "ports": [
                f"{port}:8000",
                f"{p2p_port}:{p2p_port}"
            ],
            "environment": [
                f"PORT=8000",
                f"P2P_PORT={p2p_port}",
                f"INSTANCE_ID=surge-{i}",
                "DEBUG=false"
            ],
            "volumes": [
                f"./data/surge-{i}:/app/data",
                "./apps:/app/apps"
            ],
            "networks": ["surge-net"],
            "restart": "unless-stopped"
        }
    
    compose_config = {
        "version": "3.8",
        "services": services,
        "networks": {
            "surge-net": {
                "driver": "bridge"
            }
        },
        "volumes": {
            f"surge-data-{i}": {} for i in range(instances)
        }
    }
    
    with open("docker-compose.surge.yml", "w") as f:
        import yaml
        yaml.dump(compose_config, f, default_flow_style=False)
    
    print(f"Created docker-compose.surge.yml with {instances} instances")


def create_dockerfile():
    """Create Dockerfile for Surge deployment"""
    
    dockerfile_content = """
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile.surge", "w") as f:
        f.write(dockerfile_content.strip())
    
    print("Created Dockerfile.surge")


def create_k8s_manifests(instances: int = 3):
    """Create Kubernetes manifests for surge deployment"""
    
    # Create namespace
    namespace = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": "surge"}
    }
    
    # Create deployment
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "surge-deployment",
            "namespace": "surge"
        },
        "spec": {
            "replicas": instances,
            "selector": {
                "matchLabels": {"app": "surge"}
            },
            "template": {
                "metadata": {
                    "labels": {"app": "surge"}
                },
                "spec": {
                    "containers": [{
                        "name": "surge",
                        "image": "surge:latest",
                        "ports": [
                            {"containerPort": 8000},
                            {"containerPort": 8001}
                        ],
                        "env": [
                            {"name": "PORT", "value": "8000"},
                            {"name": "P2P_PORT", "value": "8001"}
                        ],
                        "resources": {
                            "requests": {
                                "memory": "256Mi",
                                "cpu": "250m"
                            },
                            "limits": {
                                "memory": "512Mi", 
                                "cpu": "500m"
                            }
                        },
                        "livenessProbe": {
                            "httpGet": {
                                "path": "/health",
                                "port": 8000
                            },
                            "initialDelaySeconds": 30,
                            "periodSeconds": 10
                        }
                    }]
                }
            }
        }
    }
    
    # Create service
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "surge-service",
            "namespace": "surge"
        },
        "spec": {
            "selector": {"app": "surge"},
            "ports": [
                {
                    "name": "http",
                    "port": 8000,
                    "targetPort": 8000
                },
                {
                    "name": "p2p",
                    "port": 8001,
                    "targetPort": 8001
                }
            ],
            "type": "LoadBalancer"
        }
    }
    
    # Create ingress
    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": "surge-ingress",
            "namespace": "surge",
            "annotations": {
                "nginx.ingress.kubernetes.io/rewrite-target": "/"
            }
        },
        "spec": {
            "rules": [{
                "host": "surge.local",
                "http": {
                    "paths": [{
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {
                            "service": {
                                "name": "surge-service",
                                "port": {"number": 8000}
                            }
                        }
                    }]
                }
            }]
        }
    }
    
    # Write manifests
    manifests_dir = Path("k8s")
    manifests_dir.mkdir(exist_ok=True)
    
    with open(manifests_dir / "namespace.yaml", "w") as f:
        import yaml
        yaml.dump(namespace, f)
    
    with open(manifests_dir / "deployment.yaml", "w") as f:
        import yaml
        yaml.dump(deployment, f)
    
    with open(manifests_dir / "service.yaml", "w") as f:
        import yaml
        yaml.dump(service, f)
    
    with open(manifests_dir / "ingress.yaml", "w") as f:
        import yaml
        yaml.dump(ingress, f)
    
    print(f"Created Kubernetes manifests in k8s/ directory")


def deploy_local(instances: int = 3):
    """Deploy locally using docker-compose"""
    print(f"Deploying {instances} local instances...")
    
    # Create docker-compose file
    create_docker_compose(instances)
    create_dockerfile()
    
    # Build and start
    subprocess.run(["docker-compose", "-f", "docker-compose.surge.yml", "build"])
    subprocess.run(["docker-compose", "-f", "docker-compose.surge.yml", "up", "-d"])
    
    print(f"Deployment complete! Access instances at:")
    for i in range(instances):
        port = 8000 + i
        print(f"  Instance {i}: http://localhost:{port}")


def deploy_k8s(instances: int = 3):
    """Deploy to Kubernetes cluster"""
    print(f"Deploying {instances} instances to Kubernetes...")
    
    # Create manifests
    create_k8s_manifests(instances)
    
    # Apply manifests
    subprocess.run(["kubectl", "apply", "-f", "k8s/"])
    
    print("Kubernetes deployment initiated!")
    print("Check status with: kubectl get pods -n surge")


def create_startup_script():
    """Create startup script for P2P networking"""
    
    script_content = '''#!/bin/bash
# Surge Multi-VM Startup Script

set -e

echo "Starting Surge P2P Surgery Platform..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/app"
export PORT=${PORT:-8000}
export P2P_PORT=${P2P_PORT:-8001}
export INSTANCE_ID=${INSTANCE_ID:-surge-local}

# Wait for dependencies
echo "Waiting for dependencies..."
sleep 5

# Start the application
echo "Starting Surge on port $PORT with P2P on port $P2P_PORT"
python -m uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info
'''
    
    with open("start-surge.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("start-surge.sh", 0o755)
    print("Created start-surge.sh script")


def main():
    parser = argparse.ArgumentParser(description="Surge Multi-VM Deployment")
    parser.add_argument("command", choices=["local", "k8s", "scripts"], 
                       help="Deployment target")
    parser.add_argument("--instances", type=int, default=3,
                       help="Number of instances to deploy")
    
    args = parser.parse_args()
    
    if args.command == "local":
        deploy_local(args.instances)
    elif args.command == "k8s":
        deploy_k8s(args.instances)
    elif args.command == "scripts":
        create_dockerfile()
        create_startup_script()
        print("Created deployment scripts")


if __name__ == "__main__":
    main()
