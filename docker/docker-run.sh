#!/bin/bash

# Docker run script for pymono services
# Usage: ./docker-run.sh [service] [additional-args]
#        Environment variables can be passed via -e flags or --env-file
# Example: ./docker-run.sh api -e OPENAI_API_KEY=sk-xxx -e LOG_LEVEL=DEBUG
# Can be run from docker/ folder or project root

set -e

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# Configuration
IMAGE_NAME="treasury/pymono"
TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SERVICE="${1:-api}"
shift || true  # Remove first argument, ignore error if no args

# Function to get entry point for a service (compatible with bash 3.2+)
get_service_entry_point() {
    case "$1" in
        api)
            echo "treasury/services/gateways/ttb_api/__main__.py"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: ./docker-run.sh [service] [additional-args]${NC}"
    echo ""
    echo -e "${YELLOW}Available services:${NC}"
    echo "  - api: treasury/services/gateways/ttb_api/__main__.py"
    echo ""
    echo -e "${YELLOW}Basic Examples:${NC}"
    echo "  ./docker-run.sh api"
    echo "  ./docker-run.sh api --port 8080"
    echo ""
    echo -e "${YELLOW}Pass environment variables:${NC}"
    echo "  ./docker-run.sh api -e OPENAI_API_KEY=sk-xxx"
    echo "  ./docker-run.sh api -e OPENAI_API_KEY=sk-xxx -e LOG_LEVEL=DEBUG"
    echo ""
    echo -e "${YELLOW}Use custom .env file:${NC}"
    echo "  ./docker-run.sh api --env-file /path/to/custom.env"
    echo ""
    echo -e "${YELLOW}Custom entry point:${NC}"
    echo "  docker run --rm -p 8080:8080 ${IMAGE_NAME}:${TAG} treasury/services/custom/__main__.py"
    exit 0
}

# Check if help is requested
if [[ "$SERVICE" == "help" ]] || [[ "$SERVICE" == "-h" ]] || [[ "$SERVICE" == "--help" ]]; then
    show_usage
fi

# Get entry point for service
ENTRY_POINT=$(get_service_entry_point "$SERVICE")

if [ -z "$ENTRY_POINT" ]; then
    echo -e "${RED}✗ Unknown service: ${SERVICE}${NC}"
    echo ""
    show_usage
fi

echo -e "${GREEN}Starting ${SERVICE} service...${NC}"
echo -e "${YELLOW}Entry point: ${ENTRY_POINT}${NC}"

# Check if .env file exists in project root
ENV_FILE=""
if [ -f "${PROJECT_ROOT}/.env" ]; then
    ENV_FILE="--env-file ${PROJECT_ROOT}/.env"
    echo -e "${YELLOW}Using .env file from project root${NC}"
fi

# Run the container
docker run \
    --rm \
    --env "ENV=${dev}" \
    --name "pymono-${SERVICE}" \
    -p 8080:8080 \
    ${ENV_FILE} \
    -e PYTHONUNBUFFERED=1 \
    -v "${PROJECT_ROOT}/logs:/app/logs" \
    "${IMAGE_NAME}:${TAG}" \
    "${ENTRY_POINT}" \
    "$@"