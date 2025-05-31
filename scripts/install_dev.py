"""
Development environment installation script for Conda in WSL
"""
import os
import sys
import subprocess

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

from pathlib import Path
from getpass import getpass

def run_command(command, shell=False, timeout=30):
    """Run a shell command and print output with timeout"""
    print(f"Running: {command}")
    
    # If shell=True, command should be a string, otherwise a list
    if shell and isinstance(command, list):
        command = ' '.join(str(arg) for arg in command)
    elif not shell and isinstance(command, str):
        command = command.split()
        
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=shell,
        text=True
    )
    
    try:
        for line in process.stdout:
            print(line, end='')
        
        process.wait(timeout=timeout)
        if process.returncode != 0:
            raise Exception(f"Command failed with return code {process.returncode}")
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise Exception(f"Command timed out after {timeout} seconds")

def check_service_running(service_name, check_command, timeout=5):
    """Check if a service is running with timeout"""
    try:
        result = subprocess.run(
            check_command,
            capture_output=True,
            text=True,
            shell=True,
            timeout=timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_redis():
    """Install and configure Redis in WSL"""
    print("Checking Redis installation...")
    
    # Check if Redis is installed and running
    if check_service_running("Redis", "redis-cli ping"):
        print("Redis is already installed and running")
        return
    
    print("Redis not found or not running, installing...")
    
    # Update package list
    run_command(["sudo", "apt-get", "update"], shell=True)
    
    # Install Redis
    run_command([
        "sudo", "apt-get", "install",
        "-y",
        "redis-server"
    ], shell=True)
    
    # Configure Redis
    redis_conf = """
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "appendonly.aof"
"""
    
    # Backup existing config
    run_command([
        "sudo", "cp", "/etc/redis/redis.conf",
        "/etc/redis/redis.conf.backup"
    ], shell=True)
    
    # Write new config
    with open("/tmp/redis.conf", "w") as f:
        f.write(redis_conf)
    
    run_command([
        "sudo", "cp", "/tmp/redis.conf",
        "/etc/redis/redis.conf"
    ], shell=True)
    
    # Start Redis service
    run_command(["sudo", "service", "redis-server", "start"], shell=True)
    
    # Wait for Redis to be ready
    max_retries = 5
    for i in range(max_retries):
        if check_service_running("Redis", "redis-cli ping"):
            print("Redis is now running")
            break
        if i < max_retries - 1:
            print("Waiting for Redis to start...")
            import time
            time.sleep(2)
        else:
            print("Error: Redis failed to start")
            sys.exit(1)

def install_postgresql():
    """Install PostgreSQL in WSL"""
    print("Checking PostgreSQL installation...")
    
    # Check if PostgreSQL is installed and running
    if check_service_running("PostgreSQL", "pg_isready"):
        print("PostgreSQL is already installed and running")
        return
    
    print("PostgreSQL not found or not running, installing...")
    
    # Update package list
    run_command(["sudo", "apt-get", "update"], shell=True)
    
    # Install PostgreSQL and contrib package
    run_command([
        "sudo", "apt-get", "install",
        "-y",
        "postgresql",
        "postgresql-contrib"
    ], shell=True)
    
    # Start PostgreSQL service
    run_command(["sudo", "service", "postgresql", "start"], shell=True)
    
    # Wait for PostgreSQL to be ready
    max_retries = 5
    for i in range(max_retries):
        if check_service_running("PostgreSQL", "pg_isready"):
            print("PostgreSQL is now running")
            break
        if i < max_retries - 1:
            print("Waiting for PostgreSQL to start...")
            import time
            time.sleep(2)
        else:
            print("Error: PostgreSQL failed to start")
            sys.exit(1)

def create_database(db_name, user, password, host="localhost", port=5432):
    """Create PostgreSQL database"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database {db_name}...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print("Database created successfully")
        else:
            print(f"Database {db_name} already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def setup_postgres_user(username, password):
    """Set up PostgreSQL user"""
    print(f"Setting up PostgreSQL user '{username}'...")
    
    try:
        # Check if user exists
        check_user_cmd = f"sudo -u postgres psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='{username}'\""
        result = subprocess.run(
            check_user_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        user_exists = "1" in result.stdout
        
        if not user_exists:
            print(f"Creating PostgreSQL user '{username}'...")
            # Create user
            create_user_cmd = f"sudo -u postgres psql -c \"CREATE USER {username} WITH PASSWORD '{password}'\""
            subprocess.run(create_user_cmd, shell=True, check=True, timeout=10)
            
            # Grant privileges
            grant_privileges_cmd = f"sudo -u postgres psql -c \"ALTER USER {username} WITH SUPERUSER\""
            subprocess.run(grant_privileges_cmd, shell=True, check=True, timeout=10)
            
            print(f"PostgreSQL user '{username}' created successfully")
        else:
            print(f"PostgreSQL user '{username}' already exists")
            # Update password for existing user
            update_password_cmd = f"sudo -u postgres psql -c \"ALTER USER {username} WITH PASSWORD '{password}'\""
            subprocess.run(update_password_cmd, shell=True, check=True, timeout=10)
            print(f"Password updated for PostgreSQL user '{username}'")
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up PostgreSQL user: {e}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: PostgreSQL user setup timed out")
        sys.exit(1)

def setup_conda_environment():
    """Create and activate Conda environment"""
    env_name = "nocturna-dev"
    
    # Check if conda is available
    try:
        run_command(["conda", "--version"])
    except Exception:
        print("Error: conda is not installed or not in PATH")
        sys.exit(1)
    
    # Check if environment exists
    result = subprocess.run(
        ["conda", "env", "list"],
        capture_output=True,
        text=True
    )
    
    if env_name not in result.stdout:
        print(f"Creating Conda environment '{env_name}'...")
        run_command([
            "conda", "create",
            "-n", env_name,
            "python=3.11",
            "-y"
        ])
    else:
        print(f"Conda environment '{env_name}' already exists")
    
    # Get conda environment path
    result = subprocess.run(
        ["conda", "env", "list"],
        capture_output=True,
        text=True
    )
    
    # Parse conda env list output to find the environment path
    for line in result.stdout.splitlines():
        if env_name in line and not line.startswith('#'):
            env_path = line.split()[-1]
            break
    else:
        print(f"Error: Could not find path for environment '{env_name}'")
        sys.exit(1)
    
    # Determine the path to the Python executable in the conda environment
    if os.name == "nt":  # Windows
        python_path = Path(env_path) / "python.exe"
        pip_path = Path(env_path) / "Scripts" / "pip.exe"
    else:  # Unix-like
        python_path = Path(env_path) / "bin" / "python"
        pip_path = Path(env_path) / "bin" / "pip"
    
    return python_path, pip_path, env_name

def install_dependencies(pip_path):
    """Install project dependencies"""
    print("Installing dependencies...")
    
    # Skip conda package installation due to potential permission conflicts
    # Install all packages via pip from requirements files instead
    print("Installing packages via pip...")
    run_command([str(pip_path), "install", "-r", "requirements.txt"])
    run_command([str(pip_path), "install", "-r", "requirements-api.txt"])
    run_command([str(pip_path), "install", "-r", "requirements-dev.txt"])
    
    # Setup database and run migrations using the shell script
    print("\nSetting up database...")
    run_command(["./scripts/setup_db.sh", "setup"])
    run_command(["./scripts/setup_db.sh", "migrate"])

def create_env_file(db_name, user, password, host="localhost", port=5432):
    """Create .env file with database configuration"""
    env_content = f"""# Database configuration
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{db_name}

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
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5

# Rate limiting
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_PREMIUM=1000
RATE_LIMIT_WINDOW=3600  # 1 hour in seconds

# Cache configuration
CACHE_TTL=3600  # 1 hour in seconds
CACHE_PREFIX=nocturna:
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("Created .env file")

def main():
    """Main installation function."""
    print("Starting development environment setup...")
    
    # Install PostgreSQL
    install_postgresql()
    
    # Install Redis
    install_redis()
    
    # Get database credentials
    print("\nDatabase Configuration:")
    db_name = input("Database name [nocturna]: ") or "nocturna"
    db_user = input("PostgreSQL username [postgres]: ") or "postgres"
    db_password = getpass("PostgreSQL password: ")
    db_host = input("Database host [localhost]: ") or "localhost"
    db_port_input = input("Database port [5432]: ") or "5432"
    
    # Convert port to integer
    try:
        db_port = int(db_port_input)
    except ValueError:
        print(f"Invalid port number: {db_port_input}. Using default 5432")
        db_port = 5432
    
    # Set up PostgreSQL user
    setup_postgres_user(db_user, db_password)
    
    # Create database
    create_database(db_name, db_user, db_password, db_host, db_port)
    
    # Create .env file first, before other operations
    create_env_file(db_name, db_user, db_password, db_host, db_port)
    
    # Setup conda environment
    try:
        python_path, pip_path, env_name = setup_conda_environment()
        
        # Install dependencies
        install_dependencies(pip_path)
        
        # Run migrations
        print("\nRunning database migrations...")
        run_command([str(python_path), "scripts/migrate.py"])
        
        print("\nDevelopment environment setup complete!")
        print("\nTo activate the conda environment:")
        print(f"    conda activate {env_name}")
        
        print("\nTo start the development server:")
        print("    python -m nocturna_calculations.api.app")
        
    except Exception as e:
        print(f"Warning: Conda environment setup failed: {e}")
        print("You can set up the Python environment manually:")
        print("1. Create a virtual environment")
        print("2. Install requirements from requirements.txt, requirements-api.txt, requirements-dev.txt")
        print("3. Run migrations manually")
        print("\nThe .env file has been created successfully.")
        
        # Still exit successfully since basic setup is done
        print("\nBasic setup (PostgreSQL, Redis, .env) completed successfully!")

if __name__ == "__main__":
    main() 