# Environment Management Guide

This guide provides comprehensive information about managing conda environments in the Nocturna Calculations project.

## Overview

The Nocturna Calculations project uses **three separate conda environments** to support different phases of the development lifecycle:

| Environment | Name | Python | Purpose |
|-------------|------|--------|---------|
| **Development** | `nocturna-dev` | 3.11 | Daily development, debugging, feature development |
| **Testing** | `nocturna-test` | 3.9 | Testing, benchmarking, compatibility testing |
| **Production** | `nocturna-prod` | 3.11 | Production deployment, minimal dependencies |

## Why Multiple Environments?

### Isolation Benefits
- **Dependency separation**: Different environments can have different versions of packages
- **Testing isolation**: Test environment ensures compatibility across Python versions
- **Production safety**: Production environment has minimal dependencies to reduce attack surface
- **Development freedom**: Development environment includes all tools and debug packages

### Workflow Benefits
- **Clear separation of concerns**: Each environment serves a specific purpose
- **Reproducible builds**: Environment files ensure consistent setups across machines
- **Easy switching**: Automated tools make switching between environments seamless
- **Parallel work**: Team members can work on different aspects simultaneously

## Environment Details

### Development Environment (`nocturna-dev`)

**File**: `environments/development.yml`
**Python Version**: 3.11 (latest stable)

**Purpose**: 
- Daily development work
- Interactive debugging
- Feature prototyping
- Code exploration

**Key Dependencies**:
- **Development Tools**: IPython, Jupyter, pdb++
- **Code Quality**: Black, Flake8, MyPy, isort
- **Debugging**: Memory profiler, line profiler
- **Database/Cache**: PostgreSQL, Redis clients
- **Web Framework**: FastAPI, Uvicorn with debugging features

**When to Use**:
- Writing new features
- Debugging issues
- Interactive development sessions
- Proof-of-concept development

### Testing Environment (`nocturna-test`)

**File**: `environments/testing.yml`
**Python Version**: 3.9 (for compatibility testing)

**Purpose**:
- Running comprehensive test suites
- Performance benchmarking
- Security testing
- Compatibility verification
- Code quality checking

**Key Dependencies**:
- **Testing Frameworks**: pytest, hypothesis, pytest-xdist
- **Performance Testing**: pytest-benchmark, locust
- **Security Testing**: bandit, safety
- **Code Coverage**: pytest-cov
- **Quality Assurance**: All linting and formatting tools

**When to Use**:
- Running unit tests
- Performance benchmarking
- Security audits
- Pre-commit validation
- CI/CD pipeline testing

### Production Environment (`nocturna-prod`)

**File**: `environments/production.yml`
**Python Version**: 3.11 (optimal performance)

**Purpose**:
- Production deployments
- Docker containers
- Performance-critical applications
- Security-sensitive environments

**Key Dependencies**:
- **Runtime Only**: Minimal set of packages needed to run the application
- **Web Server**: Gunicorn for production serving
- **Core Libraries**: Only essential calculation and API packages
- **No Development Tools**: No debugging, testing, or development packages

**When to Use**:
- Production deployments
- Docker container builds
- Performance testing under production conditions
- Security validation

## Environment Setup

### Quick Setup

```bash
# Development environment
make setup-dev
conda activate nocturna-dev

# Testing environment  
make setup-test
conda activate nocturna-test

# Production environment
make setup-prod
conda activate nocturna-prod
```

### Manual Setup

```bash
# Create environments from YAML files
conda env create -f environments/development.yml
conda env create -f environments/testing.yml
conda env create -f environments/production.yml

# Activate specific environment
conda activate nocturna-dev
```

### Verification

```bash
# Verify environment setup
make validate-env

# Or manually check
python --version
conda list
```

## Environment Switching

### Using Make Commands

```bash
# List available environments
make list-env

# Switch to development
make switch-env ENV=dev

# Switch to testing
make switch-env ENV=test

# Switch to production
make switch-env ENV=prod
```

### Using Switch Script

```bash
# Interactive environment information
./scripts/environments/switch_environment.py

# Switch to specific environment
./scripts/environments/switch_environment.py --env dev

# List all environments
./scripts/environments/switch_environment.py --list

# Validate environment
./scripts/environments/switch_environment.py --validate dev
```

### Manual Switching

```bash
# Deactivate current environment
conda deactivate

# Activate target environment
conda activate nocturna-dev  # or nocturna-test, nocturna-prod
```

## Development Workflows

### Daily Development Workflow

```bash
# 1. Activate development environment
conda activate nocturna-dev

# 2. Update if needed
make update-deps

# 3. Start development server
make dev-server

# 4. Work in another terminal with Jupyter
make jupyter

# 5. Run quick tests during development
make test-quick
```

### Testing Workflow

```bash
# 1. Switch to testing environment
conda activate nocturna-test

# 2. Run full test suite
make test

# 3. Run benchmarks
make benchmark

# 4. Check code quality
make quality

# 5. Security testing
make security
```

### Pre-Deployment Workflow

```bash
# 1. Test in production-like environment
conda activate nocturna-prod

# 2. Install package
make install

# 3. Run production checks
make health-check

# 4. Test API endpoints
# (manual testing or automated production tests)
```

## Environment Maintenance

### Regular Updates

