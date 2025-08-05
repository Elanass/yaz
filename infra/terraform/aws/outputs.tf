output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}
output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}
