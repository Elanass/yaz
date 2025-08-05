# GCP Cloud Run + Spanner Module

variable "gcp_project" {}
variable "region" {}
variable "spanner_instance" {}
variable "spanner_db" {}

provider "google" {
  project = var.gcp_project
  region  = var.region
}

resource "google_spanner_instance" "main" {
  name         = var.spanner_instance
  config       = "regional-${var.region}"
  display_name = var.spanner_instance
  num_nodes    = 1
}

resource "google_spanner_database" "main" {
  name     = var.spanner_db
  instance = google_spanner_instance.main.name
}

# ... (Cloud Run service, IAM, VPC, etc.)
