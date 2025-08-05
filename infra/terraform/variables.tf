# Global variables for all environments
variable "environment" {
  description = "Environment: dev, staging, prod"
  type        = string
}

# Contabo VPS Configuration
variable "contabo_username" {
  description = "Contabo API username"
  type        = string
  sensitive   = true
}

variable "contabo_password" {
  description = "Contabo API password"
  type        = string
  sensitive   = true
}

variable "contabo_customer_id" {
  description = "Contabo customer ID"
  type        = string
  sensitive   = true
}

variable "contabo_product_id" {
  description = "Contabo VPS product ID (e.g. 400 for VPS S SSD)"
  type        = string
  default     = "400"  # VPS S SSD
}

variable "contabo_region" {
  description = "Contabo region (e.g. EU, US)"
  type        = string
  default     = "EU"
}

variable "contabo_image_id" {
  description = "Image ID (e.g. 100 for Ubuntu 22.04)"
  type        = string
  default     = "100"  # Ubuntu 22.04
}

variable "ssh_public_key" {
  description = "SSH public key for VPS access"
  type        = string
}
