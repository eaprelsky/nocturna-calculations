# Nocturna Calculations

A Python library and REST API service for astrological calculations based on Swiss Ephemeris. This project provides both a comprehensive library for direct Python integration and a production-ready API server for remote access to astrological calculation services.

## Features

### Library Features
- Natal chart calculations
- Planetary positions and movements
- House system calculations (Placidus, Koch, etc.)
- Aspect calculations
- Primary and secondary progressions
- Solar and lunar returns
- Eclipse calculations
- Chart rectification
- And more...

### API Features
- RESTful endpoints for all calculation methods
- User authentication and authorization
- Chart storage and management
- Batch calculations
- WebSocket support for real-time calculations
- Rate limiting and usage tracking
- API key management

## Installation

### As a Python Library

```bash
pip install nocturna-calculations
```

### As an API Server

```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Install with API dependencies
pip install -e ".[api]"

# Run the API server
python -m nocturna_calculations.api
```

## Quick Start

### Library Usage

```python
from nocturna_calculations import ChartCalculator
from nocturna_calculations.adapters import SwissEphAdapter

# Create calculator instance
calculator = ChartCalculator(adapter=SwissEphAdapter())

# Calculate natal chart
chart = calculator.calculate_natal_chart(
    date="2024-03-20",
    time="12:00:00",
    latitude=55.7558,
    longitude=37.6173
)

# Get planetary positions
planets = chart.get_planetary_positions()

# Calculate aspects
aspects = chart.calculate_aspects()
```

### API Usage

```bash
# Start the API server
python -m nocturna_calculations.api

# Make API requests
curl -X POST http://localhost:8000/api/charts/natal \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173
  }'
```

## Documentation

Full documentation is available at [ReadTheDocs](https://nocturna-calculations.readthedocs.io/).

- [Library Documentation](https://nocturna-calculations.readthedocs.io/en/latest/library/)
- [API Documentation](https://nocturna-calculations.readthedocs.io/en/latest/api/)
- [API Reference (OpenAPI)](http://localhost:8000/docs) (when running locally)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and more.

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install API development dependencies
pip install -r requirements-api-dev.txt

# Run tests
pytest

# Run API tests
pytest tests/api/

# Run the development server
uvicorn nocturna_calculations.api:app --reload
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- Author: Yegor Aprelsky
- Email: yegor.aprelsky@gmail.com
- GitHub: [eaprelsky](https://github.com/eaprelsky) 