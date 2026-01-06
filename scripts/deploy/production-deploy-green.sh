#!/bin/bash
# Deployment script for Production Green environment
# This deploys to the green slot without affecting blue
# Usage: ./scripts/deploy/production-deploy-green.sh [--rebuild] [--tag IMAGE_TAG]

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Nocturna Production Green Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Load environment variables (check multiple locations)
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables from .env...${NC}"
    set -a
    source .env
    set +a
elif [ -f "config/production.env" ]; then
    echo -e "${YELLOW}Loading environment variables from config/production.env...${NC}"
    set -a
    source config/production.env
    set +a
else
    echo -e "${RED}Error: .env or config/production.env not found${NC}"
    exit 1
fi

# Parse arguments
REBUILD=false
IMAGE_TAG="${IMAGE_TAG:-latest}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD=true
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

export IMAGE_TAG

# Ensure database and redis are running (from blue deployment)
if ! docker ps | grep -q nocturna-prod-db; then
    echo -e "${RED}Error: Database is not running. Deploy blue first.${NC}"
    exit 1
fi

# Build images
if [ "$REBUILD" = true ]; then
    echo -e "${YELLOW}Rebuilding images from scratch...${NC}"
    docker-compose -f docker-compose.production.green.yml build --no-cache
else
    echo -e "${YELLOW}Building images (using cache)...${NC}"
    docker-compose -f docker-compose.production.green.yml build
fi

# Tag the image
docker tag nocturna-production:latest nocturna-production:${IMAGE_TAG}

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p logs/production/green

# Stop old green container if running
if docker ps -a | grep -q nocturna-prod-green-api; then
    echo -e "${YELLOW}Stopping old green container...${NC}"
    docker stop nocturna-prod-green-api || true
    docker rm nocturna-prod-green-api || true
fi

# Start green application
echo -e "${YELLOW}Starting green application...${NC}"
docker-compose -f docker-compose.production.green.yml up -d app-green

# Wait for health check
echo -e "${YELLOW}Waiting for application to be healthy...${NC}"
RETRY_COUNT=0
MAX_RETRIES=60

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:${GREEN_API_PORT:-8201}/health > /dev/null 2>&1; then
        echo -e "${GREEN}Application is healthy!${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}Waiting for health check... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Application did not become healthy in time${NC}"
    docker-compose -f docker-compose.production.green.yml logs --tail=50 app-green
    exit 1
fi

# Show status
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Production Green Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
docker-compose -f docker-compose.production.green.yml ps

echo -e "\n${GREEN}Green API available at:${NC}"
echo -e "  http://localhost:${GREEN_API_PORT:-8201}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Test green deployment: http://localhost:${GREEN_API_PORT:-8201}/health"
echo -e "  2. When ready, switch traffic: ./scripts/deploy/switch-to-green.sh"
echo -e "  3. Monitor logs: docker-compose -f docker-compose.production.green.yml logs -f"
