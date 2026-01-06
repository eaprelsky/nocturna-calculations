# Admin Tests Documentation

## Overview

This document describes the comprehensive test suite for admin functionality in the Nocturna Calculations project. The tests are organized across multiple categories to ensure thorough coverage of admin features, security, and integration.

## Test Structure

### Test Categories

1. **Unit Tests** (`tests/unit/test_admin_management.py`)
2. **API Tests** (`tests/api/test_admin_api.py`)  
3. **Integration Tests** (`tests/integration/test_admin_integration.py`)
4. **Security Tests** (`tests/security/test_admin_security.py`)

## Running Admin Tests

### Quick Commands

```bash
# Run all admin tests
make test-admin

# Run specific categories
make test-admin-unit        # Unit tests only
make test-admin-api         # API tests only  
make test-admin-integration # Integration tests only
make test-admin-security    # Security tests only
```

### Manual Commands

```bash
# All admin tests
pytest tests/unit/test_admin_management.py tests/api/test_admin_api.py tests/integration/test_admin_integration.py tests/security/test_admin_security.py -v

# Individual test files
pytest tests/unit/test_admin_management.py -v
pytest tests/api/test_admin_api.py -v -m api
pytest tests/integration/test_admin_integration.py -v -m integration
pytest tests/security/test_admin_security.py -v
```

## Test Details

### 1. Unit Tests (`test_admin_management.py`)

Tests the core admin management functionality with mocked dependencies.

#### TestAdminCreation
- ✅ `test_create_admin_user_success` - Valid admin creation
- ✅ `test_create_admin_user_duplicate_email` - Duplicate email handling
- ✅ `test_create_admin_user_invalid_email` - Email validation
- ✅ `test_create_admin_user_password_mismatch` - Password confirmation

#### TestAdminPromotion  
- ✅ `test_promote_existing_user_success` - User promotion to admin
- ✅ `test_promote_user_not_found` - Non-existent user handling
- ✅ `test_promote_already_admin_user` - Already admin user handling
- ✅ `test_promote_user_cancelled` - User cancellation

#### TestAdminListing
- ✅ `test_list_admin_users_success` - Admin listing functionality
- ✅ `test_list_admin_users_empty` - Empty admin list handling

#### TestPasswordSecurity
- ✅ `test_password_hashing` - Password hashing verification
- ✅ `test_password_verification` - Password verification

#### TestAdminModelIntegration
- ✅ `test_user_model_admin_fields` - User model admin field validation
- ✅ `test_user_model_default_values` - Default value testing (Python vs Database)

### 2. API Tests (`test_admin_api.py`)

Integration tests with real HTTP requests to the running API server.

#### TestAdminAPI
- ✅ `test_get_current_user_info` - `/api/auth/me` endpoint
- ✅ `test_get_current_user_unauthorized` - Unauthorized access handling
- ✅ `test_get_current_user_invalid_token` - Invalid token handling
- ✅ `test_verify_admin_access_with_admin_user` - Admin verification success
- ✅ `test_verify_admin_access_with_regular_user` - Admin verification failure
- ✅ `test_verify_admin_access_unauthorized` - Unauthorized admin access
- ✅ `test_verify_admin_access_invalid_token` - Invalid token admin access

#### TestAdminUserManagement
- ✅ `test_admin_user_registration_flow` - Complete admin workflow
- ✅ `test_token_refresh_preserves_admin_status` - Token refresh behavior

#### TestAdminSecurity
- ✅ `test_admin_endpoint_security` - Endpoint security validation
- ✅ `test_admin_endpoint_without_auth` - Unauthenticated access prevention
- ✅ `test_admin_token_validation` - Token validation scenarios

#### TestAdminAPIIntegration
- ✅ `test_user_registration_includes_admin_field` - Registration response validation
- ✅ `test_login_preserves_admin_status` - Login admin status preservation

#### TestAdminDatabaseIntegration
- ✅ `test_user_model_admin_functionality` - Database model testing
- ✅ `test_admin_user_authentication_flow` - Complete auth flow
- ✅ `test_user_model_database_defaults` - Database default values testing

### 3. Integration Tests (`test_admin_integration.py`)

End-to-end testing of admin functionality including script execution and database operations.

#### TestAdminScriptIntegration
- ✅ `test_admin_script_help` - Script help functionality
- ✅ `test_admin_creation_script_integration` - Script creation testing
- ✅ `test_admin_listing_script_integration` - Script listing testing  
- ✅ `test_admin_promotion_script_integration` - Script promotion testing

