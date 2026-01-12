#!/bin/bash
set -e

# Deployment script for CI/CD Pipeline Demo
# Usage: ./scripts/deploy.sh <environment> <image_tag>

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
REGISTRY="ghcr.io"
IMAGE_NAME="masteroflink/cicd-pipeline-demo"

echo "==================================="
echo "Deploying CI/CD Pipeline Demo"
echo "==================================="
echo "Environment: $ENVIRONMENT"
echo "Image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
echo "==================================="

# Pull the latest image
echo "Pulling image..."
docker pull "$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

# Stop existing container if running
echo "Stopping existing container..."
docker stop cicd-demo-$ENVIRONMENT 2>/dev/null || true
docker rm cicd-demo-$ENVIRONMENT 2>/dev/null || true

# Run the new container
echo "Starting new container..."
docker run -d \
  --name "cicd-demo-$ENVIRONMENT" \
  -p 8000:8000 \
  -e ENVIRONMENT="$ENVIRONMENT" \
  "$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

# Wait for container to be ready
echo "Waiting for container to be ready..."
sleep 5

# Health check
echo "Running health check..."
./scripts/health-check.sh http://localhost:8000

echo "==================================="
echo "Deployment completed successfully!"
echo "==================================="
