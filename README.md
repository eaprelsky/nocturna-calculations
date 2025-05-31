# Nocturna Calculations

A Python library and REST API service for astrological calculations based on Swiss Ephemeris. This project provides both a comprehensive library for direct Python integration and a production-ready API server for remote access to astrological calculation services.

THIS PROJECT IS YET UNDER ACTIVE DEVELOPMENT, THE DOCUMENTATION MAY NOT REFLECT THE ACTUAL STATE OF THE CODEBASE

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

## Quick Start

### Environment Management

This project uses **three separate conda environments** for different purposes:

- **`nocturna-dev`** (Python 3.11): Development work, debugging, feature development
- **`nocturna-test`** (Python 3.9): Testing, benchmarking, compatibility testing  
- **`nocturna-prod`** (Python 3.11): Production deployment, minimal dependencies

### For Developers
```bash
# Clone and setup development environment
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations
make setup-dev

# Activate environment and complete setup
conda activate nocturna-dev
python scripts/install_dev.py

# Start development server
make dev-server
```

### For Testers/QA
```bash
# Setup testing environment
make setup-test

# Activate environment and run tests
conda activate nocturna-test
make test

# Run benchmarks
make benchmark
```

### For Production Deployment
```bash
# Setup production environment
make setup-prod

# Activate environment
conda activate nocturna-prod
```

## Installation Options

| Method | Use Case | Command |
|--------|----------|---------|
| **Development** | Feature development, debugging | `make setup-dev` |
| **Testing** | Running tests, benchmarks | `make setup-test` |
| **Production** | Deployment, production use | `make setup-prod` |

See the [Installation Guide](docs/installation/README.md) for detailed setup instructions.

## Environment Switching

```bash
# List available environments
make list-env

# Switch between environments
make switch-env ENV=dev    # Development
make switch-env ENV=test   # Testing  
make switch-env ENV=prod   # Production

# Validate current environment
make validate-env
```

## Quick Commands

```bash
# Environment management
make setup-dev          # Setup development environment
make setup-test         # Setup testing environment  
make setup-prod         # Setup production environment

# Development
make dev-server         # Start development server
make jupyter            # Start Jupyter Lab
make dev-shell          # Interactive Python shell

# Testing
make test              # Run full test suite
make test-quick        # Quick unit tests
make benchmark         # Performance benchmarks

# Code quality
make lint              # Code formatting and linting
make type-check        # Type checking
make security          # Security scanning
make quality           # All quality checks

# Database
make db-setup          # Setup database
make db-migrate        # Run migrations
make db-status         # Check database status

# Maintenance
make clean             # Clean build artifacts
make update-deps       # Update dependencies
make health-check      # System health check
```

## Library Usage

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

## API Usage

```bash
# Start the API server
make dev-server

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

Comprehensive documentation is available in the `docs/` directory:

- **[Installation Guide](docs/installation/README.md)** - Setup for different environments
- **[Development Guide](docs/development/README.md)** - Development workflow and tools
- **[API Documentation](docs/api/README.md)** - REST API reference
- **[Environment Management](environments/README.md)** - Conda environment details

### Online Documentation
- [API Reference (OpenAPI)](http://localhost:8000/docs) (when running locally)
- [ReadTheDocs](https://nocturna-calculations.readthedocs.io/) (if available)

## Contributing

We welcome contributions! See our [Contributing Guide](docs/development/contributing-guide.md) for details.

### Development Workflow

```bash
# 1. Setup development environment
make setup-dev
conda activate nocturna-dev

# 2. Complete database setup
python scripts/install_dev.py

# 3. Run tests before making changes
make test-quick

# 4. Make your changes
# ... edit code ...

# 5. Run quality checks
make quality

# 6. Run tests
make test

# 7. Submit pull request
```

### Testing

```bash
# Switch to testing environment
conda activate nocturna-test

# Run specific test types
make test-unit          # Unit tests
make test-integration   # Integration tests
make test-api          # API tests
make benchmark         # Performance benchmarks

# Code quality
make lint              # Formatting and style
make type-check        # Type checking
make security          # Security scanning
```

## Project Structure

```
nocturna-calculations/
├── environments/           # Conda environment definitions
│   ├── development.yml    # Development environment
│   ├── testing.yml        # Testing environment
│   ├── production.yml     # Production environment
│   └── README.md          # Environment documentation
├── docs/                  # Documentation
│   ├── installation/      # Installation guides
│   ├── development/       # Development guides
│   └── api/               # API documentation
├── scripts/               # Installation and utility scripts
│   └── environments/      # Environment management scripts
├── nocturna_calculations/ # Main package
├── tests/                 # Test suite
├── Makefile              # Development automation
└── README.md             # This file
```

## System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL
- **Conda**: Miniconda or Anaconda installed
- **Database**: PostgreSQL (auto-installed in development)
- **Cache**: Redis (auto-installed in development)
- **Hardware**: 4GB+ RAM, 2GB+ storage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- Author: Yegor Aprelsky
- Email: yegor.aprelsky@gmail.com
- GitHub: [eaprelsky](https://github.com/eaprelsky)

## Help

```bash
# Get help with available commands
make help

# Check system health
make health-check

# Validate current environment
make validate-env

# List all environments
make list-env
```

For detailed troubleshooting, see the [Installation Troubleshooting Guide](docs/installation/troubleshooting.md). 