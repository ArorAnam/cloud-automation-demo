# Terraform configuration for dev environment

terraform {
  required_version = ">= 1.0"
  
  # Uncomment and configure for remote state
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "cloud-automation-demo/dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-state-locks"
  #   encrypt        = true
  # }
}