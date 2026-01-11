# Nocturna Calculations

A comprehensive astrological calculations library and REST API service built with Python and powered by Swiss Ephemeris.

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Setup and deploy with Docker
make docker-deploy
```

Visit http://localhost:8000/docs for API documentation.

### Option 2: Development Setup

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

## 📋 Prerequisites

### For Docker Deployment
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **2GB RAM** minimum
- **10GB disk space** minimum

### For Development Setup
- **Python 3.9+**
- **Conda** (Miniconda or Anaconda) - [Installation Guide](https://docs.conda.io/en/latest/miniconda.html)
- **Git**
- **PostgreSQL** and **Redis** (optional - will be installed automatically)

## 🐳 Docker Deployment

### Quick Docker Setup

```bash
# One-command deployment
make docker-deploy
```

This will:
- ✅ Build the Docker image
- ✅ Start PostgreSQL and Redis containers
- ✅ Run database migrations
- ✅ Setup admin user and service token
- ✅ Configure for service component mode

### Docker Commands

```bash
make docker-check         # Check Docker prerequisites
make docker-setup         # Setup environment files
make docker-build         # Build application image
make docker-up             # Start all services
make docker-down           # Stop all services
make docker-logs           # View service logs
make docker-status         # Check service status
make docker-shell          # Open shell in container
```

### Service Component Mode

Docker deployment configures Nocturna as a **service component** for integration with your main backend:

- 🚫 **Disabled user registration**
- 👤 **Admin user** for system management
- 🔑 **Service token** for API integration
- 🔒 **Production-ready security** defaults

See [Docker Deployment Guide](docs/deployment/docker.md) for complete documentation.

## 🛠️ Development Installation

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
│   │   └── routers/           # API routes including WebSocket support
│   └── models/                # Data models
├── environments/              # Conda environment definitions
├── scripts/                   # Utility scripts
│   ├── bootstrap.py          # Main setup script
│   ├── setup_production.py   # Production deployment setup
│   ├── testing/              # Testing utilities (NEW)
│   │   ├── test_with_server.py # 🚀 Integrated API testing with server management
│   │   └── run_api_tests.py  # Legacy API integration tests
│   └── services/             # Service management
├── tests/                     # Comprehensive test suite (92+ tests)
│   ├── websocket/            # 30 WebSocket tests (ConnectionManager + Router)
│   ├── unit/                 # 41 authentication unit tests
│   ├── api/                  # 21 API integration tests  
│   ├── security/             # Security and admin tests
│   └── integration/          # Database integration tests
├── docs/                      # Documentation
│   ├── testing-guide.md      # 📚 Complete testing documentation
│   ├── websockets.md         # WebSocket implementation guide
│   ├── releases/             # Release notes and documentation
│   ├── deployment/           # Deployment guides
│   ├── architecture/         # Architecture documentation
│   ├── installation/         # Installation guides
│   └── ...                   # Other documentation
├── config/                    # Configuration files
│   ├── production.env        # Production environment template
│   └── ...
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Multi-service orchestration
├── requirements.txt           # Python dependencies
├── Makefile                   # Command interface (enhanced with testing)
└── setup.py                   # Package configuration
```

## 🎯 Key Features

- **Astrological Calculations**: Comprehensive ephemeris calculations using Swiss Ephemeris
- **REST API**: Modern FastAPI-based web service
- **🆕 Stateless API**: Complete calculations without database - perfect for LLM agents
  - ✨ All features available in stateless mode (natal, synastry, transits, progressions, etc.)
  - 🤖 Optimized for AI agent function calling (ChatGPT, Claude, custom LLMs)
  - ⚡ Zero database latency - pure computational service
  - 🔧 Swiss Army knife for astrological calculations
- **WebSocket Support**: Real-time astrological calculations and data streaming
- **Docker Support**: Production-ready containerized deployment
- **Service Component**: Designed for integration with larger systems
- **Environment Management**: Separate environments for development, testing, and production
- **Database Support**: PostgreSQL with migrations (optional for stateless mode)
- **Caching**: Redis integration for performance
- **Documentation**: Auto-generated API docs
- **Comprehensive Testing**: 92+ automated tests with server management
  - ✅ **WebSocket Testing** (30 tests) - Real-time communication validation
  - ✅ **Authentication Testing** (41 tests) - Security and token management  
  - ✅ **API Integration Testing** (21 tests) - Complete HTTP endpoint validation
  - ✅ **Automatic Server Management** - Zero manual steps for testing

