#!/bin/bash
# Blue-Green Deployment Script for Nocturna Telegram Bot
# Usage: ./scripts/deploy.sh [blue|green|auto]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
METADATA_FILE="$PROJECT_ROOT/.current-env"
NGINX_UPSTREAM_FILE="/etc/nginx/upstreams/nocturna-tg-production.conf"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get current active instance
get_active_instance() {
    if [ -f "$METADATA_FILE" ]; then
        cat "$METADATA_FILE"
    else
        # Try to detect from nginx config
        if grep -q "^server 127.0.0.1:8081" "$NGINX_UPSTREAM_FILE" 2>/dev/null; then
            echo "blue"
        elif grep -q "^server 127.0.0.1:8082" "$NGINX_UPSTREAM_FILE" 2>/dev/null; then
            echo "green"
        else
            echo "none"
        fi
    fi
}

# Get inactive instance
get_inactive_instance() {
    local active=$(get_active_instance)
    if [ "$active" = "blue" ]; then
        echo "green"
    elif [ "$active" = "green" ]; then
        echo "blue"
    else
        echo "blue"  # Default to blue if no active instance
    fi
}

# Check if instance is running
is_instance_running() {
    local instance=$1
    docker-compose -p nocturna -f "$PROJECT_ROOT/docker-compose.$instance.yml" ps --services --filter "status=running" | grep -q "nocturna-bot-$instance"
}

# Wait for healthcheck
wait_for_health() {
    local instance=$1
    local port
    if [ "$instance" = "blue" ]; then
        port=8081
    else
        port=8082
    fi
    
    log_info "Waiting for $instance instance to become healthy (port $port)..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "$instance instance is healthy!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    echo ""
    log_error "$instance instance failed health check after $max_attempts attempts"
    return 1
}

# Ensure shared infrastructure is running
ensure_shared_infrastructure() {
    log_info "Ensuring shared infrastructure is running..."
    
    # Check if postgres container is running
    if docker ps --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
        log_info "Postgres is already running"
        
        # Verify network exists
        if ! docker network inspect nocturna-network >/dev/null 2>&1; then
            log_warning "Network not found, recreating shared infrastructure..."
            docker-compose -f "$PROJECT_ROOT/docker-compose.shared.yml" down
            docker-compose -f "$PROJECT_ROOT/docker-compose.shared.yml" up -d
        fi
    else
        log_info "Starting shared infrastructure (postgres + network)..."
        
        # Check if old stopped container exists and remove it
        if docker ps -a --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
            log_warning "Found stopped postgres container, removing..."
            docker rm -f nocturna-postgres || true
        fi
        
        # Stop any partial infrastructure first
        docker-compose -p nocturna -f "$PROJECT_ROOT/docker-compose.shared.yml" down 2>/dev/null || true
        
        # Start fresh with explicit project name
        if ! docker-compose -p nocturna -f "$PROJECT_ROOT/docker-compose.shared.yml" up -d; then
            log_error "Failed to start shared infrastructure"
            docker-compose -f "$PROJECT_ROOT/docker-compose.shared.yml" logs
            return 1
        fi
        
        # Wait for postgres to be healthy
        log_info "Waiting for postgres to become healthy..."
        local max_attempts=30
        local attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if docker ps --filter "name=nocturna-postgres" --filter "health=healthy" | grep -q "nocturna-postgres"; then
                log_success "Postgres is healthy!"
                
                # Verify network was created
                if docker network inspect nocturna-network >/dev/null 2>&1; then
                    log_success "Network nocturna-network is ready!"
                    return 0
                else
                    log_error "Network nocturna-network was not created"
                    return 1
                fi
            fi
            
            attempt=$((attempt + 1))
            echo -n "."
            sleep 2
        done
        
        echo ""
        log_error "Postgres failed to become healthy"
        docker-compose -f "$PROJECT_ROOT/docker-compose.shared.yml" logs postgres
        return 1
    fi
}

