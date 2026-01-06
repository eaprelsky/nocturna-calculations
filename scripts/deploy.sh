#!/bin/bash
# Blue-Green Deployment Script for Nocturna Calculations
# Usage: ./scripts/deploy.sh [blue|green|staging|auto] [--rebuild]

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

# Load environment variables
load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_info "Loading environment from .env..."
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    else
        log_error ".env file not found!"
        exit 1
    fi
}

# Get current active instance
get_active_instance() {
    if [ -f "$METADATA_FILE" ]; then
        cat "$METADATA_FILE"
    else
        echo "none"
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
    docker ps --format '{{.Names}}' | grep -q "^nocturna-api-$instance$"
}

# Wait for healthcheck
wait_for_health() {
    local instance=$1
    local port
    if [ "$instance" = "blue" ]; then
        port=8200
    elif [ "$instance" = "green" ]; then
        port=8201
    else
        port=8100  # staging
    fi
    
    log_info "Waiting for $instance instance to become healthy (port $port)..."
    
    local max_attempts=60
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
        log_info "Starting shared infrastructure (postgres + redis + network)..."
        
        # Check if old stopped container exists and remove it
        if docker ps -a --format '{{.Names}}' | grep -q "^nocturna-postgres$"; then
            log_warning "Found stopped postgres container, removing..."
            docker rm -f nocturna-postgres || true
        fi
        
        if docker ps -a --format '{{.Names}}' | grep -q "^nocturna-redis$"; then
            log_warning "Found stopped redis container, removing..."
            docker rm -f nocturna-redis || true
        fi
        
        # Stop any partial infrastructure first
        docker-compose -f "$PROJECT_ROOT/docker-compose.shared.yml" down 2>/dev/null || true
        
        # Start fresh
        if ! docker-compose -f "$PROJECT_ROOT/docker-compose.shared.yml" up -d; then
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

# Run database migrations
run_migrations() {
    local instance=$1
    
    log_info "Running database migrations..."
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.$instance.yml" exec -T "nocturna-api-$instance" alembic upgrade head; then
        log_success "Migrations completed successfully"
        return 0
    else
        log_error "Migration failed"
        return 1
    fi
}

# Deploy to instance
deploy_instance() {
    local instance=$1
    local build_flag=$2
    
    log_info "Deploying to $instance instance..."
    
    cd "$PROJECT_ROOT"
    
    # For production instances, ensure shared infrastructure
    if [ "$instance" != "staging" ]; then
        if ! ensure_shared_infrastructure; then
            log_error "Failed to ensure shared infrastructure"
            return 1
        fi
    fi
    
    # Create log directory
    mkdir -p "logs/$instance"
    
    # Build and start the instance
    log_info "Building Docker image..."
    if [ "$build_flag" = "--rebuild" ] || [ "$build_flag" = "--no-cache" ]; then
        log_info "Building without cache (full rebuild)..."
        docker-compose -f "docker-compose.$instance.yml" build --no-cache
    else
        docker-compose -f "docker-compose.$instance.yml" build
    fi
    
    log_info "Starting $instance instance..."
    docker-compose -f "docker-compose.$instance.yml" up -d
    
    # Wait for health check
    if wait_for_health "$instance"; then
        log_success "Deployment to $instance completed successfully!"
        
        # Show logs
        log_info "Last 20 lines of logs:"
        docker-compose -f "docker-compose.$instance.yml" logs --tail=20
        
        return 0
    else
        log_error "Deployment to $instance failed health check"
        log_info "Checking logs..."
        docker-compose -f "docker-compose.$instance.yml" logs --tail=50
        return 1
    fi
}

# Deploy staging
deploy_staging() {
    local build_flag=$1
    
    log_info "Deploying to STAGING environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing staging
    docker-compose -f docker-compose.staging.yml down 2>/dev/null || true
    
    # Build and deploy
    if deploy_instance "staging" "$build_flag"; then
        log_success "Staging deployment completed!"
        log_info ""
        log_info "Staging API: http://localhost:8100"
        log_info "Staging Docs: http://localhost:8100/docs"
        log_info ""
        return 0
    else
        log_error "Staging deployment failed!"
        return 1
    fi
}

# Main script
main() {
    local target_instance=$1
    local build_flag=$2
    
    cd "$PROJECT_ROOT"
    
    # Load environment
    load_env
    
    log_info "Blue-Green Deployment Script"
    log_info "=============================="
    
    # Handle staging separately
    if [ "$target_instance" = "staging" ]; then
        deploy_staging "$build_flag"
        exit $?
    fi
    
    # Determine target instance for production
    local active_instance=$(get_active_instance)
    log_info "Currently active instance: $active_instance"
    
    if [ "$target_instance" = "auto" ] || [ -z "$target_instance" ]; then
        target_instance=$(get_inactive_instance)
        log_info "Auto-selected target instance: $target_instance"
    elif [ "$target_instance" != "blue" ] && [ "$target_instance" != "green" ]; then
        log_error "Invalid instance: $target_instance. Use 'blue', 'green', 'staging', or 'auto'"
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
        log_info "     curl http://localhost:$([ "$target_instance" = "blue" ] && echo "8200" || echo "8201")/health"
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
    echo "Usage: $0 [blue|green|staging|auto] [--rebuild]"
    echo ""
    echo "Deploy Nocturna Calculations to specified instance"
    echo ""
    echo "Arguments:"
    echo "  blue     - Deploy to blue instance (port 8200)"
    echo "  green    - Deploy to green instance (port 8201)"
    echo "  staging  - Deploy to staging instance (port 8100)"
    echo "  auto     - Auto-select inactive instance (default)"
    echo ""
    echo "Options:"
    echo "  --rebuild    - Build without cache (full rebuild)"
    echo ""
    echo "Examples:"
    echo "  $0 auto              # Deploy to inactive instance"
    echo "  $0 blue              # Deploy specifically to blue"
    echo "  $0 staging --rebuild # Deploy staging with rebuild"
    exit 0
fi

main "${1:-auto}" "$2"
