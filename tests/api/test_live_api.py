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
    def test_user_registration(self):
        """Test user registration endpoint"""
        # Use a completely unique user for this test to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"register_test_{unique_id}@example.com",
            "username": f"registeruser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Register",
            "last_name": "Test"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=user_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "created_at" in data

    @pytest.mark.api
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Use a unique user for this test
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"duplicate_test_{unique_id}@example.com",
            "username": f"duplicateuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Duplicate",
            "last_name": "Test"
        }
        
        # Register once
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        
        # Try to register again with same email
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=user_data
        )
        
        assert response.status_code == 400
        assert "already registered" in response.text.lower()

    @pytest.mark.api
    def test_user_login(self):
        """Test user login endpoint"""
        # Use a unique user for this test
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"login_test_{unique_id}@example.com",
            "username": f"loginuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Login",
            "last_name": "Test"
        }
        
        # Register user first
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        
        # Test login
        response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
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
    def test_refresh_token(self):
        """Test token refresh endpoint"""
        # Create a fresh user for this test to ensure valid tokens
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"refresh_test_{unique_id}@example.com",
            "username": f"refreshuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Refresh",
            "last_name": "Test"
        }
        
        # Register and login to get fresh tokens
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        tokens = login_response.json()
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/refresh",
            params={"refresh_token": tokens["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.api
    def test_logout(self):
        """Test logout endpoint"""
        # Create a fresh user for this test
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"logout_test_{unique_id}@example.com",
            "username": f"logoutuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Logout",
            "last_name": "Test"
        }
        
        # Register and login to get fresh tokens
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        tokens = login_response.json()
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/logout",
            params={"refresh_token": tokens["refresh_token"]}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True

    # Test Chart Endpoints
    @pytest.mark.api
    def test_get_user_charts_empty(self):
        """Test getting user charts when none exist"""
        # Create a unique user just for this test to ensure isolation
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"empty_charts_test_{unique_id}@example.com",
            "username": f"emptychartuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "EmptyCharts",
            "last_name": "Test"
        }
        
        # Register user
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=user_data
        )
        assert register_response.status_code == 200
        
        # Login to get tokens
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Test that this fresh user has no charts
        response = requests.get(
            f"{self.BASE_URL}/api/charts",
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.api
    def test_create_natal_chart(self, auth_headers):
        """Test creating a natal chart"""
        chart_data = {
            "date": "2000-01-01",
            "time": "12:00:00",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200  # Actual API returns 200, not 201
        data = response.json()
        assert "chart_id" in data  # API returns chart_id, not id
        assert "planets" in data
        assert "houses" in data

    @pytest.mark.api
    def test_get_chart_by_id(self, auth_headers):
        """Test getting a specific chart by ID"""
        # Create a chart first
        chart_data = {
            "date": "2000-01-01",
            "time": "12:00:00",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC"
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        chart_id = create_response.json()["chart_id"]  # Use chart_id from natal endpoint
        
        # Get the chart
        response = requests.get(
            f"{self.BASE_URL}/api/charts/{chart_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chart_id  # Regular chart response uses id

    @pytest.mark.api
    def test_update_chart(self, auth_headers):
        """Test updating a chart"""
        # Create a chart first
        chart_data = {
            "date": "2000-01-01",
            "time": "12:00:00",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC"
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        chart_id = create_response.json()["chart_id"]
        
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
            "date": "2000-01-01",
            "time": "12:00:00", 
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC"
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/charts/natal",
            json=chart_data,
            headers=auth_headers
        )
        chart_id = create_response.json()["chart_id"]
        
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
            "date": "2000-01-01",
            "time": "12:00:00",
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

    @pytest.mark.api
    def test_aspects_calculation(self, auth_headers):
        """Test aspects calculation"""
        calculation_data = {
            "date": "2000-01-01",
            "time": "12:00:00",
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
            "date": "2000-01-01",
            "time": "12:00:00",
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
            json={"date": "2000-01-01", "time": "12:00:00"}
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
            "time": "invalid_time",
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
    
    # Add shared fixtures for performance class
    @pytest.fixture(scope="class")
    def perf_user_data(self):
        """Generate unique user data for performance tests"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"perf_{unique_id}@example.com",
            "username": f"perfuser_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Perf",
            "last_name": "User"
        }
    
    @pytest.fixture(scope="class") 
    def perf_auth_tokens(self, perf_user_data):
        """Register performance test user and return authentication tokens"""
        # Register user
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=perf_user_data
        )
        assert register_response.status_code == 200
        
        # Login to get tokens
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": perf_user_data["email"],
                "password": perf_user_data["password"]
            }
        )
        assert login_response.status_code == 200
        
        return login_response.json()
    
    @pytest.fixture
    def perf_auth_headers(self, perf_auth_tokens):
        """Return authorization headers for performance tests"""
        return {"Authorization": f"Bearer {perf_auth_tokens['access_token']}"}
    
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
    def test_calculation_performance(self, perf_auth_headers):
        """Test calculation endpoint performance"""
        calculation_data = {
            "date": "2000-01-01",
            "time": "12:00:00",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "UTC",
            "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"]
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.BASE_URL}/api/calculations/planetary-positions",
            json=calculation_data,
            headers=perf_auth_headers
        )
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should complete in under 2 seconds


if __name__ == "__main__":
    # Run tests directly with python
    pytest.main([__file__, "-v", "-m", "api"]) 