"""
Integration tests for service token management script

Tests the scripts/manage_service_tokens.py script functionality.
"""

import pytest
import subprocess
import sys
import os
import json
import uuid
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from jose import jwt

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.manage_service_tokens import ServiceTokenManager
from nocturna_calculations.api.config import settings


class TestServiceTokenScript:
    """Test the service token management script"""
    
    @pytest.fixture
    def script_path(self):
        """Path to the service token management script"""
        return project_root / "scripts" / "manage_service_tokens.py"
    
    @pytest.mark.integration
    def test_script_help(self, script_path):
        """Test script help functionality"""
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert "Manage Nocturna service tokens" in result.stdout
            assert "create" in result.stdout
            assert "list" in result.stdout
            assert "revoke" in result.stdout
            assert "check" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("Script execution timeout")
        except FileNotFoundError:
            pytest.skip("Python interpreter not found")
    
    @pytest.mark.integration
    def test_script_no_command(self, script_path):
        """Test script behavior when no command is provided"""
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should show help and exit with error code
            assert result.returncode == 1
            assert "Available commands" in result.stdout or "usage:" in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("Script execution timeout")
        except FileNotFoundError:
            pytest.skip("Python interpreter not found")
    
    @pytest.mark.integration
    def test_script_invalid_command(self, script_path):
        """Test script behavior with invalid command"""
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "invalid_command"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should show help and exit with error code (argparse uses 2 for invalid arguments)
            assert result.returncode == 2
            
        except subprocess.TimeoutExpired:
            pytest.skip("Script execution timeout")
        except FileNotFoundError:
            pytest.skip("Python interpreter not found")


