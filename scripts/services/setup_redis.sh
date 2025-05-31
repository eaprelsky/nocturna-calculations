#!/bin/bash
# Redis Setup Script
# Handles Redis installation and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Redis is installed
check_redis() {
    if command -v redis-cli &> /dev/null && command -v redis-server &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Install Redis
install_redis() {
    log_info "Installing Redis..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y redis-server
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS
            sudo yum install -y epel-release
            sudo yum install -y redis
        else
            log_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install redis
            brew services start redis
        else
            log_error "Homebrew not found. Please install Homebrew first."
            exit 1
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Configure Redis
configure_redis() {
    log_info "Configuring Redis..."
    
    local config_file="/etc/redis/redis.conf"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        config_file="/usr/local/etc/redis.conf"
    fi
    
    # Create custom configuration
    cat > /tmp/redis-nocturna.conf << EOF
# Nocturna Redis Configuration
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "nocturna.aof"
dir /var/lib/redis
logfile /var/log/redis/nocturna.log
EOF
    
    # Backup original config if exists
    if [ -f "$config_file" ]; then
        sudo cp "$config_file" "${config_file}.backup"
    fi
    
    # Apply configuration based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo cp /tmp/redis-nocturna.conf "$config_file"
        sudo chown redis:redis "$config_file"
        sudo chmod 640 "$config_file"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        cp /tmp/redis-nocturna.conf "$config_file"
    fi
    
    rm /tmp/redis-nocturna.conf
    log_info "Redis configuration complete"
}

# Start Redis service
start_redis() {
    log_info "Starting Redis service..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v systemctl &> /dev/null; then
            sudo systemctl enable redis-server
            sudo systemctl restart redis-server
        else
            sudo service redis-server restart
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services restart redis
    fi
    
    # Wait for Redis to be ready
    local max_attempts=30
    local attempt=0
    
    while ! redis-cli ping &> /dev/null; do
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            log_error "Redis failed to start after $max_attempts attempts"
            exit 1
        fi
        log_info "Waiting for Redis to be ready... (attempt $attempt/$max_attempts)"
        sleep 1
    done
    
    log_info "Redis is ready"
}

# Test Redis connection
test_redis() {
    log_info "Testing Redis connection..."
    
    if redis-cli ping | grep -q "PONG"; then
        log_info "Redis connection successful"
        
        # Show Redis info
        echo "Redis version: $(redis-cli --version)"
        echo "Redis memory usage: $(redis-cli info memory | grep used_memory_human | cut -d: -f2)"
    else
        log_error "Redis connection failed"
        exit 1
    fi
}

# Main function
main() {
    case "${1:-check}" in
        check)
            if check_redis; then
                log_info "Redis is installed"
                redis-cli ping &> /dev/null && log_info "Redis is running" || log_warn "Redis is not running"
            else
                log_warn "Redis is not installed"
                exit 1
            fi
            ;;
        install)
            if check_redis; then
                log_info "Redis is already installed"
            else
                install_redis
            fi
            configure_redis
            start_redis
            ;;
        start)
            start_redis
            ;;
        test)
            test_redis
            ;;
        *)
            echo "Usage: $0 {check|install|start|test}"
            echo "  check   - Check if Redis is installed and running"
            echo "  install - Install and configure Redis"
            echo "  start   - Start Redis service"
            echo "  test    - Test Redis connection"
            exit 1
            ;;
    esac
}

main "$@" 