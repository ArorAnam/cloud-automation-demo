#!/bin/bash

# Cloud Automation Demo - Initial Setup Script

set -e

echo "🚀 Cloud Automation Demo - Setup Script"
echo "======================================"

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version is installed (minimum required: $required_version)"
else
    echo "❌ Python $python_version is too old. Please install Python $required_version or newer."
    exit 1
fi

# Check if Terraform is installed
echo "📌 Checking Terraform..."
if command -v terraform &> /dev/null; then
    terraform_version=$(terraform version | head -n1 | cut -d' ' -f2)
    echo "✅ Terraform $terraform_version is installed"
else
    echo "⚠️  Terraform is not installed. Please install Terraform 1.0+ from https://www.terraform.io/downloads"
fi

# Check if AWS CLI is installed
echo "📌 Checking AWS CLI..."
if command -v aws &> /dev/null; then
    aws_version=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2)
    echo "✅ AWS CLI $aws_version is installed"
else
    echo "⚠️  AWS CLI is not installed. Please install AWS CLI from https://aws.amazon.com/cli/"
fi

# Create virtual environment
echo "📌 Creating Python virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📌 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📌 Installing Python dependencies..."
pip install -r requirements.txt

# Install the CLI tool
echo "📌 Installing cloud_manager CLI..."
pip install -e .

# Make scripts executable
chmod +x scripts/cloud_manager.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Configure AWS credentials: aws configure"
echo "3. Copy and update Terraform variables: cp terraform/environments/dev/example.tfvars terraform/environments/dev/terraform.tfvars"
echo "4. Initialize Terraform: cd terraform/environments/dev && terraform init"
echo "5. Test the CLI: cloud_manager --help"
echo ""
echo "For more information, see README.md"