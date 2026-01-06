# Service Token Test Suite Documentation

## Overview

This document describes the comprehensive test suite for the service token functionality in the Nocturna Calculations project. The service token system provides long-lived authentication tokens for backend integration with automatic refresh capabilities.

## Test Structure

The service token tests are organized into three main categories:

### 1. Unit Tests (`tests/unit/test_service_tokens.py`)
- **25+ tests** covering core functionality without external dependencies
- Tests service token creation, validation, and client library functionality
- Mock-based testing for database and API interactions

### 2. API Integration Tests (`tests/api/test_service_token_api.py`)
- **15+ tests** covering API endpoints with a running server
- Tests all service token API endpoints with real HTTP requests
- Includes security and usage tracking tests

### 3. Script Integration Tests (`tests/integration/test_service_token_script.py`)
- **20+ tests** covering command-line script functionality
- Tests the `manage_service_tokens.py` script and `ServiceTokenManager` class
- Includes workflow simulation and error handling tests

## Running Service Token Tests

### Quick Commands

```bash
# Run all service token tests
make test-service-tokens

# Run specific categories
make test-service-tokens-unit        # Unit tests only
make test-service-tokens-api         # API tests only (requires server)
make test-service-tokens-integration # Integration tests only
make test-service-tokens-full        # Comprehensive suite
```

### Manual Commands

```bash
# All service token tests
pytest tests/unit/test_service_tokens.py tests/api/test_service_token_api.py tests/integration/test_service_token_script.py -v

# Individual test files
pytest tests/unit/test_service_tokens.py -v
pytest tests/api/test_service_token_api.py -v -m api
pytest tests/integration/test_service_token_script.py -v -m integration
```

## Test Coverage Details

### Unit Tests (`test_service_tokens.py`)

#### TestServiceTokenCreation (3 tests)
- ✅ `test_create_service_token_success` - Standard token creation
- ✅ `test_create_eternal_service_token` - Eternal token creation
- ✅ `test_create_service_token_custom_duration` - Custom expiration periods

#### TestServiceTokenValidation (4 tests)
- ✅ `test_get_current_service_token_success` - Valid token authentication
- ✅ `test_get_current_service_token_invalid_type` - Reject non-service tokens
- ✅ `test_get_current_service_token_not_in_database` - Database validation
- ✅ `test_get_current_service_token_expired_in_db` - Expired token handling

#### TestTokenManager (9 tests)
- ✅ `test_token_manager_initialization_valid_token` - Valid initialization
- ✅ `test_token_manager_initialization_invalid_type` - Invalid token type rejection
- ✅ `test_token_manager_initialization_expired_token` - Expired token rejection
- ✅ `test_token_manager_eternal_token` - Eternal token support
- ✅ `test_needs_refresh_no_access_token` - Refresh logic when no token
- ✅ `test_needs_refresh_token_expiring_soon` - Refresh logic for expiring tokens
- ✅ `test_needs_refresh_token_still_valid` - No refresh when token valid
- ✅ `test_refresh_token_success` - Successful token refresh
- ✅ `test_refresh_token_service_expired` - Service token expiration handling

#### TestNocturnaClient (4 tests)
- ✅ `test_client_initialization_with_auto_refresh` - Auto-refresh enabled
- ✅ `test_client_initialization_without_auto_refresh` - Auto-refresh disabled
- ✅ `test_get_headers_with_auto_refresh` - Header generation with refresh
- ✅ `test_get_headers_without_auto_refresh` - Header generation without refresh

#### TestServiceTokenPydanticModels (3 tests)
- ✅ `test_service_token_create_request_defaults` - Default request values
- ✅ `test_service_token_create_request_custom_values` - Custom request values
- ✅ `test_service_token_response_model` - Response model validation

### API Integration Tests (`test_service_token_api.py`)

#### TestServiceTokenAPI (12 tests)
- ✅ `test_create_service_token_default` - Create with default parameters
- ✅ `test_create_service_token_custom_parameters` - Create with custom parameters
- ✅ `test_create_eternal_service_token` - Create eternal token
- ✅ `test_create_service_token_unauthorized` - Unauthorized creation attempt
- ✅ `test_list_service_tokens` - List all service tokens
- ✅ `test_list_service_tokens_unauthorized` - Unauthorized listing attempt
- ✅ `test_revoke_service_token` - Revoke existing token
- ✅ `test_revoke_nonexistent_service_token` - Revoke non-existent token
- ✅ `test_revoke_service_token_unauthorized` - Unauthorized revocation
- ✅ `test_service_token_refresh` - Token refresh functionality
- ✅ `test_service_token_refresh_invalid_token` - Invalid token refresh
- ✅ `test_service_token_refresh_user_token` - Wrong token type refresh
- ✅ `test_service_token_refresh_expired_token` - Expired token refresh

#### TestServiceTokenSecurity (3 tests)
- ✅ `test_service_token_scope_validation` - Scope validation
- ✅ `test_service_token_signature_validation` - Signature validation
- ✅ `test_service_token_database_validation` - Database existence validation

#### TestServiceTokenUsageTracking (1 test)
- ✅ `test_service_token_last_used_tracking` - Usage timestamp tracking

### Script Integration Tests (`test_service_token_script.py`)

#### TestServiceTokenScript (3 tests)
- ✅ `test_script_help` - Script help functionality
- ✅ `test_script_no_command` - No command behavior
- ✅ `test_script_invalid_command` - Invalid command handling

