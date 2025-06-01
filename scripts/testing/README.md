# Testing Scripts

This directory contains utility scripts for running various types of tests in the Nocturna Calculations project.

## Available Scripts

### `run_api_tests.py`

Comprehensive API integration test runner for live server testing.

**Features:**
- Tests against running server (localhost:8000)
- Environment validation (nocturna-test recommended)
- Filtered test execution (auth, charts, calculations, performance)
- Verbose output options

**Usage:**
```bash
# Run all API tests
python scripts/testing/run_api_tests.py

# Run specific test categories
python scripts/testing/run_api_tests.py --auth
python scripts/testing/run_api_tests.py --charts
python scripts/testing/run_api_tests.py --calculations
python scripts/testing/run_api_tests.py --performance

# Verbose output
python scripts/testing/run_api_tests.py --verbose
```

**Prerequisites:**
- Server running on localhost:8000 (`make dev` in nocturna-dev environment)
- nocturna-test environment activated (`conda activate nocturna-test`)

### `run_tests.sh`

Legacy test runner with advanced logging and cross-platform support.

**Features:**
- Comprehensive test suite execution
- Timestamped log files
- Coverage report generation
- Virtual environment auto-detection
- Cross-platform compatibility (Windows/Unix)

**Usage:**
```bash
# Run all tests with logging
./scripts/testing/run_tests.sh
```

**Generated Output:**
- Test logs in `logs/test_run_TIMESTAMP.log`
- Coverage reports in `htmlcov/index.html`

## Integration with Make

These scripts are integrated with the project's Makefile:

```bash
# API tests (uses run_api_tests.py)
make test-api
make test-api-auth
make test-api-charts

# Standard tests (uses pytest directly)
make test
make test-unit
make coverage
```

## Recommendation

For most development work, use the Makefile targets which provide a consistent interface. Use the individual scripts directly when you need their specific features like detailed logging or custom filtering.

---

For more information about testing, see the [Development Guide](../../docs/development/README.md). 