# Cloud Automation Demo

A comprehensive cloud automation project demonstrating infrastructure as code, CI/CD pipelines, and Python-based cloud management tools.

## Overview

This project showcases modern cloud automation practices using:
- **Terraform**: Infrastructure as Code for AWS resources
- **Python**: Automation scripts and CLI tools using Click framework
- **Docker**: Containerization for consistent deployments
- **GitHub Actions**: CI/CD pipeline automation
- **AWS CloudWatch**: Monitoring and observability

## Project Structure

```
cloud-automation-demo/
├── terraform/              # Infrastructure as Code
│   ├── modules/           # Reusable Terraform modules
│   └── environments/      # Environment-specific configurations
│       ├── dev/
│       └── staging/
├── scripts/               # Python automation scripts
│   └── cloud_manager.py   # Main CLI tool
├── docker/                # Docker configurations
├── .github/workflows/     # CI/CD pipeline definitions
├── monitoring/            # CloudWatch configurations
├── tests/                 # Python test suite
├── requirements.txt       # Python dependencies
├── setup.py              # Python package setup
├── Makefile              # Common commands
└── README.md             # This file
```

## Prerequisites

- Python 3.8+
- Terraform 1.0+
- AWS CLI configured with appropriate credentials
- Docker (optional for containerization)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cloud-automation-demo
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install the CLI tool:
   ```bash
   pip install -e .
   ```

4. Initialize Terraform:
   ```bash
   cd terraform/environments/dev
   terraform init
   ```

## Usage

### CLI Tool

The `cloud_manager` CLI provides various commands for managing cloud resources:

```bash
# Show available commands
cloud_manager --help

# Example commands (to be implemented)
cloud_manager deploy --environment dev
cloud_manager status
cloud_manager destroy --environment dev
```

### Makefile Commands

Common tasks are available through the Makefile:

```bash
make help        # Show available commands
make setup       # Set up development environment
make test        # Run tests
make deploy-dev  # Deploy to development environment
make clean       # Clean up generated files
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Use `black` for code formatting:

```bash
black scripts/ tests/
```

## CI/CD

GitHub Actions workflows are configured to:
- Run tests on pull requests
- Validate Terraform configurations
- Deploy to environments based on branch merges

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details