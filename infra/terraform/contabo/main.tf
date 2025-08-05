# Contabo Terraform Provider Configuration
terraform {
  required_providers {
    contabo = {
      source  = "contabo/contabo"
      version = "~> 0.1.0"
    }
  }
}

# Configure the Contabo Provider
provider "contabo" {
  username    = var.contabo_username
  password    = var.contabo_password
  customer_id = var.contabo_customer_id
}

# Create a Contabo VPS instance
resource "contabo_instance" "main" {
  display_name = var.vps_name
  product_id   = var.product_id
  region       = var.region
  image_id     = var.image_id
  
  # SSH Key for access
  ssh_keys = [var.ssh_key]
  
  # Optional: Add user data script for initial setup
  user_data = base64encode(<<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu
    
    # Create application directory
    mkdir -p /opt/surgify
    
    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    EOF
  )
}

# Output the VPS details
output "vps_id" {
  value = contabo_instance.main.id
}

output "vps_ip" {
  value = contabo_instance.main.ip_config[0].v4[0].ip
}

output "vps_name" {
  value = contabo_instance.main.display_name
}