```bash
# Update specific environment (activate first)
conda activate nocturna-dev
make update-deps

# Or update environment file and recreate
conda env update -f environments/development.yml --prune
```

### Adding Dependencies

1. **Identify target environments**: Which environments need the new dependency?
2. **Update YAML files**: Add dependency to appropriate environment files
3. **Test locally**: Update and test the environment
4. **Document changes**: Update this guide if needed

#### Example: Adding a new calculation library

```yaml
# Add to environments/development.yml
- pip:
  - new-astro-library>=1.0.0

# Add to environments/testing.yml (if testing is needed)
- pip:
  - new-astro-library>=1.0.0

# Add to environments/production.yml (if runtime dependency)
- pip:
  - new-astro-library>=1.0.0
```

### Version Management

```bash
# Check current versions
conda list

# Export current environment
conda env export > current-env.yml

# Compare with environment file
diff current-env.yml environments/development.yml
```

### Cleanup

```bash
# Clean specific environment
conda activate nocturna-dev
conda clean --all

# Remove and recreate environment
conda env remove -n nocturna-dev
conda env create -f environments/development.yml

# Clean all environments
make clean-env
```

## Troubleshooting

### Common Issues

1. **Environment doesn't exist**:
   ```bash
   # Create it
   make setup-dev  # or setup-test, setup-prod
   ```

2. **Package conflicts**:
   ```bash
   # Clean and recreate
   conda env remove -n nocturna-dev
   conda clean --all
   conda env create -f environments/development.yml
   ```

3. **Slow environment creation**:
   ```bash
   # Use libmamba solver (faster)
   conda install -n base conda-libmamba-solver
   conda config --set solver libmamba
   ```

4. **Permission issues**:
   ```bash
   # Check conda permissions
   conda info
   
   # Fix ownership if needed
   sudo chown -R $USER:$USER ~/miniconda3/
   ```

5. **Environment activation fails**:
   ```bash
   # Reinitialize conda
   conda init
   source ~/.bashrc
   ```

### Validation

```bash
# Validate environment setup
./scripts/environments/validate_environment.py

# Check environment health
make health-check

# Verify Python version and key packages
python --version
python -c "import nocturna_calculations; print('Package available')"
```

### Performance Issues

1. **Slow package installation**:
   - Use `mamba` instead of `conda`
   - Use `conda-libmamba-solver`
   - Clean conda cache regularly

2. **Large environment size**:
   - Review dependencies in YAML files
   - Remove unused packages
   - Use production environment for deployments

## Best Practices

### Environment Hygiene

1. **Always use environment files**: Don't install packages manually
2. **Keep environments clean**: Remove unused packages
3. **Regular updates**: Keep dependencies current
4. **Version pinning**: Pin critical package versions
5. **Documentation**: Document environment changes

### Development Practices

1. **Use appropriate environment**: Development for coding, testing for validation
2. **Switch environments**: Don't mix purposes
3. **Validate changes**: Test in appropriate environments
4. **Clean transitions**: Deactivate before switching
5. **Monitor resources**: Large environments can consume disk space

### Team Collaboration

1. **Commit environment files**: Always version control YAML files
2. **Document changes**: Update this guide when making environment changes
3. **Test across environments**: Ensure compatibility
4. **Share knowledge**: Train team members on environment management
5. **Consistent setups**: Use automated setup commands

## Advanced Topics

### Custom Environment Variables

```bash
# Set environment-specific variables
export NOCTURNA_ENV=development
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Environment-Specific Configuration

```python
# In your code
import os

if os.getenv('CONDA_DEFAULT_ENV') == 'nocturna-dev':
    # Development-specific settings
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
elif os.getenv('CONDA_DEFAULT_ENV') == 'nocturna-test':
    # Testing-specific settings
    DEBUG = False
    LOG_LEVEL = 'INFO'
else:
    # Production settings
    DEBUG = False
    LOG_LEVEL = 'WARNING'
```

### Docker Integration

```dockerfile
# Use production environment in Docker
FROM continuumio/miniconda3
COPY environments/production.yml /tmp/
RUN conda env create -f /tmp/production.yml
RUN echo "conda activate nocturna-prod" >> ~/.bashrc
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Setup Testing Environment
  run: |
    conda env create -f environments/testing.yml
    conda activate nocturna-test
    
- name: Run Tests
  run: |
    conda activate nocturna-test
    make test
```

## Migration Guide

### From Single Environment

If migrating from a single environment setup:

1. **Backup current environment**:
   ```bash
   conda env export > backup-env.yml
   ```

2. **Create new environments**:
   ```bash
   make setup-all
   ```

3. **Migrate dependencies**:
   - Review `backup-env.yml`
   - Add necessary packages to appropriate environment files
   - Update and test each environment

4. **Update workflows**:
   - Update scripts to use appropriate environments
   - Update documentation
   - Train team members

### Environment Naming Changes

If changing from old naming conventions:

1. **Create new environments** with correct names
2. **Update scripts** to reference new names
3. **Update documentation**
4. **Remove old environments** after verification

## Resources

- [Conda Environment Documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Environment Files Best Practices](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)
- [Mamba (Faster Package Manager)](https://mamba.readthedocs.io/)
- [Project Installation Guide](../installation/README.md)
- [Development Setup Guide](../installation/development-setup.md)
- [Testing Setup Guide](../installation/testing-setup.md) 