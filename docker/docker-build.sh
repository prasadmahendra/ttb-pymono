#!/bin/bash

# Docker build script for pymono
# Usage: ./docker-build.sh [tag] [platform]
# Can be run from docker/ folder or project root

set -e

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# Configuration
IMAGE_NAME="treasury/pymono"
DEFAULT_TAG="latest"
DEFAULT_PLATFORM="linux/amd64"

# Parse arguments
TAG="${1:-$DEFAULT_TAG}"
PLATFORM="${2:-$DEFAULT_PLATFORM}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Docker image: ${IMAGE_NAME}:${TAG}${NC}"
echo -e "${YELLOW}Platform: ${PLATFORM}${NC}"
echo -e "${YELLOW}Context: ${PROJECT_ROOT}${NC}"

# Build the Docker image from project root with Dockerfile in docker/
cd "${PROJECT_ROOT}"
docker build \
  --platform "${PLATFORM}" \
  --tag "${IMAGE_NAME}:${TAG}" \
  --file docker/Dockerfile \
  .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "Image: ${IMAGE_NAME}:${TAG}"

    # Show image size
    IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${TAG}" --format "{{.Size}}")
    echo -e "Size: ${IMAGE_SIZE}"

    echo ""
    echo -e "${YELLOW}To run the API gateway:${NC}"
    echo "  cd docker && ./docker-run.sh api"
    echo "  OR from project root: docker/docker-run.sh api"
    echo ""
    echo -e "${YELLOW}To run with custom entry point:${NC}"
    echo "  docker run --rm ${IMAGE_NAME}:${TAG} treasury/services/your-service/__main__.py"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi