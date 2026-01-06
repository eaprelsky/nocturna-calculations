#!/bin/bash
# Check Blue-Green Infrastructure Status
# Quick diagnostic tool for troubleshooting

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Nocturna Blue-Green Infrastructure Check ===${NC}\n"

# Check Docker
echo -e "${BLUE}1. Docker Status${NC}"
if command -v docker >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Docker is installed"
    docker --version
else
    echo -e "   ${RED}✗${NC} Docker not found"
    exit 1
fi

echo ""

# Check Docker Compose
echo -e "${BLUE}2. Docker Compose Status${NC}"
if command -v docker-compose >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Docker Compose is installed"
    docker-compose --version
else
    echo -e "   ${RED}✗${NC} Docker Compose not found"
    exit 1
fi

echo ""

# Check PostgreSQL Container
echo -e "${BLUE}3. PostgreSQL Container${NC}"
if docker ps --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
    echo -e "   ${GREEN}✓${NC} Container is running"
    
    # Check health
    health=$(docker inspect --format='{{.State.Health.Status}}' nocturna-postgres 2>/dev/null || echo "no-healthcheck")
    if [ "$health" = "healthy" ]; then
        echo -e "   ${GREEN}✓${NC} Health status: healthy"
    else
        echo -e "   ${YELLOW}⚠${NC} Health status: $health"
    fi
    
    # Show uptime
    started=$(docker inspect --format='{{.State.StartedAt}}' nocturna-postgres 2>/dev/null)
    echo -e "   ${BLUE}ℹ${NC} Started: $started"
elif docker ps -a --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
    echo -e "   ${YELLOW}⚠${NC} Container exists but is STOPPED"
    echo -e "   ${YELLOW}➜${NC} Fix: docker rm -f nocturna-postgres && docker-compose -f docker-compose.shared.yml up -d"
else
    echo -e "   ${RED}✗${NC} Container not found"
    echo -e "   ${YELLOW}➜${NC} Fix: docker-compose -f docker-compose.shared.yml up -d"
fi

echo ""

# Check Redis Container
echo -e "${BLUE}4. Redis Container${NC}"
if docker ps --format '{{.Names}}' | grep -q "^nocturna-redis$"; then
    echo -e "   ${GREEN}✓${NC} Container is running"
    
    # Check health
    health=$(docker inspect --format='{{.State.Health.Status}}' nocturna-redis 2>/dev/null || echo "no-healthcheck")
    if [ "$health" = "healthy" ]; then
        echo -e "   ${GREEN}✓${NC} Health status: healthy"
    else
        echo -e "   ${YELLOW}⚠${NC} Health status: $health"
    fi
elif docker ps -a --format '{{.Names}}' | grep -q "^nocturna-redis$"; then
    echo -e "   ${YELLOW}⚠${NC} Container exists but is STOPPED"
    echo -e "   ${YELLOW}➜${NC} Fix: docker rm -f nocturna-redis && docker-compose -f docker-compose.shared.yml up -d"
else
    echo -e "   ${RED}✗${NC} Container not found"
    echo -e "   ${YELLOW}➜${NC} Fix: docker-compose -f docker-compose.shared.yml up -d"
fi

echo ""

