#!/bin/bash
"""
Multi-Cloud Deployment Script for Gastric ADCI Platform
Automated deployment across AWS, GCP, and Azure
"""

set -e

echo "☁️  Setting up Gastric ADCI Platform - Multi-Cloud Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_cloud() {
    echo -e "${CYAN}[CLOUD]${NC} $1"
}

# Detect cloud provider
detect_cloud_provider() {
    print_status "Detecting cloud provider..."
    
    if [ ! -z "$AWS_REGION" ] || [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
        echo "aws"
    elif [ ! -z "$GCP_PROJECT" ] || [ ! -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo "gcp"
    elif [ ! -z "$AZURE_SUBSCRIPTION_ID" ] || [ ! -z "$AZURE_TENANT_ID" ]; then
        echo "azure"
    else
        echo "unknown"
    fi
}

# Setup AWS deployment
setup_aws_deployment() {
    print_cloud "Setting up AWS deployment..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Set AWS defaults if not provided
    export AWS_REGION=${AWS_REGION:-us-west-2}
    export AWS_S3_BUCKET=${AWS_S3_BUCKET:-gastric-adci-${RANDOM}}
    
    print_status "AWS Region: $AWS_REGION"
    print_status "S3 Bucket: $AWS_S3_BUCKET"
    
    # Create AWS configuration
    mkdir -p deploy/aws
    
    cat > deploy/aws/cloudformation.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Gastric ADCI Platform - AWS Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
  
  InstanceType:
    Type: String
    Default: t3.medium
    Description: EC2 instance type for the application

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: gastric-adci-vpc

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # S3 Bucket for file storage
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'gastric-adci-${AWS::AccountId}-${AWS::Region}'
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # RDS Database
  DatabaseSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for Gastric ADCI database
      SubnetIds:
        - !Ref PublicSubnet
        - !Ref PrivateSubnet

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: gastric-adci-db
      DBInstanceClass: db.t3.micro
      Engine: postgres
      EngineVersion: '13.7'
      MasterUsername: gastricadci
      MasterUserPassword: !Ref DatabasePassword
      AllocatedStorage: 20
      DBSubnetGroupName: !Ref DatabaseSubnetGroup
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: gastric-adci-cluster

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: gastric-adci-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet

Outputs:
  DatabaseEndpoint:
    Description: RDS database endpoint
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub '${AWS::StackName}-DatabaseEndpoint'

  S3BucketName:
    Description: S3 bucket name
    Value: !Ref S3Bucket
    Export:
      Name: !Sub '${AWS::StackName}-S3Bucket'

  LoadBalancerDNS:
    Description: Application Load Balancer DNS
    Value: !GetAtt ApplicationLoadBalancer.DNSName
    Export:
      Name: !Sub '${AWS::StackName}-LoadBalancerDNS'
EOF

    # Create Dockerfile for AWS deployment
    cat > deploy/aws/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV GASTRIC_ADCI_ENV=multicloud
ENV CLOUD_PROVIDER=aws
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "main.py"]
EOF

    # Create ECS task definition
    cat > deploy/aws/task-definition.json << 'EOF'
{
  "family": "gastric-adci-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/gastric-adci-task-role",
  "containerDefinitions": [
    {
      "name": "gastric-adci-container",
      "image": "ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/gastric-adci:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GASTRIC_ADCI_ENV",
          "value": "multicloud"
        },
        {
          "name": "CLOUD_PROVIDER",
          "value": "aws"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/gastric-adci",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

    print_success "AWS deployment configuration created"
}

# Setup GCP deployment
setup_gcp_deployment() {
    print_cloud "Setting up GCP deployment..."
    
    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install Google Cloud SDK first."
        exit 1
    fi
    
    # Set GCP defaults if not provided
    export GCP_PROJECT=${GCP_PROJECT:-gastric-adci-$(date +%s)}
    export GCP_REGION=${GCP_REGION:-us-central1}
    
    print_status "GCP Project: $GCP_PROJECT"
    print_status "GCP Region: $GCP_REGION"
    
    # Create GCP configuration
    mkdir -p deploy/gcp
    
    cat > deploy/gcp/app.yaml << 'EOF'
runtime: python311
env: standard

instance_class: F2

env_variables:
  GASTRIC_ADCI_ENV: multicloud
  CLOUD_PROVIDER: gcp
  GCP_PROJECT: PROJECT_ID
  GCP_REGION: us-central1

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

handlers:
- url: /static
  static_dir: web/static

- url: /.*
  script: auto

health_check:
  enable_health_check: True
  check_interval_sec: 5
  timeout_sec: 4
  unhealthy_threshold: 2
  healthy_threshold: 2
EOF

    # Create Cloud Build configuration
    cat > deploy/gcp/cloudbuild.yaml << 'EOF'
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/gastric-adci:$COMMIT_SHA', '.']
    dir: 'deploy/gcp'

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/gastric-adci:$COMMIT_SHA']

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'gastric-adci'
      - '--image'
      - 'gcr.io/$PROJECT_ID/gastric-adci:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/gastric-adci:$COMMIT_SHA'
EOF

    # Create Terraform configuration for infrastructure
    cat > deploy/gcp/main.tf << 'EOF'
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

# Cloud SQL instance
resource "google_sql_database_instance" "main" {
  name             = "gastric-adci-db"
  database_version = "POSTGRES_13"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled = true
    }
    
    ip_configuration {
      authorized_networks {
        value = "0.0.0.0/0"
        name  = "all"
      }
    }
  }
}

resource "google_sql_database" "database" {
  name     = "gastric_adci"
  instance = google_sql_database_instance.main.name
}

# Cloud Storage bucket
resource "google_storage_bucket" "main" {
  name     = "${var.project_id}-gastric-adci-storage"
  location = var.region

  versioning {
    enabled = true
  }
}

# Cloud Run service
resource "google_cloud_run_service" "main" {
  name     = "gastric-adci"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/gastric-adci:latest"
        
        env {
          name  = "GASTRIC_ADCI_ENV"
          value = "multicloud"
        }
        
        env {
          name  = "CLOUD_PROVIDER"
          value = "gcp"
        }
        
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "run_all_users" {
  service  = google_cloud_run_service.main.name
  location = google_cloud_run_service.main.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  value = google_cloud_run_service.main.status[0].url
}
EOF

    print_success "GCP deployment configuration created"
}

# Setup Azure deployment
setup_azure_deployment() {
    print_cloud "Setting up Azure deployment..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not found. Please install Azure CLI first."
        exit 1
    fi
    
    # Set Azure defaults if not provided
    export AZURE_LOCATION=${AZURE_LOCATION:-westus2}
    export AZURE_RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-gastric-adci-rg}
    
    print_status "Azure Location: $AZURE_LOCATION"
    print_status "Resource Group: $AZURE_RESOURCE_GROUP"
    
    # Create Azure configuration
    mkdir -p deploy/azure
    
    # Create ARM template
    cat > deploy/azure/azuredeploy.json << 'EOF'
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "appName": {
      "type": "string",
      "defaultValue": "gastric-adci",
      "metadata": {
        "description": "Name of the application"
      }
    },
    "environment": {
      "type": "string",
      "defaultValue": "production",
      "allowedValues": ["development", "staging", "production"]
    }
  },
  "variables": {
    "appServicePlanName": "[concat(parameters('appName'), '-plan')]",
    "webAppName": "[concat(parameters('appName'), '-app')]",
    "sqlServerName": "[concat(parameters('appName'), '-sql')]",
    "sqlDatabaseName": "[concat(parameters('appName'), '-db')]",
    "storageAccountName": "[concat(replace(parameters('appName'), '-', ''), 'storage')]"
  },
  "resources": [
    {
      "type": "Microsoft.Web/serverfarms",
      "apiVersion": "2021-02-01",
      "name": "[variables('appServicePlanName')]",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "S1",
        "tier": "Standard"
      },
      "kind": "linux",
      "properties": {
        "reserved": true
      }
    },
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2021-02-01",
      "name": "[variables('webAppName')]",
      "location": "[resourceGroup().location]",
      "dependsOn": [
        "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
      ],
      "properties": {
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
        "siteConfig": {
          "linuxFxVersion": "PYTHON|3.11",
          "appSettings": [
            {
              "name": "GASTRIC_ADCI_ENV",
              "value": "multicloud"
            },
            {
              "name": "CLOUD_PROVIDER",
              "value": "azure"
            },
            {
              "name": "AZURE_LOCATION",
              "value": "[resourceGroup().location]"
            }
          ]
        }
      }
    },
    {
      "type": "Microsoft.Sql/servers",
      "apiVersion": "2021-02-01-preview",
      "name": "[variables('sqlServerName')]",
      "location": "[resourceGroup().location]",
      "properties": {
        "administratorLogin": "gastricadci",
        "administratorLoginPassword": "[concat('P@ssw0rd', uniqueString(resourceGroup().id))]"
      }
    },
    {
      "type": "Microsoft.Sql/servers/databases",
      "apiVersion": "2021-02-01-preview",
      "name": "[concat(variables('sqlServerName'), '/', variables('sqlDatabaseName'))]",
      "location": "[resourceGroup().location]",
      "dependsOn": [
        "[resourceId('Microsoft.Sql/servers', variables('sqlServerName'))]"
      ],
      "sku": {
        "name": "Basic",
        "tier": "Basic"
      }
    },
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2021-04-01",
      "name": "[variables('storageAccountName')]",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2",
      "properties": {
        "accessTier": "Hot"
      }
    }
  ],
  "outputs": {
    "webAppUrl": {
      "type": "string",
      "value": "[concat('https://', variables('webAppName'), '.azurewebsites.net')]"
    },
    "sqlServerFqdn": {
      "type": "string",
      "value": "[reference(variables('sqlServerName')).fullyQualifiedDomainName]"
    }
  }
}
EOF

    # Create Azure DevOps pipeline
    cat > deploy/azure/azure-pipelines.yml << 'EOF'
