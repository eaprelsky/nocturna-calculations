#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/test_run_${TIMESTAMP}.log"

# Remove previous log files
echo -e "${YELLOW}Cleaning up previous test logs...${NC}"
rm -f logs/test_run_*.log

# Function to log output
log_output() {
    echo "$1" | tee -a "$LOG_FILE"
}

log_output "Running Nocturna Calculations Tests"
log_output "----------------------------------------"

# Check if running in Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PYTHON="python"
else
    PYTHON="python3"
fi

# Use pytest command for all platforms
PYTEST="pytest"

# Check if virtual environment exists
if [ -d "venv" ]; then
    log_output "${YELLOW}Activating virtual environment...${NC}"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Install test requirements if needed
log_output "${YELLOW}Checking test dependencies...${NC}"
$PYTHON -m pip install -r requirements-dev.txt 2>&1 | tee -a "$LOG_FILE"

# Run regular tests
log_output "Running regular tests..."
$PYTEST tests/ -v 2>&1 | tee -a "$LOG_FILE"

# Run benchmark tests separately
log_output "Running benchmark tests..."
$PYTEST tests/performance/ -v --benchmark-only 2>&1 | tee -a "$LOG_FILE"

# Run with coverage report
log_output "Generating coverage report..."
$PYTEST tests/ -v --cov=nocturna_calculations --cov-report=term-missing --cov-report=html 2>&1 | tee -a "$LOG_FILE"

# Check if tests passed
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_output "${GREEN}All tests passed successfully!${NC}"
    log_output "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
    log_output "${YELLOW}Test log saved to ${LOG_FILE}${NC}"
else
    log_output "${RED}Some tests failed!${NC}"
    log_output "${YELLOW}Check the test log at ${LOG_FILE} for details${NC}"
    exit 1
fi

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi 