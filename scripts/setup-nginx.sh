#!/bin/bash
# Setup nginx configuration for Nocturna Calculations
# Usage: ./scripts/setup-nginx.sh

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

# Main script
main() {
    log_info "Nocturna Calculations - Nginx Setup"
    log_info "===================================="
    echo ""
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run with sudo"
        exit 1
    fi
    
    # Create upstream directory if doesn't exist
    if [ ! -d "/etc/nginx/upstreams" ]; then
        log_info "Creating /etc/nginx/upstreams directory..."
        mkdir -p /etc/nginx/upstreams
        log_success "Directory created"
    fi
    
    # Create staging upstream config
    log_info "Creating staging upstream config..."
    cat > /etc/nginx/upstreams/nocturna-calc-staging.conf << 'EOF'
# Staging instance
server 127.0.0.1:18100;
EOF
    log_success "Created: /etc/nginx/upstreams/nocturna-calc-staging.conf"
    
    # Create production upstream config (default to blue)
    log_info "Creating production upstream config..."
    cat > /etc/nginx/upstreams/nocturna-calc-production.conf << 'EOF'
# Active instance for production
# Managed by scripts/switch.sh
# Switch between blue and green by commenting/uncommenting lines

# Blue instance (currently active)
server 127.0.0.1:18200;

# Green instance (inactive)
# server 127.0.0.1:18201;
EOF
    log_success "Created: /etc/nginx/upstreams/nocturna-calc-production.conf"
    
    # Create staging site config
    log_info "Creating staging site config..."
    cat > /etc/nginx/sites-available/stage.calc.nocturna.ru << 'EOF'
# Nginx configuration for Staging environment
# Domain: stage.calc.nocturna.ru

upstream nocturna_calc_staging {
    include /etc/nginx/upstreams/nocturna-calc-staging.conf;
    
    keepalive 16;
    keepalive_requests 100;
    keepalive_timeout 60s;
}

server {
    listen 80;
    listen [::]:80;
    server_name stage.calc.nocturna.ru;

    # Logging
    access_log /var/log/nginx/stage.calc.nocturna.ru.access.log;
    error_log /var/log/nginx/stage.calc.nocturna.ru.error.log;

    # Client settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Proxy to staging API
    location / {
        proxy_pass http://nocturna_calc_staging;
        
        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://nocturna_calc_staging/health;
        access_log off;
    }
}
EOF
    log_success "Created: /etc/nginx/sites-available/stage.calc.nocturna.ru"
    
    # Create production site config
    log_info "Creating production site config..."
    cat > /etc/nginx/sites-available/www.calc.nocturna.ru << 'EOF'
# Nginx configuration for Production environment (Blue-Green)
# Domain: www.calc.nocturna.ru

upstream nocturna_calc_production {
    include /etc/nginx/upstreams/nocturna-calc-production.conf;
    
    keepalive 32;
    keepalive_requests 100;
    keepalive_timeout 60s;
}

server {
    listen 80;
    listen [::]:80;
    server_name www.calc.nocturna.ru calc.nocturna.ru;

    # Logging
    access_log /var/log/nginx/www.calc.nocturna.ru.access.log;
    error_log /var/log/nginx/www.calc.nocturna.ru.error.log;

    # Client settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Proxy to production API (blue-green)
    location / {
        proxy_pass http://nocturna_calc_production;
        
        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://nocturna_calc_production/health;
        access_log off;
    }
}
EOF
    log_success "Created: /etc/nginx/sites-available/www.calc.nocturna.ru"
    
    # Enable sites
    log_info "Enabling sites..."
    
    if [ ! -L "/etc/nginx/sites-enabled/stage.calc.nocturna.ru" ]; then
        ln -s /etc/nginx/sites-available/stage.calc.nocturna.ru /etc/nginx/sites-enabled/
        log_success "Enabled: stage.calc.nocturna.ru"
    else
        log_info "Already enabled: stage.calc.nocturna.ru"
    fi
    
    if [ ! -L "/etc/nginx/sites-enabled/www.calc.nocturna.ru" ]; then
        ln -s /etc/nginx/sites-available/www.calc.nocturna.ru /etc/nginx/sites-enabled/
        log_success "Enabled: www.calc.nocturna.ru"
    else
        log_info "Already enabled: www.calc.nocturna.ru"
    fi
    
    # Test nginx configuration
    log_info "Testing nginx configuration..."
    if nginx -t; then
        log_success "Nginx configuration is valid"
    else
        log_error "Nginx configuration test failed!"
        exit 1
    fi
    
    # Reload nginx
    log_info "Reloading nginx..."
    if systemctl reload nginx; then
        log_success "Nginx reloaded successfully"
    else
        log_error "Failed to reload nginx"
        exit 1
    fi
    
    echo ""
    log_success "Nginx setup completed!"
    echo ""
    log_info "Next steps:"
    log_info "  1. Ensure your applications are running:"
    log_info "     - Staging: http://127.0.0.1:18100"
    log_info "     - Production Blue: http://127.0.0.1:18200"
    log_info ""
    log_info "  2. Test the sites:"
    log_info "     curl -H 'Host: stage.calc.nocturna.ru' http://localhost/health"
    log_info "     curl -H 'Host: www.calc.nocturna.ru' http://localhost/health"
    log_info ""
    log_info "  3. Get SSL certificates:"
    log_info "     sudo certbot --nginx -d stage.calc.nocturna.ru"
    log_info "     sudo certbot --nginx -d www.calc.nocturna.ru -d calc.nocturna.ru"
    echo ""
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: sudo $0"
    echo ""
    echo "Setup nginx configuration for Nocturna Calculations"
    echo ""
    echo "This script will:"
    echo "  - Create upstream configs in /etc/nginx/upstreams/"
    echo "  - Create site configs in /etc/nginx/sites-available/"
    echo "  - Enable sites in /etc/nginx/sites-enabled/"
    echo "  - Test and reload nginx"
    exit 0
fi

main
