#!/bin/bash
set -e

# Build script for GTD Backend Docker image

# Configuration
IMAGE_NAME="gtd-backend"
IMAGE_TAG=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-""}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building GTD Backend Docker image...${NC}"

# Change to script directory
cd "$(dirname "$0")/.."

# Build the image
echo -e "${YELLOW}Building image: ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

# Tag for registry if specified
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo -e "${YELLOW}Tagging for registry: ${FULL_IMAGE_NAME}${NC}"
    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${FULL_IMAGE_NAME}"
fi

# Display image size
echo -e "${GREEN}Build completed successfully!${NC}"
docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Optional: Run security scan
if command -v trivy &> /dev/null; then
    echo -e "${YELLOW}Running security scan...${NC}"
    trivy image "${IMAGE_NAME}:${IMAGE_TAG}"
fi

echo -e "${GREEN}Done!${NC}"