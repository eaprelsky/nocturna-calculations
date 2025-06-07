"""
Unit tests for service token functionality

Tests the core service token creation, validation, and management functionality
without requiring a running API server.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from jose import jwt

from nocturna_calculations.api.models import User, Token
from nocturna_calculations.api.routers.auth import (
    create_service_token,
    get_current_service_token,
    ServiceTokenCreateRequest,
    ServiceTokenResponse
)
from nocturna_calculations.api.config import settings
from nocturna_calculations.client import TokenManager, NocturnaClient
from nocturna_calculations.client.exceptions import (
    TokenExpiredError,
    AuthenticationError,
    APIError
)


class TestServiceTokenCreation:
    """Test service token creation functionality"""
    
    def test_create_service_token_success(self):
        """Test successful service token creation"""
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        user_id = "test-user-id"
        days = 30
        scope = "calculations"
        
        # Create service token
        jwt_token, token_id = create_service_token(
            user_id=user_id,
            db=mock_db,
            days=days,
            scope=scope,
            eternal=False
        )
        
        # Verify token was created
        assert jwt_token is not None
        assert token_id is not None
        assert len(token_id) == 36  # UUID length
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verify token content
        payload = jwt.decode(jwt_token, key="", options={"verify_signature": False})
        assert payload["sub"] == user_id
        assert payload["type"] == "service"
        assert payload["scope"] == scope
        assert payload["token_id"] == token_id
        assert "exp" in payload  # Should have expiration
    
    def test_create_eternal_service_token(self):
        """Test eternal service token creation"""
        mock_db = Mock(spec=Session)
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        user_id = "test-user-id"
        scope = "calculations,admin"
        
        # Create eternal service token
        jwt_token, token_id = create_service_token(
            user_id=user_id,
            db=mock_db,
            days=30,  # Ignored for eternal tokens
            scope=scope,
            eternal=True
        )
        
        # Verify token content
        payload = jwt.decode(jwt_token, key="", options={"verify_signature": False})
        assert payload["sub"] == user_id
        assert payload["type"] == "service"
        assert payload["scope"] == scope
        assert "exp" not in payload  # Eternal tokens have no expiration
    
    def test_create_service_token_custom_duration(self):
        """Test service token creation with custom duration"""
        mock_db = Mock(spec=Session)
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        user_id = "test-user-id"
        days = 90
        
        jwt_token, token_id = create_service_token(
            user_id=user_id,
            db=mock_db,
            days=days,
            scope="calculations",
            eternal=False
        )
        
        # Verify expiration is set correctly
        payload = jwt.decode(jwt_token, key="", options={"verify_signature": False})
        exp_timestamp = payload["exp"]
        exp_date = datetime.utcfromtimestamp(exp_timestamp)  # Use UTC to match utcnow()
        
        # Verify the expiration is approximately the right number of days from now
        # Allow for some tolerance due to execution time
        now = datetime.utcnow()
        expected_seconds = days * 24 * 60 * 60  # Convert days to seconds
        actual_seconds = (exp_date - now).total_seconds()
        
        # Allow 1 minute tolerance for execution time
        assert abs(actual_seconds - expected_seconds) < 60, f"Expected ~{expected_seconds} seconds, got {actual_seconds} seconds"


class TestServiceTokenValidation:
    """Test service token validation and authentication"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def valid_service_token(self):
        """Create a valid service token for testing"""
        token_id = "test-token-id"
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": token_id,
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM), token_id
    
    @pytest.fixture
    def expired_service_token(self):
        """Create an expired service token for testing"""
        token_id = "expired-token-id"
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": token_id,
            "exp": int((datetime.utcnow() - timedelta(days=1)).timestamp())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM), token_id
    
    @pytest.mark.asyncio
    async def test_get_current_service_token_success(self, mock_db_session, valid_service_token):
        """Test successful service token validation"""
        jwt_token, token_id = valid_service_token
        
        # Mock database token
        mock_token = Mock(spec=Token)
        mock_token.id = token_id
        mock_token.token_type = "service"
        mock_token.expires_at = datetime.utcnow() + timedelta(days=30)
        mock_token.last_used_at = None
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_token
        mock_db_session.query.return_value = mock_query
        mock_db_session.commit = Mock()
        
        # Test validation
        result = await get_current_service_token(jwt_token, mock_db_session)
        
        assert result == mock_token
        mock_db_session.commit.assert_called_once()  # Should update last_used_at
    
    @pytest.mark.asyncio
    async def test_get_current_service_token_invalid_type(self, mock_db_session):
        """Test rejection of non-service tokens"""
        # Create user token instead of service token
        payload = {
            "sub": "test-user-id",
            "type": "user",  # Wrong type
            "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp())
        }
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await get_current_service_token(jwt_token, mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_current_service_token_not_in_database(self, mock_db_session, valid_service_token):
        """Test rejection when token not found in database"""
        jwt_token, token_id = valid_service_token
        
        # Mock database query returning None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await get_current_service_token(jwt_token, mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_current_service_token_expired_in_db(self, mock_db_session, valid_service_token):
        """Test rejection when token is expired in database"""
        jwt_token, token_id = valid_service_token
        
        # Mock expired database token
        mock_token = Mock(spec=Token)
        mock_token.id = token_id
        mock_token.token_type = "service"
        mock_token.expires_at = datetime.utcnow() - timedelta(days=1)  # Expired
        
        # Mock database query returning expired token
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # Filter excludes expired
        mock_db_session.query.return_value = mock_query
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await get_current_service_token(jwt_token, mock_db_session)


class TestTokenManager:
    """Test the TokenManager client class"""
    
    def test_token_manager_initialization_valid_token(self):
        """Test TokenManager initialization with valid service token"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id",
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000"
        )
        
        assert manager.service_token == service_token
        assert manager.api_url == "http://localhost:8000"
        assert manager.access_token is None
        assert manager.token_expires_at is None
    
    def test_token_manager_initialization_invalid_type(self):
        """Test TokenManager initialization with invalid token type"""
        payload = {
            "sub": "test-user-id",
            "type": "user",  # Wrong type
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        with pytest.raises(AuthenticationError, match="Invalid token type"):
            TokenManager(
                service_token=service_token,
                api_url="http://localhost:8000"
            )
    
    def test_token_manager_initialization_expired_token(self):
        """Test TokenManager initialization with expired service token"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id",
            "exp": int((datetime.utcnow() - timedelta(days=1)).timestamp())  # Expired
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        with pytest.raises(TokenExpiredError, match="Service token expired"):
            TokenManager(
                service_token=service_token,
                api_url="http://localhost:8000"
            )
    
    def test_token_manager_eternal_token(self):
        """Test TokenManager with eternal service token (no expiration)"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
            # No 'exp' field = eternal token
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        # Should not raise exception
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000"
        )
        
        assert manager.service_token == service_token
    
    def test_needs_refresh_no_access_token(self):
        """Test that refresh is needed when no access token exists"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000"
        )
        
        assert manager._needs_refresh() is True
    
    def test_needs_refresh_token_expiring_soon(self):
        """Test that refresh is needed when token expires soon"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000",
            refresh_threshold=300  # 5 minutes
        )
        
        # Set access token that expires in 2 minutes
        manager.access_token = "test-access-token"
        manager.token_expires_at = datetime.utcnow() + timedelta(minutes=2)
        
        assert manager._needs_refresh() is True
    
    def test_needs_refresh_token_still_valid(self):
        """Test that refresh is not needed when token is still valid"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000",
            refresh_threshold=300  # 5 minutes
        )
        
        # Set access token that expires in 10 minutes
        manager.access_token = "test-access-token"
        manager.token_expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        assert manager._needs_refresh() is False
    
    @patch('requests.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh"""
        # Mock successful refresh response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-access-token",
            "expires_in": 900  # 15 minutes
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000"
        )
        
        # Trigger refresh
        manager._refresh_token()
        
        # Verify token was updated
        assert manager.access_token == "new-access-token"
        assert manager.token_expires_at is not None
        
        # Verify API call was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/auth/service-token/refresh",
            headers={
                "Authorization": f"Bearer {service_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
    
    @patch('requests.post')
    def test_refresh_token_service_expired(self, mock_post):
        """Test token refresh when service token is expired"""
        # Mock 401 response with expired token message
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "detail": "Service token has expired"
        }
        mock_post.return_value = mock_response
        
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        manager = TokenManager(
            service_token=service_token,
            api_url="http://localhost:8000"
        )
        
        # Should raise TokenExpiredError
        with pytest.raises(TokenExpiredError, match="Service token has expired"):
            manager._refresh_token()


