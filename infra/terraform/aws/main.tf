# AWS ECS + RDS Terraform Module
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_db_instance" "main" {
  allocated_storage    = 20
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  name                 = var.db_name
  username             = var.db_user
  password             = var.db_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
}

resource "aws_ecs_cluster" "main" {
  name = var.ecs_cluster_name
}

# ... (ECS service/task definition, ALB, security groups, etc.)

variable "aws_region" {}
variable "db_name" {}
variable "db_user" {}
variable "db_password" {}
variable "ecs_cluster_name" {}
