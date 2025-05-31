#!/usr/bin/env python3
"""
Bootstrap script for Nocturna Calculations
Orchestrates environment setup, service installation, and initial configuration
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message: str):
    """Print a header message"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 50}{Colors.ENDC}\n")

def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def run_command(cmd: List[str], check: bool = True, shell: bool = False) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        if shell:
            cmd = ' '.join(cmd) if isinstance(cmd, list) else cmd
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print_error(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_conda():
    """Check if conda is available"""
    result = run_command(['conda', '--version'], check=False)
    if result.returncode != 0:
        print_error("Conda not found. Please install Miniconda or Anaconda first.")
        print("Visit: https://docs.conda.io/en/latest/miniconda.html")
        sys.exit(1)
    print_success(f"Found {result.stdout.strip()}")

def check_environment(env_name: str) -> bool:
    """Check if a conda environment exists"""
    result = run_command(['conda', 'env', 'list'], check=False)
    return env_name in result.stdout

def create_environment(env_type: str):
    """Create or update a conda environment"""
    env_map = {
        'dev': ('nocturna-dev', 'environments/development.yml'),
        'test': ('nocturna-test', 'environments/testing.yml'),
        'prod': ('nocturna-prod', 'environments/production.yml'),
    }
    
    if env_type not in env_map:
        print_error(f"Unknown environment type: {env_type}")
        sys.exit(1)
    
    env_name, env_file = env_map[env_type]
    
    if not Path(env_file).exists():
        print_error(f"Environment file not found: {env_file}")
        sys.exit(1)
    
    if check_environment(env_name):
        print_warning(f"Environment '{env_name}' already exists. Updating...")
        cmd = ['conda', 'env', 'update', '-f', env_file, '--name', env_name, '--prune']
    else:
        print(f"Creating environment '{env_name}'...")
        cmd = ['conda', 'env', 'create', '-f', env_file, '--name', env_name]
    
    run_command(cmd)
    print_success(f"Environment '{env_name}' is ready")

def setup_services(install: bool = False):
    """Setup PostgreSQL and Redis"""
    script_dir = Path(__file__).parent
    postgres_script = script_dir / 'services' / 'setup_postgres.sh'
    redis_script = script_dir / 'services' / 'setup_redis.sh'
    
    # Make scripts executable
    for script in [postgres_script, redis_script]:
        if script.exists():
            script.chmod(0o755)
    
    # PostgreSQL
    print_header("Setting up PostgreSQL")
    if postgres_script.exists():
        if install:
            run_command([str(postgres_script), 'install'])
        else:
            result = run_command([str(postgres_script), 'check'], check=False)
            if result.returncode != 0:
                print_warning("PostgreSQL not installed. Use --install-services to install.")
            else:
                run_command([str(postgres_script), 'start'])
    
    # Redis
    print_header("Setting up Redis")
    if redis_script.exists():
        if install:
            run_command([str(redis_script), 'install'])
        else:
            result = run_command([str(redis_script), 'check'], check=False)
            if result.returncode != 0:
                print_warning("Redis not installed. Use --install-services to install.")
            else:
                run_command([str(redis_script), 'start'])

def create_env_files():
    """Create environment configuration files"""
    print_header("Creating environment files")
    
    env_example = """\
# Database configuration
DATABASE_URL=postgresql://nocturna:nocturna@localhost:5432/nocturna

# API configuration
API_VERSION_PREFIX=/v1
PROJECT_NAME=Nocturna Calculations
SECRET_KEY=dev_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS configuration
CORS_ORIGINS=["http://localhost:3000"]

# Redis configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10

# Environment
ENVIRONMENT=development
"""
    
    # Create .env.example
    with open('.env.example', 'w') as f:
        f.write(env_example)
    print_success("Created .env.example")
    
    # Create .env if it doesn't exist
    if not Path('.env').exists():
        with open('.env', 'w') as f:
            f.write(env_example)
        print_success("Created .env")
    else:
        print_warning(".env already exists, skipping")

def setup_database():
    """Setup database and run migrations"""
    print_header("Setting up database")
    
    # Check if database setup script exists
    setup_db_script = Path('scripts/setup_db.sh')
    if setup_db_script.exists():
        setup_db_script.chmod(0o755)
        run_command([str(setup_db_script), 'setup'])
        run_command([str(setup_db_script), 'migrate'])
        print_success("Database setup complete")
    else:
        print_warning("Database setup script not found")

def main():
    parser = argparse.ArgumentParser(
        description='Bootstrap Nocturna Calculations development environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/bootstrap.py --env dev              # Setup development environment
  python scripts/bootstrap.py --env test             # Setup testing environment
  python scripts/bootstrap.py --env prod             # Setup production environment
  python scripts/bootstrap.py --all                  # Setup everything
  python scripts/bootstrap.py --install-services     # Install system services
"""
    )
    
    parser.add_argument(
        '--env',
        choices=['dev', 'test', 'prod'],
        help='Environment to setup'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Setup everything (dev environment + services)'
    )
    parser.add_argument(
        '--install-services',
        action='store_true',
        help='Install PostgreSQL and Redis'
    )
    parser.add_argument(
        '--skip-services',
        action='store_true',
        help='Skip service setup'
    )
    parser.add_argument(
        '--skip-db',
        action='store_true',
        help='Skip database setup'
    )
    
    args = parser.parse_args()
    
    if not args.env and not args.all and not args.install_services:
        parser.print_help()
        sys.exit(1)
    
    print_header(f"Nocturna Calculations Bootstrap")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Check conda
    check_conda()
    
    # Setup environment
    if args.env:
        create_environment(args.env)
    elif args.all:
        create_environment('dev')
    
    # Setup services
    if not args.skip_services:
        setup_services(install=args.install_services or args.all)
    
    # Create environment files
    create_env_files()
    
    # Setup database
    if not args.skip_db and (args.env == 'dev' or args.all):
        setup_database()
    
    print_header("Setup Complete!")
    
    if args.env:
        env_name = f"nocturna-{args.env}"
        print(f"\nTo activate the environment:")
        print(f"  conda activate {env_name}")
    
    print("\nNext steps:")
    print("  1. Activate your environment")
    print("  2. Run 'make dev-server' to start the development server")
    print("  3. Visit http://localhost:8000/docs for API documentation")

if __name__ == '__main__':
    main() 