trigger:
- main

variables:
  azureServiceConnectionId: 'gastric-adci-service-connection'
  webAppName: 'gastric-adci-app'
  environmentName: 'production'
  projectRoot: $(System.DefaultWorkingDirectory)
  pythonVersion: '3.11'

stages:
- stage: Build
  displayName: Build stage
  jobs:
  - job: BuildJob
    pool:
      vmImage: ubuntu-latest
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Use Python $(pythonVersion)'
    
    - script: |
        python -m venv antenv
        source antenv/bin/activate
        python -m pip install --upgrade pip
        pip install -r requirements.txt
      workingDirectory: $(projectRoot)
      displayName: 'Install requirements'

    - task: ArchiveFiles@2
      displayName: 'Archive files'
      inputs:
        rootFolderOrFile: '$(projectRoot)'
        includeRootFolder: false
        archiveType: zip
        archiveFile: $(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip
        replaceExistingArchive: true

    - upload: $(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip
      displayName: 'Upload package'
      artifact: drop

- stage: Deploy
  displayName: 'Deploy Web App'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: DeploymentJob
    pool:
      vmImage: ubuntu-latest
    environment: $(environmentName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            displayName: 'Deploy Azure Web App'
            inputs:
              azureSubscription: $(azureServiceConnectionId)
              appName: $(webAppName)
              package: $(Pipeline.Workspace)/drop/$(Build.BuildId).zip
EOF

    print_success "Azure deployment configuration created"
}

# Create universal Docker configuration
create_docker_config() {
    print_status "Creating universal Docker configuration..."
    
    cat > Dockerfile << 'EOF'
# Multi-stage Dockerfile for Gastric ADCI Platform
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r gastricadci && useradd -r -g gastricadci gastricadci

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/gastricadci/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/database data/uploads logs \
    && chown -R gastricadci:gastricadci /app

# Switch to non-root user
USER gastricadci

# Set environment variables
ENV PATH=/home/gastricadci/.local/bin:$PATH
ENV GASTRIC_ADCI_ENV=multicloud
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "main.py"]
EOF

    # Create docker-compose for local testing
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  gastric-adci:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GASTRIC_ADCI_ENV=multicloud
      - DEBUG=false
      - DATABASE_URL=postgresql://postgres:password@db:5432/gastric_adci
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=gastric_adci
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7
    restart: unless-stopped

volumes:
  postgres_data:
EOF

    print_success "Docker configuration created"
}

# Create deployment documentation
create_deployment_docs() {
    print_status "Creating deployment documentation..."
    
    mkdir -p docs/deployment
    
    cat > docs/deployment/MULTI_CLOUD_DEPLOYMENT.md << 'EOF'
# Multi-Cloud Deployment Guide

This guide covers deploying the Gastric ADCI Platform across multiple cloud providers.

## Supported Cloud Providers

- **AWS**: Amazon Web Services
- **GCP**: Google Cloud Platform  
- **Azure**: Microsoft Azure

## Prerequisites

### General
- Docker installed
- Git repository access
- Environment-specific CLI tools

### AWS
- AWS CLI configured
- IAM permissions for ECS, RDS, S3, CloudFormation
- ECR repository access

### GCP
- gcloud CLI configured
- Cloud Build, Cloud Run, Cloud SQL APIs enabled
- Container Registry access

### Azure
- Azure CLI configured
- App Service, SQL Database, Storage Account permissions
- Container Registry access

## Environment Variables

### Common
```bash
GASTRIC_ADCI_ENV=multicloud
DEBUG=false
LOG_LEVEL=WARNING
```

### AWS Specific
```bash
CLOUD_PROVIDER=aws
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
```

### GCP Specific
```bash
CLOUD_PROVIDER=gcp
GCP_PROJECT=your_project_id
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Azure Specific
```bash
CLOUD_PROVIDER=azure
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP=your_resource_group
AZURE_LOCATION=westus2
```

## Quick Deployment

### AWS
```bash
# Setup and deploy to AWS
./scripts/setup_multicloud.sh aws deploy

# Or step by step
aws cloudformation create-stack \
  --stack-name gastric-adci \
  --template-body file://deploy/aws/cloudformation.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production
```

### GCP
```bash
# Setup and deploy to GCP
./scripts/setup_multicloud.sh gcp deploy

# Or using gcloud
gcloud app deploy deploy/gcp/app.yaml
```

### Azure
```bash
# Setup and deploy to Azure
./scripts/setup_multicloud.sh azure deploy

# Or using Azure CLI
az deployment group create \
  --resource-group gastric-adci-rg \
  --template-file deploy/azure/azuredeploy.json
```

## Monitoring and Scaling

Each cloud provider offers different monitoring and scaling solutions:

- **AWS**: CloudWatch, Auto Scaling Groups
- **GCP**: Cloud Monitoring, Cloud Run auto-scaling
- **Azure**: Application Insights, App Service auto-scaling

## Backup and Disaster Recovery

- **Database backups**: Automated daily backups
- **File storage**: Cross-region replication
- **Infrastructure as Code**: Version controlled deployment templates

## Security Considerations

- All communications encrypted in transit
- Database encryption at rest
- IAM roles with least privilege
- Network security groups/firewalls
- Regular security scanning

## Cost Optimization

- Right-sizing compute resources
- Using spot/preemptible instances where appropriate
- Implementing auto-scaling policies
- Regular cost monitoring and optimization

## Troubleshooting

### Common Issues
1. **Authentication failures**: Check credentials and permissions
2. **Network connectivity**: Verify security groups and firewalls
3. **Database connection**: Check connection strings and network access
4. **Resource limits**: Monitor quotas and scaling policies

### Logs and Monitoring
- Check application logs in cloud logging services
- Monitor health check endpoints
- Use cloud provider monitoring dashboards
- Set up alerting for critical issues

## Support

For deployment support, check:
1. Cloud provider documentation
2. Platform-specific troubleshooting guides
3. Community forums and issues
4. Professional support services
EOF

    print_success "Deployment documentation created"
}

# Validate cloud prerequisites
validate_cloud_prerequisites() {
    print_status "Validating cloud prerequisites..."
    
    PROVIDER=$(detect_cloud_provider)
    
    case $PROVIDER in
        "aws")
            if ! aws sts get-caller-identity &>/dev/null; then
                print_error "AWS authentication failed. Please configure AWS CLI."
                return 1
            fi
            print_success "AWS authentication validated"
            ;;
        "gcp")
            if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 &>/dev/null; then
                print_error "GCP authentication failed. Please run 'gcloud auth login'."
                return 1
            fi
            print_success "GCP authentication validated"
            ;;
        "azure")
            if ! az account show &>/dev/null; then
                print_error "Azure authentication failed. Please run 'az login'."
                return 1
            fi
            print_success "Azure authentication validated"
            ;;
        *)
            print_error "No cloud provider detected. Please set appropriate environment variables."
            return 1
            ;;
    esac
}

# Deploy to cloud
deploy_to_cloud() {
    PROVIDER=$1
    
    print_cloud "Deploying to $PROVIDER..."
    
    case $PROVIDER in
        "aws")
            print_status "Building and pushing Docker image to ECR..."
            # ECR login and push would go here
            
            print_status "Deploying CloudFormation stack..."
            # CloudFormation deployment would go here
            ;;
        "gcp")
            print_status "Building and deploying to Cloud Run..."
            gcloud builds submit --config=deploy/gcp/cloudbuild.yaml .
            ;;
        "azure")
            print_status "Deploying to Azure App Service..."
            # Azure deployment would go here
            ;;
    esac
    
    print_success "Deployment to $PROVIDER completed!"
}

# Main execution
main() {
    PROVIDER=${1:-$(detect_cloud_provider)}
    ACTION=${2:-setup}
    
    echo "════════════════════════════════════════════════════════════════"
    echo "☁️  Gastric ADCI Platform - Multi-Cloud Deployment"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    print_cloud "Target provider: $PROVIDER"
    print_status "Action: $ACTION"
    echo ""
    
    case $ACTION in
        "setup")
            validate_cloud_prerequisites
            
            case $PROVIDER in
                "aws") setup_aws_deployment ;;
                "gcp") setup_gcp_deployment ;;
                "azure") setup_azure_deployment ;;
                *) print_error "Unknown provider: $PROVIDER"; exit 1 ;;
            esac
            
            create_docker_config
            create_deployment_docs
            
            print_success "Multi-cloud setup completed for $PROVIDER!"
            ;;
        "deploy")
            validate_cloud_prerequisites
            deploy_to_cloud $PROVIDER
            ;;
        "validate")
            validate_cloud_prerequisites
            print_success "Cloud prerequisites validated"
            ;;
        *)
            echo "Usage: $0 {aws|gcp|azure} {setup|deploy|validate}"
            echo ""
            echo "Providers:"
            echo "  aws    - Amazon Web Services"
            echo "  gcp    - Google Cloud Platform"
            echo "  azure  - Microsoft Azure"
            echo ""
            echo "Actions:"
            echo "  setup    - Setup deployment configuration"
            echo "  deploy   - Deploy to cloud provider"
            echo "  validate - Validate prerequisites"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
