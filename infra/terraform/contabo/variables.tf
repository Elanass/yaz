variable "contabo_username" {}
variable "contabo_password" {}
variable "contabo_customer_id" {}
variable "product_id" { description = "Contabo VPS product ID (e.g. 400 for VPS S SSD)" }
variable "region" { description = "Contabo region (e.g. EU, US)" }
variable "image_id" { description = "Image ID (e.g. 100 for Ubuntu 22.04)" }
variable "ssh_key" { description = "SSH public key for access" }
variable "vps_name" { description = "Name for the VPS" }
