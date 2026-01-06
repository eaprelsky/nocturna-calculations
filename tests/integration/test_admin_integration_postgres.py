"""
PostgreSQL Integration Tests for Admin Functionality

These tests run against actual PostgreSQL database to ensure production parity.
Use these for critical path testing and database-specific functionality.

Prerequisites:
- PostgreSQL server running
- Test database configured
- Environment variables set

Run with: pytest tests/integration/test_admin_integration_postgres.py -m postgres
"""
import pytest
import os
import uuid
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestAdminPostgreSQLIntegration:
    """Test admin functionality against PostgreSQL database"""
    
    @pytest.fixture(scope="class")
    def postgres_test_db_url(self):
        """Get PostgreSQL test database URL"""
        # Use separate test database to avoid conflicts
        base_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/nocturna')
        
        # Replace database name with test database
        if base_url.endswith('/nocturna'):
            test_db_url = base_url.replace('/nocturna', '/nocturna_test')
        else:
            test_db_url = f"{base_url}_test"
        
        return test_db_url
    
    @pytest.fixture(scope="class")
    def postgres_test_engine(self, postgres_test_db_url):
        """Create PostgreSQL test engine and database"""
        try:
            # Create engine for default database to create test database
            base_url = postgres_test_db_url.rsplit('/', 1)[0] + '/postgres'
            admin_engine = create_engine(base_url, isolation_level='AUTOCOMMIT')
            
            # Extract test database name
            test_db_name = postgres_test_db_url.split('/')[-1]
            
            # Create test database if it doesn't exist
            with admin_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                    {"dbname": test_db_name}
                )
                if not result.fetchone():
                    conn.execute(text(f"CREATE DATABASE {test_db_name}"))
            
            # Create engine for test database
            test_engine = create_engine(postgres_test_db_url)
            
            yield test_engine
            
            # Cleanup: Drop test database
            test_engine.dispose()
            with admin_engine.connect() as conn:
                # Terminate connections to test database
                conn.execute(
                    text("""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = :dbname AND pid <> pg_backend_pid()
                    """),
                    {"dbname": test_db_name}
                )
                conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
            
            admin_engine.dispose()
            
        except Exception as e:
            pytest.skip(f"PostgreSQL not available for testing: {e}")
    
    @pytest.fixture
    def postgres_db_session(self, postgres_test_engine):
        """Create PostgreSQL database session with schema"""
        try:
            from nocturna_calculations.api.models import Base, User
            
            # Create all tables
            Base.metadata.create_all(postgres_test_engine)
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_test_engine)
            session = SessionLocal()
            
            yield session
            
            # Cleanup
            session.rollback()
            session.close()
            
            # Drop all tables
            Base.metadata.drop_all(postgres_test_engine)
            
        except ImportError:
            pytest.skip("Database models not available")

    @pytest.mark.postgres
    @pytest.mark.integration
    def test_admin_user_with_postgresql_constraints(self, postgres_db_session):
        """Test admin user creation with PostgreSQL-specific constraints"""
        from nocturna_calculations.api.models import User
        from nocturna_calculations.api.routers.auth import get_password_hash
        
        session = postgres_db_session
        
        # Test PostgreSQL UUID generation
        admin_user = User(
            email="postgres_admin@example.com",
            username="postgres_admin",
            hashed_password=get_password_hash("PostgreSQLAdminPassword123!"),
            first_name="PostgreSQL",
            last_name="Admin",
            is_active=True,
            is_superuser=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        # Verify PostgreSQL-specific behavior
        assert admin_user.id is not None
        assert isinstance(admin_user.id, str)  # UUID as string
        assert len(admin_user.id) > 20  # UUID length
        assert admin_user.is_superuser is True
        
        # Test PostgreSQL UNIQUE constraints
        duplicate_user = User(
            email="postgres_admin@example.com",  # Duplicate email
            username="different_username",
            hashed_password=get_password_hash("DifferentPassword123!"),
            is_superuser=False
        )
        
        session.add(duplicate_user)
        
        # This should raise IntegrityError due to unique email constraint
        with pytest.raises(Exception) as exc_info:
            session.commit()
        
        # PostgreSQL-specific error message
        assert "duplicate key" in str(exc_info.value).lower() or "unique" in str(exc_info.value).lower()

    @pytest.mark.postgres
    @pytest.mark.integration  
    def test_admin_query_with_postgresql_features(self, postgres_db_session):
        """Test admin queries using PostgreSQL-specific features"""
        from nocturna_calculations.api.models import User
        from nocturna_calculations.api.routers.auth import get_password_hash
        
        session = postgres_db_session
        
        # Create multiple admin users
        admin_users = []
        for i in range(3):
            user = User(
                email=f"admin{i}@postgres-test.com",
                username=f"admin{i}",
                hashed_password=get_password_hash(f"AdminPassword{i}123!"),
                first_name=f"Admin{i}",
                last_name="User",
                is_superuser=True
            )
            admin_users.append(user)
            session.add(user)
        
        session.commit()
        
        # Test PostgreSQL-specific query features
        # Case-insensitive search (PostgreSQL ILIKE)
        result = session.query(User).filter(
            User.email.ilike('%ADMIN%')
        ).all()
        assert len(result) == 3
        
        # Test JSON operations if your model has JSON fields
        # This would test PostgreSQL JSON operators
        
        # Test array operations if you have array fields
        # This would test PostgreSQL array features
        
        # Test full-text search if implemented
        # This would test PostgreSQL full-text search features

    @pytest.mark.postgres
    @pytest.mark.integration
    def test_admin_transaction_behavior(self, postgres_db_session):
        """Test admin operations with PostgreSQL transaction behavior"""
        from nocturna_calculations.api.models import User
        from nocturna_calculations.api.routers.auth import get_password_hash
        
        session = postgres_db_session
        
        # Test transaction rollback behavior
        user = User(
            email="transaction_test@example.com",
            username="transaction_test",
            hashed_password=get_password_hash("TransactionTestPassword123!"),
            is_superuser=True
        )
        
        session.add(user)
        session.flush()  # Send to DB but don't commit
        
        # User should be visible in this transaction
        found_user = session.query(User).filter(User.email == "transaction_test@example.com").first()
        assert found_user is not None
        
        # Rollback transaction
        session.rollback()
        
        # User should no longer be visible
        found_user = session.query(User).filter(User.email == "transaction_test@example.com").first()
        assert found_user is None

    @pytest.mark.postgres
    @pytest.mark.integration
    def test_admin_concurrent_access(self, postgres_test_engine):
        """Test admin operations under concurrent access"""
        from nocturna_calculations.api.models import Base, User
        from nocturna_calculations.api.routers.auth import get_password_hash
        from threading import Thread
        import time
        
        # Create separate sessions for concurrent access
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_test_engine)
        
        def create_admin_user(user_id):
            session = SessionLocal()
            try:
                user = User(
                    email=f"concurrent_admin_{user_id}@example.com",
                    username=f"concurrent_admin_{user_id}",
                    hashed_password=get_password_hash(f"ConcurrentPassword{user_id}123!"),
                    is_superuser=True
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                return user.id
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        
        # Test concurrent admin creation
        threads = []
        results = {}
        
        def thread_worker(thread_id):
            try:
                user_id = create_admin_user(thread_id)
                results[thread_id] = user_id
            except Exception as e:
                results[thread_id] = str(e)
        
        # Create multiple threads
        for i in range(3):
            thread = Thread(target=thread_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all users were created successfully
        session = SessionLocal()
        try:
            admin_count = session.query(User).filter(User.is_superuser == True).count()
            assert admin_count == 3
        finally:
            session.close()


class TestAdminMigrationCompatibility:
    """Test admin functionality with database migrations"""
    
    @pytest.mark.postgres
    @pytest.mark.integration
    def test_admin_fields_in_migration(self):
        """Test that admin fields are properly handled in migrations"""
        # This would test that database migrations properly handle:
        # - Adding is_superuser field
        # - Setting default values
        # - Creating indexes
        # - Handling existing data
        
        # In a real test, you'd:
        # 1. Create database with old schema
        # 2. Run migration
        # 3. Verify admin fields exist and work
        # 4. Test data migration if needed
        
        pass

    @pytest.mark.postgres  
    @pytest.mark.integration
    def test_admin_performance_at_scale(self):
        """Test admin operations performance with larger datasets"""
        # This would test:
        # - Admin user queries with many users
        # - Index performance on is_superuser field
        # - Query optimization for admin operations
        
        pass


# Configuration for pytest markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "postgres: mark test as requiring PostgreSQL database"
    ) 