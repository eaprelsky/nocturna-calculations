# Testing Guide

This guide explains how to run the API tests for the Nocturna Calculations project.

## Quick Start

### 1. Set up the test environment (one-time setup)

```bash
make setup-test
```

### 2. Start the development server (in one terminal)

```bash
conda activate nocturna-dev
make dev
```

### 3. Run API tests (in another terminal)

```bash
conda activate nocturna-test
make test-api
```

## Test Environment Setup

The project uses separate conda environments for development and testing:

- **nocturna-dev**: For running the development server
- **nocturna-test**: For running tests (includes testing-specific packages)

### Why separate environments?

- **Isolation**: Tests run in a clean environment without dev-specific packages
- **Python Version**: Test environment uses Python 3.9 for compatibility testing
- **Dependencies**: Includes testing frameworks and performance profiling tools
- **Stability**: Avoids conflicts between development and testing dependencies

## Running Tests

### Available Make Targets

```bash
# Run all API tests
make test-api

# Run specific test categories
make test-api-auth           # Authentication tests
make test-api-charts         # Chart management tests  
make test-api-calculations   # Calculation tests
make test-api-performance    # Performance tests

# Quick run (less verbose)
make test-api-quick
```

### Direct Test Runner

You can also run the test runner directly:

```bash
# In nocturna-test environment
python run_api_tests.py --help

# Examples
python run_api_tests.py                    # All tests
python run_api_tests.py --auth             # Auth tests only
python run_api_tests.py --verbose          # Verbose output
python run_api_tests.py --performance      # Performance tests
```

## Test Categories

### 🔐 Authentication Tests (`test-api-auth`)
- User registration
- Login/logout
- Token refresh
- Authorization checks
- Invalid credentials handling

### 📊 Chart Tests (`test-api-charts`)
- Creating natal charts
- Retrieving charts
- Updating chart data
- Deleting charts
- Chart ownership validation

### 🔬 Calculation Tests (`test-api-calculations`)
- Planetary position calculations
- Aspect calculations
- House system calculations
- Input validation

### ⚡ Performance Tests (`test-api-performance`)
- Response time validation
- Health check performance
- Calculation speed tests

## Troubleshooting

### Server Not Running
```
❌ Server is not running at http://localhost:8000
```

**Solution**: Start the development server:
```bash
conda activate nocturna-dev
make dev
```

### Wrong Environment
```
❌ Test environment not active
```

**Solution**: Activate the test environment:
```bash
conda activate nocturna-test
```

### Environment Not Set Up
```
❌ Please activate nocturna-test environment first
```

**Solution**: Set up and activate the test environment:
```bash
make setup-test
conda activate nocturna-test
```

### Test Failures

1. **Check server is running**: Make sure the dev server is running in another terminal
2. **Database issues**: Run `make db-migrate` in the dev environment
3. **Port conflicts**: Ensure port 8000 is available
4. **Environment issues**: Try recreating the test environment

## Test Results

Tests generate several outputs:

- **Console output**: Real-time test results
- **Coverage reports**: In `htmlcov/` directory (if enabled)
- **Performance metrics**: Response times and benchmark results

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```bash
# Setup
make setup-test
conda activate nocturna-test

# Start server in background
conda activate nocturna-dev
make dev &

# Wait for server to start
sleep 10

# Run tests
make test-api-quick
```

## Writing New Tests

API tests are located in `tests/api/test_live_api.py`. To add new tests:

1. Follow the existing test structure
2. Use the `auth_headers` fixture for authenticated requests
3. Mark tests with `@pytest.mark.api`
4. Add performance tests with `@pytest.mark.performance`
5. Test both success and error cases

Example test:
```python
@pytest.mark.api
def test_new_endpoint(self, auth_headers):
    """Test description"""
    response = requests.post(
        f"{self.BASE_URL}/api/new-endpoint",
        json={"data": "value"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "expected_field" in response.json()
``` 