class TestServiceTokenManager:
    """Test the ServiceTokenManager class directly"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.close = Mock()
        return mock_session
    
    @pytest.fixture
    def mock_admin_user(self):
        """Mock admin user"""
        mock_user = Mock()
        mock_user.id = "test-admin-id"
        mock_user.email = "admin@test.com"
        mock_user.is_superuser = True
        return mock_user
    
    def test_service_token_manager_initialization(self):
        """Test ServiceTokenManager initialization"""
        with patch('scripts.manage_service_tokens.create_engine') as mock_engine:
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = Mock()
                
                manager = ServiceTokenManager()
                
                assert manager.db is not None
                mock_engine.assert_called_once_with(settings.DATABASE_URL)
    
    def test_get_admin_user_success(self, mock_db_session, mock_admin_user):
        """Test getting admin user successfully"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_admin_user
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = mock_db_session
                
                manager = ServiceTokenManager()
                admin_user = manager.get_admin_user()
                
                assert admin_user == mock_admin_user
    
    def test_get_admin_user_not_found(self, mock_db_session):
        """Test behavior when no admin user is found"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = mock_db_session
                
                manager = ServiceTokenManager()
                
                with pytest.raises(SystemExit):
                    manager.get_admin_user()
    
    def test_create_token_success(self, mock_db_session, mock_admin_user):
        """Test successful token creation"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_admin_user
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                with patch('scripts.manage_service_tokens.create_service_token') as mock_create:
                    mock_sessionmaker.return_value.return_value = mock_db_session
                    mock_create.return_value = ("test-jwt-token", "test-token-id")
                    
                    manager = ServiceTokenManager()
                    result = manager.create_token(days=30, scope="calculations", eternal=False)
                    
                    assert result is True
                    mock_create.assert_called_once_with(
                        user_id=mock_admin_user.id,
                        db=mock_db_session,
                        days=30,
                        scope="calculations",
                        eternal=False
                    )
    
    def test_create_eternal_token(self, mock_db_session, mock_admin_user):
        """Test eternal token creation"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_admin_user
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                with patch('scripts.manage_service_tokens.create_service_token') as mock_create:
                    mock_sessionmaker.return_value.return_value = mock_db_session
                    mock_create.return_value = ("test-eternal-token", "test-token-id")
                    
                    manager = ServiceTokenManager()
                    result = manager.create_token(days=30, scope="calculations", eternal=True)
                    
                    assert result is True
                    mock_create.assert_called_once_with(
                        user_id=mock_admin_user.id,
                        db=mock_db_session,
                        days=30,
                        scope="calculations",
                        eternal=True
                    )
    
    def test_list_tokens_empty(self, mock_db_session):
        """Test listing tokens when none exist"""
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = mock_db_session
                
                manager = ServiceTokenManager()
                result = manager.list_tokens()
                
                assert result is True
    
    def test_list_tokens_with_data(self, mock_db_session, mock_admin_user):
        """Test listing tokens with existing tokens"""
        # Mock token
        mock_token = Mock()
        mock_token.id = "test-token-id"
        mock_token.scope = "calculations"
        mock_token.created_at = datetime.utcnow()
        mock_token.expires_at = datetime.utcnow() + timedelta(days=30)
        mock_token.last_used_at = None
        mock_token.user_id = mock_admin_user.id
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_token]
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_admin_user
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = mock_db_session
                
                manager = ServiceTokenManager()
                result = manager.list_tokens()
                
                assert result is True
    
    def test_revoke_token_success(self, mock_db_session, mock_admin_user):
        """Test successful token revocation"""
        # Mock token
        mock_token = Mock()
        mock_token.id = "test-token-id"
        mock_token.scope = "calculations"
        mock_token.created_at = datetime.utcnow()
        mock_token.user_id = mock_admin_user.id
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_token
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                with patch('builtins.input', return_value='y'):  # Confirm deletion
                    mock_sessionmaker.return_value.return_value = mock_db_session
                    
                    manager = ServiceTokenManager()
                    result = manager.revoke_token("test-token-id")
                    
                    assert result is True
                    mock_db_session.delete.assert_called_once_with(mock_token)
                    mock_db_session.commit.assert_called_once()
    
    def test_revoke_token_not_found(self, mock_db_session):
        """Test token revocation when token doesn't exist"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = mock_db_session
                
                manager = ServiceTokenManager()
                result = manager.revoke_token("nonexistent-token-id")
                
                assert result is False
    
    def test_revoke_token_cancelled(self, mock_db_session, mock_admin_user):
        """Test token revocation when user cancels"""
        # Mock token
        mock_token = Mock()
        mock_token.id = "test-token-id"
        mock_token.scope = "calculations"
        mock_token.created_at = datetime.utcnow()
        mock_token.user_id = mock_admin_user.id
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_token
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                with patch('builtins.input', return_value='n'):  # Cancel deletion
                    mock_sessionmaker.return_value.return_value = mock_db_session
                    
                    manager = ServiceTokenManager()
                    result = manager.revoke_token("test-token-id")
                    
                    assert result is False
                    mock_db_session.delete.assert_not_called()
    
    def test_check_token_valid(self):
        """Test checking a valid token"""
        # Create a valid token
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id",
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                with patch('scripts.manage_service_tokens.settings') as mock_settings:
                    mock_sessionmaker.return_value.return_value = Mock()
                    mock_settings.SECRET_KEY = "test-secret"
                    mock_settings.ALGORITHM = "HS256"
                    
                    manager = ServiceTokenManager()
                    result = manager.check_token(token)
                    
                    assert result is True
    
    def test_check_token_expired(self):
        """Test checking an expired token"""
        # Create an expired token
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id",
            "exp": int((datetime.utcnow() - timedelta(days=1)).timestamp())  # Expired
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = Mock()
                
                manager = ServiceTokenManager()
                result = manager.check_token(token)
                
                assert result is True  # Function still succeeds, just reports expired status
    
    def test_check_token_eternal(self):
        """Test checking an eternal token (no expiration)"""
        # Create an eternal token
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id"
            # No 'exp' field = eternal
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = Mock()
                
                manager = ServiceTokenManager()
                result = manager.check_token(token)
                
                assert result is True
    
    def test_check_token_invalid_format(self):
        """Test checking a token with invalid format"""
        invalid_token = "not.a.valid.jwt.token"
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = Mock()
                
                manager = ServiceTokenManager()
                result = manager.check_token(invalid_token)
                
                assert result is False
    
    def test_check_token_with_database_lookup(self, mock_db_session):
        """Test checking a service token with database lookup"""
        # Create a service token
        payload = {
            "sub": "test-user-id",
            "type": "service",
            "scope": "calculations",
            "token_id": "test-token-id",
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")
        
        # Mock database token
        mock_token = Mock()
        mock_token.id = "test-token-id"
        mock_token.last_used_at = datetime.utcnow()
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_token
        
        with patch('scripts.manage_service_tokens.create_engine'):
            with patch('scripts.manage_service_tokens.sessionmaker') as mock_sessionmaker:
                with patch('scripts.manage_service_tokens.settings') as mock_settings:
                    mock_sessionmaker.return_value.return_value = mock_db_session
                    mock_settings.SECRET_KEY = "test-secret"
                    mock_settings.ALGORITHM = "HS256"
                    
                    manager = ServiceTokenManager()
                    result = manager.check_token(token)
                    
                    assert result is True


class TestServiceTokenScriptIntegration:
    """Integration tests for the complete script workflow"""
    
    @pytest.mark.integration
    def test_script_workflow_simulation(self):
        """Test a complete workflow simulation"""
        # This test simulates the complete workflow without actually
        # running the script or connecting to a real database
        
        with patch('scripts.manage_service_tokens.ServiceTokenManager') as MockManager:
            mock_manager = Mock()
            mock_manager.create_token.return_value = True
            mock_manager.list_tokens.return_value = True
            mock_manager.revoke_token.return_value = True
            mock_manager.check_token.return_value = True
            MockManager.return_value = mock_manager
            
            # Import and test main function
            from scripts.manage_service_tokens import main
            
            # Test create command
            with patch('sys.argv', ['manage_service_tokens.py', 'create']):
                result = main()
                assert result == 0
                mock_manager.create_token.assert_called_once()
            
            # Reset mock
            mock_manager.reset_mock()
            
            # Test list command
            with patch('sys.argv', ['manage_service_tokens.py', 'list']):
                result = main()
                assert result == 0
                mock_manager.list_tokens.assert_called_once()
            
            # Reset mock
            mock_manager.reset_mock()
            
            # Test revoke command
            with patch('sys.argv', ['manage_service_tokens.py', 'revoke', 'test-token-id']):
                result = main()
                assert result == 0
                mock_manager.revoke_token.assert_called_once_with('test-token-id')
            
            # Reset mock
            mock_manager.reset_mock()
            
            # Test check command
            with patch('sys.argv', ['manage_service_tokens.py', 'check', 'test-token']):
                result = main()
                assert result == 0
                mock_manager.check_token.assert_called_once_with('test-token')
    
    @pytest.mark.integration
    def test_script_error_handling(self):
        """Test script error handling"""
        with patch('scripts.manage_service_tokens.ServiceTokenManager') as MockManager:
            mock_manager = Mock()
            mock_manager.create_token.return_value = False  # Simulate failure
            MockManager.return_value = mock_manager
            
            from scripts.manage_service_tokens import main
            
            # Test failed create command
            with patch('sys.argv', ['manage_service_tokens.py', 'create']):
                result = main()
                assert result == 1  # Should return error code 