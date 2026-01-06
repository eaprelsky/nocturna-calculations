#!/bin/bash
# Deployment script for Staging environment
# Usage: ./scripts/deploy/staging-deploy.sh [--rebuild]

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
echo -e "${GREEN}Nocturna Staging Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Load environment variables (check multiple locations)
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables from .env...${NC}"
    set -a
    source .env
    set +a
elif [ -f "config/staging.env" ]; then
    echo -e "${YELLOW}Loading environment variables from config/staging.env...${NC}"
    set -a
    source config/staging.env
    set +a
else
    echo -e "${RED}Error: .env or config/staging.env not found${NC}"
    exit 1
fi

# Check for rebuild flag
REBUILD=false
if [ "${1:-}" = "--rebuild" ]; then
    REBUILD=true
fi

# Stop existing containers
echo -e "${YELLOW}Stopping existing staging containers...${NC}"
docker-compose -f docker-compose.staging.yml down

# Remove old images if rebuild requested
if [ "$REBUILD" = true ]; then
    echo -e "${YELLOW}Rebuilding images from scratch...${NC}"
    docker-compose -f docker-compose.staging.yml build --no-cache
else
    echo -e "${YELLOW}Building images (using cache)...${NC}"
    docker-compose -f docker-compose.staging.yml build
fi

# Create necessary directories
echo -e "${YELLOW}Creating log directories...${NC}"
mkdir -p logs/staging

# Start services
echo -e "${YELLOW}Starting staging services...${NC}"
docker-compose -f docker-compose.staging.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 5

# Check health
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker-compose -f docker-compose.staging.yml ps | grep -q "healthy"; then
        echo -e "${GREEN}Services are healthy!${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}Waiting for services... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Services did not become healthy in time${NC}"
    docker-compose -f docker-compose.staging.yml logs --tail=50
    exit 1
fi

# Show running containers
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Staging Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
docker-compose -f docker-compose.staging.yml ps

# Display access information
echo -e "\n${GREEN}Staging API available at:${NC}"
echo -e "  http://localhost:${STAGING_API_PORT:-8100}"
echo -e "  http://localhost:${STAGING_API_PORT:-8100}/docs"
echo -e "\n${GREEN}Database:${NC}"
echo -e "  Host: localhost:${STAGING_POSTGRES_PORT:-5433}"
echo -e "  Database: ${POSTGRES_DB:-nocturna_staging}"
echo -e "\n${GREEN}Redis:${NC}"
echo -e "  Host: localhost:${STAGING_REDIS_PORT:-6380}"
echo -e "\n${YELLOW}View logs:${NC}"
echo -e "  docker-compose -f docker-compose.staging.yml logs -f"
