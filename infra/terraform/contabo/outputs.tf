output "vps_ip" {
  value = contabo_instance.main.ipv4_address
}

output "vps_id" {
  value = contabo_instance.main.id
}

output "vps_name" {
  value = contabo_instance.main.display_name
}
