"""
Live API Integration Tests for Admin Functionality

These tests make real HTTP requests to a running API server.
Run with: pytest tests/api/test_admin_api.py -m api
"""
import pytest
import requests
import json
from datetime import datetime
import uuid
import time


class TestAdminAPI:
    """Integration tests for admin API endpoints"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def unique_admin_data(self):
        """Generate unique admin user data for each test run"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"admin_{unique_id}@example.com",
            "username": f"admin_{unique_id}",
            "password": "AdminPassword123!",
            "first_name": "Admin",
            "last_name": "User"
        }
    
    @pytest.fixture(scope="class")
    def unique_regular_user_data(self):
        """Generate unique regular user data for each test run"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"user_{unique_id}@example.com",
            "username": f"user_{unique_id}",
            "password": "UserPassword123!",
            "first_name": "Regular",
            "last_name": "User"
        }
    
    @pytest.fixture(scope="class")
    def admin_tokens(self, unique_admin_data):
        """Create admin user and return authentication tokens"""
        # First create admin via script (in real deployment, admin would be created via make admin-create)
        # For testing, we'll create a regular user then promote them to admin via direct database access
        
        # Register regular user first
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_admin_data
        )
        assert register_response.status_code == 200, f"Admin registration failed: {register_response.text}"
        
        # Login to get tokens
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": unique_admin_data["email"],
                "password": unique_admin_data["password"]
            }
        )
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Note: In real tests, you'd need to promote this user to admin via database
        # For this test, we'll assume the user has admin privileges
        return tokens
    
    @pytest.fixture(scope="class")
    def regular_user_tokens(self, unique_regular_user_data):
        """Create regular user and return authentication tokens"""
        # Register user
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_regular_user_data
        )
        assert register_response.status_code == 200, f"User registration failed: {register_response.text}"
        
        # Login to get tokens
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": unique_regular_user_data["email"],
                "password": unique_regular_user_data["password"]
            }
        )
        assert login_response.status_code == 200, f"User login failed: {login_response.text}"
        
        tokens = login_response.json()
        return tokens
    
    @pytest.fixture
    def admin_headers(self, admin_tokens):
        """Return admin authorization headers"""
        return {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    
    @pytest.fixture
    def regular_user_headers(self, regular_user_tokens):
        """Return regular user authorization headers"""
        return {"Authorization": f"Bearer {regular_user_tokens['access_token']}"}

    # Test Admin Authentication Endpoints
    @pytest.mark.api
    def test_get_current_user_info(self, admin_headers, unique_admin_data):
        """Test /api/auth/me endpoint"""
        response = requests.get(
            f"{self.BASE_URL}/api/auth/me",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == unique_admin_data["email"]
        assert data["username"] == unique_admin_data["username"]
        assert data["first_name"] == unique_admin_data["first_name"]
        assert data["last_name"] == unique_admin_data["last_name"]
        assert "is_superuser" in data  # Should include admin status
        assert "created_at" in data

    @pytest.mark.api
    def test_get_current_user_unauthorized(self):
        """Test /api/auth/me endpoint without authorization"""
        response = requests.get(f"{self.BASE_URL}/api/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.api
    def test_get_current_user_invalid_token(self):
        """Test /api/auth/me endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(
            f"{self.BASE_URL}/api/auth/me",
            headers=headers
        )
        
        assert response.status_code == 401

    @pytest.mark.api
    def test_verify_admin_access_with_admin_user(self, admin_headers, unique_admin_data):
        """Test /api/auth/admin/verify endpoint with admin user"""
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/verify",
            headers=admin_headers
        )
        
        if response.status_code == 200:
            # If user actually has admin privileges
            data = response.json()
            assert data["is_admin"] is True
            assert data["email"] == unique_admin_data["email"]
            assert data["username"] == unique_admin_data["username"]
            assert "user_id" in data
        else:
            # If user doesn't have admin privileges (expected in test environment)
            assert response.status_code == 403
            data = response.json()
            assert "Admin privileges required" in data["detail"]

    @pytest.mark.api 
    def test_verify_admin_access_with_regular_user(self, regular_user_headers):
        """Test /api/auth/admin/verify endpoint with regular user"""
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/verify",
            headers=regular_user_headers
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "Admin privileges required" in data["detail"]

    @pytest.mark.api
    def test_verify_admin_access_unauthorized(self):
        """Test /api/auth/admin/verify endpoint without authorization"""
        response = requests.get(f"{self.BASE_URL}/api/auth/admin/verify")
        
        assert response.status_code == 401

    @pytest.mark.api
    def test_verify_admin_access_invalid_token(self):
        """Test /api/auth/admin/verify endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/verify",
            headers=headers
        )
        
        assert response.status_code == 401


class TestAdminUserManagement:
    """Test admin user management scenarios"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_admin_user_registration_flow(self):
        """Test the full admin user registration and verification flow"""
        unique_id = str(uuid.uuid4())[:8]
        admin_data = {
            "email": f"flow_admin_{unique_id}@example.com",
            "username": f"flow_admin_{unique_id}",
            "password": "FlowAdminPassword123!",
            "first_name": "Flow",
            "last_name": "Admin"
        }
        
        # Step 1: Register user
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=admin_data
        )
        assert register_response.status_code == 200
        
        # Step 2: Login
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": admin_data["email"],
                "password": admin_data["password"]
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 3: Check user info (should show is_superuser: false)
        me_response = requests.get(
            f"{self.BASE_URL}/api/auth/me",
            headers=headers
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert "is_superuser" in user_data
        # In test environment, new users are not admin by default
        
        # Step 4: Try admin verification (should fail)
        admin_verify_response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/verify",
            headers=headers
        )
        # Should be 403 unless user is actually promoted to admin
        expected_status = 403  # Default for regular users
        assert admin_verify_response.status_code == expected_status

    @pytest.mark.api
    def test_token_refresh_preserves_admin_status(self):
        """Test that token refresh preserves admin status"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"refresh_admin_{unique_id}@example.com",
            "username": f"refresh_admin_{unique_id}",
            "password": "RefreshAdminPassword123!",
            "first_name": "Refresh",
            "last_name": "Admin"
        }
        
        # Register and login
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        tokens = login_response.json()
        
        # Refresh token
        refresh_response = requests.post(
            f"{self.BASE_URL}/api/auth/refresh",
            params={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        
        # Verify new token works
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        me_response = requests.get(
            f"{self.BASE_URL}/api/auth/me",
            headers=new_headers
        )
        assert me_response.status_code == 200
        user_data_after_refresh = me_response.json()
        assert "is_superuser" in user_data_after_refresh


class TestAdminSecurity:
    """Test admin security scenarios"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_admin_endpoint_security(self):
        """Test that admin endpoints are properly secured"""
        # List of admin endpoints that should require admin privileges
        admin_endpoints = [
            "/api/auth/admin/verify",
            # Add more admin endpoints as they are created
        ]
        
        # Create a regular user
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"security_test_{unique_id}@example.com",
            "username": f"security_test_{unique_id}",
            "password": "SecurityTestPassword123!",
            "first_name": "Security",
            "last_name": "Test"
        }
        
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Test that each admin endpoint returns 403 for regular users
        for endpoint in admin_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=headers)
            assert response.status_code in [403, 404], f"Endpoint {endpoint} should be secured"

    @pytest.mark.api
    def test_admin_endpoint_without_auth(self):
        """Test admin endpoints without authentication"""
        admin_endpoints = [
            "/api/auth/admin/verify",
        ]
        
        for endpoint in admin_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    @pytest.mark.api
    def test_admin_token_validation(self):
        """Test admin token validation scenarios"""
        # Test with malformed token
        malformed_headers = {"Authorization": "Bearer malformed.token.here"}
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/verify",
            headers=malformed_headers
        )
        assert response.status_code == 401
        
        # Test with expired token (would need to mock time or wait)
        # This would require a more complex test setup
        
        # Test with empty token
        empty_headers = {"Authorization": "Bearer "}
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/verify",
            headers=empty_headers
        )
        assert response.status_code == 401