## 📚 Documentation

- [Quick Start Guide](docs/installation/quick-start.md)
- [Docker Deployment Guide](docs/deployment/docker.md) - **⭐ Recommended for Production**
- [Installation Overview](docs/installation/README.md)
- [API Documentation](docs/api/specification.md)
- [🆕 Stateless API Guide](docs/api/stateless-api.md) - **🤖 Perfect for LLM Agents**
- [Development Guide](docs/development/README.md)
- [Architecture Documentation](docs/architecture/)
- [Release Notes](docs/releases/)

## 🧪 Development

### Common Commands

| Command       | Description                 |
| ------------- | --------------------------- |
| `make dev`    | Start development server    |
| `make test-complete-integrated` | **🏆 Complete test suite (92+ tests) with automatic server** |
| `make test-working` | Fast comprehensive testing (71+ tests) |
| `make test-api-integrated` | API tests with automatic server management |
| `make format` | Format code with black      |
| `make lint`   | Run code quality checks     |
| `make docs`   | Build documentation         |
| `make help`   | Show all available commands |

### Docker Development Commands

| Command                    | Description                        |
| -------------------------- | ---------------------------------- |
| `make docker-deploy`       | Complete Docker deployment        |
| `make docker-up`           | Start Docker services              |
| `make docker-logs`         | View service logs                  |
| `make docker-shell`        | Open shell in API container       |
| `make docker-setup-production` | Configure production settings |

### Running Tests

**🚀 NEW: Fully Automated Testing (No Manual Steps)**

```bash
# 🏆 BEST: Complete automated test suite (92+ tests)
make test-complete-integrated    # WebSocket + Auth + API with automatic server

# ⚡ Quick comprehensive testing  
make test-working               # 71+ tests (WebSocket + Authentication)

# 🌐 API tests with automatic server management
make test-api-integrated        # 21 API tests, zero manual setup

# 🔍 Component-specific testing
make test-websocket            # 30 WebSocket tests
make test-auth                 # 41 authentication tests

# 📊 Coverage and reporting
make coverage                  # Generate coverage report
make test-summary              # Show test status overview
```

**Key Testing Features:**
- ✅ **Automatic server management** - No manual server startup needed
- ✅ **Comprehensive coverage** - 92+ tests across all components  
- ✅ **WebSocket testing** - Real-time communication validation
- ✅ **API integration testing** - Complete HTTP endpoint validation
- ✅ **Authentication testing** - Security and token management
- ✅ **Single command execution** - Everything automated

See [Complete Testing Guide](docs/testing-guide.md) for detailed testing documentation.

### Code Quality

```bash
make format        # Auto-format code
make lint          # Check code style
make type-check    # Run type checking
make security      # Run security checks
```

## 🚢 Deployment

### Production Docker Deployment (Recommended)

```bash
# Clone and setup
git clone <repository-url>
cd nocturna-calculations

# Configure environment
make docker-setup
# Edit .env with your production values

# Deploy
make docker-deploy
```

**Benefits of Docker deployment:**
- 🐳 Isolated, reproducible environment
- 🔧 Automated setup and configuration
- 📊 Built-in monitoring and health checks
- 🔒 Security best practices
- 🚀 Easy scaling and management

### Traditional Production Setup

```bash
make setup-prod
conda activate nocturna-prod
```

See [Production Deployment Guide](docs/deployment/production.md) for detailed instructions.

### Deployment Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Main     │◄──►│  Nocturna API    │    │   PostgreSQL    │
│   Backend       │    │  (Service)       │◄──►│   + Redis       │
│                 │    │  Port: 8000      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│   Frontend      │    │   Admin Panel    │
│   Application   │    │   (Optional)     │
└─────────────────┘    └──────────────────┘
```

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