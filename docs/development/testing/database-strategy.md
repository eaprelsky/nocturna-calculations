# Database Testing Strategy

## Overview

This document explains why we use different databases for testing and when to choose SQLite vs PostgreSQL for your tests.

## Current Testing Setup

### 🚀 **SQLite Tests** (Default)
- **Files**: `test_admin_integration.py`, unit tests
- **Use Case**: Fast, isolated testing
- **Database**: In-memory SQLite (`sqlite:///:memory:`)

### 🐘 **PostgreSQL Tests** (Production Parity)
- **Files**: `test_admin_integration_postgres.py`
- **Use Case**: Production-like testing  
- **Database**: PostgreSQL test database

## When to Use SQLite Tests

### ✅ **Perfect For:**

1. **Unit Tests** 
   ```bash
   make test-admin-unit
   ```
   - Fast execution (milliseconds)
   - No external dependencies
   - Perfect isolation

2. **Development Testing**
   ```bash
   make test-admin  # Uses SQLite by default
   ```
   - Quick feedback during development
   - No database setup required
   - Run anywhere

3. **CI/CD Pipelines**
   ```bash
   pytest tests/unit/ tests/integration/test_admin_integration.py
   ```
   - No PostgreSQL server needed
   - Faster CI builds
   - Easier to parallelize

4. **Basic Integration Testing**
   - Testing business logic
   - Model relationships
   - Basic CRUD operations

### ✅ **SQLite Advantages:**
- ⚡ **Speed**: 10-100x faster than PostgreSQL for tests
- 🎯 **Simplicity**: No setup, configuration, or cleanup
- 🔒 **Isolation**: Each test gets fresh database
- 🚀 **Portability**: Works everywhere Python works

## When to Use PostgreSQL Tests

### ✅ **Required For:**

1. **Database-Specific Features**
   ```python
   # PostgreSQL ILIKE operator
   users = session.query(User).filter(User.email.ilike('%admin%')).all()
   
   # JSON operations  
   users = session.query(User).filter(User.metadata['role'] == 'admin').all()
   
   # Array operations
   users = session.query(User).filter(User.tags.any('admin')).all()
   ```

2. **Production Parity Testing**
   ```bash
   make test-admin-postgres
   ```
   - Before production deployments
   - Testing migrations
   - Performance validation

3. **Constraint Testing**
   ```python
   # PostgreSQL-specific constraint behavior
   # Foreign key handling
   # Transaction isolation levels
   ```

4. **Complex Queries**
   - Full-text search
   - Window functions  
   - Advanced indexing

### ✅ **PostgreSQL Test Scenarios:**

```bash
# Critical path testing
make test-admin-postgres

# Full test suite before deployment  
make test-admin-full

# Migration testing
pytest tests/integration/test_admin_integration_postgres.py::TestAdminMigrationCompatibility
```

## Recommended Testing Strategy

### 🔄 **Development Workflow:**

```bash
# 1. During development (fast feedback)
make test-admin-unit

# 2. Before committing (comprehensive but fast)
make test-admin

# 3. Before deploying (production parity)
make test-admin-postgres

# 4. Full validation (everything)
make test-admin-full
```

### 🏗️ **CI/CD Pipeline:**

```yaml
# Example CI configuration
stages:
  - test-fast:     # SQLite tests
      script: make test-admin
      
  - test-integration:  # PostgreSQL tests  
      script: make test-admin-postgres
      services:
        - postgres:13
        
  - deploy:
      needs: [test-fast, test-integration]
```

## Database Differences to Watch

### ⚠️ **SQLite vs PostgreSQL Differences:**

| Feature | SQLite | PostgreSQL | Impact |
|---------|--------|------------|---------|
| **Data Types** | Limited | Rich types | Test data validation |
| **Constraints** | Basic | Advanced | Test constraint behavior |
| **JSON Support** | Basic | Native | Test JSON operations |
| **Case Sensitivity** | Configurable | Case sensitive | Test search/filtering |
| **Transactions** | Simpler | Full ACID | Test concurrency |
| **Error Messages** | Generic | Specific | Test error handling |

### 🔍 **Things That Might Work in SQLite but Fail in PostgreSQL:**

1. **Case Sensitivity**
   ```python
   # Works in SQLite, might fail in PostgreSQL
   User.email == 'ADMIN@EXAMPLE.COM'  # vs user input 'admin@example.com'
   ```

2. **Data Type Handling**
   ```python
   # SQLite is more forgiving with type coercion
   User.created_at = '2023-01-01'  # String instead of datetime
   ```

3. **Constraint Enforcement**
   ```python
   # PostgreSQL might enforce constraints more strictly
   User.email = None  # When email is NOT NULL
   ```

## Configuration Examples

### 🔧 **Environment Variables:**

```bash
# For SQLite tests (default)
# No DATABASE_URL needed

# For PostgreSQL tests
export DATABASE_URL="postgresql://user:password@localhost:5432/nocturna"
# Test database will be created as nocturna_test
```

### 🔧 **pytest.ini Configuration:**

```ini
[tool:pytest]
markers =
    postgres: marks tests as requiring PostgreSQL database
    sqlite: marks tests as using SQLite database
    integration: marks tests as integration tests
    api: marks tests as API integration tests
```

### 🔧 **Running Specific Database Tests:**

```bash
# SQLite only
pytest -m "not postgres"

# PostgreSQL only  
pytest -m postgres

# Both databases
pytest tests/integration/

# With coverage
pytest tests/ --cov=nocturna_calculations --cov-report=html
```

## Best Practices

### ✅ **Do:**

1. **Use SQLite for fast iteration**
   - Unit tests
   - Development testing
   - CI smoke tests

2. **Use PostgreSQL for validation**
   - Before production deployment
   - Database-specific features
   - Performance testing

3. **Test both when in doubt**
   ```bash
   make test-admin-full
   ```

4. **Document database-specific tests**
   ```python
   @pytest.mark.postgres
   def test_postgresql_specific_feature():
       """This test requires PostgreSQL ILIKE operator"""
   ```

### ❌ **Don't:**

1. **Don't use only SQLite** for production apps
2. **Don't use only PostgreSQL** for all tests (too slow)
3. **Don't ignore database differences** in critical features
4. **Don't test migrations only in SQLite**

## Troubleshooting

### 🔧 **Common Issues:**

1. **PostgreSQL not available in CI**
   ```bash
   # Tests should skip gracefully
   pytest.skip("PostgreSQL not available for testing")
   ```

2. **Test database conflicts**
   ```bash
   # Use separate test database
   nocturna_test  # instead of nocturna
   ```

3. **Slow PostgreSQL tests**
   ```bash
   # Run in parallel
   pytest -n auto -m postgres
   ```

### 🔧 **Debug Commands:**

```bash
# Check which tests are running against which database
pytest --collect-only tests/integration/

# Run only fast tests
pytest -m "not postgres"

# Run with database debug info
pytest -v -s tests/integration/test_admin_integration_postgres.py
```

## Summary

**Use SQLite for:**
- 🚀 Development and unit testing
- ⚡ Fast CI/CD feedback  
- 🎯 Business logic validation

**Use PostgreSQL for:**
- 🐘 Production parity testing
- 🔍 Database-specific features
- 🚀 Pre-deployment validation

**Best Approach:**
```bash
# Fast development
make test-admin          # SQLite

# Before deployment  
make test-admin-postgres # PostgreSQL

# Full confidence
make test-admin-full     # Both
``` 