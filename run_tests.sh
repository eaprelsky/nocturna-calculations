#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Nocturna Calculations Tests${NC}"
echo "----------------------------------------"

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
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Install test requirements if needed
echo -e "${YELLOW}Checking test dependencies...${NC}"
$PYTHON -m pip install -r requirements-dev.txt

# Run tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}"
$PYTEST tests/ \
    --cov=nocturna_calculations \
    --cov-report=term-missing \
    --cov-report=html \
    -v

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi 