# Installation Overview

Nocturna Calculations provides a unified installation system that makes setup simple and consistent across all environments.

## Architecture

The installation system follows a **single entry point** principle:

```
make setup → Bootstrap Script → Environment Setup → Service Installation → Configuration
```

## Installation Methods

### 1. Quick Start (Recommended)
```bash
make setup
```
This is the recommended method for new users. It sets up everything automatically.

### 2. Environment-Specific Setup
```bash
make setup-dev   # Development environment
make setup-test  # Testing environment  
make setup-prod  # Production environment
```

### 3. Manual Setup
For advanced users who want more control:
```bash
python scripts/bootstrap.py --env dev --skip-services
```

## How It Works

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

### 2. Bootstrap Script
`scripts/bootstrap.py` orchestrates setup:
- Environment creation
- Service installation
- Database setup
- Configuration generation

### 3. Service Scripts
`scripts/services/` contains dedicated scripts:
- `setup_postgres.sh`: PostgreSQL management
- `setup_redis.sh`: Redis management

### 4. Environment Files
`environments/` contains Conda definitions:
- `base.yml`: Shared dependencies
- `development.yml`: Dev tools
- `testing.yml`: Test tools
- `production.yml`: Runtime only

## Benefits

1. **Simplicity**: One command to get started
2. **Consistency**: Same process on all platforms
3. **Isolation**: Clean environment separation
4. **Flexibility**: Multiple setup options
5. **Maintainability**: Single source of truth

## Migration from Old System

If you have an existing setup:

1. **Backup your data**
2. **Deactivate old environment**: `conda deactivate`
3. **Run new setup**: `make setup`
4. **Migrate configuration**: Copy `.env` settings

The old `nocturna` environment can coexist with new environments during migration.

## Troubleshooting

### Common Issues

**Q: Command 'make' not found**  
A: Install make for your platform or use the bootstrap script directly

**Q: Conda environment conflicts**  
A: Remove old environments with `conda env remove -n environment-name`

**Q: Service installation fails**  
A: Use `make services-check` to diagnose, then `make services-install`

### Getting Help

1. Check specific guides in this directory
2. Run `make help` for command reference
3. See `scripts/bootstrap.py --help` for options
4. Open a GitHub issue for bugs

## Next Steps

- [Development Setup Guide](development-setup.md)
- [Testing Setup Guide](testing-setup.md)
- [Production Deployment](../deployment/production.md) 