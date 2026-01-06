#!/bin/bash
# Show status of Blue-Green deployment
# Usage: ./scripts/status.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
METADATA_FILE="$PROJECT_ROOT/.current-env"

# Functions
log_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  $1"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
}

log_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "  ────────────────────────────────────────────────"
}

log_item() {
    echo -e "  $1: ${GREEN}$2${NC}"
}

log_item_warn() {
    echo -e "  $1: ${YELLOW}$2${NC}"
}

log_item_error() {
    echo -e "  $1: ${RED}$2${NC}"
}

# Get current active instance
get_active_instance() {
    if [ -f "$METADATA_FILE" ]; then
        cat "$METADATA_FILE"
    else
        echo "unknown"
    fi
}

# Check if instance is running
is_instance_running() {
    local instance=$1
    docker-compose -p nocturna -f "$PROJECT_ROOT/docker-compose.$instance.yml" ps --services --filter "status=running" 2>/dev/null | grep -q "nocturna-bot-$instance"
}

# Check if instance is healthy
check_health() {
    local instance=$1
    local port
    if [ "$instance" = "blue" ]; then
        port=8081
    else
        port=8082
    fi
    
    if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "healthy"
    else
        echo "unhealthy"
    fi
}

# Get instance version
get_instance_version() {
    local instance=$1
    local env_file="$PROJECT_ROOT/.env.$instance"
    
    if [ -f "$env_file" ]; then
        grep "^APP_VERSION=" "$env_file" 2>/dev/null | cut -d'=' -f2 || echo "unknown"
    else
        echo "no-env-file"
    fi
}

# Get git info
get_git_info() {
    cd "$PROJECT_ROOT"
    local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    local commit=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    echo "$branch ($commit)"
}

# Get instance uptime
get_instance_uptime() {
    local instance=$1
    local container="nocturna-bot-$instance"
    
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
        local created=$(docker inspect --format='{{.State.StartedAt}}' "$container" 2>/dev/null)
        if [ -n "$created" ]; then
            local created_ts=$(date -d "$created" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$created" +%s 2>/dev/null || echo "0")
            local now_ts=$(date +%s)
            local diff=$((now_ts - created_ts))
            
            if [ $diff -gt 0 ]; then
                local days=$((diff / 86400))
                local hours=$(( (diff % 86400) / 3600 ))
                local minutes=$(( (diff % 3600) / 60 ))
                
                if [ $days -gt 0 ]; then
                    echo "${days}d ${hours}h ${minutes}m"
                elif [ $hours -gt 0 ]; then
                    echo "${hours}h ${minutes}m"
                else
                    echo "${minutes}m"
                fi
            else
                echo "just started"
            fi
        else
            echo "unknown"
        fi
    else
        echo "not running"
    fi
}

# Show instance status
show_instance_status() {
    local instance=$1
    local is_active=$2
    
    log_section "$(echo $instance | tr '[:lower:]' '[:upper:]') Instance"
    
    # Active status
    if [ "$is_active" = "true" ]; then
        log_item "Status" "🟢 ACTIVE (receiving traffic)"
    else
        log_item_warn "Status" "⚪ INACTIVE (standby)"
    fi
    
    # Running status
    if is_instance_running "$instance"; then
        log_item "Container" "Running"
        
        # Uptime
        local uptime=$(get_instance_uptime "$instance")
        log_item "Uptime" "$uptime"
    else
        log_item_error "Container" "Stopped"
    fi
    
    # Health check
    local health=$(check_health "$instance")
    if [ "$health" = "healthy" ]; then
        log_item "Health" "✓ Healthy"
    else
        log_item_error "Health" "✗ Unhealthy"
    fi
    
    # Version
    local version=$(get_instance_version "$instance")
    log_item "Version" "$version"
    
    # Port
    local port
    if [ "$instance" = "blue" ]; then
        port=8081
    else
        port=8082
    fi
    log_item "Port" "$port"
    
    # Compose file
    log_item "Config" "docker-compose.$instance.yml"
}

# Main script
main() {
    cd "$PROJECT_ROOT"
    
    # Header
    log_header "Nocturna Bot - Blue-Green Deployment Status"
    
    # Active instance
    local active_instance=$(get_active_instance)
    
    # Git info
    log_section "Repository Info"
    log_item "Git Branch" "$(get_git_info)"
    log_item "Active Instance" "$(echo $active_instance | tr '[:lower:]' '[:upper:]')"
    
    # Blue instance status
    if [ "$active_instance" = "blue" ]; then
        show_instance_status "blue" "true"
    else
        show_instance_status "blue" "false"
    fi
    
    # Green instance status
    if [ "$active_instance" = "green" ]; then
        show_instance_status "green" "true"
    else
        show_instance_status "green" "false"
    fi
    
    # Staging instance status (if exists)
    if docker-compose -p nocturna -f "$PROJECT_ROOT/docker-compose.staging.yml" ps --services 2>/dev/null | grep -q "nocturna-bot-staging"; then
        log_section "STAGING Instance"
        
        if is_instance_running "staging"; then
            log_item "Container" "Running"
            local uptime=$(get_instance_uptime "staging")
            log_item "Uptime" "$uptime"
        else
            log_item_warn "Container" "Stopped"
        fi
        
        local health=$(check_health "staging")
        if [ "$health" = "healthy" ]; then
            log_item "Health" "✓ Healthy"
        else
            log_item_error "Health" "✗ Unhealthy"
        fi
        
        log_item "Port" "8083"
    fi
    
    # Database status
    log_section "Database"
    if docker ps --format '{{.Names}}' | grep -q "nocturna-postgres"; then
        log_item "PostgreSQL" "Running"
        local pg_uptime=$(get_instance_uptime "postgres")
        log_item "Uptime" "$pg_uptime"
    else
        log_item_error "PostgreSQL" "Stopped"
    fi
    
    # Quick actions
    log_section "Quick Commands"
    echo "  Deploy:    ./scripts/deploy.sh auto"
    echo "  Switch:    ./scripts/switch.sh [blue|green]"
    echo "  Rollback:  ./scripts/rollback.sh"
    echo "  Logs:      docker-compose -f docker-compose.$active_instance.yml logs -f"
    echo ""
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0"
    echo ""
    echo "Show status of Blue-Green deployment"
    exit 0
fi

main
