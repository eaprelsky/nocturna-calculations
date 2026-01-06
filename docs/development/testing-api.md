# API Testing Guide

**🚀 NEW: Fully Automated API Testing with Server Management**

This guide explains how to run API tests with our new integrated testing infrastructure that automatically manages server startup, testing, and cleanup.

## Quick Start (Zero Manual Steps)

### 1. Set up the test environment (one-time setup)

```bash
make setup-test
```

### 2. Run complete automated testing

```bash
conda activate nocturna-test

# 🏆 BEST: Complete test suite with automatic server management
make test-complete-integrated    # 92+ tests including API

# 🚀 API tests only with automatic server management
make test-api-integrated         # 21 API tests, zero manual setup

# ⚡ Quick API validation
make test-api-integrated-quick   # Fast API health check
```

**That's it! No manual server management needed.** ✨

## 🆚 Old vs New Testing

### ❌ Old Way (Manual Process)
```bash
# Terminal 1: Start server manually
conda activate nocturna-dev
make dev

# Terminal 2: Run tests manually  
conda activate nocturna-test
make test-api

# Manual cleanup and management
```

### ✅ New Way (Fully Automated)
```bash
# Single terminal, single command
conda activate nocturna-test
make test-api-integrated    # Automatic server + tests + cleanup
```

## 🎯 Available Test Commands

### **Integrated API Tests (NEW - Recommended)**

```bash
# Complete API test suite with managed server
make test-api-integrated         # All 21 API tests

# Specific API test categories
make test-api-integrated-auth    # Authentication tests only
make test-api-integrated-charts  # Chart operation tests only
make test-api-integrated-calculations # Calculation tests only

# Quick API validation
make test-api-integrated-quick   # Fast health check and core tests
```

### **Complete Test Suites**

```bash
# 🏆 ULTIMATE: Everything automated (recommended)
make test-complete-integrated    # 92+ tests (WebSocket + Auth + API)

# Fast comprehensive testing
make test-working               # 71+ tests (WebSocket + Auth only)

# Test status and summary
make test-summary              # Show all test categories status
```

### **Legacy Commands (Manual Server Required)**

```bash
# These still require manual server management
make test-api                   # Traditional API tests
make test-api-auth             # Authentication tests (manual)
make test-api-charts           # Chart tests (manual)
```

## 🔧 How Automatic Server Management Works

Our new integrated testing system:

1. **🚀 Starts development server** automatically in background
2. **⏳ Waits for server readiness** with health checks  
3. **🧪 Runs comprehensive API tests** (21 tests)
4. **🛑 Stops server and cleans up** automatically
5. **📊 Reports results** with detailed output

### Technical Details

- **Server startup timeout**: 30 seconds (configurable)
- **Health check**: Validates `/health` endpoint
- **Port management**: Handles conflicts automatically
- **Process cleanup**: Graceful shutdown with fallback to force-kill
- **Error handling**: Robust error recovery and cleanup

## 📊 Test Categories & Coverage

### 🔐 Authentication Tests (6 tests)
- ✅ User registration and validation
- ✅ Login/logout with JWT tokens
- ✅ Token refresh mechanisms  
- ✅ Authorization and access control
- ✅ Invalid credentials handling
- ✅ Security boundary testing

### 📊 Chart Management Tests (5 tests)
- ✅ Creating natal charts with validation
- ✅ Retrieving charts by ID
- ✅ Updating chart data
- ✅ Deleting charts with authorization
- ✅ Chart ownership validation

### 🔬 Calculation Tests (3 tests)
- ✅ Planetary position calculations
- ✅ Aspect calculations with orbs
- ✅ House system calculations
- ✅ Input validation and error handling

### ⚡ Performance Tests (2 tests)
- ✅ Response time validation (< 2 seconds)
- ✅ Health check performance
- ✅ Calculation speed benchmarks

### 🛡️ Security & Error Tests (5 tests)
- ✅ Unauthorized access prevention
- ✅ Invalid token handling
- ✅ Malformed request validation
- ✅ Non-existent resource handling
- ✅ Input sanitization

## 🎯 Advanced Usage

### Custom Server Configuration

```bash
# Custom timeout and port
python scripts/testing/test_with_server.py --timeout 60 --port 8001

# Verbose output for debugging
python scripts/testing/test_with_server.py --verbose

# Specific test categories
python scripts/testing/test_with_server.py --auth
python scripts/testing/test_with_server.py --charts
python scripts/testing/test_with_server.py --calculations
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Run API Tests
  run: |
    conda activate nocturna-test
    make test-api-integrated
```

### Development Workflow

```bash
# 1. Quick validation during development
make test-api-integrated-quick   # ~10-15 seconds

# 2. Full validation before commit
make test-complete-integrated    # ~20-25 seconds

# 3. Component-specific testing
make test-websocket             # When working on WebSocket features
make test-auth                  # When working on authentication
```

## 🐛 Troubleshooting

### Server Startup Issues

```
❌ Server failed to start within 30 seconds
```

**Solutions:**
- Increase timeout: `--timeout 60`
- Check port availability: `netstat -an | grep 8000`
- Verify environment: `conda activate nocturna-test`

### Port Conflicts

```
ℹ️ Server already running at http://localhost:8000
```

**Behavior**: Tests will use existing server (safe for development)

### Environment Issues

```
⚠️ Current environment: base
🧪 Tests should run in nocturna-test environment
```

**Solution:**
```bash
make setup-test                 # If not set up
conda activate nocturna-test    # Activate correct environment
```

### Test Failures

Common causes and solutions:

1. **Database issues**: Server uses in-memory SQLite for tests
2. **Dependency issues**: Recreate test environment: `make setup-test`
3. **Network issues**: Check localhost connectivity
4. **Environment issues**: Ensure `nocturna-test` is active

## 📈 Performance Metrics

### Execution Times
- **API Test Suite**: 10-15 seconds (including server management)
- **Complete Integration**: 20-25 seconds (92+ tests)
- **Quick Validation**: 5-10 seconds (essential tests only)

### Resource Usage
- **Memory**: ~200MB during testing
- **CPU**: Moderate during server startup
- **Network**: Localhost HTTP requests only
- **Disk**: Temporary SQLite database

## 🚀 Benefits of New System

### For Developers
- **Zero manual steps** - Focus on coding, not test setup
- **Fast feedback** - Quick validation during development  
- **Reliable** - Consistent test environment every time
- **Comprehensive** - Full API coverage in single command

### For CI/CD
- **Automated** - No manual intervention required
- **Reliable** - Eliminates environment setup issues
- **Fast** - Optimized for quick feedback
- **Comprehensive** - Complete validation in one step

### For Quality Assurance
- **Real integration testing** - Actual HTTP requests
- **Complete coverage** - All endpoints and scenarios
- **Performance validation** - Response time benchmarks
- **Security testing** - Authentication and authorization

## 🔗 Related Documentation

- [Complete Testing Guide](../testing-guide.md) - Comprehensive testing overview
- [WebSocket Testing](../websockets.md) - Real-time communication testing
- [Development Setup](../installation/development-setup.md) - Environment setup
- [Contributing Guide](../../CONTRIBUTING.md) - Development workflow

---

**🎉 The new integrated testing system eliminates all manual steps and provides comprehensive API validation with a single command!** 