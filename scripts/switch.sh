#!/bin/bash
# Switch traffic between Blue and Green instances
# Usage: ./scripts/switch.sh [blue|green]

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
NGINX_UPSTREAM_FILE="$PROJECT_ROOT/nginx/conf.d/upstream.conf"

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

# Switch nginx upstream
switch_upstream() {
    local target_instance=$1
    
    log_info "Updating nginx upstream configuration..."
    
    # Copy the appropriate upstream config
    if [ "$target_instance" = "blue" ]; then
        cp "$PROJECT_ROOT/nginx/conf.d/upstream-blue.conf" "$NGINX_UPSTREAM_FILE"
    else
        cp "$PROJECT_ROOT/nginx/conf.d/upstream-green.conf" "$NGINX_UPSTREAM_FILE"
    fi
    
    log_success "Nginx upstream configuration updated"
}

# Reload nginx
reload_nginx() {
    log_info "Reloading nginx..."
    
    # Try different methods to reload nginx
    if docker ps --format '{{.Names}}' | grep -q "^nocturna-nginx$"; then
        if docker exec nocturna-nginx nginx -t 2>/dev/null; then
            docker exec nocturna-nginx nginx -s reload
            log_success "Nginx reloaded successfully"
            return 0
        fi
    fi
    
    # Try systemctl
    if command -v systemctl > /dev/null 2>&1; then
        if sudo systemctl reload nginx 2>/dev/null; then
            log_success "Nginx reloaded via systemctl"
            return 0
        fi
    fi
    
    # Try direct nginx
    if command -v nginx > /dev/null 2>&1; then
        if sudo nginx -t 2>/dev/null; then
            sudo nginx -s reload
            log_success "Nginx reloaded"
            return 0
        fi
    fi
    
    log_warning "Could not reload nginx automatically"
    log_warning "Please reload nginx manually: sudo nginx -s reload"
    return 1
}

# Update metadata
update_metadata() {
    local instance=$1
    
    # Backup current instance
    if [ -f "$METADATA_FILE" ]; then
        cp "$METADATA_FILE" "$METADATA_BACKUP"
    fi
    
    # Update current instance
    echo "$instance" > "$METADATA_FILE"
    log_info "Updated metadata: active instance is now $instance"
}

# Main script
main() {
    local target_instance=$1
    
    cd "$PROJECT_ROOT"
    
    log_info "Blue-Green Traffic Switch"
    log_info "========================="
    
    # Validate target instance
    if [ "$target_instance" != "blue" ] && [ "$target_instance" != "green" ]; then
        log_error "Invalid instance: $target_instance"
        log_error "Usage: $0 [blue|green]"
        exit 1
    fi
    
    # Get current active instance
    local current_instance=$(get_active_instance)
    log_info "Current active instance: $current_instance"
    log_info "Target instance: $target_instance"
    
    if [ "$current_instance" = "$target_instance" ]; then
        log_warning "$target_instance is already active!"
        read -p "Do you want to reload nginx anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Aborted"
            exit 0
        fi
    fi
    
    # Check if target instance is healthy
    log_info "Checking health of $target_instance instance..."
    if ! check_health "$target_instance"; then
        log_error "$target_instance instance is not healthy!"
        log_error "Please ensure the instance is running and healthy before switching"
        log_error ""
        log_error "Check logs: docker-compose -f docker-compose.$target_instance.yml logs"
        exit 1
    fi
    log_success "$target_instance instance is healthy"
    
    # Confirm switch
    log_warning "About to switch traffic from $current_instance to $target_instance"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Aborted"
        exit 0
    fi
    
    # Perform switch
    switch_upstream "$target_instance"
    reload_nginx
    update_metadata "$target_instance"
    
    # Verify switch
    log_info "Verifying switch..."
    sleep 2
    if check_health "$target_instance"; then
        log_success "Traffic successfully switched to $target_instance!"
        log_info ""
        log_info "Status:"
        log_info "  Active: $target_instance (port $([ "$target_instance" = "blue" ] && echo "${BLUE_API_PORT:-18200}" || echo "${GREEN_API_PORT:-18201}"))"
        if [ "$current_instance" != "none" ]; then
            log_info "  Inactive: $current_instance (port $([ "$current_instance" = "blue" ] && echo "${BLUE_API_PORT:-18200}" || echo "${GREEN_API_PORT:-18201}"))"
        fi
        log_info ""
        log_info "You can now stop the inactive instance if needed:"
        if [ "$current_instance" != "none" ]; then
            log_info "  docker-compose -f docker-compose.$current_instance.yml down"
        fi
    else
        log_error "Health check failed after switch!"
        log_warning "Consider rolling back: ./scripts/rollback.sh"
        exit 1
    fi
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ -z "$1" ]; then
    echo "Usage: $0 [blue|green]"
    echo ""
    echo "Switch traffic between blue and green instances"
    echo ""
    echo "Arguments:"
    echo "  blue   - Switch to blue instance (port 18200)"
    echo "  green  - Switch to green instance (port 18201)"
    echo ""
    echo "Examples:"
    echo "  $0 blue          # Switch to blue instance"
    echo "  $0 green         # Switch to green instance"
    exit 0
fi

main "$1"
