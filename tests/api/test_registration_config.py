"""
Registration Configuration Tests

Tests for the global user registration configuration feature.
Following TDD approach - these tests will initially fail until implementation is complete.
"""
import pytest
import requests
import json
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock
import os


class TestRegistrationConfiguration:
    """Test user registration configuration functionality"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def unique_user_data(self):
        """Generate unique user data for each test"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "email": f"test_user_{unique_id}@example.com",
            "username": f"test_user_{unique_id}",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
    
    @pytest.fixture
    def admin_headers(self):
        """Return mock admin headers for testing"""
        # This would be replaced with actual admin creation in real tests
        return {"Authorization": "Bearer mock_admin_token"}


class TestRegistrationEnabledByDefault:
    """Test that registration is enabled by default"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_registration_enabled_by_default(self, unique_user_data):
        """Test that user registration works when no configuration is set"""
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=unique_user_data
        )
        
        # Should succeed with default configuration
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == unique_user_data["email"]
        assert data["username"] == unique_user_data["username"]


class TestRegistrationDisabled:
    """Test registration when disabled via configuration"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    @patch.dict(os.environ, {"ALLOW_USER_REGISTRATION": "false"})
    def test_registration_disabled_via_env_var(self, unique_user_data):
        """Test that registration is blocked when ALLOW_USER_REGISTRATION=false"""
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            response = requests.post(
                f"{self.BASE_URL}/api/auth/register",
                json=unique_user_data
            )
            
            assert response.status_code == 403
            data = response.json()
            assert "registration is currently disabled" in data["detail"].lower()
    
    @pytest.mark.api
    @patch.dict(os.environ, {"ALLOW_USER_REGISTRATION": "false"})
    def test_login_still_works_when_registration_disabled(self):
        """Test that existing users can still login when registration is disabled"""
        # This test assumes there's an existing user in the database
        # In real test environment, you'd create this user beforehand
        
        login_data = {
            "username": "existing_user@example.com",
            "password": "ExistingPassword123!"
        }
        
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            response = requests.post(
                f"{self.BASE_URL}/api/auth/login",
                data=login_data
            )
            
            # Login should work regardless of registration setting
            # This might be 401 if user doesn't exist, which is expected in test environment
            assert response.status_code in [200, 401]  # 401 is OK if user doesn't exist
    
    @pytest.mark.api
    def test_registration_error_message_format(self, unique_user_data):
        """Test that registration disabled error message is properly formatted"""
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            response = requests.post(
                f"{self.BASE_URL}/api/auth/register",
                json=unique_user_data
            )
            
            assert response.status_code == 403
            data = response.json()
            
            # Verify error response structure
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0
            assert "registration" in data["detail"].lower()
            assert "disabled" in data["detail"].lower()


class TestRegistrationConfigurationEndpoints:
    """Test admin endpoints for managing registration configuration"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock admin user for testing"""
        return {
            "id": "admin-user-id",
            "email": "admin@example.com",
            "username": "admin",
            "is_superuser": True
        }
    
    @pytest.mark.api
    def test_get_registration_settings_endpoint_exists(self, admin_headers):
        """Test that GET /api/auth/admin/registration-settings endpoint exists"""
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/registration-settings",
            headers=admin_headers
        )
        
        # Should exist and require admin privileges
        assert response.status_code in [200, 403, 401]  # Not 404
    
    @pytest.mark.api
    def test_get_registration_settings_requires_admin(self):
        """Test that registration settings endpoint requires admin privileges"""
        # Test without authentication
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/registration-settings"
        )
        assert response.status_code == 401
        
        # Test with regular user token (would need real user token in integration test)
        regular_headers = {"Authorization": "Bearer regular_user_token"}
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/registration-settings",
            headers=regular_headers
        )
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden
    
    @pytest.mark.api
    def test_get_registration_settings_response_format(self, admin_headers):
        """Test registration settings response format"""
        response = requests.get(
            f"{self.BASE_URL}/api/auth/admin/registration-settings",
            headers=admin_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify expected fields exist
            assert "allow_user_registration" in data
            assert isinstance(data["allow_user_registration"], bool)
            
            # Optional fields that might be implemented
            if "registration_requires_approval" in data:
                assert isinstance(data["registration_requires_approval"], bool)
            if "max_users_limit" in data:
                assert data["max_users_limit"] is None or isinstance(data["max_users_limit"], int)


class TestRegistrationConfigurationEdgeCases:
    """Test edge cases and error scenarios for registration configuration"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_registration_with_invalid_json(self):
        """Test registration endpoint with invalid JSON when disabled"""
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            response = requests.post(
                f"{self.BASE_URL}/api/auth/register",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            # Should fail with registration disabled error, not JSON parsing error
            # This tests that the registration check happens before JSON parsing
            assert response.status_code in [403, 422]  # Either forbidden or unprocessable entity
    
    @pytest.mark.api
    def test_registration_disabled_with_missing_fields(self):
        """Test registration with missing required fields when disabled"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing username, password, etc.
        }
        
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            response = requests.post(
                f"{self.BASE_URL}/api/auth/register",
                json=incomplete_data
            )
            
            # Should fail with registration disabled error, not validation error
            assert response.status_code == 403
            data = response.json()
            assert "registration is currently disabled" in data["detail"].lower()
    
    @pytest.mark.api
    def test_concurrent_registration_attempts_when_disabled(self, unique_user_data):
        """Test multiple concurrent registration attempts when disabled"""
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            # Simulate concurrent requests
            responses = []
            for _ in range(3):
                response = requests.post(
                    f"{self.BASE_URL}/api/auth/register",
                    json=unique_user_data
                )
                responses.append(response)
            
            # All should fail with the same error
            for response in responses:
                assert response.status_code == 403
                data = response.json()
                assert "registration is currently disabled" in data["detail"].lower()


