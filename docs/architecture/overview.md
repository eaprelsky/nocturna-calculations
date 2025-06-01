# Nocturna Calculations Architecture

## Overview

Nocturna Calculations is designed as a modular, extensible system that functions both as a Python library and a REST API service for astrological calculations. The architecture follows SOLID principles and is built with maintainability, extensibility, and scalability in mind.

## Architecture Layers

### 1. Core Library Layer
The foundation that provides all astrological calculation functionality:
- Direct Python API for library users
- Calculation engines and algorithms
- Swiss Ephemeris integration
- Data models and validators

### 2. Service Layer
Business logic that bridges the library and API:
- Request validation and transformation
- Result formatting and serialization
- Caching strategies
- Batch processing logic

### 3. API Layer
RESTful endpoints for remote access:
- HTTP request handling
- Authentication and authorization
- Rate limiting and usage tracking
- WebSocket support for real-time calculations

### 4. Data Layer
Persistence and caching:
- User management
- Chart storage
- Calculation cache (Redis/Memcached)
- API key management

## Core Components

### 1. Chart Class
The central class that represents an astrological chart. It contains:
- Date and time information
- Geographic coordinates
- Calculation methods
- Result caching
- Serialization methods for API responses

### 2. Calculation Modules

#### Planetary Calculations
- Position calculations
- Aspect calculations
- House system calculations
- Coordinate system transformations

#### Direction Methods
- Primary directions
- Secondary progressions
- Solar arc directions
- Transits

#### Return Methods
- Solar returns
- Lunar returns
- Progressed returns

#### Rectification Methods
- Single event rectification
- Multiple events rectification
- Result aggregation

### 3. API Modules

#### Authentication
- JWT token management
- API key validation
- Role-based access control
- Session management

#### Endpoints
- Chart management (CRUD)
- Calculation endpoints
- User management
- Subscription/usage tracking

#### Middleware
- Request logging
- Error handling
- CORS management
- Response compression

### 4. Utility Modules

#### Astronomical Calculations
- Ephemeris calculations
- Coordinate transformations
- Time calculations

#### Data Structures
- Custom types for angles, coordinates
- Result containers
- Configuration objects
- API request/response models

## Design Patterns

### Factory Pattern
Used for creating different types of calculations and charts.

### Strategy Pattern
Implemented for different calculation methods and house systems.

### Observer Pattern
Used for progress tracking and result updates.

### Builder Pattern
For constructing complex calculation configurations.

### Repository Pattern
For data access abstraction in the API layer.

### Adapter Pattern
For integrating external services (Swiss Ephemeris, databases).

## Dependencies

### Core Library
- **pyswisseph:** Swiss Ephemeris Python wrapper
- **NumPy:** Numerical computations
- **Pydantic:** Data validation

### API Service
- **FastAPI/Flask/Django:** Web framework
- **SQLAlchemy:** ORM for database operations
- **Redis:** Caching and session storage
- **Celery:** Async task processing (optional)
- **JWT:** Authentication tokens

### Development
- **Pytest:** Testing framework
- **Black:** Code formatting
- **MyPy:** Type checking

## Code Organization

```
nocturna-calculations/
├── nocturna_calculations/     # Core library
│   ├── __init__.py
│   ├── core/                  # Core calculation classes
│   ├── calculations/          # Calculation methods
│   ├── adapters/             # External service adapters
│   └── utils/                # Utility functions
├── nocturna_calculations_api/ # API service
│   ├── __init__.py
│   ├── api/                  # API endpoints
│   ├── auth/                 # Authentication
│   ├── models/               # Database models
│   ├── services/             # Business logic
│   └── middleware/           # API middleware
├── tests/
│   ├── library/              # Library tests
│   ├── api/                  # API tests
│   └── integration/          # Integration tests
└── docs/                     # Documentation
```

## Deployment Architecture

### Library Deployment
- PyPI package distribution
- Version management
- Dependency resolution

### API Deployment
- Containerized with Docker
- Kubernetes orchestration (optional)
- Load balancing
- Auto-scaling based on demand

### Infrastructure Components
- API Gateway
- Cache cluster (Redis)
- Database (PostgreSQL/MySQL)
- Message queue (for async tasks)
- Monitoring stack (Prometheus/Grafana)

## Error Handling

The system implements a comprehensive error handling strategy:

### Library Errors
- Custom exception classes
- Validation at input boundaries
- Graceful degradation
- Detailed error messages

### API Errors
- Standardized error responses
- HTTP status code mapping
- Error logging and tracking
- User-friendly error messages

## Performance Considerations

### Library Performance
- Caching of intermediate results
- Optimized algorithms for common calculations
- Parallel processing for complex operations
- Memory-efficient data structures

### API Performance
- Response caching strategies
- Database query optimization
- Connection pooling
- Async request handling
- CDN for static assets

## Security Architecture

### Library Security
- Input validation
- Safe astronomical calculations
- No external network calls (except Swiss Ephemeris data)

### API Security
- HTTPS enforcement
- Authentication (JWT/API keys)
- Authorization (RBAC)
- Rate limiting
- Input sanitization
- SQL injection prevention
- XSS protection

## Testing Strategy

### Library Tests
- Unit tests for all calculation methods
- Integration tests with Swiss Ephemeris
- Performance benchmarks
- Accuracy validation against known results

### API Tests
- Endpoint testing
- Authentication/authorization tests
- Load testing
- Security testing
- End-to-end scenarios

## Monitoring and Observability

### Metrics
- Calculation performance metrics
- API response times
- Error rates
- Resource utilization

### Logging
- Structured logging
- Log aggregation
- Error tracking
- Audit trails

### Health Checks
- Library functionality checks
- API endpoint health
- Database connectivity
- External service availability

For detailed API documentation, see the [API Reference](../api/reference.md) and [API Endpoints](./api-endpoints.md). 