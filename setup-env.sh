#!/bin/bash

# Exit on error
set -e

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create logs directory
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/install.log"

# Remove old log file if exists
rm -f "$LOG_FILE"

# Create new log file with proper permissions
touch "$LOG_FILE"
chmod 666 "$LOG_FILE"

# Function to log messages
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Start logging
log "🚀 Starting environment setup..."
log "Log file location: $LOG_FILE"

# Debug information
log "Debug information:"
log "Current user: $(whoami)"
log "Current directory: $(pwd)"
log "PATH: $PATH"
log "SHELL: $SHELL"
log "HOME: $HOME"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find conda
find_conda() {
    # Common conda installation paths
    local conda_paths=(
        "$HOME/miniconda3"
        "$HOME/anaconda3"
        "/opt/conda"
        "/usr/local/conda"
        "/usr/local/miniconda3"
        "/usr/local/anaconda3"
        "/mnt/c/Users/*/miniconda3"
        "/mnt/c/Users/*/anaconda3"
        "/mnt/c/ProgramData/miniconda3"
        "/mnt/c/ProgramData/anaconda3"
    )
    
    # Check if conda is in PATH
    if command_exists conda; then
        log "Found conda in PATH"
        return 0
    fi
    
    # Check common installation paths
    for path in "${conda_paths[@]}"; do
        if [ -d "$path" ]; then
            log "Found conda at: $path"
            export PATH="$path/bin:$PATH"
            return 0
        fi
    done
    
    return 1
}

# Install system dependencies
log "📦 Installing system dependencies..."
if command_exists apt-get; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib redis-server
elif command_exists yum; then
    # CentOS/RHEL
    sudo yum install -y postgresql-server postgresql-contrib redis
else
    log "❌ Unsupported package manager"
    exit 1
fi

# Start and enable services
log "🔄 Starting services..."
if command_exists systemctl; then
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
else
    sudo service postgresql start
    sudo service redis-server start
fi

# Wait for services to be ready
log "⏳ Waiting for services to be ready..."
until pg_isready -h localhost -p 5432; do
    sleep 1
done

# Python setup
log "🐍 Running Python setup scripts..."

# Initialize Conda
log "Initializing Conda..."
if ! find_conda; then
    log "❌ Conda not found. Please install Miniconda or Anaconda first."
    log "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Initialize conda for shell interaction
eval "$(conda shell.bash hook)"

# Add conda-forge channel
log "Adding conda-forge channel..."
conda config --add channels conda-forge
conda config --set channel_priority flexible

# Create conda environment if it doesn't exist
if ! conda env list | grep -q "^nocturna "; then
    log "Creating conda environment 'nocturna'..."
    conda create -y -n nocturna python=3.11
fi

# Activate environment
conda activate nocturna

# Install Python dependencies
log "Installing Python dependencies..."

# Install packages from requirements files
log "Installing packages from requirements files..."
conda run -n nocturna pip install -r "$SCRIPT_DIR/requirements.txt"
conda run -n nocturna pip install -r "$SCRIPT_DIR/requirements-api.txt"

# Install yq (not in requirements as it's a system tool)
log "Installing yq..."
conda run -n nocturna pip install yq

# Verify installation
log "Verifying installation..."
if ! conda run -n nocturna python -c "import uvicorn; print('Uvicorn version:', uvicorn.__version__)"; then
    log "❌ Failed to verify uvicorn installation"
    exit 1
fi

log "✅ Environment setup completed successfully!"
log "To activate the environment, run: conda activate nocturna"
log "To start the server, run: ./run_server.sh start"

exit 0 