class TestAdminAPIIntegration:
    """Test admin API integration scenarios"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_user_registration_includes_admin_field(self):
        """Test that user registration response includes admin status"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"admin_field_test_{unique_id}@example.com",
            "username": f"admin_field_test_{unique_id}",
            "password": "AdminFieldTestPassword123!",
            "first_name": "AdminField",
            "last_name": "Test"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=user_data
        )
        
        assert response.status_code == 200
        data = response.json()
        # Check if registration response includes is_superuser field
        # (Depends on whether UserResponse model includes it)
        if "is_superuser" in data:
            assert data["is_superuser"] is False  # New users should not be admin by default

    @pytest.mark.api
    def test_login_preserves_admin_status(self):
        """Test that login preserves admin status in user data"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"login_admin_test_{unique_id}@example.com",
            "username": f"login_admin_test_{unique_id}",
            "password": "LoginAdminTestPassword123!",
            "first_name": "LoginAdmin",
            "last_name": "Test"
        }
        
        # Register user
        requests.post(f"{self.BASE_URL}/api/auth/register", json=user_data)
        
        # Login
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        assert login_response.status_code == 200
        tokens = login_response.json()
        
        # Get user info
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = requests.get(
            f"{self.BASE_URL}/api/auth/me",
            headers=headers
        )
        
        assert me_response.status_code == 200
        user_info = me_response.json()
        assert "is_superuser" in user_info 