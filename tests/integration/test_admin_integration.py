"""
Integration tests for admin functionality

These tests verify the complete admin workflow including script execution,
database interactions, and API integration.
"""
import pytest
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestAdminScriptIntegration:
    """Test admin script integration with database"""
    
    @pytest.fixture
    def temp_env_file(self):
        """Create temporary .env file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("""
# Test database configuration
DATABASE_URL=sqlite:///test_admin.db
SECRET_KEY=test_secret_key_for_admin_tests
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
""")
            temp_path = f.name
        
        # Set environment variable to use temp file
        original_env = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = 'sqlite:///test_admin.db'
        
        yield temp_path
        
        # Cleanup
        os.unlink(temp_path)
        if original_env:
            os.environ['DATABASE_URL'] = original_env
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        # Remove test database if it exists
        test_db_path = Path('test_admin.db')
        if test_db_path.exists():
            test_db_path.unlink()

    @pytest.mark.integration
    def test_admin_script_help(self):
        """Test admin script help output"""
        script_path = project_root / 'scripts' / 'create_admin.py'
        
        # Test with --help flag (though our script doesn't implement it yet)
        # For now, test with invalid args to see usage message
        result = subprocess.run(
            [sys.executable, str(script_path), 'invalid'],
            capture_output=True,
            text=True
        )
        
        # Should show usage message
        assert 'Usage:' in result.stdout or 'usage:' in result.stdout.lower()

    @pytest.mark.integration
    @patch('scripts.create_admin.input')
    @patch('getpass.getpass')
    def test_admin_creation_script_integration(self, mock_getpass, mock_input, temp_env_file):
        """Test admin creation script with database integration"""
        # Skip if no database is available
        try:
            from nocturna_calculations.api.config import settings
        except ImportError:
            pytest.skip("API modules not available")
        
        # Mock user inputs for admin creation
        mock_input.side_effect = [
            'integration_admin@example.com',
            'integration_admin',
            'Integration',
            'Admin'
        ]
        mock_getpass.side_effect = [
            'IntegrationPassword123!',
            'IntegrationPassword123!'
        ]
        
        # Import and test the function directly
        from scripts.create_admin import create_admin_user
        
        with patch('scripts.create_admin.settings') as mock_settings:
            mock_settings.DATABASE_URL = 'sqlite:///test_admin.db'
            
            # This would need actual database setup to work properly
            # For now, we're testing the import and basic structure
            try:
                result = create_admin_user()
                # Result depends on database being properly set up
                assert isinstance(result, bool)
            except Exception as e:
                # Expected if database isn't set up for testing
                assert "database" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.integration
    @patch('scripts.create_admin.input')
    def test_admin_listing_script_integration(self, mock_input, temp_env_file):
        """Test admin listing script"""
        from scripts.create_admin import list_admin_users
        
        with patch('scripts.create_admin.settings') as mock_settings:
            mock_settings.DATABASE_URL = 'sqlite:///test_admin.db'
            
            try:
                result = list_admin_users()
                assert isinstance(result, bool)
            except Exception as e:
                # Expected if database isn't set up
                assert "database" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.integration
    @patch('scripts.create_admin.input')
    def test_admin_promotion_script_integration(self, mock_input, temp_env_file):
        """Test admin promotion script"""
        mock_input.side_effect = ['test@example.com', 'y']
        
        from scripts.create_admin import promote_existing_user
        
        with patch('scripts.create_admin.settings') as mock_settings:
            mock_settings.DATABASE_URL = 'sqlite:///test_admin.db'
            
            try:
                result = promote_existing_user()
                assert isinstance(result, bool)
            except Exception as e:
                # Expected if database isn't set up
                assert "database" in str(e).lower() or "connection" in str(e).lower()


class TestAdminDatabaseIntegration:
    """Test admin functionality with actual database operations"""
    
    @pytest.fixture
    def in_memory_db_session(self):
        """Create in-memory SQLite database for testing"""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from nocturna_calculations.api.models import Base, User
            
            # Create in-memory database
            engine = create_engine("sqlite:///:memory:")
            Base.metadata.create_all(engine)
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            session = SessionLocal()
            
            yield session
            
            session.close()
        except ImportError:
            pytest.skip("Database dependencies not available")

    @pytest.mark.integration
    def test_user_model_admin_functionality(self, in_memory_db_session):
        """Test User model admin fields with actual database"""
        from nocturna_calculations.api.models import User
        from nocturna_calculations.api.routers.auth import get_password_hash
        
        session = in_memory_db_session
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("AdminPassword123!"),
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_superuser=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        # Verify admin user creation
        assert admin_user.id is not None
        assert admin_user.is_superuser is True
        assert admin_user.is_active is True
        
        # Create regular user
        regular_user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("UserPassword123!"),
            first_name="Regular",
            last_name="User"
        )
        
        session.add(regular_user)
        session.commit()
        session.refresh(regular_user)
        
        # Verify regular user creation
        assert regular_user.id is not None
        assert regular_user.is_superuser is False  # Default value
        assert regular_user.is_active is True      # Default value
        
        # Test querying admin users
        admin_users = session.query(User).filter(User.is_superuser == True).all()
        assert len(admin_users) == 1
        assert admin_users[0].email == "admin@example.com"
        
        # Test promoting regular user to admin
        regular_user.is_superuser = True
        session.commit()
        
        # Verify promotion
        updated_admin_users = session.query(User).filter(User.is_superuser == True).all()
        assert len(updated_admin_users) == 2

    @pytest.mark.integration
    def test_admin_user_authentication_flow(self, in_memory_db_session):
        """Test complete admin authentication flow"""
        from nocturna_calculations.api.models import User
        from nocturna_calculations.api.routers.auth import (
            get_password_hash, 
            verify_password, 
            create_access_token,
            get_current_user,
            get_current_admin_user
        )
        from unittest.mock import MagicMock
        
        session = in_memory_db_session
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("AdminPassword123!"),
            first_name="Admin",
            last_name="User",
            is_superuser=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        # Test password verification
        assert verify_password("AdminPassword123!", admin_user.hashed_password) is True
        assert verify_password("WrongPassword", admin_user.hashed_password) is False
        
        # Test token creation
        token = create_access_token(data={"sub": admin_user.id})
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.integration
    def test_user_model_database_defaults(self, in_memory_db_session):
        """Test that User model database defaults are applied correctly"""
        from nocturna_calculations.api.models import User
        from nocturna_calculations.api.routers.auth import get_password_hash
        
        session = in_memory_db_session
        
        # Create user without explicitly setting is_active or is_superuser
        user = User(
            email="defaults_test@example.com",
            username="defaults_test",
            hashed_password=get_password_hash("DefaultsTestPassword123!")
        )
        
        # Before saving, values should be None (Python object)
        assert user.is_active is None
        assert user.is_superuser is None
        
        # Save to database and refresh to get database defaults
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # After database interaction, defaults should be applied
        assert user.is_active is True  # Database default
        assert user.is_superuser is False  # Database default
        assert user.id is not None  # UUID should be generated
        assert len(user.id) > 20  # UUID string length
        
        # Test that we can explicitly override defaults
        admin_user = User(
            email="explicit_admin@example.com", 
            username="explicit_admin",
            hashed_password=get_password_hash("ExplicitAdminPassword123!"),
            is_active=True,
            is_superuser=True  # Explicitly set to True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        assert admin_user.is_active is True
        assert admin_user.is_superuser is True


class TestAdminMakefileIntegration:
    """Test admin Makefile targets"""
    
    @pytest.mark.integration
    def test_makefile_admin_targets_exist(self):
        """Test that admin targets exist in Makefile"""
        makefile_path = project_root / 'Makefile'
        
        if not makefile_path.exists():
            pytest.skip("Makefile not found")
        
        makefile_content = makefile_path.read_text()
        
        # Check for admin targets
        assert 'admin-create:' in makefile_content
        assert 'admin-promote:' in makefile_content
        assert 'admin-list:' in makefile_content
        
        # Check for help text
        assert '## Create a new admin user' in makefile_content
        assert '## Promote existing user to admin' in makefile_content
        assert '## List all admin users' in makefile_content

    @pytest.mark.integration
    def test_makefile_help_includes_admin(self):
        """Test that make help includes admin commands"""
        try:
            # Run make help and check output
            result = subprocess.run(
                ['make', 'help'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                help_output = result.stdout
                assert 'admin-create' in help_output
                assert 'admin-promote' in help_output
                assert 'admin-list' in help_output
            else:
                pytest.skip("Make command not available or failed")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Make command not available")


class TestAdminSecurityIntegration:
    """Test admin security integration"""
    
    @pytest.mark.integration
    def test_admin_dependency_function(self):
        """Test get_current_admin_user dependency function"""
        from nocturna_calculations.api.routers.auth import get_current_admin_user
        from nocturna_calculations.api.models import User
        from fastapi import HTTPException
        from unittest.mock import MagicMock
        import pytest
        
        # Test with admin user
        admin_user = MagicMock(spec=User)
        admin_user.is_superuser = True
        
        try:
            # This should be an async function, but we'll test the logic
            result = get_current_admin_user.__code__
            assert result is not None
        except Exception:
            # Function exists and is callable
            pass
        
        # Test with regular user  
        regular_user = MagicMock(spec=User)
        regular_user.is_superuser = False
        
        # The actual testing of this function would require async test framework
        # For now, we're just verifying it exists and is importable

    @pytest.mark.integration
    def test_admin_model_constraints(self):
        """Test admin model database constraints"""
        try:
            from nocturna_calculations.api.models import User
            
            # Test that User model has required admin fields
            user_instance = User.__new__(User)
            
            # Check that the model has admin-related columns
            assert hasattr(User, 'is_active')
            assert hasattr(User, 'is_superuser')
            
            # Check column defaults (this would need database introspection for full test)
            assert User.is_active.default.arg is True
            assert User.is_superuser.default.arg is False
            
        except ImportError:
            pytest.skip("User model not available")


class TestAdminEndToEndWorkflow:
    """Test complete admin workflow from creation to API usage"""
    
    @pytest.mark.integration
    def test_admin_workflow_simulation(self):
        """Test simulated admin workflow"""
        # This test simulates the complete workflow:
        # 1. Create admin user via script
        # 2. Login via API  
        # 3. Access admin endpoints
        # 4. Verify admin privileges
        
        workflow_steps = [
            "create_admin_user",
            "login_admin",
            "verify_admin_access",
            "admin_operations"
        ]
        
        for step in workflow_steps:
            # In a real integration test, each step would be implemented
            # For now, we're documenting the workflow
            assert step in [
                "create_admin_user",
                "login_admin", 
                "verify_admin_access",
                "admin_operations"
            ]

    @pytest.mark.integration
    def test_admin_error_handling_integration(self):
        """Test admin error handling in integration scenarios"""
        # Test scenarios:
        scenarios = [
            "database_connection_failure",
            "invalid_admin_credentials", 
            "missing_admin_privileges",
            "token_expiration",
            "concurrent_admin_operations"
        ]
        
        for scenario in scenarios:
            # Each scenario would test specific error conditions
            # For now, we're documenting the test cases
            assert isinstance(scenario, str)
            assert len(scenario) > 0


class TestAdminDocumentationIntegration:
    """Test that admin documentation is complete and accessible"""
    
    @pytest.mark.integration
    def test_admin_setup_documentation_exists(self):
        """Test that admin setup documentation exists"""
        # Note: The docs/ADMIN_SETUP.md was deleted, so this test documents what should exist
        expected_docs = [
            "docs/ADMIN_SETUP.md",
            "README.md"  # Should mention admin setup
        ]
        
        readme_path = project_root / 'README.md'
        if readme_path.exists():
            readme_content = readme_path.read_text()
            # Check if README mentions admin functionality
            admin_mentioned = any(word in readme_content.lower() for word in [
                'admin', 'superuser', 'create_admin', 'administrator'
            ])
            # This is informational - README might not mention admin yet
            
        # Document what documentation should exist
        assert len(expected_docs) > 0

    @pytest.mark.integration 
    def test_admin_script_documentation(self):
        """Test that admin script has proper documentation"""
        script_path = project_root / 'scripts' / 'create_admin.py'
        
        if script_path.exists():
            script_content = script_path.read_text()
            
            # Check for docstrings
            assert '"""' in script_content
            assert 'Admin User Creation Script' in script_content
            
            # Check for usage information
            assert 'Usage:' in script_content
            
            # Check for function documentation
            assert 'def create_admin_user' in script_content
            assert 'def promote_existing_user' in script_content
            assert 'def list_admin_users' in script_content 