#### TestAdminDatabaseIntegration
- ✅ `test_user_model_admin_functionality` - Database model testing
- ✅ `test_admin_user_authentication_flow` - Complete auth flow

#### TestAdminMakefileIntegration
- ✅ `test_makefile_admin_targets_exist` - Makefile target verification
- ✅ `test_makefile_help_includes_admin` - Help text inclusion

#### TestAdminSecurityIntegration
- ✅ `test_admin_dependency_function` - Dependency function testing
- ✅ `test_admin_model_constraints` - Model constraint validation

#### TestAdminEndToEndWorkflow
- ✅ `test_admin_workflow_simulation` - Complete workflow simulation
- ✅ `test_admin_error_handling_integration` - Error handling testing

#### TestAdminDocumentationIntegration
- ✅ `test_admin_setup_documentation_exists` - Documentation validation
- ✅ `test_admin_script_documentation` - Script documentation testing

### 4. Security Tests (`test_admin_security.py`)

Security-focused testing of admin functionality.

#### TestAdminAccessControl
- ✅ `test_admin_dependency_rejects_regular_user` - Access control validation
- ✅ `test_admin_dependency_accepts_admin_user` - Admin access validation
- ✅ `test_admin_dependency_rejects_inactive_admin` - Inactive admin handling
- ✅ `test_admin_field_not_editable_by_regular_user` - Field protection

#### TestAdminAuthenticationSecurity
- ✅ `test_admin_password_hashing` - Password security validation
- ✅ `test_admin_token_contains_user_id_only` - Token content validation
- ✅ `test_admin_token_expiration` - Token expiration testing
- ✅ `test_admin_script_password_validation` - Script password validation

#### TestAdminPrivilegeEscalation
- ✅ `test_regular_user_cannot_access_admin_endpoints` - Privilege escalation prevention
- ✅ `test_admin_status_not_in_token_payload` - Token payload security
- ✅ `test_token_tampering_detection` - Token tampering detection
- ✅ `test_admin_creation_requires_strong_password` - Strong password enforcement

#### TestAdminSessionSecurity
- ✅ `test_admin_session_invalidation` - Session management
- ✅ `test_admin_token_refresh_security` - Token refresh security
- ✅ `test_concurrent_admin_sessions` - Concurrent session handling

#### TestAdminAuditingSecurity
- ✅ `test_admin_action_logging` - Admin action auditing
- ✅ `test_admin_creation_logging` - Admin creation logging
- ✅ `test_failed_admin_access_logging` - Failed access logging

#### TestAdminInputValidation
- ✅ `test_admin_email_validation` - Email input validation
- ✅ `test_admin_username_validation` - Username input validation
- ✅ `test_admin_script_sql_injection_prevention` - SQL injection prevention

#### TestAdminRateLimiting
- ✅ `test_admin_endpoint_rate_limiting` - Endpoint rate limiting
- ✅ `test_admin_creation_rate_limiting` - Creation rate limiting
- ✅ `test_admin_login_attempt_limiting` - Login attempt limiting

#### TestAdminSecurityHeaders
- ✅ `test_admin_api_security_headers` - Security headers validation
- ✅ `test_admin_csrf_protection` - CSRF protection testing

#### TestAdminErrorHandling
- ✅ `test_admin_error_information_disclosure` - Information disclosure prevention
- ✅ `test_admin_authentication_error_messages` - Error message security

## Test Coverage Areas

### ✅ Functional Testing
- Admin user creation via script
- Admin user promotion
- Admin user listing
- API endpoint access control
- Authentication and authorization flows
- Token management and refresh

### ✅ Security Testing
- Access control enforcement
- Privilege escalation prevention
- Password security and hashing
- Token security and validation
- Input validation and sanitization
- SQL injection prevention
- Session management security

### ✅ Integration Testing
- Script and database integration
- API and authentication integration
- Makefile target validation
- End-to-end workflow testing

### ✅ Error Handling
- Invalid input handling
- Database connection failures
- Authentication failures
- Authorization failures

## Prerequisites for Running Tests

### For Unit Tests
- Python environment with project dependencies
- Mocked database connections (no real database required)

### For API Tests
- Running API server at `http://localhost:8000`
- Database setup and migrations applied
- Test environment with proper configuration

### For Integration Tests  
- Complete development environment setup
- Database access for model testing
- Makefile availability for target testing

