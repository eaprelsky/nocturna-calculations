# Deployment Scripts

This directory contains deployment scripts for Nocturna Calculations Service.

## Overview

The deployment infrastructure supports three environments:

1. **Staging** - Single instance for testing
2. **Production Blue** - Active production slot
3. **Production Green** - Standby production slot (for blue-green deployment)

## Prerequisites

- Docker and Docker Compose installed
- Proper environment configuration files in `config/`
- Access to the target server (SSH)

## Quick Start

### Initial Setup

1. Copy environment templates:
```bash
cp config/staging.env.example config/staging.env
cp config/production.env.example config/production.env
```

2. Edit environment files with your values:
```bash
# Generate secret keys
openssl rand -hex 32

# Edit files
vim config/staging.env
vim config/production.env
```

3. Make scripts executable:
```bash
chmod +x scripts/deploy/*.sh
```

## Deployment Workflows

### Staging Deployment

Deploy to staging for testing:

```bash
# Initial deployment
./scripts/deploy/staging-deploy.sh

# Rebuild from scratch
./scripts/deploy/staging-deploy.sh --rebuild
```

Access:
- API: http://localhost:8100
- Docs: http://localhost:8100/docs
- Database: localhost:5433
- Redis: localhost:6380

### Production Deployment (Blue-Green)

#### Initial Production Setup

1. Deploy blue slot:
```bash
./scripts/deploy/production-deploy-blue.sh
```

2. Verify blue is working:
```bash
curl http://localhost:8200/health
```

3. Start nginx (routes traffic to blue):
```bash
docker-compose -f docker-compose.nginx.yml up -d
```

#### Zero-Downtime Update

1. Deploy new version to green slot:
```bash
./scripts/deploy/production-deploy-green.sh --tag v1.1.0
```

2. Test green deployment:
```bash
curl http://localhost:8201/health
```

3. Switch traffic from blue to green:
```bash
./scripts/deploy/switch-to-green.sh
```

4. Monitor green deployment. If issues arise, rollback:
```bash
./scripts/deploy/switch-to-green.sh --rollback
```

5. Stop old blue deployment:
```bash
docker-compose -f docker-compose.production.blue.yml stop app-blue
```

#### Next Update Cycle

Deploy to blue slot (green is active):

```bash
./scripts/deploy/production-deploy-blue.sh --tag v1.2.0
# Test blue
./scripts/deploy/switch-to-blue.sh
# Stop green if successful
```

## Scripts Reference

### `staging-deploy.sh`

Deploy to staging environment.

**Usage:**
```bash
./scripts/deploy/staging-deploy.sh [--rebuild]
```

**Options:**
- `--rebuild` - Rebuild images without cache

### `production-deploy-blue.sh`

Deploy to production blue slot.

**Usage:**
```bash
./scripts/deploy/production-deploy-blue.sh [--rebuild] [--tag IMAGE_TAG]
```

**Options:**
- `--rebuild` - Rebuild images without cache
- `--tag IMAGE_TAG` - Tag for the Docker image (default: latest)

**Features:**
- Automatic database backup before deployment
- Database migrations
- Health check verification

### `production-deploy-green.sh`

Deploy to production green slot.

**Usage:**
```bash
./scripts/deploy/production-deploy-green.sh [--rebuild] [--tag IMAGE_TAG]
```

**Options:**
- `--rebuild` - Rebuild images without cache
- `--tag IMAGE_TAG` - Tag for the Docker image (default: latest)

**Note:** Requires blue deployment to be running (shares database and Redis).

### `switch-to-green.sh`

Switch production traffic to green deployment.

**Usage:**
```bash
# Switch to green
./scripts/deploy/switch-to-green.sh

# Rollback to blue
./scripts/deploy/switch-to-green.sh --rollback
```

### `switch-to-blue.sh`

Switch production traffic to blue deployment.

**Usage:**
```bash
./scripts/deploy/switch-to-blue.sh
```

## Docker Image Caching Strategy

The Dockerfile uses multi-stage builds with three layers:

1. **base-os** - Operating system and system packages (rarely changes)
2. **python-deps** - Python dependencies (changes when requirements.txt changes)
3. **application** - Application code (changes frequently)

This approach ensures fast rebuilds:
- If only code changes: only the application layer rebuilds (~5 seconds)
- If dependencies change: python-deps and application layers rebuild (~2 minutes)
- If system packages change: full rebuild (~5 minutes)

## Monitoring

### View Logs

```bash
# Staging
docker-compose -f docker-compose.staging.yml logs -f

# Production Blue
docker-compose -f docker-compose.production.blue.yml logs -f app-blue

# Production Green
docker-compose -f docker-compose.production.green.yml logs -f app-green

# Nginx
docker logs -f nocturna-nginx
```

### Check Status

```bash
# Staging
docker-compose -f docker-compose.staging.yml ps

# Production
docker-compose -f docker-compose.production.blue.yml ps
docker-compose -f docker-compose.production.green.yml ps
```

### Database Backups

Backups are automatically created before production deployments in:
```
backups/postgres/backup_YYYYMMDD_HHMMSS.sql
```

Manual backup:
```bash
docker exec nocturna-prod-db pg_dump -U nocturna_prod_user nocturna_prod > backup.sql
```

Restore:
```bash
docker exec -i nocturna-prod-db psql -U nocturna_prod_user nocturna_prod < backup.sql
```

## Troubleshooting

### Container Not Healthy

Check logs:
```bash
docker-compose -f docker-compose.production.blue.yml logs app-blue
```

Check health endpoint:
```bash
curl http://localhost:8200/health
```

### Database Connection Issues

Check database is running:
```bash
docker ps | grep nocturna-prod-db
```

Test connection:
```bash
docker exec nocturna-prod-db pg_isready -U nocturna_prod_user -d nocturna_prod
```

### Nginx Issues

Test nginx configuration:
```bash
docker exec nocturna-nginx nginx -t
```

Reload nginx:
```bash
docker exec nocturna-nginx nginx -s reload
```

### Clean Rebuild

If experiencing issues, clean rebuild:

```bash
# Stop all containers
docker-compose -f docker-compose.production.blue.yml down
docker-compose -f docker-compose.production.green.yml down

# Remove volumes (WARNING: deletes data!)
docker volume rm nocturna_postgres_prod_data
docker volume rm nocturna_redis_prod_data

# Rebuild and deploy
./scripts/deploy/production-deploy-blue.sh --rebuild
```

## Security Notes

1. Never commit `config/*.env` files to git
2. Use strong passwords for production
3. Restrict CORS_ORIGINS in production
4. Keep IMAGE_TAG updated with semantic versioning
5. Regular database backups (automated before deployments)
6. Monitor logs for security issues

## Additional Resources

- [Docker Deployment Documentation](../../docs/deployment/docker.md)
- [Architecture Overview](../../docs/architecture/overview.md)
- [Troubleshooting Guide](../../docs/guides/troubleshooting.md)
