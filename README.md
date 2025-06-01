# Nocturna Calculations

A comprehensive astrological calculations library and REST API service built with Python and powered by Swiss Ephemeris.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Run complete setup (recommended)
make setup

# Activate the environment
conda activate nocturna-dev

# Start the development server
make dev
```

Visit http://localhost:8000/docs for API documentation.

## 📋 Prerequisites

- **Python 3.9+**
- **Conda** (Miniconda or Anaconda) - [Installation Guide](https://docs.conda.io/en/latest/miniconda.html)
- **Git**
- **PostgreSQL** and **Redis** (optional - will be installed automatically)

## 🛠️ Installation

### One-Command Setup (Recommended)

```bash
make setup
```

This command will:

- ✅ Create a development environment with all dependencies
- ✅ Install and configure PostgreSQL and Redis
- ✅ Setup the database and run migrations
- ✅ Generate configuration files

### Environment-Specific Setup

```bash
make setup-dev   # Development environment
make setup-test  # Testing environment
make setup-prod  # Production environment
```

### Manual Setup

For more control over the installation process:

```bash
python scripts/bootstrap.py --help
```

See [Installation Guide](docs/installation/README.md) for detailed instructions.

## 🏗️ Project Structure

```
nocturna-calculations/
├── nocturna_calculations/     # Core library package
│   ├── core/                  # Core calculations
│   ├── api/                   # FastAPI application
│   └── models/                # Data models
├── environments/              # Conda environment definitions
├── scripts/                   # Utility scripts
│   ├── bootstrap.py          # Main setup script
│   ├── testing/              # Testing utilities
│   │   ├── run_api_tests.py  # API integration tests
│   │   └── run_tests.sh      # Comprehensive test runner
│   └── services/             # Service management
├── tests/                     # Test suite
├── docs/                      # Documentation
│   ├── releases/             # Release notes and documentation
│   ├── architecture/         # Architecture documentation
│   ├── installation/         # Installation guides
│   └── ...                   # Other documentation
├── Makefile                   # Command interface
└── setup.py                   # Package configuration
```

## 🎯 Key Features

- **Astrological Calculations**: Comprehensive ephemeris calculations using Swiss Ephemeris
- **REST API**: Modern FastAPI-based web service
- **Environment Management**: Separate environments for development, testing, and production
- **Database Support**: PostgreSQL with migrations
- **Caching**: Redis integration for performance
- **Documentation**: Auto-generated API docs
- **Testing**: Comprehensive test suite with pytest

## 📚 Documentation

- [Quick Start Guide](docs/installation/quick-start.md)
- [Installation Overview](docs/installation/README.md)
- [API Documentation](docs/api/specification.md)
- [Development Guide](docs/development/README.md)
- [Architecture Documentation](docs/architecture/)
- [Release Notes](docs/releases/)

## 🧪 Development

### Common Commands

| Command       | Description                 |
| ------------- | --------------------------- |
| `make dev`    | Start development server    |
| `make test`   | Run test suite              |
| `make format` | Format code with black      |
| `make lint`   | Run code quality checks     |
| `make docs`   | Build documentation         |
| `make help`   | Show all available commands |

### Running Tests

```bash
make test          # Run all tests
make test-unit     # Run unit tests only
make test-api      # Run API tests only
make coverage      # Generate coverage report
```

### Code Quality

```bash
make format        # Auto-format code
make lint          # Check code style
make type-check    # Run type checking
make security      # Run security checks
```

## 🚢 Deployment

### Production Setup

```bash
make setup-prod
conda activate nocturna-prod
```

See [Production Deployment Guide](docs/deployment/production.md) for detailed instructions.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Swiss Ephemeris](https://www.astro.com/swisseph/) for astronomical calculations
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## 📞 Support

- 📧 Email: yegor.aprelsky@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/eaprelsky/nocturna-calculations/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/eaprelsky/nocturna-calculations/discussions)

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes and version history.

For comprehensive release documentation, visit [docs/releases/](docs/releases/).

---

Built with ❤️ by the Nocturna team 