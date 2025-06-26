# Staging environment configuration

module "infrastructure" {
  source = "../../"
  
  # Environment-specific settings
  environment    = "staging"
  aws_region     = "us-east-1"
  project_name   = "cloud-automation-demo"
  
  # Network configuration
  vpc_cidr           = "10.1.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  
  # Instance configuration
  instance_type    = "t3.small"
  min_instances    = 2
  max_instances    = 4
  desired_capacity = 2
  
  # Staging-specific settings
  ssh_allowed_ips = ["10.0.0.0/8"]  # Restrict SSH to internal network
  enable_monitoring = true           # Enable monitoring in staging
  backup_retention_days = 7          # Standard retention
  
  # Additional tags
  tags = {
    CostCenter = "staging"
    Owner      = "qa-team"
  }
}