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

## Core Features

- High-precision astronomical calculations using Swiss Ephemeris
- Support for multiple calculation methods and house systems
- Dual deployment options (library or API service)
- Extensible architecture for adding new methods
- Comprehensive test coverage for both library and API
- Well-documented interfaces
- Production-ready with monitoring and health checks

## Installation

### As a Python Library

```bash
pip install nocturna-calculations
```

### As an API Service

```bash
# Clone and install with API dependencies
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations
pip install -e ".[api]"

# Run the API server
python -m nocturna_calculations.api
```

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

### API Usage

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

# Make request
response = requests.post(
    url,
    json=data,
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)

# Get results
chart_data = response.json()
```

## Documentation

For detailed documentation, please refer to the following sections:

### Library Documentation
- [Architecture](architecture.md)
- [API Reference](api-reference.md)
- [Calculation Methods](calculation-methods.md)
- [Rectification](rectification.md)

### API Documentation
- [API Endpoints](api-endpoints.md)
- [Authentication](api-authentication.md)
- [Rate Limiting](api-rate-limiting.md)
- [WebSocket Interface](api-websocket.md)

### Development
- [Contributing Guide](../CONTRIBUTING.md)
- [Testing Guide](testing-guide.md)
- [Deployment Guide](deployment-guide.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details. 