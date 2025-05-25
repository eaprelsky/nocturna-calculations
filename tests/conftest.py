import os
import pytest
from pathlib import Path
from typing import Generator, Dict, Any

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

# Ensure test data directory exists
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test data subdirectories
TEST_DATA_SUBDIRS = [
    "charts",
    "positions",
    "aspects",
    "houses",
    "coordinates",
    "dates",
    "security",
    "performance"
]

for subdir in TEST_DATA_SUBDIRS:
    (TEST_DATA_DIR / subdir).mkdir(exist_ok=True)

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return the test data directory path."""
    return TEST_DATA_DIR

@pytest.fixture(scope="session")
def test_charts_dir(test_data_dir: Path) -> Path:
    """Return the test charts directory path."""
    return test_data_dir / "charts"

@pytest.fixture(scope="session")
def test_positions_dir(test_data_dir: Path) -> Path:
    """Return the test positions directory path."""
    return test_data_dir / "positions"

@pytest.fixture(scope="session")
def test_aspects_dir(test_data_dir: Path) -> Path:
    """Return the test aspects directory path."""
    return test_data_dir / "aspects"

@pytest.fixture(scope="session")
def test_houses_dir(test_data_dir: Path) -> Path:
    """Return the test houses directory path."""
    return test_data_dir / "houses"

@pytest.fixture(scope="session")
def test_coordinates_dir(test_data_dir: Path) -> Path:
    """Return the test coordinates directory path."""
    return test_data_dir / "coordinates"

@pytest.fixture(scope="session")
def test_dates_dir(test_data_dir: Path) -> Path:
    """Return the test dates directory path."""
    return test_data_dir / "dates"

@pytest.fixture(scope="session")
def test_security_dir(test_data_dir: Path) -> Path:
    """Return the test security directory path."""
    return test_data_dir / "security"

@pytest.fixture(scope="session")
def test_performance_dir(test_data_dir: Path) -> Path:
    """Return the test performance directory path."""
    return test_data_dir / "performance"

@pytest.fixture(scope="function")
def test_data_cleanup() -> Generator[None, None, None]:
    """Clean up test data after each test."""
    yield
    # Add cleanup logic here if needed

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Return test configuration."""
    return {
        "coverage_threshold": 90,
        "performance_threshold": {
            "response_time": 1.0,  # seconds
            "memory_usage": 100,   # MB
            "cpu_usage": 50        # percent
        },
        "security_threshold": {
            "max_failed_attempts": 3,
            "token_expiry": 3600,  # seconds
            "password_min_length": 8
        }
    } 