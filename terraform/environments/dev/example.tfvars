# Example Terraform variables for development environment
# Copy this file to terraform.tfvars and update with your values

# AWS Configuration
aws_region = "us-east-1"

# Project Configuration
project_name = "cloud-automation-demo"
environment  = "dev"

# Network Configuration
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# Instance Configuration
instance_type    = "t3.micro"
min_instances    = 1
max_instances    = 2
desired_capacity = 1

# Security Configuration
ssh_allowed_ips = ["YOUR_IP_ADDRESS/32"]  # Replace with your IP address

# Monitoring and Backup
enable_monitoring     = false
backup_retention_days = 3

# Application Configuration
app_name = "demo-app"
app_port = 8080

# Tags
tags = {
  Owner      = "your-name"
  CostCenter = "development"
  Purpose    = "demo"
}