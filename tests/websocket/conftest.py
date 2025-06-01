import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json

from nocturna_calculations.api.app import app
from nocturna_calculations.api.database import get_db
from nocturna_calculations.api.models import User
from nocturna_calculations.api.routers.auth import create_access_token
from tests.conftest import test_config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    """Mock database session for WebSocket tests."""
    return Mock()


@pytest.fixture
def test_user():
    """Create a test user for WebSocket authentication."""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.is_active = True
    user.is_admin = False
    return user


@pytest.fixture
def test_admin_user():
    """Create a test admin user for WebSocket authentication."""
    user = Mock(spec=User)
    user.id = 2
    user.email = "admin@example.com"
    user.is_active = True
    user.is_admin = True
    return user


@pytest.fixture
def valid_token(test_user):
    """Create a valid JWT token for testing."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(test_admin_user):
    """Create a valid admin JWT token for testing."""
    return create_access_token(data={"sub": test_admin_user.email})


@pytest.fixture
def invalid_token():
    """Create an invalid JWT token for testing."""
    return "invalid.jwt.token"


@pytest.fixture
def websocket_client():
    """Create a test client for WebSocket testing."""
    return TestClient(app)


@pytest.fixture
def mock_chart_data():
    """Mock chart data for WebSocket calculation tests."""
    return {
        "id": "test-chart-123",
        "date": "1990-05-15",
        "time": "14:30:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "config": {
            "house_system": "PLACIDUS",
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
            "orbs": {
                "conjunction": 10.0,
                "opposition": 10.0,
                "trine": 8.0,
                "square": 8.0,
                "sextile": 6.0
            }
        }
    }


@pytest.fixture
def websocket_calculation_request():
    """Sample WebSocket calculation request."""
    return {
        "chart_id": "test-chart-123",
        "calculation_type": "positions",
        "parameters": {
            "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"]
        }
    }


@pytest.fixture
def mock_calculation_result():
    """Mock calculation result for WebSocket tests."""
    return {
        "SUN": {
            "longitude": 54.7,
            "latitude": 0.0,
            "distance": 1.0,
            "speed": 0.96,
            "is_retrograde": False
        },
        "MOON": {
            "longitude": 142.3,
            "latitude": -1.2,
            "distance": 0.002,
            "speed": 12.5,
            "is_retrograde": False
        }
    }


@pytest.fixture
def websocket_test_config():
    """WebSocket-specific test configuration."""
    config = test_config()
    config.update({
        "websocket": {
            "connection_timeout": 30,
            "max_connections_per_user": 5,
            "heartbeat_interval": 30,
            "max_message_size": 1024 * 1024,  # 1MB
            "rate_limit_messages_per_minute": 60
        }
    })
    return config


class MockWebSocket:
    """Mock WebSocket for testing without actual connections."""
    
    def __init__(self):
        self.state = "CONNECTING"
        self.messages_sent = []
        self.messages_received = []
        self.closed = False
        self.close_code = None
        
    async def accept(self):
        """Mock WebSocket accept."""
        self.state = "CONNECTED"
        
    async def send_json(self, data: Dict[str, Any]):
        """Mock sending JSON data."""
        if self.closed:
            raise RuntimeError("WebSocket is closed")
        self.messages_sent.append(json.dumps(data))
        
    async def send_text(self, data: str):
        """Mock sending text data."""
        if self.closed:
            raise RuntimeError("WebSocket is closed")
        self.messages_sent.append(data)
        
    async def receive_json(self) -> Dict[str, Any]:
        """Mock receiving JSON data."""
        if self.closed:
            raise RuntimeError("WebSocket is closed")
        if not self.messages_received:
            raise RuntimeError("No messages to receive")
        return json.loads(self.messages_received.pop(0))
        
    async def receive_text(self) -> str:
        """Mock receiving text data."""
        if self.closed:
            raise RuntimeError("WebSocket is closed")
        if not self.messages_received:
            raise RuntimeError("No messages to receive")
        return self.messages_received.pop(0)
        
    async def close(self, code: int = 1000):
        """Mock WebSocket close."""
        self.closed = True
        self.close_code = code
        self.state = "CLOSED"
        
    def add_received_message(self, message: str):
        """Add a message to be received."""
        self.messages_received.append(message)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    return MockWebSocket()


@pytest.fixture
async def mock_connection_manager():
    """Mock ConnectionManager for testing."""
    from nocturna_calculations.api.routers.websocket import ConnectionManager
    
    manager = ConnectionManager()
    # Replace the connections dict with a mock-friendly version
    manager.active_connections = {}
    return manager 