# Installation Overview

Nocturna Calculations provides multiple installation options to suit different deployment scenarios, from development to production service components.

## Installation Options

Choose the installation method that best fits your use case:

### 🐳 Docker Deployment (Recommended for Production)

**Best for**: Production service components, backend integration, containerized environments

```bash
git clone <repository-url>
cd nocturna-calculations

# One-command deployment
make docker-deploy
```

**Features:**
- 🔑 **Service token authentication** for backend integration
- 🚫 **Disabled user registration** (managed by your main backend)
- 👤 **Admin access** for system management
- 📊 **Built-in monitoring** and health checks
- 🔄 **Automated token renewal** capabilities
- 🐳 **Containerized** with Docker Compose

See [Docker Deployment Guide](../deployment/docker.md) for complete instructions.

### 🛠️ Traditional Development Setup

**Best for**: Local development, library usage, customization

```bash
# Quick setup (recommended for new users)
make setup

# Environment-specific setup
make setup-dev   # Development environment
make setup-test  # Testing environment  
make setup-prod  # Production environment
```

**Features:**
- 🧪 **Full development environment** with all tools
- 📚 **Library access** for direct integration
- 🔧 **Customizable** configuration and dependencies
- 🧩 **Multiple environments** for different use cases

### 📦 Library Installation Only

**Best for**: Integrating calculations directly into your Python application

```bash
# Basic library installation
pip install nocturna-calculations

# With API server capabilities
pip install nocturna-calculations[api]
```

## Architecture Comparison

| Aspect | Docker Deployment | Traditional Setup | Library Only |
|--------|-------------------|-------------------|--------------|
| **Deployment** | Containerized service | Local development | In-process library |
| **Use Case** | Backend integration | Development/testing | Direct integration |
| **User Management** | Service tokens | Full authentication | N/A |
| **Setup Time** | 5 minutes | 10-15 minutes | 1 minute |
| **Maintenance** | Automated updates | Manual management | Dependency updates |
| **Scaling** | Container orchestration | Manual scaling | Application scaling |

## Deployment Patterns

### Pattern 1: Service Component (Docker)

```
┌─────────────────┐    API calls    ┌──────────────────┐
│   Your Main     │◄──────────────►│  Nocturna API    │
│   Backend       │  (service token) │  (Docker)       │
└─────────────────┘                 └──────────────────┘
```

**Setup:**
```bash
make docker-deploy
# Get service token from deployment_summary.json
```

### Pattern 2: Development Environment (Traditional)

```
┌─────────────────┐    Direct calls    ┌──────────────────┐
│   Development   │◄─────────────────►│  Nocturna        │
│   Application   │    (Python API)    │  (Local Install) │
└─────────────────┘                    └──────────────────┘
```

**Setup:**
```bash
make setup-dev
conda activate nocturna-dev
```

### Pattern 3: Library Integration

```
┌─────────────────┐    Import/Call    ┌──────────────────┐
│   Your          │◄────────────────►│  Nocturna        │
│   Application   │   (Python lib)    │  (Library)       │
└─────────────────┘                   └──────────────────┘
```

**Setup:**
```bash
pip install nocturna-calculations
```

## Traditional Setup Architecture

The traditional installation system follows a **single entry point** principle:

```
make setup → Bootstrap Script → Environment Setup → Service Installation → Configuration
```

### Unified Dependencies
All dependencies are defined in `setup.py` with appropriate extras:
- **Core**: Minimal dependencies for the library
- **API**: Dependencies for running the API server
- **Dev**: Development tools (includes test, docs, and performance tools)
- **Test**: Testing frameworks and tools
- **Docs**: Documentation generation tools

### Environment Management
Conda environments provide isolation:
- `nocturna-dev`: Python 3.11 with all development tools
- `nocturna-test`: Python 3.9 for compatibility testing
- `nocturna-prod`: Python 3.11 with minimal dependencies

### Service Management
Dedicated scripts handle PostgreSQL and Redis:
- Automatic detection and installation
- Cross-platform support (Linux, macOS, WSL)
- Isolated configuration

## Key Components

### 1. Makefile
The single entry point for all operations:
- Detects active environment
- Provides consistent interface
- Enforces best practices
- **Docker deployment commands**

