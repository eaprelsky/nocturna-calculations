"""
Unit tests for admin management functionality
"""
import pytest
import sys
from unittest.mock import Mock, patch, call
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.create_admin import create_admin_user, promote_existing_user, list_admin_users
from nocturna_calculations.api.models import User
from nocturna_calculations.api.routers.auth import get_password_hash, verify_password


class TestAdminCreation:
    """Test admin user creation functionality"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock()
        session.rollback = Mock()
        session.close = Mock()
        return session
    
    @pytest.fixture
    def mock_engine(self, mock_db_session):
        """Mock database engine"""
        engine = Mock()
        session_maker = Mock(return_value=mock_db_session)
        return engine, session_maker
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_admin_user_success(self, mock_getpass, mock_input, mock_sessionmaker, mock_create_engine):
        """Test successful admin user creation"""
        # Mock database setup
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user inputs
        mock_input.side_effect = [
            'admin@example.com',  # email
            'admin',              # username  
            'Admin',              # first_name
            'User'                # last_name
        ]
        mock_getpass.side_effect = [
            'AdminPassword123!',  # password
            'AdminPassword123!'   # password confirmation
        ]
        
        # Mock user creation
        mock_user = Mock()
        mock_user.id = 'test-uuid'
        mock_user.email = 'admin@example.com'
        mock_user.username = 'admin'
        mock_user.is_superuser = True
        mock_db.refresh = Mock(side_effect=lambda user: setattr(user, 'id', 'test-uuid'))
        
        with patch('scripts.create_admin.User') as mock_user_class:
            mock_user_class.return_value = mock_user
            
            result = create_admin_user()
            
            assert result is True
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_user_class.assert_called_once()
            
            # Verify user was created with correct attributes
            call_args = mock_user_class.call_args[1]
            assert call_args['email'] == 'admin@example.com'
            assert call_args['username'] == 'admin'
            assert call_args['first_name'] == 'Admin'
            assert call_args['last_name'] == 'User'
            assert call_args['is_active'] is True
            assert call_args['is_superuser'] is True
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_admin_user_duplicate_email(self, mock_getpass, mock_input, mock_sessionmaker, mock_create_engine):
        """Test admin creation with duplicate email"""
        # Mock database setup with existing user
        mock_db = Mock()
        existing_user = Mock()
        existing_user.email = 'admin@example.com'
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user inputs
        mock_input.side_effect = [
            'admin@example.com',  # email (duplicate)
            'admin',              # username
        ]
        
        result = create_admin_user()
        
        assert result is False
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    def test_create_admin_user_invalid_email(self, mock_input, mock_sessionmaker, mock_create_engine):
        """Test admin creation with invalid email"""
        # Mock database setup
        mock_db = Mock()
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock invalid email input
        mock_input.side_effect = [
            'invalid-email',  # invalid email
        ]
        
        result = create_admin_user()
        
        assert result is False
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_admin_user_password_mismatch(self, mock_getpass, mock_input, mock_sessionmaker, mock_create_engine):
        """Test admin creation with password mismatch"""
        # Mock database setup
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user inputs
        mock_input.side_effect = [
            'admin@example.com',
            'admin',
            'Admin',
            'User'
        ]
        # Passwords don't match, then they do
        mock_getpass.side_effect = [
            'password1',
            'password2',  # mismatch
            'ValidPassword123!',
            'ValidPassword123!'  # match
        ]
        
        with patch('scripts.create_admin.User') as mock_user_class:
            mock_user = Mock()
            mock_user_class.return_value = mock_user
            
            result = create_admin_user()
            
            assert result is True
            # Should be called 4 times due to mismatch retry
            assert mock_getpass.call_count == 4


class TestAdminPromotion:
    """Test admin user promotion functionality"""
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker') 
    @patch('builtins.input')
    def test_promote_existing_user_success(self, mock_input, mock_sessionmaker, mock_create_engine):
        """Test successful user promotion to admin"""
        # Mock database setup
        mock_db = Mock()
        existing_user = Mock()
        existing_user.email = 'user@example.com'
        existing_user.username = 'user'
        existing_user.first_name = 'Test'
        existing_user.last_name = 'User'
        existing_user.is_superuser = False
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user inputs
        mock_input.side_effect = [
            'user@example.com',  # email to promote
            'y'                  # confirm promotion
        ]
        
        result = promote_existing_user()
        
        assert result is True
        assert existing_user.is_superuser is True
        mock_db.commit.assert_called_once()
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    def test_promote_user_not_found(self, mock_input, mock_sessionmaker, mock_create_engine):
        """Test promotion of non-existent user"""
        # Mock database setup
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # User not found
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user input
        mock_input.side_effect = ['nonexistent@example.com']
        
        result = promote_existing_user()
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    def test_promote_already_admin_user(self, mock_input, mock_sessionmaker, mock_create_engine):
        """Test promotion of user who is already admin"""
        # Mock database setup
        mock_db = Mock()
        existing_user = Mock()
        existing_user.email = 'admin@example.com'
        existing_user.is_superuser = True  # Already admin
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user input
        mock_input.side_effect = ['admin@example.com']
        
        result = promote_existing_user()
        
        assert result is True  # Should return True but not modify
        mock_db.commit.assert_not_called()
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    @patch('builtins.input')
    def test_promote_user_cancelled(self, mock_input, mock_sessionmaker, mock_create_engine):
        """Test promotion cancelled by user"""
        # Mock database setup
        mock_db = Mock()
        existing_user = Mock()
        existing_user.email = 'user@example.com'
        existing_user.username = 'user'
        existing_user.first_name = 'Test'
        existing_user.last_name = 'User'
        existing_user.is_superuser = False
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        mock_sessionmaker.return_value = lambda: mock_db
        
        # Mock user inputs
        mock_input.side_effect = [
            'user@example.com',  # email to promote
            'n'                  # cancel promotion
        ]
        
        result = promote_existing_user()
        
        assert result is False
        assert existing_user.is_superuser is False
        mock_db.commit.assert_not_called()


class TestAdminListing:
    """Test admin user listing functionality"""
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    def test_list_admin_users_success(self, mock_sessionmaker, mock_create_engine):
        """Test successful listing of admin users"""
        # Mock database setup
        mock_db = Mock()
        admin1 = Mock()
        admin1.id = 'admin1-id'
        admin1.email = 'admin1@example.com'
        admin1.username = 'admin1'
        admin1.first_name = 'Admin'
        admin1.last_name = 'One'
        admin1.created_at = datetime.now()
        admin1.is_active = True
        
        admin2 = Mock()
        admin2.id = 'admin2-id'
        admin2.email = 'admin2@example.com'
        admin2.username = 'admin2'
        admin2.first_name = 'Admin'
        admin2.last_name = 'Two'
        admin2.created_at = datetime.now()
        admin2.is_active = True
        
        mock_db.query.return_value.filter.return_value.all.return_value = [admin1, admin2]
        mock_sessionmaker.return_value = lambda: mock_db
        
        result = list_admin_users()
        
        assert result is True
        mock_db.query.assert_called_once()
    
    @patch('scripts.create_admin.create_engine')
    @patch('scripts.create_admin.sessionmaker')
    def test_list_admin_users_empty(self, mock_sessionmaker, mock_create_engine):
        """Test listing when no admin users exist"""
        # Mock database setup
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_sessionmaker.return_value = lambda: mock_db
        
        result = list_admin_users()
        
        assert result is True
        mock_db.query.assert_called_once()


class TestPasswordSecurity:
    """Test password hashing and verification"""
    
    def test_password_hashing(self):
        """Test password hashing function"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are long
        assert hashed.startswith('$2b$')  # Bcrypt identifier
    
    def test_password_verification(self):
        """Test password verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
        assert verify_password("", hashed) is False


class TestAdminModelIntegration:
    """Test User model admin-related functionality"""
    
    def test_user_model_admin_fields(self):
        """Test that User model has admin-related fields"""
        from nocturna_calculations.api.models import User
        
        # Create a user instance
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=True
        )
        
        assert hasattr(user, 'is_active')
        assert hasattr(user, 'is_superuser')
        assert user.is_active is True
        assert user.is_superuser is True
    
    def test_user_model_default_values(self):
        """Test User model default values"""
        from nocturna_calculations.api.models import User
        
        # Test 1: SQLAlchemy defaults only apply at database level
        # When creating Python objects in memory, fields without explicit values are None
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        
        # These will be None until saved to database and refreshed
        assert user.is_active is None  # Not set yet
        assert user.is_superuser is None  # Not set yet
        
        # Test 2: When explicitly set, values work correctly
        user_with_explicit_values = User(
            email="test2@example.com",
            username="testuser2",
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False
        )
        
        assert user_with_explicit_values.is_active is True
        assert user_with_explicit_values.is_superuser is False
        
        # Test 3: Check that the model has the correct column defaults defined
        # These defaults will be used when inserting into the database
        assert User.is_active.default.arg is True
        assert User.is_superuser.default.arg is False 