class TestNocturnaClient:
    """Test the NocturnaClient class"""
    
    def test_client_initialization_with_auto_refresh(self):
        """Test client initialization with auto-refresh enabled"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        client = NocturnaClient(
            service_token=service_token,
            api_url="http://localhost:8000",
            auto_refresh=True
        )
        
        assert client.token_manager is not None
        assert client.token_manager.service_token == service_token
    
    def test_client_initialization_without_auto_refresh(self):
        """Test client initialization with auto-refresh disabled"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        client = NocturnaClient(
            service_token=service_token,
            api_url="http://localhost:8000",
            auto_refresh=False
        )
        
        assert client.token_manager is None
        assert client.service_token == service_token
    
    def test_get_headers_with_auto_refresh(self):
        """Test header generation with auto-refresh"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        client = NocturnaClient(
            service_token=service_token,
            api_url="http://localhost:8000",
            auto_refresh=True
        )
        
        # Mock token manager to return access token
        client.token_manager.get_valid_token = Mock(return_value="access-token")
        
        headers = client._get_headers()
        
        assert headers["Authorization"] == "Bearer access-token"
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers
    
    def test_get_headers_without_auto_refresh(self):
        """Test header generation without auto-refresh"""
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
        }
        service_token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        client = NocturnaClient(
            service_token=service_token,
            api_url="http://localhost:8000",
            auto_refresh=False
        )
        
        headers = client._get_headers()
        
        assert headers["Authorization"] == f"Bearer {service_token}"
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers


class TestServiceTokenPydanticModels:
    """Test Pydantic models for service tokens"""
    
    def test_service_token_create_request_defaults(self):
        """Test ServiceTokenCreateRequest with default values"""
        request = ServiceTokenCreateRequest()
        
        assert request.days == 30
        assert request.scope == "calculations"
        assert request.eternal is False
    
    def test_service_token_create_request_custom_values(self):
        """Test ServiceTokenCreateRequest with custom values"""
        request = ServiceTokenCreateRequest(
            days=90,
            scope="calculations,admin",
            eternal=True
        )
        
        assert request.days == 90
        assert request.scope == "calculations,admin"
        assert request.eternal is True
    
    def test_service_token_response_model(self):
        """Test ServiceTokenResponse model"""
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        response = ServiceTokenResponse(
            service_token="test-token",
            expires_at=expires_at,
            expires_in_days=30,
            scope="calculations",
            token_id="test-token-id"
        )
        
        assert response.service_token == "test-token"
        assert response.expires_at == expires_at
        assert response.expires_in_days == 30
        assert response.scope == "calculations"
        assert response.token_id == "test-token-id" 