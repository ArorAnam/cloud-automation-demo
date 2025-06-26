# Development environment configuration

module "infrastructure" {
  source = "../../"
  
  # Environment-specific settings
  environment    = "dev"
  aws_region     = "us-east-1"
  project_name   = "cloud-automation-demo"
  
  # Network configuration
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  
  # Instance configuration
  instance_type    = "t3.micro"
  min_instances    = 1
  max_instances    = 2
  desired_capacity = 1
  
  # Development-specific settings
  ssh_allowed_ips = ["0.0.0.0/0"]  # Allow SSH from anywhere in dev
  enable_monitoring = false         # Disable monitoring to save costs
  backup_retention_days = 3         # Shorter retention in dev
  
  # Additional tags
  tags = {
    CostCenter = "development"
    Owner      = "dev-team"
  }
}