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
touch "$LOG_FILE"
chmod 666 "$LOG_FILE"
echo "Starting new installation at $(date)" > "$LOG_FILE"

# Redirect all output to both console and log file
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "🚀 Starting environment setup..."
echo "Log file location: $LOG_FILE"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
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

# Try to find conda in common locations
CONDA_PATHS=(
    "$HOME/miniconda3/etc/profile.d/conda.sh"
    "$HOME/anaconda3/etc/profile.d/conda.sh"
    "/opt/conda/etc/profile.d/conda.sh"
    "/usr/local/conda/etc/profile.d/conda.sh"
    "/opt/miniconda3/etc/profile.d/conda.sh"
    "/opt/anaconda3/etc/profile.d/conda.sh"
)

# Also check if conda is in PATH
if command -v conda &> /dev/null; then
    echo "Found conda in PATH"
    CONDA_PATH=$(which conda)
    CONDA_DIR=$(dirname $(dirname "$CONDA_PATH"))
    CONDA_PATHS+=("$CONDA_DIR/etc/profile.d/conda.sh")
fi

# Try to source conda.sh from found locations
CONDA_INITIALIZED=false
for conda_path in "${CONDA_PATHS[@]}"; do
    if [ -f "$conda_path" ]; then
        echo "Found conda.sh at: $conda_path"
        . "$conda_path"
        CONDA_INITIALIZED=true
        break
    fi
done

if [ "$CONDA_INITIALIZED" = false ]; then
    echo "❌ Could not find conda.sh. Checking conda installation..."
    
    # Try to run conda directly
    if command -v conda &> /dev/null; then
        echo "Conda is installed and available in PATH"
        CONDA_VERSION=$(conda --version)
        echo "Conda version: $CONDA_VERSION"
    else
        echo "❌ Conda is not installed or not in PATH"
        echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
fi

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

echo "Installation completed at $(date)" >> "$LOG_FILE"
echo "Log file saved at: $LOG_FILE" 