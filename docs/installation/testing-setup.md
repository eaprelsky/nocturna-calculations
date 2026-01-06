# Testing Environment Setup

This guide covers setting up the Nocturna Calculations project for **testing and benchmarking**, including unit tests, integration tests, performance benchmarks, and quality assurance.

## Overview

The testing environment (`nocturna-test`) includes:
- Python 3.9 (for compatibility testing)
- Comprehensive testing frameworks
- Performance benchmarking tools
- Security testing tools
- Code quality verification tools

## Quick Setup

### Automated Setup (Recommended)
```bash
# Clone the repository (if not already done)
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Setup testing environment
make setup-test

# Activate environment
conda activate nocturna-test
```

### Manual Setup
```bash
# Create conda environment
conda env create -f environments/testing.yml

# Activate environment
conda activate nocturna-test

# Install additional test dependencies
pip install -r requirements-test.txt
```

## Detailed Installation Steps

### 1. Prerequisites Check
```bash
# Verify conda installation
conda --version

# Check available disk space (need ~1.5GB)
df -h .

# Verify git installation (for test data)
git --version
```

### 2. Environment Creation
```bash
# Create testing environment
conda env create -f environments/testing.yml

# Verify environment creation
conda env list | grep nocturna-test
```

### 3. Environment Activation
```bash
# Activate testing environment
conda activate nocturna-test

# Verify activation
which python
python --version  # Should show Python 3.9.x
```

### 4. Test Dependencies Installation
```bash
# Install test-specific dependencies
pip install -r requirements-test.txt

# Verify key testing tools
pytest --version
black --version
flake8 --version
mypy --version
```

### 5. Test Configuration
```bash
# Verify pytest configuration
cat pytest.ini

# Check test discovery
pytest --collect-only
```

## Testing Framework Overview

### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── core/               # Core calculation tests
│   ├── api/                # API unit tests
│   └── utils/              # Utility function tests
├── integration/            # Integration tests
│   ├── database/           # Database integration
│   ├── api/                # Full API integration
│   └── services/           # Service integration
├── performance/            # Performance benchmarks
│   ├── calculations/       # Calculation benchmarks
│   ├── api/                # API performance tests
│   └── database/           # Database performance
├── security/               # Security tests
│   ├── api/                # API security tests
│   └── data/               # Data validation tests
└── regression/             # Regression tests
    ├── fixtures/           # Test data fixtures
    └── snapshots/          # Expected outputs
```

### Test Categories

| Category | Purpose | Command |
|----------|---------|---------|
| **Unit** | Fast, isolated tests | `pytest tests/unit/` |
| **Integration** | Component interaction tests | `pytest tests/integration/` |
| **Performance** | Benchmarks and performance | `pytest tests/performance/` |
| **Security** | Security vulnerability tests | `pytest tests/security/` |
| **Regression** | Prevent regressions | `pytest tests/regression/` |

## Running Tests

### Basic Test Commands
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=nocturna_calculations

# Run in parallel
pytest -n auto

# Run specific test file
pytest tests/unit/core/test_calculations.py

# Run specific test function
pytest tests/unit/core/test_calculations.py::test_natal_chart_calculation
```

### Advanced Test Options
```bash
# Run with markers
pytest -m unit              # Run only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m "api and not slow" # API tests excluding slow ones

# Run with specific configurations
pytest --benchmark-only     # Only benchmark tests
pytest --no-cov            # Skip coverage
pytest --timeout=30        # Set timeout for tests

# Generate reports
pytest --html=report.html   # HTML report
pytest --junitxml=junit.xml # JUnit XML report
pytest --cov-report=html    # HTML coverage report
```

### Test Environment Variables
```bash
# Set test database (optional)
export TEST_DATABASE_URL="postgresql://test:test@localhost:5432/nocturna_test"

# Enable debug mode for tests
export NOCTURNA_DEBUG=true

# Set test data path
export TEST_DATA_PATH="tests/fixtures/data"

# Configure test logging
export LOG_LEVEL=DEBUG
```

## Performance Benchmarking

### Benchmark Tests
```bash
# Run all benchmarks
pytest tests/performance/ --benchmark-only

# Run specific benchmark
pytest tests/performance/test_calculation_benchmarks.py --benchmark-only

# Compare benchmarks
pytest --benchmark-compare

# Save benchmark results
pytest --benchmark-save=baseline

# Compare against baseline
pytest --benchmark-compare=baseline
```

### Benchmark Configuration
The testing environment includes `pytest-benchmark` configuration:

```ini
# pytest.ini
benchmark_min_rounds = 5
benchmark_warmup = True
benchmark_warmup_iterations = 100000
```

### Custom Benchmark Example
```python
def test_natal_chart_calculation_performance(benchmark):
    """Benchmark natal chart calculation performance."""
    calculator = ChartCalculator()
    
    result = benchmark(
        calculator.calculate_natal_chart,
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    assert result is not None
```

## Code Quality Testing

### Linting and Formatting
```bash
# Check code formatting
black --check .

# Format code
black .

# Check code style
flake8

# Sort imports
isort --check-only .

# Fix import sorting
isort .
```

