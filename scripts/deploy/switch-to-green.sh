#!/bin/bash
# Switch production traffic from blue to green
# Usage: ./scripts/deploy/switch-to-green.sh [--rollback]

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

cd "$PROJECT_ROOT"

# Check if rollback is requested
ROLLBACK=false
if [ "${1:-}" = "--rollback" ]; then
    ROLLBACK=true
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}Rolling back to Blue deployment${NC}"
    echo -e "${YELLOW}========================================${NC}"
else
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Switching to Green deployment${NC}"
    echo -e "${GREEN}========================================${NC}"
fi

# Load environment variables
if [ -f "config/production.env" ]; then
    set -a
    source config/production.env
    set +a
fi

# Verify green is healthy (unless rolling back)
if [ "$ROLLBACK" = false ]; then
    echo -e "${YELLOW}Verifying green deployment health...${NC}"
    
    if ! curl -f http://localhost:${GREEN_API_PORT:-8201}/health > /dev/null 2>&1; then
        echo -e "${RED}Error: Green deployment is not healthy!${NC}"
        echo -e "${RED}Cannot switch traffic. Check green logs:${NC}"
        echo -e "${RED}  docker-compose -f docker-compose.production.green.yml logs app-green${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Green deployment is healthy!${NC}"
    
    # Update nginx configuration to use green
    echo -e "${YELLOW}Updating nginx configuration...${NC}"
    cp nginx/conf.d/upstream-green.conf nginx/conf.d/upstream.conf
else
    # Rollback: switch back to blue
    echo -e "${YELLOW}Updating nginx configuration to blue...${NC}"
    cp nginx/conf.d/upstream-blue.conf nginx/conf.d/upstream.conf
fi

# Reload nginx
if docker ps | grep -q nocturna-nginx; then
    echo -e "${YELLOW}Reloading nginx...${NC}"
    docker exec nocturna-nginx nginx -t  # Test configuration
    docker exec nocturna-nginx nginx -s reload
    echo -e "${GREEN}Nginx reloaded successfully!${NC}"
else
    echo -e "${YELLOW}Warning: nginx container not found. Starting nginx...${NC}"
    docker-compose -f docker-compose.nginx.yml up -d
fi

# Verify the switch
sleep 3
echo -e "${YELLOW}Verifying traffic switch...${NC}"

if [ "$ROLLBACK" = false ]; then
    # Switched to green
    ACTIVE_SLOT="green"
    EXPECTED_PORT="${GREEN_API_PORT:-8201}"
else
    # Rolled back to blue
    ACTIVE_SLOT="blue"
    EXPECTED_PORT="${BLUE_API_PORT:-8200}"
fi

# Test through nginx
if curl -f http://localhost:${NGINX_HTTP_PORT:-80}/health > /dev/null 2>&1; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Traffic switched successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Active deployment: ${ACTIVE_SLOT}${NC}"
    echo -e "\n${YELLOW}Monitor the deployment:${NC}"
    echo -e "  watch -n 5 'docker-compose -f docker-compose.production.${ACTIVE_SLOT}.yml ps'"
    echo -e "\n${YELLOW}Check logs:${NC}"
    echo -e "  docker-compose -f docker-compose.production.${ACTIVE_SLOT}.yml logs -f"
    echo -e "  docker logs -f nocturna-nginx"
    
    if [ "$ROLLBACK" = false ]; then
        echo -e "\n${YELLOW}To rollback to blue if needed:${NC}"
        echo -e "  ./scripts/deploy/switch-to-green.sh --rollback"
        echo -e "\n${YELLOW}To stop the old blue deployment:${NC}"
        echo -e "  docker-compose -f docker-compose.production.blue.yml stop app-blue"
    fi
else
    echo -e "${RED}Error: Could not verify traffic switch${NC}"
    exit 1
fi