### For Security Tests
- All dependencies available
- Test environment isolated from production

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.api` - API integration tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security-focused tests

Run specific markers:
```bash
pytest -m api           # API tests only
pytest -m integration   # Integration tests only  
pytest -m security     # Security tests only
```

## Test Data and Fixtures

### Common Fixtures
- `mock_regular_user` - Regular user without admin privileges
- `mock_admin_user` - Admin user with full privileges
- `mock_inactive_admin` - Inactive admin user
- `unique_admin_data` - Unique admin user data for each test
- `unique_regular_user_data` - Unique regular user data
- `admin_tokens` - Admin authentication tokens
- `regular_user_tokens` - Regular user authentication tokens

### Test Isolation
- Each test uses unique data to prevent conflicts
- Database operations are mocked in unit tests
- API tests use unique users for each test run
- Integration tests clean up after themselves

## Continuous Integration

These tests are designed to run in CI/CD environments:

1. **Unit Tests** - Fast, no external dependencies
2. **API Tests** - Require running server, suitable for integration testing stage
3. **Integration Tests** - Require full environment, suitable for deployment testing
4. **Security Tests** - Can run independently, suitable for security scanning

## Coverage Goals

The admin test suite aims for:
- **95%+ code coverage** of admin-related functionality
- **100% security scenario coverage** for admin features
- **Complete API endpoint coverage** for admin endpoints
- **Full workflow coverage** from admin creation to API usage

## Maintenance

### Adding New Admin Tests
1. Choose appropriate test category (unit/api/integration/security)
2. Follow existing naming conventions
3. Use appropriate fixtures and markers
4. Update this documentation

### Test Updates Required When:
- New admin functionality is added
- Admin API endpoints change
- Security requirements change
- Database schema changes affecting admin features

## Troubleshooting Tests

### Common Issues
1. **Database connection failures** - Check test environment setup
2. **API server not running** - Start server before running API tests
3. **Import errors** - Verify Python path and dependencies
4. **Token validation failures** - Check SECRET_KEY configuration

### Debug Commands
```bash
# Run with verbose output
pytest tests/unit/test_admin_management.py -v -s

# Run specific test
pytest tests/unit/test_admin_management.py::TestAdminCreation::test_create_admin_user_success -v

# Run with coverage
pytest tests/unit/test_admin_management.py --cov=scripts.create_admin --cov-report=term-missing
```

## Important Testing Notes

### SQLAlchemy Default Values

**Understanding SQLAlchemy Defaults:**
- `Column(Boolean, default=True)` only applies when inserting into database
- Python object creation does NOT trigger defaults
- Use `.refresh()` after database insert to get defaults

**Example:**
```python
# In-memory object - defaults are None
user = User(email="test@example.com", username="test", hashed_password="hash")
assert user.is_active is None  # Not set yet

# After database interaction - defaults applied
session.add(user)
session.commit() 
session.refresh(user)
assert user.is_active is True  # Database default applied
```

**Test Strategy:**
- **Unit tests**: Test explicit values and column definitions
- **Integration tests**: Test actual database default behavior
- **API tests**: Test complete workflows with real data

### Database Testing Approach

The project uses a **layered database testing strategy**:

1. **SQLite Tests** (Fast Development)
   - In-memory database: `sqlite:///:memory:`
   - 10-100x faster than PostgreSQL
   - Perfect for unit and integration tests
   - No external dependencies

2. **PostgreSQL Tests** (Production Parity) 
   - Real PostgreSQL database with test data
   - Tests database-specific features (ILIKE, JSON, etc.)
   - Critical for deployment validation
   - Requires PostgreSQL server

**When Each Database Catches Issues:**
- **SQLite**: Logic errors, model relationships, basic constraints
- **PostgreSQL**: Case sensitivity, data types, constraint differences, performance

### Test Environment Setup

**For Unit Tests:**
```bash
conda activate nocturna-test  # or nocturna-dev
make test-admin-unit         # No database required
```

**For Integration Tests:**
```bash
conda activate nocturna-test
make test-admin              # SQLite integration tests
make test-admin-postgres     # PostgreSQL integration tests (requires DB)
```

**Environment Issues:**
- Always activate conda environment first
- Use `nocturna-test` environment for testing
- Use `nocturna-dev` for development

### Common Test Failures

#### 1. SQLAlchemy Default Values
**Error:** `assert None is True` 
**Cause:** Testing defaults on Python objects instead of database objects
**Fix:** Test explicit values or use database interaction

#### 2. Environment Not Activated
**Error:** `No Nocturna environment active`
**Fix:** `conda activate nocturna-test`

#### 3. Database Connection
**Error:** `Failed to connect to database`
**Fix:** Ensure PostgreSQL running for postgres tests, or use SQLite tests 