#!/bin/bash

# Exit on error
set -e

# Setup logging
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/install.log"

# Create logs directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    chmod 777 "$LOG_DIR"
fi

# Clear previous log and ensure write permissions
rm -f "$LOG_FILE"  # Remove old log if exists
touch "$LOG_FILE"
chmod 666 "$LOG_FILE"
echo "Starting new installation at $(date)" > "$LOG_FILE"

# Redirect all output to both console and log file
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "🚀 Starting environment setup..."
echo "Log file location: $LOG_FILE"

# Debug information
echo "Debug information:"
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
echo "PATH: $PATH"
echo "SHELL: $SHELL"
echo "HOME: $HOME"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as: sudo -E ./setup-env.sh"
    echo "The -E flag is required to preserve your environment variables"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    echo "❌ Could not detect OS"
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt-get update
    apt-get install -y postgresql postgresql-contrib redis-server
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"RHEL"* ]]; then
    dnf install -y postgresql-server postgresql-contrib redis
    postgresql-setup --initdb
else
    echo "❌ Unsupported OS: $OS"
    exit 1
fi

# Start and enable services
echo "🔄 Starting services..."
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    systemctl start postgresql
    systemctl enable postgresql
    systemctl start redis-server
    systemctl enable redis-server
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"RHEL"* ]]; then
    systemctl start postgresql
    systemctl enable postgresql
    systemctl start redis
    systemctl enable redis
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
max_retries=5
for i in $(seq 1 $max_retries); do
    if pg_isready -h localhost -p 5432 && redis-cli ping > /dev/null 2>&1; then
        break
    fi
    if [ $i -eq $max_retries ]; then
        echo "❌ Services failed to start properly"
        exit 1
    fi
    echo "Waiting for services to start... ($i/$max_retries)"
    sleep 2
done

# Run Python setup scripts
echo "🐍 Running Python setup scripts..."

# Initialize conda
echo "Initializing Conda..."

# Try to find conda in common WSL locations
CONDA_PATHS=(
    "/mnt/c/Users/$SUDO_USER/miniconda3"
    "/mnt/c/Users/$SUDO_USER/anaconda3"
    "/mnt/c/Users/$SUDO_USER/AppData/Local/Continuum/miniconda3"
    "/mnt/c/Users/$SUDO_USER/AppData/Local/Continuum/anaconda3"
    "$HOME/miniconda3"
    "$HOME/anaconda3"
    "/opt/conda"
)

for CONDA_PATH in "${CONDA_PATHS[@]}"; do
    if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
        echo "Found conda at: $CONDA_PATH"
        source "$CONDA_PATH/etc/profile.d/conda.sh"
        break
    fi
done

# Try to find conda in PATH
if command -v conda &> /dev/null; then
    echo "Found conda in PATH"
    CONDA_PATH=$(which conda)
    echo "Conda path: $CONDA_PATH"
    CONDA_VERSION=$(conda --version)
    echo "Conda version: $CONDA_VERSION"
    
    # Create conda environment if it doesn't exist
    if ! conda env list | grep -q "^nocturna "; then
        echo "Creating conda environment 'nocturna'..."
        conda create -y -n nocturna python=3.11
    else
        echo "Conda environment 'nocturna' already exists"
    fi
    
    # Activate conda environment
    echo "Activating conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate nocturna
    
    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pip install -r requirements-test.txt
    
    # Run install_dev.py
    echo "📦 Running install_dev.py..."
    python scripts/install_dev.py
    
    # Run database migrations
    echo "🔄 Running database migrations..."
    python scripts/migrate.py
    
    echo "✅ Environment setup completed!"
    echo "
To activate the Conda environment:
conda activate nocturna
"
else
    echo "❌ Conda is not installed or not in PATH"
    echo "Current PATH: $PATH"
    echo "Please ensure conda is installed and run the script with: sudo -E ./setup-env.sh"
    echo "The -E flag is required to preserve your environment variables"
    echo "If conda is installed but not found, please add it to your PATH"
    exit 1
fi

echo "Installation completed at $(date)" >> "$LOG_FILE"
echo "Log file saved at: $LOG_FILE" 