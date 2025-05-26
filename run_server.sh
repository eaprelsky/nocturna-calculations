#!/bin/bash

# Configuration
APP_NAME="nocturna-calculations"
CONFIG_FILE="config/system.yaml"
LOG_DIR="logs"
PID_FILE="logs/server.pid"
CONDA_ENV="nocturna"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${2:-$GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Error logging function
error_log() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    log "Checking dependencies..."
    
    # Check if conda is installed
    if ! command -v conda &> /dev/null; then
        error_log "conda is not installed. Please install Miniconda or Anaconda first."
        exit 1
    fi
    
    # Check if yq is installed
    if ! command -v yq &> /dev/null; then
        error_log "yq is not installed. Please install it first: pip install yq"
        exit 1
    fi
    
    # Check if config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        error_log "Configuration file $CONFIG_FILE not found"
        exit 1
    fi
    
    log "All dependencies are satisfied"
}

# Get configuration values
get_config() {
    local key=$1
    local default=$2
    local value=$(yq eval ".$key" "$CONFIG_FILE")
    if [ "$value" = "null" ]; then
        if [ -n "$default" ]; then
            echo "$default"
        else
            error_log "Configuration key '$key' not found in $CONFIG_FILE"
            exit 1
        fi
    else
        echo "$value"
    fi
}

# Start the server
start_server() {
    log "Starting $APP_NAME server..."
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            error_log "Server is already running with PID $pid"
            exit 1
        else
            log "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi
    
    # Create log directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    # Get configuration
    local host=$(get_config "server.host" "127.0.0.1")
    local port=$(get_config "server.port" "8000")
    local workers=$(get_config "server.workers" "1")
    local log_level=$(get_config "server.log_level" "info")
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV"
    
    # Start server with proper error handling
    if [ "$workers" -gt 1 ]; then
        # Production mode with workers
        log "Starting in production mode with $workers workers"
        uvicorn nocturna_calculations.api.app:app \
            --host "$host" \
            --port "$port" \
            --workers "$workers" \
            --log-level "$log_level" \
            --no-access-log \
            --no-server-header \
            --no-date-header \
            --proxy-headers \
            --forwarded-allow-ips "*" \
            --timeout-keep-alive 75 \
            --limit-concurrency 1000 \
            --backlog 2048 \
            --limit-max-requests 10000 \
            --reload-dir nocturna_calculations \
            > "$LOG_DIR/server.log" 2>&1 &
    else
        # Development mode with reload
        log "Starting in development mode with auto-reload"
        uvicorn nocturna_calculations.api.app:app \
            --host "$host" \
            --port "$port" \
            --reload \
            --reload-dir nocturna_calculations \
            --log-level "$log_level" \
            > "$LOG_DIR/server.log" 2>&1 &
    fi
    
    # Save PID
    echo $! > "$PID_FILE"
    
    # Wait for server to start
    local max_attempts=30
    local attempt=1
    local started=false
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://$host:$port/health" > /dev/null; then
            started=true
            break
        fi
        
        # Check if process is still running
        if ! ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
            error_log "Server failed to start. Check logs for details:"
            echo "=== Server Log ==="
            tail -n 20 "$LOG_DIR/server.log"
            echo "=== Error Log ==="
            tail -n 20 "$LOG_DIR/error.log"
            rm -f "$PID_FILE"
            exit 1
        fi
        
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ "$started" = true ]; then
        log "Server started successfully on http://$host:$port"
    else
        error_log "Server failed to start within $max_attempts seconds"
        echo "=== Server Log ==="
        tail -n 20 "$LOG_DIR/server.log"
        echo "=== Error Log ==="
        tail -n 20 "$LOG_DIR/error.log"
        stop_server
        exit 1
    fi
}

# Stop the server
stop_server() {
    log "Stopping $APP_NAME server..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        # Check if process exists and is our server
        if ps -p "$pid" > /dev/null 2>&1; then
            # Try graceful shutdown first
            kill -TERM "$pid"
            
            # Wait for process to stop
            local max_attempts=30
            local attempt=1
            
            while [ $attempt -le $max_attempts ]; do
                if ! ps -p "$pid" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
                attempt=$((attempt + 1))
            done
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                log "Server did not stop gracefully, forcing shutdown..."
                kill -9 "$pid"
            fi
        fi
        
        rm -f "$PID_FILE"
        log "Server stopped"
    else
        log "No PID file found, server may not be running"
    fi
}

# Check server status
check_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Server is running with PID $pid"
            return 0
        else
            log "Server is not running (stale PID file)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        log "Server is not running"
        return 1
    fi
}

# Main script
case "$1" in
    start)
        check_dependencies
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 