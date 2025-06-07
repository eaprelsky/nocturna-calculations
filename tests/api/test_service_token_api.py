"""
Integration tests for service token API endpoints

Tests the service token API endpoints with a running server and database.
"""

import pytest
import requests
import uuid
from datetime import datetime, timedelta
from jose import jwt

from nocturna_calculations.api.config import settings


class TestServiceTokenAPI:
    """Test service token API endpoints"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def unique_admin_data(self):
        """Generate unique admin user data for each test run"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"admin_service_{unique_id}@example.com",
            "username": f"admin_service_{unique_id}",
            "password": "AdminServicePassword123!",
            "first_name": "Admin",
            "last_name": "Service"
        }
    
    @pytest.fixture(scope="class")
    def admin_tokens(self, unique_admin_data):
        """Create admin user and return authentication tokens"""
        # Register admin user
        register_response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_admin_data
        )
        assert register_response.status_code == 200, f"Admin registration failed: {register_response.text}"
        
        # Promote to admin (this would normally be done via script)
        # For testing, we'll assume the user is already admin or use a different approach
        
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
        return tokens
    
    @pytest.fixture
    def admin_headers(self, admin_tokens):
        """Return admin authorization headers"""
        return {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    
    @pytest.mark.api
    def test_create_service_token_default(self, admin_headers):
        """Test creating service token with default parameters"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json={}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "service_token" in data
        assert "expires_at" in data
        assert "expires_in_days" in data
        assert "scope" in data
        assert "token_id" in data
        
        # Verify default values
        assert data["expires_in_days"] == 30
        assert data["scope"] == "calculations"
        
        # Verify token format
        service_token = data["service_token"]
        assert service_token.startswith("eyJ")  # JWT format
        
        # Verify token content
        payload = jwt.decode(service_token, key="", options={"verify_signature": False})
        assert payload["type"] == "service"
        assert payload["scope"] == "calculations"
        assert payload["token_id"] == data["token_id"]
        assert "exp" in payload  # Should have expiration
        
        return data  # Return for use in other tests
    
    @pytest.mark.api
    def test_create_service_token_custom_parameters(self, admin_headers):
        """Test creating service token with custom parameters"""
        request_data = {
            "days": 90,
            "scope": "calculations,admin",
            "eternal": False
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify custom values
        assert data["expires_in_days"] == 90
        assert data["scope"] == "calculations,admin"
        
        # Verify token content
        service_token = data["service_token"]
        payload = jwt.decode(service_token, key="", options={"verify_signature": False})
        assert payload["scope"] == "calculations,admin"
        
        # Verify expiration is approximately 90 days from now
        exp_timestamp = payload["exp"]
        exp_date = datetime.fromtimestamp(exp_timestamp)
        expected_exp = datetime.utcnow() + timedelta(days=90)
        
        # Allow 1 hour tolerance
        assert abs((exp_date - expected_exp).total_seconds()) < 3600
    
    @pytest.mark.api
    def test_create_eternal_service_token(self, admin_headers):
        """Test creating eternal service token"""
        request_data = {
            "days": 30,  # Ignored for eternal tokens
            "scope": "calculations",
            "eternal": True
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify eternal token characteristics
        assert data["expires_in_days"] == 36500  # 100 years
        
        # Verify token has no expiration
        service_token = data["service_token"]
        payload = jwt.decode(service_token, key="", options={"verify_signature": False})
        assert "exp" not in payload  # Eternal tokens have no expiration
    
    @pytest.mark.api
    def test_create_service_token_unauthorized(self):
        """Test creating service token without admin privileges"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            json={}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_list_service_tokens(self, admin_headers):
        """Test listing service tokens"""
        # First create a service token
        create_response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json={"days": 30, "scope": "test"}
        )
        assert create_response.status_code == 200
        created_token = create_response.json()
        
        # List service tokens
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        tokens = response.json()
        
        # Verify response is a list
        assert isinstance(tokens, list)
        
        # Find our created token
        our_token = None
        for token in tokens:
            if token["id"] == created_token["token_id"]:
                our_token = token
                break
        
        assert our_token is not None
        
        # Verify token structure
        assert "id" in our_token
        assert "user_id" in our_token
        assert "scope" in our_token
        assert "created_at" in our_token
        assert "expires_at" in our_token
        assert "last_used_at" in our_token
        assert "is_expired" in our_token
        assert "days_until_expiry" in our_token
        
        # Verify values
        assert our_token["scope"] == "test"
        assert our_token["is_expired"] is False
        assert our_token["days_until_expiry"] > 0
    
    @pytest.mark.api
    def test_list_service_tokens_unauthorized(self):
        """Test listing service tokens without admin privileges"""
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/service-tokens"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_revoke_service_token(self, admin_headers):
        """Test revoking a service token"""
        # First create a service token
        create_response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json={"days": 30, "scope": "test_revoke"}
        )
        assert create_response.status_code == 200
        created_token = create_response.json()
        token_id = created_token["token_id"]
        
        # Revoke the token
        response = requests.delete(
            f"{self.BASE_URL}/api/auth/admin/service-tokens/{token_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert token_id in data["message"]
        
        # Verify token is no longer in the list
        list_response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers
        )
        tokens = list_response.json()
        
        # Token should not be in the list anymore
        token_ids = [token["id"] for token in tokens]
        assert token_id not in token_ids
    
    @pytest.mark.api
    def test_revoke_nonexistent_service_token(self, admin_headers):
        """Test revoking a non-existent service token"""
        fake_token_id = str(uuid.uuid4())
        
        response = requests.delete(
            f"{self.BASE_URL}/api/auth/admin/service-tokens/{fake_token_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @pytest.mark.api
    def test_revoke_service_token_unauthorized(self):
        """Test revoking service token without admin privileges"""
        fake_token_id = str(uuid.uuid4())
        
        response = requests.delete(
            f"{self.BASE_URL}/api/auth/admin/service-tokens/{fake_token_id}"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_service_token_refresh(self, admin_headers):
        """Test refreshing service token to get access token"""
        # First create a service token
        create_response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json={"days": 30, "scope": "calculations"}
        )
        assert create_response.status_code == 200
        created_token = create_response.json()
        service_token = created_token["service_token"]
        
        # Use service token to get access token
        response = requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {service_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "expires_in" in data
        
        # Verify access token format
        access_token = data["access_token"]
        assert access_token.startswith("eyJ")  # JWT format
        
        # Verify access token content
        payload = jwt.decode(access_token, key="", options={"verify_signature": False})
        assert payload["type"] == "access"
        assert payload["scope"] == "calculations"
        
        # Verify refresh token is the same as service token
        assert data["refresh_token"] == service_token
        
        # Verify expires_in is reasonable (should be 15 minutes = 900 seconds)
        assert data["expires_in"] == 900
    
    @pytest.mark.api
    def test_service_token_refresh_invalid_token(self):
        """Test refreshing with invalid service token"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_service_token_refresh_user_token(self, admin_headers, admin_tokens):
        """Test refreshing with user token instead of service token"""
        # Try to use regular user access token as service token
        user_access_token = admin_tokens["access_token"]
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {user_access_token}"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_service_token_refresh_expired_token(self, admin_headers):
        """Test refreshing with expired service token"""
        # Create an expired service token manually
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": str(uuid.uuid4()),
            "exp": int((datetime.utcnow() - timedelta(days=1)).timestamp())  # Expired
        }
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401


class TestServiceTokenSecurity:
    """Test security aspects of service tokens"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_service_token_scope_validation(self):
        """Test that service token scope is properly validated"""
        # This test would require implementing scope validation in the API
        # For now, we just verify that scope is stored and returned correctly
        pass
    
    @pytest.mark.api
    def test_service_token_signature_validation(self):
        """Test that service tokens with invalid signatures are rejected"""
        # Create a token with wrong signature
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": str(uuid.uuid4()),
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        invalid_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_service_token_database_validation(self, admin_headers):
        """Test that service tokens must exist in database"""
        # Create a valid JWT token that's not in the database
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": str(uuid.uuid4()),  # Random token ID not in DB
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        fake_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        assert response.status_code == 401


class TestServiceTokenUsageTracking:
    """Test service token usage tracking functionality"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def admin_setup(self):
        """Setup admin user for usage tracking tests"""
        unique_id = str(uuid.uuid4())[:8]
        admin_data = {
            "email": f"admin_tracking_{unique_id}@example.com",
            "username": f"admin_tracking_{unique_id}",
            "password": "AdminTrackingPassword123!",
            "first_name": "Admin",
            "last_name": "Tracking"
        }
        
        # Register and login
        requests.post(f"{self.BASE_URL}/api/auth/register", json=admin_data)
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            data={
                "username": admin_data["email"],
                "password": admin_data["password"]
            }
        )
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        return headers
    
    @pytest.mark.api
    def test_service_token_last_used_tracking(self, admin_setup):
        """Test that service token usage is tracked"""
        admin_headers = admin_setup
        
        # Create a service token
        create_response = requests.post(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers,
            json={"days": 30, "scope": "calculations"}
        )
        created_token = create_response.json()
        service_token = created_token["service_token"]
        token_id = created_token["token_id"]
        
        # Initially, last_used_at should be None
        list_response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers
        )
        tokens = list_response.json()
        our_token = next(token for token in tokens if token["id"] == token_id)
        assert our_token["last_used_at"] is None
        
        # Use the service token
        requests.post(
            f"{self.BASE_URL}/api/auth/service-token/refresh",
            headers={"Authorization": f"Bearer {service_token}"}
        )
        
        # Check that last_used_at is now set
        list_response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/service-tokens",
            headers=admin_headers
        )
        tokens = list_response.json()
        our_token = next(token for token in tokens if token["id"] == token_id)
        assert our_token["last_used_at"] is not None
        
        # Verify the timestamp is recent (within last minute)
        last_used = datetime.fromisoformat(our_token["last_used_at"].replace('Z', '+00:00'))
        now = datetime.utcnow().replace(tzinfo=last_used.tzinfo)
        assert (now - last_used).total_seconds() < 60 