# Check Network
echo -e "${BLUE}5. Docker Network${NC}"
if docker network inspect nocturna-network >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Network 'nocturna-network' exists"
    
    # Show connected containers
    containers=$(docker network inspect nocturna-network --format='{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null)
    if [ -n "$containers" ]; then
        echo -e "   ${BLUE}ℹ${NC} Connected: $containers"
    fi
else
    echo -e "   ${RED}✗${NC} Network 'nocturna-network' not found"
    echo -e "   ${YELLOW}➜${NC} Fix: docker-compose -f docker-compose.shared.yml down && docker-compose -f docker-compose.shared.yml up -d"
fi

echo ""

# Check Volumes
echo -e "${BLUE}6. Docker Volumes${NC}"
if docker volume inspect nocturna_postgres_data >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Volume 'nocturna_postgres_data' exists"
else
    echo -e "   ${YELLOW}⚠${NC} Volume 'nocturna_postgres_data' not found"
    echo -e "   ${BLUE}ℹ${NC} Will be created on first run"
fi

if docker volume inspect nocturna_redis_data >/dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Volume 'nocturna_redis_data' exists"
else
    echo -e "   ${YELLOW}⚠${NC} Volume 'nocturna_redis_data' not found"
    echo -e "   ${BLUE}ℹ${NC} Will be created on first run"
fi

echo ""

# Check Blue Instance
echo -e "${BLUE}7. Blue Instance${NC}"
if docker ps --format '{{.Names}}' | grep -q "^nocturna-api-blue$"; then
    echo -e "   ${GREEN}✓${NC} Container is running"
    
    # Check health
    if curl -sf http://localhost:8200/health >/dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} Health check: OK"
    else
        echo -e "   ${YELLOW}⚠${NC} Health check: Failed"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} Container not running"
fi

echo ""

# Check Green Instance
echo -e "${BLUE}8. Green Instance${NC}"
if docker ps --format '{{.Names}}' | grep -q "^nocturna-api-green$"; then
    echo -e "   ${GREEN}✓${NC} Container is running"
    
    # Check health
    if curl -sf http://localhost:8201/health >/dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} Health check: OK"
    else
        echo -e "   ${YELLOW}⚠${NC} Health check: Failed"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} Container not running"
fi

echo ""

# Check Staging Instance
echo -e "${BLUE}9. Staging Instance${NC}"
if docker ps --format '{{.Names}}' | grep -q "^nocturna-staging-api$"; then
    echo -e "   ${GREEN}✓${NC} Container is running"
    
    # Check health
    if curl -sf http://localhost:8100/health >/dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} Health check: OK"
    else
        echo -e "   ${YELLOW}⚠${NC} Health check: Failed"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} Container not running"
fi

echo ""

# Summary
echo -e "${BLUE}=== Summary ===${NC}"
echo ""

# Count issues
issues=0

if ! docker ps --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
    issues=$((issues + 1))
    if docker ps -a --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
        echo -e "${YELLOW}⚠${NC} PostgreSQL container exists but is stopped"
    else
        echo -e "${RED}✗${NC} PostgreSQL is not running"
    fi
fi

if ! docker ps --format '{{.Names}}' | grep -q "^nocturna-redis$"; then
    issues=$((issues + 1))
    if docker ps -a --format '{{.Names}}' | grep -q "^nocturna-redis$"; then
        echo -e "${YELLOW}⚠${NC} Redis container exists but is stopped"
    else
        echo -e "${RED}✗${NC} Redis is not running"
    fi
fi

if ! docker network inspect nocturna-network >/dev/null 2>&1; then
    issues=$((issues + 1))
    echo -e "${RED}✗${NC} Network is missing"
fi

blue_running=$(docker ps --format '{{.Names}}' | grep -c "^nocturna-api-blue$" || echo 0)
green_running=$(docker ps --format '{{.Names}}' | grep -c "^nocturna-api-green$" || echo 0)

if [ "$blue_running" -eq 0 ] && [ "$green_running" -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} No production instances running"
fi

if [ "$issues" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All infrastructure is healthy!"
    echo ""
    echo -e "Next steps:"
    echo -e "  - Deploy: ${BLUE}./scripts/deploy.sh auto${NC}"
    echo -e "  - Status: ${BLUE}./scripts/status.sh${NC}"
else
    echo ""
    echo -e "Fix infrastructure:"
    echo -e "  1. ${BLUE}docker-compose -f docker-compose.shared.yml down${NC}"
    echo -e "  2. ${BLUE}docker-compose -f docker-compose.shared.yml up -d${NC}"
    echo -e "  3. ${BLUE}./scripts/deploy.sh auto${NC}"
fi

echo ""
