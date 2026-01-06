#!/bin/bash
# Switch production traffic from green to blue
# Usage: ./scripts/deploy/switch-to-blue.sh

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

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Switching to Blue deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
elif [ -f "config/production.env" ]; then
    set -a
    source config/production.env
    set +a
fi

# Verify blue is healthy
echo -e "${YELLOW}Verifying blue deployment health...${NC}"

if ! curl -f http://localhost:${BLUE_API_PORT:-8200}/health > /dev/null 2>&1; then
    echo -e "${RED}Error: Blue deployment is not healthy!${NC}"
    echo -e "${RED}Cannot switch traffic. Check blue logs:${NC}"
    echo -e "${RED}  docker-compose -f docker-compose.production.blue.yml logs app-blue${NC}"
    exit 1
fi

echo -e "${GREEN}Blue deployment is healthy!${NC}"

# Update nginx configuration to use blue
echo -e "${YELLOW}Updating nginx configuration...${NC}"
cp nginx/conf.d/upstream-blue.conf nginx/conf.d/upstream.conf

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

if curl -f http://localhost:${NGINX_HTTP_PORT:-80}/health > /dev/null 2>&1; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Traffic switched successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Active deployment: blue${NC}"
    echo -e "\n${YELLOW}To stop the old green deployment:${NC}"
    echo -e "  docker-compose -f docker-compose.production.green.yml stop app-green"
else
    echo -e "${RED}Error: Could not verify traffic switch${NC}"
    exit 1
fi
