.PHONY: help setup test clean deploy-dev deploy-staging destroy-dev destroy-staging format lint

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip
TERRAFORM := terraform
VENV := venv
PROJECT_NAME := cloud-automation-demo

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)$(PROJECT_NAME) - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Set up development environment
	@echo "$(CYAN)Setting up development environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	. $(VENV)/bin/activate && $(PIP) install -e .
	@echo "$(GREEN)Setup complete! Activate virtual environment with: source $(VENV)/bin/activate$(NC)"

test: ## Run all tests
	@echo "$(CYAN)Running tests...$(NC)"
	. $(VENV)/bin/activate && pytest tests/ -v --cov=scripts --cov-report=html

test-watch: ## Run tests in watch mode
	. $(VENV)/bin/activate && pytest-watch tests/ -v

format: ## Format code with black
	@echo "$(CYAN)Formatting code...$(NC)"
	. $(VENV)/bin/activate && black scripts/ tests/

lint: ## Run linting checks
	@echo "$(CYAN)Running linting checks...$(NC)"
	. $(VENV)/bin/activate && flake8 scripts/ tests/
	. $(VENV)/bin/activate && pylint scripts/

type-check: ## Run type checking with mypy
	. $(VENV)/bin/activate && mypy scripts/

init-terraform: ## Initialize Terraform
	@echo "$(CYAN)Initializing Terraform...$(NC)"
	cd terraform/environments/dev && $(TERRAFORM) init
	cd terraform/environments/staging && $(TERRAFORM) init

plan-dev: ## Plan Terraform changes for dev environment
	@echo "$(CYAN)Planning Terraform changes for dev...$(NC)"
	cd terraform/environments/dev && $(TERRAFORM) plan

deploy-dev: ## Deploy to development environment
	@echo "$(CYAN)Deploying to development environment...$(NC)"
	cd terraform/environments/dev && $(TERRAFORM) apply -auto-approve

destroy-dev: ## Destroy development environment
	@echo "$(RED)Destroying development environment...$(NC)"
	cd terraform/environments/dev && $(TERRAFORM) destroy

plan-staging: ## Plan Terraform changes for staging environment
	@echo "$(CYAN)Planning Terraform changes for staging...$(NC)"
	cd terraform/environments/staging && $(TERRAFORM) plan

deploy-staging: ## Deploy to staging environment
	@echo "$(CYAN)Deploying to staging environment...$(NC)"
	cd terraform/environments/staging && $(TERRAFORM) apply

destroy-staging: ## Destroy staging environment
	@echo "$(RED)Destroying staging environment...$(NC)"
	cd terraform/environments/staging && $(TERRAFORM) destroy

docker-build: ## Build container image with Podman
	@echo "$(CYAN)Building container image with Podman...$(NC)"
	podman build -t $(PROJECT_NAME):latest docker/

docker-run: ## Run container with Podman
	@echo "$(CYAN)Running container with Podman...$(NC)"
	podman run -it --rm $(PROJECT_NAME):latest

clean: ## Clean up generated files
	@echo "$(CYAN)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf .mypy_cache/
	@echo "$(GREEN)Cleanup complete!$(NC)"

install-hooks: ## Install git hooks
	@echo "$(CYAN)Installing git hooks...$(NC)"
	pre-commit install

validate: format lint test ## Run all validation checks

localstack-start: ## Start LocalStack with Podman for local AWS testing
	@echo "$(CYAN)Starting LocalStack with Podman...$(NC)"
	podman run -d --name localstack \
		-p 4566:4566 \
		-e SERVICES=s3,ec2,iam,cloudwatch,dynamodb \
		localstack/localstack:latest
	@echo "$(GREEN)LocalStack running on http://localhost:4566$(NC)"

localstack-stop: ## Stop LocalStack
	@echo "$(CYAN)Stopping LocalStack...$(NC)"
	podman stop localstack && podman rm localstack

podman-compose-up: ## Start services with podman-compose
	@echo "$(CYAN)Starting services with podman-compose...$(NC)"
	cd docker && podman-compose -f podman-compose.yml up -d

podman-compose-down: ## Stop services with podman-compose
	@echo "$(CYAN)Stopping services with podman-compose...$(NC)"
	cd docker && podman-compose -f podman-compose.yml down