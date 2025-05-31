#!/bin/bash
# PostgreSQL Setup Script
# Handles PostgreSQL installation, configuration, and user setup

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

# Check if PostgreSQL is installed
check_postgres() {
    if command -v psql &> /dev/null && command -v pg_isready &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Install PostgreSQL
install_postgres() {
    log_info "Installing PostgreSQL..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS
            sudo yum install -y postgresql-server postgresql-contrib
            sudo postgresql-setup initdb
        else
            log_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql
            brew services start postgresql
        else
            log_error "Homebrew not found. Please install Homebrew first."
            exit 1
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Start PostgreSQL service
start_postgres() {
    log_info "Starting PostgreSQL service..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v systemctl &> /dev/null; then
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
        else
            sudo service postgresql start
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    fi
    
    # Wait for PostgreSQL to be ready
    local max_attempts=30
    local attempt=0
    
    while ! pg_isready -q; do
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            log_error "PostgreSQL failed to start after $max_attempts attempts"
            exit 1
        fi
        log_info "Waiting for PostgreSQL to be ready... (attempt $attempt/$max_attempts)"
        sleep 1
    done
    
    log_info "PostgreSQL is ready"
}

# Create user and database
setup_database() {
    local db_name="${1:-nocturna}"
    local db_user="${2:-nocturna}"
    local db_pass="${3:-nocturna}"
    
    log_info "Setting up database '$db_name' with user '$db_user'..."
    
    # Create user if it doesn't exist
    sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = '$db_user'" | grep -q 1 || \
        sudo -u postgres psql -c "CREATE USER $db_user WITH PASSWORD '$db_pass';"
    
    # Create database if it doesn't exist
    sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1 || \
        sudo -u postgres psql -c "CREATE DATABASE $db_name OWNER $db_user;"
    
    # Grant all privileges
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;"
    
    log_info "Database setup complete"
}

# Main function
main() {
    case "${1:-check}" in
        check)
            if check_postgres; then
                log_info "PostgreSQL is installed"
                pg_isready && log_info "PostgreSQL is running" || log_warn "PostgreSQL is not running"
            else
                log_warn "PostgreSQL is not installed"
                exit 1
            fi
            ;;
        install)
            if check_postgres; then
                log_info "PostgreSQL is already installed"
            else
                install_postgres
            fi
            start_postgres
            ;;
        start)
            start_postgres
            ;;
        setup)
            if ! check_postgres; then
                log_error "PostgreSQL is not installed. Run '$0 install' first."
                exit 1
            fi
            setup_database "$2" "$3" "$4"
            ;;
        *)
            echo "Usage: $0 {check|install|start|setup [db_name] [db_user] [db_pass]}"
            echo "  check   - Check if PostgreSQL is installed and running"
            echo "  install - Install PostgreSQL if not present"
            echo "  start   - Start PostgreSQL service"
            echo "  setup   - Create database and user (defaults: nocturna/nocturna/nocturna)"
            exit 1
            ;;
    esac
}

main "$@" 