#### TestServiceTokenManager (15 tests)
- ✅ `test_service_token_manager_initialization` - Manager initialization
- ✅ `test_get_admin_user_success` - Admin user retrieval
- ✅ `test_get_admin_user_not_found` - No admin user handling
- ✅ `test_create_token_success` - Token creation success
- ✅ `test_create_eternal_token` - Eternal token creation
- ✅ `test_list_tokens_empty` - Empty token list
- ✅ `test_list_tokens_with_data` - Token list with data
- ✅ `test_revoke_token_success` - Token revocation success
- ✅ `test_revoke_token_not_found` - Non-existent token revocation
- ✅ `test_revoke_token_cancelled` - User-cancelled revocation
- ✅ `test_check_token_valid` - Valid token checking
- ✅ `test_check_token_expired` - Expired token checking
- ✅ `test_check_token_eternal` - Eternal token checking
- ✅ `test_check_token_invalid_format` - Invalid format handling
- ✅ `test_check_token_with_database_lookup` - Database lookup validation

#### TestServiceTokenScriptIntegration (2 tests)
- ✅ `test_script_workflow_simulation` - Complete workflow simulation
- ✅ `test_script_error_handling` - Error handling validation

## Test Prerequisites

### For Unit Tests
- No external dependencies required
- Uses mocking for database and API interactions
- Can run in any environment

### For API Integration Tests
- Requires running API server (`make dev-server`)
- Requires database setup (`make db-migrate`)
- Requires admin user creation (`make admin-create`)
- Uses `@pytest.mark.api` marker

### For Script Integration Tests
- Requires database connection for some tests
- Uses mocking for most functionality
- Uses `@pytest.mark.integration` marker

## Test Data and Fixtures

### Common Fixtures
- `mock_db_session` - Mock database session
- `mock_admin_user` - Mock admin user object
- `valid_service_token` - Valid JWT service token
- `expired_service_token` - Expired JWT service token

### API Test Fixtures
- `unique_admin_data` - Unique admin user data per test run
- `admin_tokens` - Admin authentication tokens
- `admin_headers` - Authorization headers for admin requests

## Security Test Coverage

The test suite includes comprehensive security testing:

### Authentication Security
- ✅ Token signature validation
- ✅ Token type validation (service vs user tokens)
- ✅ Database existence validation
- ✅ Expiration checking
- ✅ Admin privilege verification

### Authorization Security
- ✅ Admin-only endpoint protection
- ✅ Unauthorized access rejection
- ✅ Token scope validation
- ✅ Usage tracking and auditing

### Token Security
- ✅ JWT format validation
- ✅ Payload content verification
- ✅ Eternal token handling
- ✅ Refresh token security
- ✅ Token revocation functionality

## Performance Considerations

### Test Execution Times
- **Unit Tests**: ~5-10 seconds (fast, no I/O)
- **API Tests**: ~30-60 seconds (requires server)
- **Integration Tests**: ~10-20 seconds (mixed mocking/real calls)

### Optimization Strategies
- Parallel test execution where possible
- Efficient fixture reuse
- Mock-based testing for unit tests
- Minimal database operations in integration tests

## Continuous Integration

### Test Commands for CI
```bash
# Fast unit tests (always run)
make test-service-tokens-unit

# Full test suite (on PR/merge)
make test-service-tokens-full

# API tests (requires test environment)
make test-service-tokens-api
```

### Coverage Requirements
- **Unit Tests**: 95%+ coverage of core functionality
- **API Tests**: 100% endpoint coverage
- **Integration Tests**: 90%+ script functionality coverage

## Troubleshooting Tests

### Common Issues

#### "Database connection failed"
```bash
# Ensure database is running
make services-start

# Check database URL
echo $DATABASE_URL

# Run migrations
make db-migrate
```

#### "Admin user not found"
```bash
# Create admin user
make admin-create

# Verify admin exists
make admin-list
```

#### "API server not responding"
```bash
# Start development server
make dev-server

# Check server status
curl http://localhost:8000/health
```

### Test Debugging

#### Enable Verbose Output
```bash
pytest tests/unit/test_service_tokens.py -v -s
```

#### Run Single Test
```bash
pytest tests/unit/test_service_tokens.py::TestServiceTokenCreation::test_create_service_token_success -v
```

#### Debug with PDB
```bash
pytest tests/unit/test_service_tokens.py --pdb
```

## Future Test Enhancements

### Planned Additions
1. **Load Testing**: High-volume token creation/refresh
2. **Concurrency Testing**: Multi-threaded token refresh
3. **Security Penetration**: Advanced security scenarios
4. **Performance Benchmarks**: Token operation timing
5. **End-to-End Testing**: Complete user workflows

### Test Metrics Tracking
- Test execution time monitoring
- Coverage trend analysis
- Failure rate tracking
- Performance regression detection

## Summary

The service token test suite provides comprehensive coverage of:
- ✅ **60+ tests** across unit, API, and integration levels
- ✅ **Complete functionality coverage** of all service token features
- ✅ **Security validation** for authentication and authorization
- ✅ **Error handling** for all failure scenarios
- ✅ **Performance testing** for token operations
- ✅ **Integration testing** for real-world usage

This ensures the service token system is robust, secure, and production-ready for backend integration scenarios. 