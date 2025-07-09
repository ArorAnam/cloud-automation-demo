# Podman Usage in Cloud Automation Demo

## What is Podman Used For in This Project?

### 1. **Local Testing Environment**
Podman creates isolated containers to test your cloud automation code locally before deploying to AWS.

```bash
# Example: Test your Python CLI in a container
podman build -t cloud-automation-demo:latest docker/
podman run -it cloud-automation-demo:latest cloud_manager --help
```

### 2. **LocalStack - Mock AWS Services**
LocalStack runs in a Podman container to simulate AWS services locally, saving money and time during development.

```bash
# Start LocalStack (fake AWS)
make localstack-start

# Now your code can connect to http://localhost:4566 instead of real AWS
export AWS_ENDPOINT_URL=http://localhost:4566
cloud_manager deploy --environment dev --local
```

### 3. **Consistent Development Environment**
Ensures everyone on the team has the same Python version, dependencies, and tools.

```bash
# Run tests in container (same environment as CI/CD)
podman run -v $(pwd):/app cloud-automation-demo:latest pytest tests/
```

## Setup Instructions

### 1. Install Podman on macOS
```bash
# Install Podman
brew install podman
brew install podman-compose

# Initialize and start Podman VM
podman machine init
podman machine start
```

### 2. Run Setup Script
```bash
./scripts/setup_podman.sh
```

### 3. Build and Test
```bash
# Build the container image
make docker-build

# Run the container
make docker-run

# Start LocalStack for AWS simulation
make localstack-start
```

## What Each Container Does

### cloud-manager Container
- **Purpose**: Runs your Python CLI tool in isolation
- **Contains**: Python, Terraform, AWS CLI, your code
- **Use Case**: Test deployments without installing tools locally

### LocalStack Container  
- **Purpose**: Simulates AWS services (S3, EC2, Lambda, etc.)
- **Contains**: Mock implementations of AWS APIs
- **Use Case**: Test AWS infrastructure without spending money

## Common Commands

```bash
# View running containers
podman ps

# View container logs
podman logs localstack

# Stop all containers
podman stop $(podman ps -q)

# Clean up
podman system prune -a
```

## Why Use Containers for This Project?

1. **Interview Demo**: Show you understand containerization
2. **Local Testing**: Test AWS deployments without AWS charges
3. **CI/CD Simulation**: Same environment locally as in GitHub Actions
4. **Dependency Management**: No need to install Terraform/AWS CLI globally
5. **Clean System**: Everything runs in containers, easy to remove

## Example Workflow

```bash
# 1. Start LocalStack (fake AWS)
make localstack-start

# 2. Run your CLI in container against LocalStack
podman run -it \
  -e AWS_ENDPOINT_URL=http://host.containers.internal:4566 \
  -e AWS_ACCESS_KEY_ID=test \
  -e AWS_SECRET_ACCESS_KEY=test \
  cloud-automation-demo:latest \
  cloud_manager deploy --environment dev

# 3. Check what was "created" in LocalStack
aws --endpoint-url=http://localhost:4566 s3 ls

# 4. Clean up
make localstack-stop
```

This demonstrates to your interviewer that you understand:
- Container orchestration
- Local development best practices  
- Cost-effective testing strategies
- Modern DevOps workflows