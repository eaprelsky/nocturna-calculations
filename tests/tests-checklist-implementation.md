# Test Coverage Checklist - Nocturna Calculations

## Overview
This checklist covers both library functionality and REST API endpoints for the astrological calculations service.

## Implemented Tests

### Library Tests
- [x] Chart Generation
  - [x] Basic chart generation
  - [x] Custom chart parameters
  - [x] Error handling
- [x] Swiss Ephemeris Integration
  - [x] Planet positions calculation
  - [x] House system calculations
  - [x] Error handling for invalid inputs

### API Tests
- [ ] None implemented yet

## Pending Tests

## 1. Library Unit Tests

### Core Classes
- [ ] Chart Class
  - [ ] Initialization with valid/invalid parameters
  - [ ] Date/time format validation
  - [ ] Coordinate validation
  - [ ] Timezone handling
- [ ] Position Class
  - [ ] Coordinate validation
  - [ ] Distance calculations
  - [ ] Declination calculations
- [ ] Aspect Class
  - [ ] Aspect detection
  - [ ] Orb calculations
  - [ ] Applying/separating determination
- [ ] Dignity Class
  - [ ] Dignity score calculations
  - [ ] Essential dignity rules
  - [ ] Accidental dignity rules

### Calculation Methods
- [ ] Planetary Positions
  - [ ] All planets calculation
  - [ ] Retrograde detection
  - [ ] Speed calculations
  - [ ] Precision validation against ephemeris
- [ ] House Systems
  - [ ] Placidus system
  - [ ] Koch system
  - [ ] Equal house system
  - [ ] Whole sign houses
  - [ ] Regiomontanus system
  - [ ] Extreme latitude handling
- [ ] Aspects
  - [ ] Major aspects (conjunction, opposition, trine, square, sextile)
  - [ ] Minor aspects (quincunx, semi-sextile, etc.)
  - [ ] Custom orb settings
  - [ ] Aspect patterns (T-square, Grand Trine, etc.)
- [ ] Directions & Progressions
  - [ ] Primary directions
  - [ ] Secondary progressions
  - [ ] Solar arc directions
  - [ ] Profections

### Rectification
- [ ] Event-Based Rectification
  - [ ] Single event rectification
  - [ ] Multiple events rectification
  - [ ] Time window calculations
- [ ] Pattern-Based Rectification
  - [ ] Pattern recognition
  - [ ] Statistical analysis
  - [ ] Confidence scoring
- [ ] Harmonic Rectification
  - [ ] Harmonic analysis
  - [ ] Age harmonics
  - [ ] Event harmonics

### Utility Functions
- [ ] Coordinate Transformations
  - [ ] Ecliptic to equatorial
  - [ ] Equatorial to horizontal
  - [ ] Geographic to geocentric
- [ ] Time Calculations
  - [ ] Julian Day conversion
  - [ ] Sidereal time
  - [ ] Delta T calculations
  - [ ] Time zone conversions

## 2. API Endpoint Tests

### Authentication & Authorization
- [ ] POST /api/auth/register
  - [ ] Valid registration
  - [ ] Duplicate email/username
  - [ ] Password validation
  - [ ] Email verification
- [ ] POST /api/auth/login
  - [ ] Valid credentials
  - [ ] Invalid credentials
  - [ ] Account lockout after failed attempts
  - [ ] Rate limiting
- [ ] POST /api/auth/refresh
  - [ ] Valid refresh token
  - [ ] Invalid/expired refresh token
- [ ] POST /api/auth/logout
  - [ ] Valid session
  - [ ] Token invalidation

### Chart Endpoints
- [ ] POST /api/charts/natal
  - [ ] Valid chart creation
  - [ ] Parameter validation
  - [ ] Error handling for invalid dates/coordinates
  - [ ] Response format validation
- [ ] GET /api/charts/{id}
  - [ ] Retrieve existing chart
  - [ ] Non-existent chart ID
  - [ ] Authorization checks
- [ ] PUT /api/charts/{id}
  - [ ] Update chart data
  - [ ] Partial updates
  - [ ] Validation
- [ ] DELETE /api/charts/{id}
  - [ ] Delete chart
  - [ ] Authorization checks

### Calculation Endpoints
- [ ] POST /api/calculations/positions
  - [ ] Calculate planetary positions
  - [ ] Custom planet selection
  - [ ] Different coordinate systems
- [ ] POST /api/calculations/aspects
  - [ ] Calculate aspects
  - [ ] Custom orb settings
  - [ ] Aspect filtering
- [ ] POST /api/calculations/houses
  - [ ] Calculate houses
  - [ ] Multiple house systems
  - [ ] Extreme latitude handling
- [ ] POST /api/calculations/directions
  - [ ] Primary directions
  - [ ] Secondary progressions
  - [ ] Solar arc directions
  - [ ] Custom keys and promissors
- [ ] POST /api/calculations/returns
  - [ ] Solar returns
  - [ ] Lunar returns
  - [ ] Custom location for returns
- [ ] POST /api/calculations/transits
  - [ ] Current transits
  - [ ] Transit search
  - [ ] Transit aspects

### Rectification Endpoints
- [ ] POST /api/rectification/calculate
  - [ ] Submit rectification request
  - [ ] Event validation
  - [ ] Time window validation
- [ ] GET /api/rectification/{id}/status
  - [ ] Check calculation status
  - [ ] Progress updates
