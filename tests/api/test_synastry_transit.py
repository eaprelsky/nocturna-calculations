"""
Tests for synastry and transit endpoints
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from nocturna_calculations.api.app import app
from nocturna_calculations.api.models import User, Chart


class TestSynastryTransitEndpoints:
    """Test synastry and transit calculation endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_token(self, client, db):
        """Create test user and return auth token"""
        # Register test user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        if response.status_code == 201:
            return response.json()["access_token"]
        
        # If user already exists, login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", data=login_data)
        return response.json()["access_token"]
    
    @pytest.fixture
    def natal_chart(self, client, auth_token, db):
        """Create natal chart for testing"""
        chart_data = {
            "date": "1985-03-10",
            "time": "01:34:00",
            "latitude": 55.0288307,
            "longitude": 82.9226887,
            "timezone": "Asia/Novosibirsk"
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/charts/natal", json=chart_data, headers=headers)
        
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture
    def comparison_chart(self, client, auth_token, db):
        """Create comparison chart for testing"""
        chart_data = {
            "date": "1990-07-15",
            "time": "14:20:00",
            "latitude": 55.0288307,
            "longitude": 82.9226887,
            "timezone": "Asia/Novosibirsk"
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/charts/natal", json=chart_data, headers=headers)
        
        assert response.status_code == 200
        return response.json()
    
    def test_synastry_calculation(self, client, auth_token, natal_chart, comparison_chart):
        """Test synastry calculation between two charts"""
        synastry_request = {
            "target_chart_id": comparison_chart["chart_id"],
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
            "orb_multiplier": 1.0
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/synastry",
            json=synastry_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"] is not None
        assert "aspects" in data["data"]
        assert isinstance(data["data"]["aspects"], list)
    
    def test_synastry_with_invalid_chart(self, client, auth_token, natal_chart):
        """Test synastry with non-existent target chart"""
        synastry_request = {
            "target_chart_id": "invalid-chart-id",
            "orb_multiplier": 1.0
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/synastry",
            json=synastry_request,
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_synastry_without_auth(self, client, natal_chart, comparison_chart):
        """Test synastry without authentication"""
        synastry_request = {
            "target_chart_id": comparison_chart["chart_id"],
            "orb_multiplier": 1.0
        }
        
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/synastry",
            json=synastry_request
        )
        
        assert response.status_code == 401
    
    def test_transit_calculation(self, client, auth_token, natal_chart):
        """Test transit calculation to natal chart"""
        transit_request = {
            "transit_date": "2025-11-24",
            "transit_time": "12:00:00",
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
            "orb_multiplier": 1.0
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/transits",
            json=transit_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"] is not None
        assert "aspects" in data["data"]
        assert "transit_positions" in data["data"]
        assert isinstance(data["data"]["aspects"], list)
        assert isinstance(data["data"]["transit_positions"], dict)
    
    def test_transit_with_invalid_date(self, client, auth_token, natal_chart):
        """Test transit with invalid date format"""
        transit_request = {
            "transit_date": "invalid-date",
            "transit_time": "12:00:00",
            "orb_multiplier": 1.0
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/transits",
            json=transit_request,
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_transit_with_invalid_time(self, client, auth_token, natal_chart):
        """Test transit with invalid time format"""
        transit_request = {
            "transit_date": "2025-11-24",
            "transit_time": "invalid-time",
            "orb_multiplier": 1.0
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/transits",
            json=transit_request,
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_transit_without_auth(self, client, natal_chart):
        """Test transit without authentication"""
        transit_request = {
            "transit_date": "2025-11-24",
            "transit_time": "12:00:00",
            "orb_multiplier": 1.0
        }
        
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/transits",
            json=transit_request
        )
        
        assert response.status_code == 401
    
    def test_transit_with_custom_orb(self, client, auth_token, natal_chart):
        """Test transit with custom orb multiplier"""
        transit_request = {
            "transit_date": "2025-11-24",
            "transit_time": "12:00:00",
            "orb_multiplier": 0.5
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/transits",
            json=transit_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_synastry_with_custom_aspects(self, client, auth_token, natal_chart, comparison_chart):
        """Test synastry with custom aspect list"""
        synastry_request = {
            "target_chart_id": comparison_chart["chart_id"],
            "aspects": ["CONJUNCTION", "OPPOSITION"],
            "orb_multiplier": 1.5
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            f"/api/charts/{natal_chart['chart_id']}/synastry",
            json=synastry_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