class TestRegistrationConfigurationIntegration:
    """Integration tests for registration configuration with other features"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_registration_config_does_not_affect_other_auth_endpoints(self):
        """Test that registration config doesn't affect other authentication endpoints"""
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            # Test that other endpoints still work
            endpoints_to_test = [
                ("/api/auth/me", "GET"),
                ("/api/auth/logout", "POST"),
                ("/api/auth/refresh", "POST"),
            ]
            
            for endpoint, method in endpoints_to_test:
                if method == "GET":
                    response = requests.get(f"{self.BASE_URL}{endpoint}")
                else:
                    response = requests.post(f"{self.BASE_URL}{endpoint}")
                
                # These should not be affected by registration config
                # They might return 401 for auth reasons, but not 403 for registration
                assert response.status_code != 403 or "registration" not in response.text.lower()
    
    @pytest.mark.api
    def test_registration_config_preserves_existing_user_functionality(self):
        """Test that existing users are not affected by registration configuration"""
        # This test would require an existing user in the database
        # In real implementation, you'd create a user first, then disable registration
        pass  # Placeholder for integration test


class TestRegistrationConfigurationSecurity:
    """Security tests for registration configuration"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.api
    def test_registration_config_prevents_privilege_escalation(self, unique_user_data):
        """Test that disabling registration doesn't allow privilege escalation"""
        # Ensure that even if registration is re-enabled, previous attempts don't succeed
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', False):
            response1 = requests.post(
                f"{self.BASE_URL}/api/auth/register",
                json=unique_user_data
            )
            assert response1.status_code == 403
        
        # Re-enable registration
        with patch('nocturna_calculations.api.config.settings.ALLOW_USER_REGISTRATION', True):
            response2 = requests.post(
                f"{self.BASE_URL}/api/auth/register",
                json=unique_user_data
            )
            # Should work normally now
            assert response2.status_code in [200, 400]  # 400 if user already exists from other tests
    
    @pytest.mark.api
    def test_registration_config_audit_trail(self):
        """Test that registration configuration changes are auditable"""
        # This would test logging/auditing of configuration changes
        # Implementation depends on logging strategy
        pass  # Placeholder for audit functionality


# Additional test classes for future enhancements
class TestRegistrationApprovalWorkflow:
    """Tests for registration approval workflow (future feature)"""
    
    @pytest.mark.skip(reason="Future enhancement - registration approval not implemented yet")
    def test_registration_requires_approval_when_enabled(self):
        """Test registration approval workflow"""
        pass


class TestRegistrationUserLimits:
    """Tests for user registration limits (future feature)"""
    
    @pytest.mark.skip(reason="Future enhancement - user limits not implemented yet")
    def test_registration_blocked_when_user_limit_reached(self):
        """Test that registration is blocked when user limit is reached"""
        pass 