- [ ] GET /api/rectification/{id}/results
  - [ ] Retrieve results
  - [ ] Result formatting

### User Management
- [ ] GET /api/users/profile
  - [ ] Get current user profile
  - [ ] Update profile
- [ ] GET /api/users/{id}/charts
  - [ ] List user's charts
  - [ ] Pagination
  - [ ] Filtering and sorting
- [ ] PUT /api/users/settings
  - [ ] Update calculation preferences
  - [ ] Default house system
  - [ ] Orb settings

### Subscription/Credits (if applicable)
- [ ] GET /api/subscription/status
  - [ ] Check subscription status
  - [ ] Credit balance
- [ ] POST /api/subscription/upgrade
  - [ ] Upgrade subscription
  - [ ] Payment processing
- [ ] GET /api/subscription/usage
  - [ ] Usage statistics
  - [ ] API call history

## 3. Integration Tests

### Library-API Integration
- [ ] Chart creation flow
  - [ ] API request → Library calculation → API response
  - [ ] Error propagation
  - [ ] Data transformation
- [ ] Calculation caching
  - [ ] Cache hit/miss scenarios
  - [ ] Cache invalidation
- [ ] Concurrent calculations
  - [ ] Thread safety
  - [ ] Resource management

### External Service Integration
- [ ] Swiss Ephemeris
  - [ ] Ephemeris file loading
  - [ ] Fallback mechanisms
  - [ ] Error handling
- [ ] Database
  - [ ] Connection pooling
  - [ ] Transaction handling
  - [ ] Migration testing
- [ ] Cache (Redis/Memcached)
  - [ ] Connection handling
  - [ ] Serialization/deserialization
  - [ ] TTL management

## 4. Performance Tests

### Library Performance
- [ ] Calculation speed
  - [ ] Single chart < 100ms
  - [ ] Batch calculations
  - [ ] Memory usage
- [ ] Complex calculations
  - [ ] Rectification performance
  - [ ] Large date ranges
  - [ ] Multiple house systems

### API Performance
- [ ] Response times
  - [ ] Simple endpoints < 200ms
  - [ ] Complex calculations < 2s
  - [ ] Concurrent request handling
- [ ] Load testing
  - [ ] 100 concurrent users
  - [ ] 1000 requests/minute
  - [ ] Resource utilization
- [ ] Rate limiting
  - [ ] Per-user limits
  - [ ] Global limits
  - [ ] Graceful degradation

## 5. Security Tests

### Input Validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Command injection prevention
- [ ] Path traversal prevention

### Authentication & Authorization
- [ ] JWT token security
  - [ ] Token expiration
  - [ ] Token refresh
  - [ ] Token revocation
- [ ] Role-based access control
  - [ ] Admin endpoints
  - [ ] User data isolation
  - [ ] Permission checks

### API Security
- [ ] HTTPS enforcement
- [ ] CORS configuration
- [ ] Request signing (if applicable)
- [ ] API key management

### Data Protection
- [ ] Password hashing (bcrypt/argon2)
- [ ] Sensitive data encryption
- [ ] PII handling
- [ ] GDPR compliance

## 6. Error Handling & Logging

### Error Responses
- [ ] 400 Bad Request - Invalid parameters
- [ ] 401 Unauthorized - Missing/invalid auth
- [ ] 403 Forbidden - Insufficient permissions
- [ ] 404 Not Found - Resource not found
- [ ] 422 Unprocessable Entity - Validation errors
- [ ] 429 Too Many Requests - Rate limiting
- [ ] 500 Internal Server Error - Server errors
- [ ] 503 Service Unavailable - Maintenance mode

### Logging
- [ ] Request/response logging
- [ ] Error logging with stack traces
- [ ] Performance metrics
- [ ] Security event logging
- [ ] Log rotation and retention

## 7. Documentation Tests

### API Documentation
- [ ] OpenAPI/Swagger spec accuracy
- [ ] Example requests/responses
- [ ] Error response documentation
- [ ] Authentication flow documentation

### Library Documentation
- [ ] Docstring completeness
- [ ] Example code functionality
- [ ] Tutorial accuracy
- [ ] API reference generation

## 8. Deployment & Operations

### Deployment Testing
- [ ] Docker container build
- [ ] Environment variable configuration
- [ ] Database migrations
- [ ] Static file serving

### Monitoring & Health Checks
- [ ] GET /api/health
  - [ ] Database connectivity
  - [ ] Swiss Ephemeris availability
  - [ ] Cache connectivity
- [ ] GET /api/metrics
  - [ ] Prometheus metrics
  - [ ] Custom metrics
- [ ] Alerting
  - [ ] Error rate thresholds
  - [ ] Performance degradation
  - [ ] Resource exhaustion

## Test Coverage Goals

- Library Code Coverage: > 90%
- API Endpoint Coverage: 100%
- Integration Test Coverage: > 80%
- Security Test Coverage: 100%
- Performance Benchmarks: All pass

## Testing Tools

### Library Testing
- pytest
- pytest-cov
- pytest-mock
- hypothesis (property-based testing)

### API Testing
- pytest
- httpx/requests
- pytest-asyncio (if async)
- locust (load testing)

### Security Testing
- bandit (static analysis)
- safety (dependency scanning)
- OWASP ZAP (dynamic testing)