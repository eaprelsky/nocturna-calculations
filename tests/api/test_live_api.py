"""
Live API Integration Tests

These tests make real HTTP requests to a running API server.
Run with: pytest tests/api/test_live_api.py -m api
"""
import pytest
import requests
import json
from datetime import datetime
import uuid
import time


class TestLiveAPI:
    """Integration tests for the live API server"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def unique_user_data(self):
        """Generate unique user data for each test run"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"test_{unique_id}@example.com",
            "username": f"testuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
    
    @pytest.fixture(scope="class")
    def auth_tokens(self, unique_user_data):
        """Register user and return authentication tokens"""
        # Register user
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_user_data
        )
        assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
        
        # Login to get tokens
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": unique_user_data["email"],
                "password": unique_user_data["password"]
            }
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        return tokens
    
    @pytest.fixture
    def auth_headers(self, auth_tokens):
        """Return authorization headers"""
        return {"Authorization": f"Bearer {auth_tokens['access_token']}"}

    # Test Health Check
    @pytest.mark.api
    def test_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    # Test Authentication Endpoints
    @pytest.mark.api
    def test_user_registration(self, unique_user_data):
        """Test user registration endpoint"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_user_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == unique_user_data["email"]
        assert data["username"] == unique_user_data["username"]
        assert "created_at" in data

    @pytest.mark.api
    def test_user_registration_duplicate_email(self, unique_user_data):
        """Test registration with duplicate email"""
        # Register once
        requests.post(f"{self.BASE_URL}/api/auth/register", json=unique_user_data)
        
        # Try to register again with same email
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_user_data
        )
        
        assert response.status_code == 400
        assert "already registered" in response.text.lower()

    @pytest.mark.api
    def test_user_login(self, unique_user_data):
        """Test user login endpoint"""
        # Register user first
        requests.post(f"{self.BASE_URL}/api/auth/register", json=unique_user_data)
        
        # Test login
        response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": unique_user_data["email"],
                "password": unique_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "expires_in" in data

    @pytest.mark.api
    def test_user_login_invalid_credentials(self, unique_user_data):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.api
    def test_refresh_token(self, auth_tokens):
        """Test token refresh endpoint"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.api
    def test_logout(self, auth_tokens):
        """Test logout endpoint"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/logout",
            json={"refresh_token": auth_tokens["refresh_token"]}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True

    # Test Chart Endpoints
    @pytest.mark.api
    def test_get_user_charts_empty(self, auth_headers):
        """Test getting user charts when none exist"""
        response = requests.get(
            f"{self.BASE_URL}/api/charts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.api
    def test_create_natal_chart(self, auth_headers):
        """Test creating a natal chart"""
        chart_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "config": {
                "house_system": "PLACIDUS",
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"]
            }
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "date" in data
        assert "latitude" in data
        assert "longitude" in data

    @pytest.mark.api
    def test_get_chart_by_id(self, auth_headers):
        """Test getting a specific chart by ID"""
        # Create a chart first
        chart_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "config": {"house_system": "PLACIDUS"}
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        chart_id = create_response.json()["id"]
        
        # Get the chart
        response = requests.get(
            f"{self.BASE_URL}/api/charts/{chart_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chart_id

    @pytest.mark.api
    def test_update_chart(self, auth_headers):
        """Test updating a chart"""
        # Create a chart first
        chart_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "config": {"house_system": "PLACIDUS"}
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        chart_id = create_response.json()["id"]
        
        # Update the chart
        update_data = {
            "date": "2000-01-02T12:00:00Z",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        response = requests.put(
            f"{self.BASE_URL}/api/charts/{chart_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.api
    def test_delete_chart(self, auth_headers):
        """Test deleting a chart"""
        # Create a chart first
        chart_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "config": {"house_system": "PLACIDUS"}
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        chart_id = create_response.json()["id"]
        
        # Delete the chart
        response = requests.delete(
            f"{self.BASE_URL}/api/charts/{chart_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204

    # Test Calculation Endpoints
    @pytest.mark.api
    def test_planetary_positions(self, auth_headers):
        """Test planetary positions calculation"""
        calculation_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/calculations/planetary-positions",
            json=calculation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "positions" in data
        assert len(data["positions"]) == 5

    @pytest.mark.api
    def test_aspects_calculation(self, auth_headers):
        """Test aspects calculation"""
        calculation_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/calculations/aspects",
            json=calculation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "aspects" in data

    @pytest.mark.api
    def test_houses_calculation(self, auth_headers):
        """Test houses calculation"""
        calculation_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "house_system": "PLACIDUS"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/calculations/houses",
            json=calculation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "houses" in data

    # Test Authentication Required
    @pytest.mark.api
    def test_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        # Try to access charts without token
        response = requests.get(f"{self.BASE_URL}/api/charts")
        assert response.status_code == 401
        
        # Try to create chart without token
        response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json={"date": "2000-01-01T12:00:00Z"}
        )
        assert response.status_code == 401

    @pytest.mark.api
    def test_invalid_token(self):
        """Test access with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = requests.get(
            f"{self.BASE_URL}/api/charts",
            headers=headers
        )
        assert response.status_code == 401

    # Test Error Handling
    @pytest.mark.api
    def test_invalid_chart_data(self, auth_headers):
        """Test creating chart with invalid data"""
        invalid_chart_data = {
            "date": "invalid_date",
            "latitude": 200,  # Invalid latitude
            "longitude": -0.1278,
            "timezone": "UTC"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=invalid_chart_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    def test_nonexistent_chart(self, auth_headers):
        """Test accessing non-existent chart"""
        fake_id = str(uuid.uuid4())
        
        response = requests.get(
            f"{self.BASE_URL}/api/charts/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestAPIPerformance:
    """Performance tests for the API"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    @pytest.mark.performance
    def test_health_check_performance(self):
        """Test health check response time"""
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should respond in under 100ms

    @pytest.mark.api
    @pytest.mark.performance
    def test_calculation_performance(self, auth_headers):
        """Test calculation endpoint performance"""
        calculation_data = {
            "date": "2000-01-01T12:00:00Z",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"]
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.BASE_URL}/api/calculations/planetary-positions",
            json=calculation_data,
            headers=auth_headers
        )
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should complete in under 2 seconds


if __name__ == "__main__":
    # Run tests directly with python
    pytest.main([__file__, "-v", "-m", "api"]) 