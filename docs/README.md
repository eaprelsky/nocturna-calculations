# Nocturna Calculations

An open-source Python library and REST API service for astrological calculations.

## Overview

Nocturna Calculations is a comprehensive solution for performing various astrological calculations, available both as a Python library for direct integration and as a REST API service for remote access. It includes:

### Calculation Features
- Planetary positions and aspects
- Primary directions
- Secondary progressions
- Solar arc directions
- Transits
- Solar and Lunar returns
- Progressed charts
- Lunar node calculations
- Rectification methods

### Service Features
- RESTful API endpoints
- User authentication & authorization
- Chart storage and management
- Batch processing
- Real-time calculations via WebSocket
- API key management
- Usage tracking and analytics
- **Service component mode** for backend integration
- **Comprehensive testing infrastructure** (92+ automated tests)

## Core Features

- High-precision astronomical calculations using Swiss Ephemeris
- Support for multiple calculation methods and house systems
- **Multiple deployment options**: library, API service, or containerized service component
- **Service token authentication** for backend-to-backend integration
- Extensible architecture for adding new methods
- **Production-ready testing**: 92+ automated tests with server management
- **WebSocket support**: Real-time calculations and data streaming
- Well-documented interfaces
- Production-ready with monitoring and health checks
- **Automated token management** for service deployments

## Installation & Deployment

For detailed installation instructions, please refer to the [Installation Guide](installation/README.md).

### As a Python Library

```bash
pip install nocturna-calculations
```

### As an API Service (Traditional)

```bash
# Clone and setup with make
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Setup development environment
make setup-dev
conda activate nocturna-dev

# Start the API server
make dev
```

**Traditional Setup Features:**
- 🧪 **Full development environment** with all tools
- 📚 **Library access** for direct integration  
- 🔧 **Customizable** configuration and dependencies
- 🧩 **Multiple environments** for different use cases

See [Installation Guide](installation/README.md) for detailed setup options.

### As a Service Component (Docker - Recommended)

```bash
# Clone and deploy with Docker
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# One-command deployment
make docker-deploy
```

**Service Component Features:**
- 🐳 **Containerized deployment** with Docker Compose
- 🔑 **Service token authentication** for backend integration
- 🚫 **Disabled user registration** (managed by your main backend)
- 👤 **Admin access** for system management
- 📊 **Built-in monitoring** and health checks
- 🔄 **Automated token renewal** capabilities

See [Docker Deployment Guide](deployment/docker.md) for complete instructions.

## Quick Start

### Library Usage

```python
from nocturna_calculations import Chart

# Create a new chart
chart = Chart(
    date="2024-03-20",
    time="12:00:00",
    latitude=55.7558,
    longitude=37.6173
)

# Calculate planetary positions
positions = chart.calculate_planetary_positions()

# Calculate aspects
aspects = chart.calculate_aspects()
```

### API Usage (Direct)

```python
import requests

# API endpoint
url = "http://localhost:8000/api/charts/natal"

# Request data
data = {
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173
}

# Make request with user token
response = requests.post(
    url,
    json=data,
    headers={"Authorization": "Bearer YOUR_USER_TOKEN"}
)

# Get results
chart_data = response.json()
```

### Service Integration (Backend-to-Backend)

```python
import requests

# Your main backend integrating with Nocturna service
class NocturnaClient:
    def __init__(self, api_url, service_token):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {service_token}",
            "Content-Type": "application/json"
        }
    
    def calculate_positions(self, chart_data):
        response = requests.post(
            f"{self.api_url}/api/v1/calculations/planetary-positions",
            headers=self.headers,
            json=chart_data
        )
        return response.json()

# Usage
client = NocturnaClient(
    api_url="http://nocturna-api:8000",
    service_token="your_30_day_service_token"
)

result = client.calculate_positions({
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173
})
```

## Documentation

For detailed documentation, please refer to the following sections:

### Testing & Quality Assurance
- **[Complete Testing Guide](testing-guide.md)** - **⭐ 92+ automated tests with server management**
- [API Testing Guide](development/testing-api.md) - Automated API testing with zero manual steps
- [WebSocket Testing](websockets.md) - Real-time communication testing

### Library Documentation
- [Architecture Overview](architecture/overview.md)
- [API Reference](api/reference.md)
- [Calculation Methods](reference/calculation-methods.md)
- [Rectification](reference/rectification.md)

### API Documentation
- [API Specification](api/specification.md)
- **[Service Token Management Guide](guides/service-token-management.md)** - Complete service token setup and usage
- **[Service Integration Guide](guides/service-integration.md)** - Backend integration with service tokens
- **[Synastry & Transit Guide](guides/synastry-transit-guide.md)** - Relationship compatibility and transit calculations

### Deployment & Operations
- **[Docker Deployment Guide](deployment/docker.md)** - **⭐ Recommended for Production**
- [Traditional Deployment Guide](deployment/README.md)
- [Token Management Guide](deployment/docker.md#token-management)

### Installation & Setup
- [Installation Guide](installation/README.md)
- [Quick Start](installation/quick-start.md)
- [Development Setup](installation/development-setup.md)
- [Testing Setup](installation/testing-setup.md)
- [Installation Flow](architecture/installation-flow.md)

### Operational Guides
- [Best Practices](guides/best-practices.md)
- [Troubleshooting](guides/troubleshooting.md)
- [Advanced Usage](guides/advanced-usage.md)
- **[Service Integration](guides/service-integration.md)** - Backend integration patterns

### Development
- [Contributing Guide](../CONTRIBUTING.md)

## Service Architecture Options

### Option 1: Standalone Library
Use Nocturna as a Python library directly in your application.

### Option 2: API Service
Deploy Nocturna as a REST API for multiple client applications.

### Option 3: Service Component (Recommended)
Deploy Nocturna as a **service component** that integrates with your main backend:

```
┌─────────────────┐    API calls    ┌──────────────────┐
│   Your Main     │◄──────────────►│  Nocturna API    │
│   Backend       │  (service token) │  (Calculations) │
│                 │                 │                  │
└─────────────────┘                 └──────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌──────────────────┐
│   Frontend      │                 │  PostgreSQL +    │
│   Application   │                 │  Redis           │
└─────────────────┘                 └──────────────────┘
```

**Benefits:**
- **Separation of concerns** - your backend handles users, Nocturna handles calculations
- **Scalable** - can be deployed independently
- **Secure** - service token authentication
- **Maintainable** - clear API boundaries

## Token Management

When deployed as a service component, Nocturna uses **JWT service tokens** for backend authentication:

### Checking Token Status
```bash
make docker-token-check
```

### Renewing Tokens
```bash
# Automatic renewal (if expiring within 7 days)
make docker-token-renew

# Force renewal
make docker-token-force-renew

# Eternal token (for lazy admins with nginx protection!)
make docker-token-eternal

# Custom duration token
make docker-token-custom DAYS=365
```

### For Lazy Admins 😴
Generate **eternal tokens** that never expire (perfect for internal deployments):
```bash
make docker-token-eternal
```
**Requirements**: Nginx reverse proxy + firewall protection to block external access.

### Integration Monitoring
```python
# Monitor token expiration in your backend
def check_nocturna_token_health():
    days_left = check_token_expiration(SERVICE_TOKEN)
    if days_left is None:  # Eternal token
        return "♾️ Eternal token - no concerns!"
    elif days_left < 7:
        send_alert("Nocturna token expires soon!")
```

See [Token Management Guide](deployment/docker.md#token-management) for complete details.

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details. 