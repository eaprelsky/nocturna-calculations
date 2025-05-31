# Development Environment Setup

This guide covers setting up the Nocturna Calculations project for **development work**, including feature development, debugging, and code exploration.

## Overview

The development environment (`nocturna-dev`) includes:
- Python 3.11 (latest stable)
- Full development toolchain
- Interactive development tools (Jupyter, IPython)
- Database and caching services
- Debugging and profiling tools
- Documentation generation tools

## Quick Setup

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Setup development environment
make setup-dev

# Activate environment
conda activate nocturna-dev
```

### Manual Setup
```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Create conda environment
conda env create -f environments/development.yml

# Activate environment
conda activate nocturna-dev

# Setup database and services
python scripts/install_dev.py
```

## Detailed Installation Steps

### 1. Prerequisites Check
```bash
# Verify conda installation
conda --version

# Verify git installation
git --version

# Check available disk space (need ~2GB)
df -h .
```

### 2. Environment Creation
```bash
# Create development environment
conda env create -f environments/development.yml

# Verify environment creation
conda env list | grep nocturna-dev
```

### 3. Environment Activation
```bash
# Activate development environment
conda activate nocturna-dev

# Verify activation
which python
python --version  # Should show Python 3.11.x
```

### 4. Database and Services Setup
The development environment requires PostgreSQL and Redis:

```bash
# Run automated setup (WSL/Linux)
python scripts/install_dev.py

# Follow prompts for:
# - Database name (default: nocturna)
# - Database user (default: postgres)  
# - Database password (required)
# - Database host (default: localhost)
# - Database port (default: 5432)
```

### 5. Environment Configuration
The setup creates a `.env` file with your configuration:

```bash
# View generated configuration
cat .env

# Example .env content:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/nocturna
# API_VERSION_PREFIX=/v1
# PROJECT_NAME=Nocturna Calculations
# SECRET_KEY=dev_secret_key_change_in_production
# REDIS_URL=redis://localhost:6379/0
```

### 6. Installation Verification
```bash
# Check database connection
./scripts/setup_db.sh status

# Verify Redis connection
redis-cli ping

# Test application startup
python -m nocturna_calculations.api.app --check-config
```

## Development Tools

### Jupyter Notebooks
```bash
# Start Jupyter Lab
jupyter lab

# Start classic Jupyter Notebook
jupyter notebook

# Available at: http://localhost:8888
```

### Interactive Python Shell
```bash
# Enhanced IPython shell
ipython

# With automatic reloading
ipython --autocall=2 --automagic
```

### Development Server
```bash
# Start development server with auto-reload
make dev-server

# Or manually:
uvicorn nocturna_calculations.api:app --reload --host 0.0.0.0 --port 8000

# API available at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

### Code Quality Tools
```bash
# Format code
black .

# Check code style
flake8

# Type checking
mypy nocturna_calculations/

# Sort imports
isort .

# Run all quality checks
make lint
```

### Debugging Tools
```bash
# Enhanced debugger (pdb++)
python -m pdb++ your_script.py

# Memory profiling
python -m memory_profiler your_script.py

# Line-by-line profiling
kernprof -l -v your_script.py
```

## Database Management

### Initial Setup
```bash
# Initialize database
alembic upgrade head

# Create test data (optional)
python scripts/create_test_data.py
```

### Database Operations
```bash
# Check database status
./scripts/setup_db.sh status

# Reset database
./scripts/setup_db.sh reset

# Backup database
./scripts/setup_db.sh backup

# Restore database
./scripts/setup_db.sh restore backup_file.sql
```

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current

# Migration history
alembic history
```

## Development Workflow

### Daily Development
```bash
# 1. Activate environment
conda activate nocturna-dev

# 2. Update dependencies (if needed)
conda env update -f environments/development.yml

# 3. Start services
make dev-server &

# 4. Open development tools
jupyter lab &

# 5. Start coding!
code .  # VS Code
# or
vim .   # Vim
```

### Testing During Development
```bash
# Quick test run
pytest tests/unit/ -v

# Test with coverage
pytest --cov=nocturna_calculations

# Test specific module
pytest tests/unit/test_calculations.py -v

# Run in parallel
pytest -n auto
```

### Code Quality Checks
```bash
# Before committing
make lint          # Code formatting and linting
make type-check    # Type checking
make security      # Security scanning
make test-quick    # Fast test suite
```

## IDE Configuration

### VS Code
Recommended extensions:
- Python
- Pylance
- Black Formatter
- Flake8
- Jupyter

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "~/miniconda3/envs/nocturna-dev/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true
}
```

### PyCharm
1. Configure interpreter: `~/miniconda3/envs/nocturna-dev/bin/python`
2. Enable pytest as test runner
3. Configure Black as formatter
4. Enable Flake8 as linter

## Performance Monitoring

### Application Performance
```bash
# Profile API endpoints
python scripts/profile_api.py

# Memory usage monitoring
python scripts/monitor_memory.py

# Database query profiling
python scripts/profile_queries.py
```

### System Monitoring
```bash
# Monitor resource usage
htop

# Database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Redis monitoring
redis-cli monitor
```

## Troubleshooting

### Common Issues

1. **Environment activation fails**:
   ```bash
   # Verify conda installation
   conda info
   
   # Refresh shell
   conda init
   source ~/.bashrc
   ```

2. **Database connection errors**:
   ```bash
   # Check PostgreSQL status
   sudo service postgresql status
   
   # Restart PostgreSQL
   sudo service postgresql restart
   
   # Test connection
   psql -h localhost -U postgres -d nocturna
   ```

3. **Redis connection errors**:
   ```bash
   # Check Redis status
   sudo service redis-server status
   
   # Restart Redis
   sudo service redis-server restart
   
   # Test connection
   redis-cli ping
   ```

4. **Package conflicts**:
   ```bash
   # Clean environment
   conda env remove -n nocturna-dev
   conda clean --all
   
   # Recreate environment
   conda env create -f environments/development.yml
   ```

### Getting Help

1. **Check logs**:
   ```bash
   # Application logs
   tail -f logs/app.log
   
   # Database logs
   tail -f /var/log/postgresql/postgresql-*.log
   
   # Redis logs
   tail -f /var/log/redis/redis-server.log
   ```

2. **Validate environment**:
   ```bash
   ./scripts/environments/validate_environment.py
   ```

3. **Health check**:
   ```bash
   make health-check
   ```

## Next Steps

After successful setup:

1. **Read the code**: Start with `nocturna_calculations/core/`
2. **Run examples**: Check `examples/` directory
3. **Write tests**: Add tests in `tests/unit/`
4. **Documentation**: Read `docs/development/`
5. **Contributing**: Review `docs/development/contributing-guide.md`

## Environment Maintenance

### Regular Updates
```bash
# Update conda
conda update conda

# Update environment
conda env update -f environments/development.yml --prune

# Update pre-commit hooks
pre-commit autoupdate
```

### Cleanup
```bash
# Clean conda cache
conda clean --all

# Clean Python cache
find . -type d -name __pycache__ -delete

# Clean test artifacts
rm -rf .pytest_cache htmlcov .coverage
``` 