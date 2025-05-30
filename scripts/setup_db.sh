#!/bin/bash

# Database setup and migration script
# Usage: ./setup_db.sh {setup|migrate|status}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Error handling
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'exit_code=$?; if [ $exit_code -ne 0 ]; then echo -e "${RED}\"${last_command}\" command failed with exit code $exit_code.${NC}"; fi' EXIT

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to ensure correct Python environment is activated
ensure_environment() {
    # Check if we're in the correct conda environment
    if [ "$CONDA_DEFAULT_ENV" != "nocturna-dev" ] && [ "$CONDA_DEFAULT_ENV" != "nocturna-test" ] && [ "$CONDA_DEFAULT_ENV" != "nocturna-prod" ]; then
        echo -e "${YELLOW}Activating nocturna-dev environment...${NC}"
        
        # Try to activate the nocturna-dev environment
        if command_exists conda; then
            # Source conda.sh to make conda available in the script
            CONDA_BASE=$(conda info --base)
            source "$CONDA_BASE/etc/profile.d/conda.sh"
            
            # Activate the environment
            conda activate nocturna-dev
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}Activated nocturna-dev environment${NC}"
            else
                echo -e "${RED}Failed to activate nocturna-dev environment${NC}"
                echo "Please run: conda activate nocturna-dev"
                exit 1
            fi
        else
            echo -e "${RED}Conda not found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}Using $CONDA_DEFAULT_ENV environment${NC}"
    fi
}

# Function to check if Python environment is activated
check_python_env() {
    if [ -z "$CONDA_DEFAULT_ENV" ] && [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${RED}Error: No Python environment activated${NC}"
        echo "Please activate your conda environment first:"
        echo "    conda activate nocturna"
        exit 1
    fi
}

# Function to check database connection
check_db_connection() {
    echo -e "${YELLOW}Checking database connection...${NC}"
    python -c "
import sys
from sqlalchemy import create_engine, text
from nocturna_calculations.api.config import settings
try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Database connection successful${NC}"
        return 0
    else
        echo -e "${RED}Database connection failed${NC}"
        return 1
    fi
}

# Function to setup Alembic
setup_alembic() {
    echo -e "${YELLOW}Setting up Alembic...${NC}"
    
    # Check if alembic is installed
    if ! command_exists alembic; then
        echo "Installing Alembic..."
        pip install alembic>=1.11.0
    fi

    # Initialize if not already initialized
    if [ ! -f "alembic.ini" ]; then
        echo "Initializing Alembic..."
        alembic init migrations
        
        # Update database URL in alembic.ini
        if [ -f ".env" ]; then
            DB_URL=$(grep "DATABASE_URL=" .env | cut -d '=' -f2-)
            if [ -n "$DB_URL" ]; then
                sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = $DB_URL|" alembic.ini
                echo -e "${GREEN}Updated alembic.ini with database URL${NC}"
            else
                echo -e "${RED}Could not find DATABASE_URL in .env file${NC}"
                exit 1
            fi
        else
            echo -e "${RED}.env file not found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}Alembic already initialized${NC}"
    fi
}

# Function to run migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    python scripts/migrate.py
}

# Function to check migration status
check_migration_status() {
    echo -e "${YELLOW}Checking migration status...${NC}"
    if command_exists alembic; then
        alembic current
        echo -e "\nMigration history:"
        alembic history
    else
        echo -e "${RED}Alembic not installed${NC}"
        exit 1
    fi
}

# Main execution
main() {
    # Ensure correct environment is activated
    ensure_environment
    
    # Check Python environment
    check_python_env
    
    # Check database connection
    check_db_connection
    
    case "$1" in
        "setup")
            setup_alembic
            ;;
        "migrate")
            run_migrations
            ;;
        "status")
            check_migration_status
            ;;
        *)
            echo "Usage: $0 {setup|migrate|status}"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 