### 2. Bootstrap Script
`scripts/bootstrap.py` orchestrates traditional setup:
- Environment creation
- Service installation
- Database setup
- Configuration generation

### 3. Docker Deployment
`docker-compose.yml` and supporting files:
- **Containerized services** (API, PostgreSQL, Redis)
- **Service token generation** and management
- **Production-ready configuration**
- **Health monitoring** and logging

### 4. Service Scripts
`scripts/services/` contains dedicated scripts:
- `setup_postgres.sh`: PostgreSQL management
- `setup_redis.sh`: Redis management
- **`renew_service_token.py`**: Token lifecycle management

### 5. Environment Files
`environments/` contains Conda definitions:
- `base.yml`: Shared dependencies
- `development.yml`: Dev tools
- `testing.yml`: Test tools
- `production.yml`: Runtime only

## Benefits

1. **Flexibility**: Multiple deployment options for different use cases
2. **Service Integration**: Built-in support for backend-to-backend communication
3. **Production Ready**: Docker deployment with monitoring and token management
4. **Development Friendly**: Full development environment with all tools
5. **Simplicity**: One command to get started with any option
6. **Consistency**: Same process on all platforms
7. **Isolation**: Clean environment separation
8. **Maintainability**: Single source of truth

## Service Token Management

When using Docker deployment, Nocturna provides **30-day service tokens** for backend authentication:

### Token Lifecycle
```bash
# Check token status
make docker-token-check

# Renew if expiring soon
make docker-token-renew

# Force renewal
make docker-token-force-renew
```

### Integration Example
```python
# Your backend integrating with Nocturna service
import requests

SERVICE_TOKEN = "your_30_day_service_token"
headers = {"Authorization": f"Bearer {SERVICE_TOKEN}"}

response = requests.post(
    "http://nocturna-api:8000/api/v1/calculations/planetary-positions",
    headers=headers,
    json=birth_data
)
```

See [Service Integration Guide](../guides/service-integration.md) for complete patterns.

## Migration from Old System

If you have an existing setup:

1. **Backup your data**
2. **Choose new deployment method**:
   - Production → Docker deployment
   - Development → Traditional setup
3. **Deactivate old environment**: `conda deactivate`
4. **Run new setup**: `make docker-deploy` or `make setup`
5. **Migrate configuration**: Copy `.env` settings

The old `nocturna` environment can coexist with new environments during migration.

## Quick Start Guide

### For Service Integration (Recommended)
```bash
# Clone and deploy as service component
git clone <repository-url>
cd nocturna-calculations
make docker-deploy

# Get service token for your backend
cat deployment_summary.json
```

### For Development
```bash
# Clone and setup development environment
git clone <repository-url>
cd nocturna-calculations
make setup-dev
conda activate nocturna-dev
```

### For Library Use
```bash
# Simple library installation
pip install nocturna-calculations

# Use in your Python code
from nocturna_calculations import Chart
```

## Troubleshooting

### Common Issues

**Q: Docker deployment fails**  
A: Check Docker prerequisites with `make docker-check`

**Q: Service token expired**  
A: Renew with `make docker-token-renew`

**Q: Command 'make' not found**  
A: Install make for your platform or use scripts directly

**Q: Conda environment conflicts**  
A: Remove old environments with `conda env remove -n environment-name`

**Q: Service installation fails**  
A: Use `make services-check` to diagnose, then `make services-install`

### Getting Help

1. Check specific guides in this directory
2. Run `make help` for command reference
3. See `scripts/bootstrap.py --help` for traditional setup options
4. Check [Docker Deployment Guide](../deployment/docker.md) for service deployment
5. Open a GitHub issue for bugs

## Next Steps

### For Service Deployment
- [Docker Deployment Guide](../deployment/docker.md) - **⭐ Complete service setup**
- [Service Integration Guide](../guides/service-integration.md) - Backend integration patterns
- [Token Management](../deployment/docker.md#token-management) - Token lifecycle

### For Development
- [Development Setup Guide](development-setup.md)
- [Testing Setup Guide](testing-setup.md)
- [Quick Start Guide](quick-start.md)

### For Production
- [Production Deployment](../deployment/README.md) - Traditional production setup
- [Best Practices](../guides/best-practices.md) - Operational guidance 