### Type Checking
```bash
# Run type checking
mypy nocturna_calculations/

# Check specific module
mypy nocturna_calculations/core/calculations.py

# Generate type coverage report
mypy --html-report mypy-report nocturna_calculations/
```

### Security Testing
```bash
# Security vulnerability scanning
bandit -r nocturna_calculations/

# Dependency security check
safety check

# Check for hardcoded secrets
pytest tests/security/test_secrets.py
```

## Load Testing

### API Load Testing with Locust
```bash
# Start locust for API load testing
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run headless load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 1m --headless
```

### Database Load Testing
```bash
# Run database performance tests
pytest tests/performance/test_database_performance.py -v

# Stress test database connections
pytest tests/performance/test_connection_pool.py -v
```

## Test Data Management

### Test Fixtures
```bash
# Create test data
python scripts/create_test_data.py --environment test

# Load test fixtures
pytest --fixtures

# Update test snapshots
pytest --snapshot-update
```

### Test Database
```bash
# Setup test database
./scripts/setup_db.sh test

# Reset test database
./scripts/setup_db.sh reset-test

# Seed test database
python scripts/seed_test_db.py
```

## Continuous Integration Testing

### GitHub Actions Integration
The testing environment is configured for CI/CD:

```yaml
# .github/workflows/test.yml
- name: Setup Testing Environment
  run: |
    conda env create -f environments/testing.yml
    conda activate nocturna-test

- name: Run Test Suite
  run: |
    pytest tests/ --cov=nocturna_calculations --cov-report=xml

- name: Run Security Tests
  run: |
    bandit -r nocturna_calculations/
    safety check
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit checks
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

## Test Coverage

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=nocturna_calculations --cov-report=html

# View coverage report
open htmlcov/index.html

# Coverage with branch analysis
pytest --cov=nocturna_calculations --cov-branch

# Fail on low coverage
pytest --cov=nocturna_calculations --cov-fail-under=90
```

### Coverage Configuration
```ini
# .coveragerc
[run]
source = nocturna_calculations
omit = 
    */tests/*
    */venv/*
    */migrations/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

## Testing Best Practices

### Writing Tests
```python
# Good test structure
def test_calculation_with_valid_input():
    """Test calculation with valid input parameters."""
    # Arrange
    calculator = ChartCalculator()
    date = "2024-03-20"
    time = "12:00:00"
    
    # Act
    result = calculator.calculate_natal_chart(date, time, 55.7558, 37.6173)
    
    # Assert
    assert result is not None
    assert result.date == date
    assert len(result.planets) > 0
```

### Test Organization
1. **One test per function/behavior**
2. **Clear test names describing the scenario**
3. **Arrange-Act-Assert pattern**
4. **Use fixtures for common setup**
5. **Mock external dependencies**

### Performance Test Guidelines
1. **Establish baselines** for critical calculations
2. **Test with realistic data sizes**
3. **Monitor memory usage**
4. **Test concurrent access patterns**
5. **Validate under load**

## Troubleshooting

### Common Issues

1. **Test discovery fails**:
   ```bash
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Verify test structure
   pytest --collect-only
   ```

2. **Benchmark tests too slow**:
   ```bash
   # Reduce benchmark iterations
   pytest --benchmark-min-rounds=1
   
   # Skip slow benchmarks
   pytest -m "not slow"
   ```

3. **Coverage collection fails**:
   ```bash
   # Install coverage plugin
   pip install pytest-cov
   
   # Clear coverage data
   coverage erase
   ```

4. **Memory issues during testing**:
   ```bash
   # Run tests sequentially
   pytest --forked
   
   # Limit parallel workers
   pytest -n 2
   ```

### Environment Issues

1. **Package conflicts**:
   ```bash
   # Recreate environment
   conda env remove -n nocturna-test
   conda env create -f environments/testing.yml
   ```

2. **Version mismatches**:
   ```bash
   # Check package versions
   conda list
   pip list
   
   # Update environment
   conda env update -f environments/testing.yml --prune
   ```

## Environment Switching

### From Development to Testing
```bash
# Deactivate current environment
conda deactivate

# Activate testing environment
conda activate nocturna-test

# Verify switch
python --version  # Should show 3.9.x
pytest --version
```

### Automated Switching
```bash
# Use environment switcher
./scripts/environments/switch_environment.py --env test

# Verify environment
./scripts/environments/validate_environment.py
```

## Next Steps

After testing environment setup:

1. **Run the full test suite**: `make test`
2. **Review test results**: Check coverage and benchmark reports
3. **Set up CI/CD**: Configure automated testing
4. **Write new tests**: Add tests for new features
5. **Monitor performance**: Track benchmark trends

## Maintenance

### Regular Maintenance
```bash
# Update test dependencies
conda env update -f environments/testing.yml --prune

# Clean test artifacts
make clean-test

# Update test data
python scripts/update_test_fixtures.py

# Refresh benchmarks
pytest tests/performance/ --benchmark-save=latest
```

### Environment Health Check
```bash
# Validate testing environment
./scripts/environments/validate_environment.py --env test

# Full test health check
make test-health-check
``` 