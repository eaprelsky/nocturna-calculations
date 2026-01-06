#!/bin/bash
# Deployment script for Production Blue environment
# This deploys the blue slot (typically the initial production deployment)
# Usage: ./scripts/deploy/production-deploy-blue.sh [--rebuild] [--tag IMAGE_TAG]

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
echo -e "${GREEN}Nocturna Production Blue Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f "config/production.env" ]; then
    echo -e "${YELLOW}Loading production environment variables...${NC}"
    set -a
    source config/production.env
    set +a
else
    echo -e "${RED}Error: config/production.env not found${NC}"
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

# Create backup of database before deployment
echo -e "${YELLOW}Creating database backup...${NC}"
BACKUP_DIR="$PROJECT_ROOT/backups/postgres"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

if docker ps | grep -q nocturna-prod-db; then
    docker exec nocturna-prod-db pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB:-nocturna_prod}" > "$BACKUP_FILE"
    echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"
fi

# Build images
if [ "$REBUILD" = true ]; then
    echo -e "${YELLOW}Rebuilding images from scratch...${NC}"
    docker-compose -f docker-compose.production.blue.yml build --no-cache
else
    echo -e "${YELLOW}Building images (using cache)...${NC}"
    docker-compose -f docker-compose.production.blue.yml build
fi

# Tag the image
docker tag nocturna-production:latest nocturna-production:${IMAGE_TAG}

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p logs/production/blue
mkdir -p backups/postgres

# Start database and redis first (if not already running)
echo -e "${YELLOW}Starting database and cache services...${NC}"
docker-compose -f docker-compose.production.blue.yml up -d db-prod redis-prod

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database...${NC}"
sleep 10

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose -f docker-compose.production.blue.yml up migrations-prod

# Stop old blue container if running
if docker ps -a | grep -q nocturna-prod-blue-api; then
    echo -e "${YELLOW}Stopping old blue container...${NC}"
    docker stop nocturna-prod-blue-api || true
    docker rm nocturna-prod-blue-api || true
fi

# Start blue application
echo -e "${YELLOW}Starting blue application...${NC}"
docker-compose -f docker-compose.production.blue.yml up -d app-blue

# Wait for health check
echo -e "${YELLOW}Waiting for application to be healthy...${NC}"
RETRY_COUNT=0
MAX_RETRIES=60

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:${BLUE_API_PORT:-8200}/health > /dev/null 2>&1; then
        echo -e "${GREEN}Application is healthy!${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}Waiting for health check... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}Application did not become healthy in time${NC}"
    docker-compose -f docker-compose.production.blue.yml logs --tail=50 app-blue
    exit 1
fi

# Switch nginx to blue
echo -e "${YELLOW}Updating nginx to route to blue...${NC}"
cp nginx/conf.d/upstream-blue.conf nginx/conf.d/upstream.conf

# Reload nginx if running
if docker ps | grep -q nocturna-nginx; then
    docker exec nocturna-nginx nginx -s reload
    echo -e "${GREEN}Nginx reloaded to use blue deployment${NC}"
fi

# Show status
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Production Blue Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
docker-compose -f docker-compose.production.blue.yml ps

echo -e "\n${GREEN}Blue API available at:${NC}"
echo -e "  http://localhost:${BLUE_API_PORT:-8200}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Test the blue deployment"
echo -e "  2. If nginx is running, traffic is now routed to blue"
echo -e "  3. Monitor logs: docker-compose -f docker-compose.production.blue.yml logs -f"
