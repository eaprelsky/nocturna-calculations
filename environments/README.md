# Environment Management

This directory contains Conda environment definitions for different purposes in the Nocturna Calculations project.

## Environment Overview

| Environment | File | Purpose | Python Version |
|-------------|------|---------|----------------|
| **Development** | `development.yml` | Daily development work, debugging, feature development | 3.11 |
| **Testing** | `testing.yml` | Running tests, benchmarks, performance analysis | 3.9 |
| **Production** | `production.yml` | Production deployment, minimal dependencies | 3.11 |

## Quick Setup

### Development Environment
```bash
# Create and activate development environment
conda env create -f environments/development.yml
conda activate nocturna-dev

# Or use the setup script
python scripts/environments/setup_development.py
```

### Testing Environment
```bash
# Create and activate testing environment
conda env create -f environments/testing.yml
conda activate nocturna-test

# Or use the setup script
python scripts/environments/setup_testing.py
```

### Production Environment
```bash
# Create and activate production environment
conda env create -f environments/production.yml
conda activate nocturna-prod
```

## Environment Details

### Development Environment (`nocturna-dev`)
**Primary use case**: Daily development work, debugging, feature development

**Key features**:
- Latest Python 3.11 for development
- Full development toolchain (Black, Flake8, MyPy, etc.)
- Jupyter notebooks for exploration
- Database and caching tools
- Debugging and profiling tools
- Documentation generation tools

**When to use**:
- Writing new features
- Debugging issues
- Code refactoring
- Documentation writing
- Interactive development

### Testing Environment (`nocturna-test`)
**Primary use case**: Running tests, benchmarks, performance analysis

**Key features**:
- Python 3.9 for compatibility testing
- Comprehensive testing frameworks (pytest, hypothesis, etc.)
- Performance testing tools (pytest-benchmark, locust)
- Security testing tools (bandit, safety)
- Code quality verification tools

**When to use**:
- Running unit tests
- Performance benchmarking
- Security audits
- Compatibility testing
- CI/CD pipeline testing

### Production Environment (`nocturna-prod`)
**Primary use case**: Production deployment with minimal dependencies

**Key features**:
- Python 3.11 for optimal performance
- Only runtime dependencies
- Optimized for deployment
- Minimal attack surface

**When to use**:
- Production deployments
- Docker containers
- Performance-critical environments
- Security-sensitive deployments

## Environment Switching

Use the provided utility to switch between environments:

```bash
# Switch to development environment
./scripts/environments/switch_environment.py --env dev

# Switch to testing environment
./scripts/environments/switch_environment.py --env test

# Switch to production environment
./scripts/environments/switch_environment.py --env prod
```

## Environment Validation

Validate your current environment setup:

```bash
./scripts/environments/validate_environment.py
```

## Troubleshooting

### Common Issues

1. **Environment already exists**:
   ```bash
   conda env remove -n nocturna-dev
   conda env create -f environments/development.yml
   ```

2. **Missing dependencies**:
   ```bash
   conda activate nocturna-dev
   conda env update -f environments/development.yml
   ```

3. **Permission issues**:
   - Ensure you have write permissions to the conda directory
   - Run with appropriate user permissions

### Environment Conflicts

If you encounter package conflicts:

1. **Clean approach** (recommended):
   ```bash
   conda env remove -n nocturna-dev
   conda clean --all
   conda env create -f environments/development.yml
   ```

2. **Update approach**:
   ```bash
   conda activate nocturna-dev
   conda update --all
   conda env update -f environments/development.yml --prune
   ```

## Maintenance

### Adding New Dependencies

1. **Development dependencies**: Add to `environments/development.yml`
2. **Testing dependencies**: Add to `environments/testing.yml`
3. **Runtime dependencies**: Add to all three files

### Version Updates

Regularly update dependency versions:

```bash
# Check for outdated packages
conda list --export > current_env.txt

# Update environment files with new versions
# Test thoroughly before committing changes
```

## Best Practices

1. **Always activate the appropriate environment** before working
2. **Keep environments clean** - don't install ad-hoc packages
3. **Update environment files** when adding new dependencies
4. **Test in the testing environment** before merging changes
5. **Use production environment** for deployment validation 