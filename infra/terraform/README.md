# Terraform Infrastructure

This directory contains Terraform configurations for deploying Surgify infrastructure across multiple cloud providers.

## Structure

```
infra/terraform/
├── main.tf              # Main configuration
├── variables.tf         # Global variables
├── terraform.tfvars.example  # Example variables
├── aws/                 # AWS resources
├── azure/              # Azure resources
├── contabo/            # Contabo VPS module
├── gcp/                # Google Cloud resources
└── modules/            # Reusable modules
```

## Quick Start

1. **Setup credentials:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

2. **Deploy to Contabo:**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. **Connect to your VPS:**
   ```bash
   ssh ubuntu@$(terraform output -raw contabo_vps_ip)
   ```

## Environment Variables

For sensitive values, you can use environment variables instead of terraform.tfvars:

```bash
export TF_VAR_contabo_username="your-username"
export TF_VAR_contabo_password="your-password"
export TF_VAR_contabo_customer_id="your-customer-id"
export TF_VAR_ssh_public_key="$(cat ~/.ssh/id_rsa.pub)"
```

## Supported Providers

- **Contabo**: VPS hosting (fully configured)
- **AWS**: (modules available)
- **Azure**: (modules available) 
- **GCP**: (modules available)

## Next Steps

After deployment:
1. SSH into your VPS
2. Deploy your application using Docker Compose
3. Configure DNS to point to your VPS IP
4. Set up SSL certificates
