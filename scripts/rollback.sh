#!/bin/bash
# Rollback to previous instance
# Usage: ./scripts/rollback.sh

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
METADATA_BACKUP="$PROJECT_ROOT/.previous-env"

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
        echo "none"
    fi
}

# Get previous instance
get_previous_instance() {
    if [ -f "$METADATA_BACKUP" ]; then
        cat "$METADATA_BACKUP"
    else
        local current=$(get_active_instance)
        if [ "$current" = "blue" ]; then
            echo "green"
        else
            echo "blue"
        fi
    fi
}

# Check if instance is running
is_instance_running() {
    local instance=$1
    docker ps --format '{{.Names}}' | grep -q "^nocturna-api-$instance$"
}

# Check if instance is healthy
check_health() {
    local instance=$1
    local port
    if [ "$instance" = "blue" ]; then
        port=${BLUE_API_PORT:-18200}
    else
        port=${GREEN_API_PORT:-18201}
    fi
    
    if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main script
main() {
    cd "$PROJECT_ROOT"
    
    log_warning "Blue-Green Rollback"
    log_warning "=================="
    
    # Get current and previous instances
    local current_instance=$(get_active_instance)
    local previous_instance=$(get_previous_instance)
    
    log_info "Current active instance: $current_instance"
    log_info "Will rollback to: $previous_instance"
    
    if [ "$current_instance" = "$previous_instance" ]; then
        log_error "Current and previous instances are the same!"
        log_error "Cannot rollback"
        exit 1
    fi
    
    # Check if previous instance is running
    log_info "Checking if $previous_instance instance is available..."
    
    if ! is_instance_running "$previous_instance"; then
        log_warning "$previous_instance instance is not running!"
        log_info "Starting $previous_instance instance..."
        docker-compose -f "docker-compose.$previous_instance.yml" up -d
        sleep 10
    fi
    
    # Check if previous instance is healthy
    if ! check_health "$previous_instance"; then
        log_error "$previous_instance instance is not healthy!"
        log_error "Cannot rollback to unhealthy instance"
        log_info "Please check logs: docker-compose -f docker-compose.$previous_instance.yml logs"
        exit 1
    fi
    log_success "$previous_instance instance is healthy"
    
    # Confirm rollback
    log_warning "This will switch traffic from $current_instance to $previous_instance"
    read -p "Continue with rollback? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback aborted"
        exit 0
    fi
    
    # Perform rollback using switch script
    log_info "Executing rollback..."
    if "$SCRIPT_DIR/switch.sh" "$previous_instance"; then
        log_success "Rollback completed successfully!"
        log_info ""
        log_info "Traffic is now routed to $previous_instance instance"
        log_info ""
        log_info "You can investigate the issue with $current_instance instance:"
        log_info "  docker-compose -f docker-compose.$current_instance.yml logs"
    else
        log_error "Rollback failed!"
        exit 1
    fi
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0"
    echo ""
    echo "Rollback to previous instance"
    echo ""
    echo "This script will switch traffic back to the previously active instance"
    exit 0
fi

main
