# Main Terraform configuration
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    contabo = {
      source  = "contabo/contabo"
      version = "~> 0.1.0"
    }
  }
}

# Contabo VPS Module
module "contabo_vps" {
  source = "./contabo"
  
  # Contabo credentials
  contabo_username    = var.contabo_username
  contabo_password    = var.contabo_password
  contabo_customer_id = var.contabo_customer_id
  
  # VPS configuration
  vps_name   = "${var.environment}-surgify-vps"
  product_id = var.contabo_product_id
  region     = var.contabo_region
  image_id   = var.contabo_image_id
  ssh_key    = var.ssh_public_key
}

# Output VPS information
output "contabo_vps_ip" {
  value       = module.contabo_vps.vps_ip
  description = "Public IP address of the Contabo VPS"
}

output "contabo_vps_id" {
  value       = module.contabo_vps.vps_id
  description = "ID of the Contabo VPS"
}
