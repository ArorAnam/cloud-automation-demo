#!/bin/bash

# Setup script for Podman on macOS
set -e

echo "Setting up Podman for cloud-automation-demo..."

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "Podman not found. Please install Podman first:"
    echo "  brew install podman"
    echo "  brew install podman-compose"
    exit 1
fi

# Check if Podman machine exists
if ! podman machine list | grep -q "podman-machine-default"; then
    echo "Creating Podman machine..."
    podman machine init
fi

# Check if Podman machine is running
if ! podman machine list | grep -q "Running"; then
    echo "Starting Podman machine..."
    podman machine start
fi

# Create Docker compatibility aliases
echo "Creating Docker compatibility aliases..."
cat << 'EOF' >> ~/.zshrc

# Podman aliases for Docker compatibility
alias docker=podman
alias docker-compose=podman-compose

EOF

# Install podman-compose if not installed
if ! command -v podman-compose &> /dev/null; then
    echo "Installing podman-compose..."
    pip3 install podman-compose
fi

echo "Podman setup complete!"
echo ""
echo "Usage:"
echo "  - Build image: make docker-build"
echo "  - Run container: make docker-run"
echo "  - Start LocalStack: make localstack-start"
echo "  - Stop LocalStack: make localstack-stop"
echo ""
echo "Note: The Makefile has been updated to use Podman instead of Docker."