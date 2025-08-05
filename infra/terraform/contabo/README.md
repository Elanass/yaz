# Contabo VPS Module

This module creates a Contabo VPS instance with Docker pre-installed for running Surgify.

## Features

- Ubuntu 22.04 LTS
- Docker and Docker Compose pre-installed
- SSH access configured
- Application directory at `/opt/surgify`

## Usage

From the main terraform directory:

```bash
# Initialize terraform
terraform init

# Plan the deployment
terraform plan

# Deploy the VPS
terraform apply
```

## Variables

| Name | Description | Type | Default |
|------|-------------|------|---------|
| contabo_username | Contabo API username | string | required |
| contabo_password | Contabo API password | string | required |
| contabo_customer_id | Contabo customer ID | string | required |
| vps_name | Name for the VPS | string | required |
| product_id | VPS product ID | string | required |
| region | Contabo region | string | required |
| image_id | OS image ID | string | required |
| ssh_key | SSH public key | string | required |

## Product IDs

- 400: VPS S SSD (1 vCPU, 4GB RAM, 50GB SSD)
- 401: VPS M SSD (2 vCPU, 8GB RAM, 100GB SSD)  
- 402: VPS L SSD (4 vCPU, 16GB RAM, 200GB SSD)

## Outputs

| Name | Description |
|------|-------------|
| vps_ip | Public IP address |
| vps_id | VPS instance ID |
| vps_name | VPS display name |
