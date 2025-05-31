# Migration Guide: New Installation Architecture

This guide helps you migrate from the old installation system to the new unified architecture.

## What's Changed

### Old System
- Multiple installation scripts (`install_dev.py`, `setup-env.sh`)
- Inconsistent environment names (`nocturna` vs `nocturna-dev`)
- Dependencies scattered across multiple `requirements-*.txt` files
- Different setup procedures for different contexts

### New System
- Single entry point: `make setup`
- Consistent environment naming: `nocturna-{dev|test|prod}`
- All dependencies in `setup.py` with extras
- Unified setup procedure via bootstrap script

## Migration Steps

### 1. Backup Your Work

```bash
# Backup your database if needed
pg_dump -U your_user your_database > backup.sql

# Save your environment variables
cp .env .env.backup

# Commit any uncommitted changes
git add .
git commit -m "WIP: Before migration"
```

### 2. Deactivate Old Environment

```bash
# If you're in the old environment
conda deactivate

# Optional: List your old environments
conda env list
```

### 3. Clean Old Files (Optional)

```bash
# Remove old requirements files (now in setup.py)
rm requirements*.txt

# Remove old setup scripts (replaced by bootstrap)
rm setup-env.sh
```

### 4. Run New Setup

```bash
# Pull latest changes
git pull

# Run the new unified setup
make setup

# This will create nocturna-dev environment
```

### 5. Migrate Configuration

```bash
# The new setup creates .env.example
# Merge your old settings
cp .env.backup .env
# Edit .env to ensure all new variables are included
```

### 6. Activate New Environment

```bash
conda activate nocturna-dev
```

### 7. Verify Installation

```bash
# Check environment info
make env-info

# Run tests
make test

# Start server
make dev
```

## Removing Old Environments (Optional)

Once you're confident the new setup works:

```bash
# Remove old environment
conda env remove -n nocturna

# Clean conda cache
conda clean --all
```

## Key Differences to Note

### Environment Names
- Old: `nocturna`
- New: `nocturna-dev`, `nocturna-test`, `nocturna-prod`

### Installation Command
- Old: `python scripts/install_dev.py` or `./setup-env.sh`
- New: `make setup`

### Dependency Management
- Old: `pip install -r requirements-*.txt`
- New: `pip install -e ".[dev]"` (handled automatically)

### Service Management
- Old: Mixed in installation scripts
- New: Dedicated scripts in `scripts/services/`

## Troubleshooting Migration

### Issue: Old environment conflicts
```bash
# Remove all nocturna environments and start fresh
conda env list | grep nocturna
conda env remove -n [environment-name]
```

### Issue: Database connection fails
```bash
# Check PostgreSQL status
make services-check

# Restart services
make services-start
```

### Issue: Missing dependencies
```bash
# Update dependencies in active environment
make update-deps
```

### Issue: Make command not found
```bash
# Use bootstrap script directly
python scripts/bootstrap.py --all
```

## Benefits After Migration

1. **Simpler Commands**: Just `make setup` instead of multiple scripts
2. **Better Organization**: Clear separation of concerns
3. **Consistent Environments**: Same setup process everywhere
4. **Easier Updates**: Single `setup.py` to maintain
5. **Better Documentation**: Integrated help with `make help`

## Need Help?

- Run `make help` to see all available commands
- Check `docs/installation/quickstart.md` for quick reference
- Open an issue on GitHub if you encounter problems

## Rollback Plan

If you need to rollback:

1. The old files are in git history
2. Your old environment still exists (unless removed)
3. Your configuration is backed up

```bash
# To rollback
git checkout <previous-commit> -- requirements*.txt setup-env.sh
conda activate nocturna  # old environment
```

Remember: The new system is designed to coexist with the old during migration, so you can take your time. 