# Deploy to instance
deploy_instance() {
    local instance=$1
    local build_flag=$2
    
    log_info "Deploying to $instance instance..."
    
    cd "$PROJECT_ROOT"
    
    # Ensure shared infrastructure is running
    if ! ensure_shared_infrastructure; then
        log_error "Failed to ensure shared infrastructure"
        return 1
    fi
    
    # Build and start the instance
    log_info "Building Docker image..."
    if [ "$build_flag" = "--no-cache" ] || [ "$build_flag" = "--rebuild" ]; then
        log_info "Building without cache (full rebuild)..."
        docker-compose -p nocturna -f "docker-compose.$instance.yml" build --no-cache
    else
        docker-compose -p nocturna -f "docker-compose.$instance.yml" build
    fi
    
    log_info "Starting $instance instance..."
    docker-compose -p nocturna -f "docker-compose.$instance.yml" up -d
    
    # Wait for health check
    if wait_for_health "$instance"; then
        log_success "Deployment to $instance completed successfully!"
        
        # Show logs
        log_info "Last 20 lines of logs:"
        docker-compose -p nocturna -f "docker-compose.$instance.yml" logs --tail=20 "nocturna-bot-$instance"
        
        return 0
    else
        log_error "Deployment to $instance failed health check"
        log_info "Checking logs..."
        docker-compose -p nocturna -f "docker-compose.$instance.yml" logs --tail=50 "nocturna-bot-$instance"
        return 1
    fi
}

# Run migrations
run_migrations() {
    local instance=$1
    
    log_info "Running database migrations on $instance instance..."
    
    if docker-compose -p nocturna -f "$PROJECT_ROOT/docker-compose.$instance.yml" exec -T "nocturna-bot-$instance" alembic upgrade head; then
        log_success "Migrations completed successfully"
        return 0
    else
        log_error "Migration failed"
        return 1
    fi
}

# Main script
main() {
    local target_instance=$1
    local build_flag=$2
    
    cd "$PROJECT_ROOT"
    
    log_info "Blue-Green Deployment Script"
    log_info "=============================="
    
    # Determine target instance
    local active_instance=$(get_active_instance)
    log_info "Currently active instance: $active_instance"
    
    if [ "$target_instance" = "auto" ] || [ -z "$target_instance" ]; then
        target_instance=$(get_inactive_instance)
        log_info "Auto-selected target instance: $target_instance"
    elif [ "$target_instance" != "blue" ] && [ "$target_instance" != "green" ]; then
        log_error "Invalid instance: $target_instance. Use 'blue', 'green', or 'auto'"
        exit 1
    fi
    
    log_info "Deploying to: $target_instance"
    log_info ""
    
    # Deploy to target instance
    if deploy_instance "$target_instance" "$build_flag"; then
        log_success "Deployment completed!"
        log_info ""
        log_info "Next steps:"
        log_info "  1. Test the $target_instance instance:"
        log_info "     curl http://localhost:$([ "$target_instance" = "blue" ] && echo "8081" || echo "8082")/health"
        log_info ""
        log_info "  2. Switch traffic to $target_instance:"
        log_info "     ./scripts/switch.sh $target_instance"
        log_info ""
        log_info "  3. If something goes wrong, rollback:"
        log_info "     ./scripts/rollback.sh"
        log_info ""
    else
        log_error "Deployment failed!"
        exit 1
    fi
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 [blue|green|auto] [--no-cache|--rebuild]"
    echo ""
    echo "Deploy Nocturna Telegram Bot to specified instance"
    echo ""
    echo "Arguments:"
    echo "  blue   - Deploy to blue instance (port 8081)"
    echo "  green  - Deploy to green instance (port 8082)"
    echo "  auto   - Auto-select inactive instance (default)"
    echo ""
    echo "Options:"
    echo "  --no-cache   - Build without cache (full rebuild)"
    echo "  --rebuild    - Alias for --no-cache"
    echo ""
    echo "Examples:"
    echo "  $0 auto                # Deploy to inactive instance (use cache)"
    echo "  $0 blue                # Deploy specifically to blue (use cache)"
    echo "  $0 green --no-cache    # Deploy to green with full rebuild"
    echo "  $0 auto --rebuild      # Deploy with full rebuild"
    exit 0
fi

main "${1:-auto}" "$2"
