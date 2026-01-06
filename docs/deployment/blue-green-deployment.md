# Blue-Green Deployment Guide

This guide explains the blue-green deployment strategy for Nocturna Calculations Service.

## Overview

Blue-green deployment is a release strategy that reduces downtime and risk by running two identical production environments (blue and green). At any time, only one environment serves production traffic, while the other is idle or being updated.

### Architecture

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (Router)   │
                    └──────┬──────┘
                           │
         ┌─────────────────┴──────────────────┐
         │                                     │
    ┌────▼────┐                          ┌────▼────┐
    │  BLUE   │                          │  GREEN  │
    │ :8200   │                          │ :8201   │
    └────┬────┘                          └────┬────┘
         │                                     │
         └─────────────────┬───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL  │
                    │    Redis     │
                    └──────────────┘
```

### Key Features

- **Zero Downtime**: Switch traffic without service interruption
- **Easy Rollback**: Instant rollback if issues detected
- **Shared Database**: Blue and green share database and cache
- **Independent Testing**: Test new version before switching traffic

## Deployment Process

### Initial Setup (First Time)

#### 1. Prepare Configuration

```bash
# Copy and edit production environment
cp config/production.env.example config/production.env
vim config/production.env

# Set strong passwords and secrets
openssl rand -hex 32  # For SECRET_KEY
```

#### 2. Deploy Blue (Initial Production)

```bash
# Deploy blue slot with initial version
./scripts/deploy/production-deploy-blue.sh --tag v1.0.0
```

This will:
- Create database and Redis containers
- Run database migrations
- Start blue application on port 8200
- Create automatic database backup

#### 3. Start Nginx

```bash
# Start nginx (routes to blue by default)
docker-compose -f docker-compose.nginx.yml up -d
```

Now traffic flows: `Internet → Nginx:80 → Blue:8200`

### Updating Production (Zero Downtime)

#### Scenario: Blue is Active, Deploying to Green

**Step 1: Deploy New Version to Green**

```bash
# Deploy new version to green slot
./scripts/deploy/production-deploy-green.sh --tag v1.1.0
```

This will:
- Build new Docker image with tag v1.1.0
- Start green container on port 8201
- Use existing database and Redis (shared with blue)
- Wait for health check to pass

**Step 2: Test Green Deployment**

```bash
# Test health endpoint
curl http://localhost:8201/health

# Test API endpoints
curl http://localhost:8201/v1/calculate/natal \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1990-01-01T12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173
  }'

# Check logs
docker-compose -f docker-compose.production.green.yml logs -f app-green
```

**Step 3: Switch Traffic to Green**

```bash
# Switch nginx to route traffic to green
./scripts/deploy/switch-to-green.sh
```

This will:
- Verify green is healthy
- Update nginx configuration
- Reload nginx (no downtime)
- Route all traffic to green

Now traffic flows: `Internet → Nginx:80 → Green:8201`

**Step 4: Monitor Green**

```bash
# Monitor logs
docker-compose -f docker-compose.production.green.yml logs -f app-green

# Check metrics
watch -n 5 'curl -s http://localhost:8201/health | jq'

# Monitor nginx
docker logs -f nocturna-nginx
```

**Step 5a: Success - Stop Blue**

If everything works:

```bash
# Stop blue (but don't remove, keep for potential rollback)
docker-compose -f docker-compose.production.blue.yml stop app-blue
```

**Step 5b: Issues - Rollback to Blue**

If issues detected:

```bash
# Instant rollback to blue
./scripts/deploy/switch-to-green.sh --rollback
```

Traffic immediately returns to blue (no service interruption).

### Next Update Cycle

#### Scenario: Green is Active, Deploying to Blue

**Update Blue with New Version**

```bash
# Deploy new version to blue slot
./scripts/deploy/production-deploy-blue.sh --tag v1.2.0
```

**Test and Switch**

```bash
# Test blue
curl http://localhost:8200/health

# Switch traffic to blue
./scripts/deploy/switch-to-blue.sh

# Stop green if successful
docker-compose -f docker-compose.production.green.yml stop app-green
```

## Commands Reference

### Deployment Commands

```bash
# Deploy to blue
./scripts/deploy/production-deploy-blue.sh [--rebuild] [--tag v1.0.0]

# Deploy to green
./scripts/deploy/production-deploy-green.sh [--rebuild] [--tag v1.0.0]

# Switch traffic to green
./scripts/deploy/switch-to-green.sh

# Rollback to blue
./scripts/deploy/switch-to-green.sh --rollback

# Switch traffic to blue
./scripts/deploy/switch-to-blue.sh
```

### Monitoring Commands

```bash
# Check status
docker-compose -f docker-compose.production.blue.yml ps
docker-compose -f docker-compose.production.green.yml ps

# View logs
docker-compose -f docker-compose.production.blue.yml logs -f app-blue
docker-compose -f docker-compose.production.green.yml logs -f app-green
docker logs -f nocturna-nginx

# Test endpoints
curl http://localhost:8200/health  # Blue
curl http://localhost:8201/health  # Green
curl http://localhost/health       # Through nginx
```

## Database Migrations

### Strategy

Database migrations are applied **before** deploying the new application version:

1. Migrations must be **backward compatible** with the current running version
2. Blue deployment always runs migrations before starting
3. Green uses the already migrated database

### Best Practices

**✅ Good Migration (Backward Compatible)**

```python
# Adding a new nullable column
def upgrade():
    op.add_column('users', sa.Column('new_field', sa.String(), nullable=True))
```

**❌ Bad Migration (Breaking Change)**

```python
# Removing a column that current version uses
def upgrade():
    op.drop_column('users', 'old_field')  # Current version will break!
```

### Handling Breaking Changes

For breaking changes, use two-phase deployment:

**Phase 1: Add New Schema**
```python
# Version 1.1.0
def upgrade():
    op.add_column('users', sa.Column('new_field', sa.String(), nullable=True))
    # Old field still exists
```

Deploy v1.1.0 → Test → Switch traffic

**Phase 2: Remove Old Schema**
```python
# Version 1.2.0
def upgrade():
    op.drop_column('users', 'old_field')
    # Now safe to remove
```

Deploy v1.2.0 → Test → Switch traffic

## Troubleshooting

### Green Deployment Fails Health Check

**Symptoms:**
```bash
Error: Application did not become healthy in time
```

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.production.green.yml logs app-green

# Check database connection
docker exec nocturna-prod-db pg_isready -U nocturna_prod_user

# Check if port is already in use
netstat -an | grep 8201

# Rebuild if needed
./scripts/deploy/production-deploy-green.sh --rebuild
```

### Nginx Switch Fails

**Symptoms:**
```bash
Error: Could not verify traffic switch
```

**Solution:**
```bash
# Check nginx is running
docker ps | grep nocturna-nginx

# Test nginx config
docker exec nocturna-nginx nginx -t

# Check logs
docker logs nocturna-nginx

# Restart nginx
docker-compose -f docker-compose.nginx.yml restart
```

### Database Connection Errors

**Symptoms:**
```
Could not connect to database
```

**Solution:**
```bash
# Ensure database is running
docker-compose -f docker-compose.production.blue.yml up -d db-prod

# Check database health
docker exec nocturna-prod-db pg_isready -U nocturna_prod_user -d nocturna_prod

# Check database logs
docker logs nocturna-prod-db
```

### Both Slots Consuming Resources

**Issue:** Both blue and green running simultaneously

**Solution:**
```bash
# Stop inactive slot after successful switch
docker-compose -f docker-compose.production.blue.yml stop app-blue
# OR
docker-compose -f docker-compose.production.green.yml stop app-green
```

## Rollback Strategies

### Instant Rollback (Same Version)

If the new deployment has issues but database is compatible:

```bash
# Immediate rollback
./scripts/deploy/switch-to-green.sh --rollback
```

Response time: ~5 seconds

### Full Rollback (Previous Version)

If you need to revert to a previous version:

```bash
# Deploy old version to inactive slot
./scripts/deploy/production-deploy-blue.sh --tag v1.0.0

# Switch traffic
./scripts/deploy/switch-to-blue.sh
```

### Database Rollback

If migrations need to be reverted:

```bash
# Stop application
docker-compose -f docker-compose.production.blue.yml stop app-blue
docker-compose -f docker-compose.production.green.yml stop app-green

# Restore database from backup
docker exec -i nocturna-prod-db psql -U nocturna_prod_user nocturna_prod < backups/postgres/backup_YYYYMMDD_HHMMSS.sql

# Deploy old version
./scripts/deploy/production-deploy-blue.sh --tag v1.0.0
```

## Best Practices

### 1. Version Tagging

Use semantic versioning for production images:

```bash
./scripts/deploy/production-deploy-green.sh --tag v1.2.0
```

Never use `latest` in production.

### 2. Testing Before Switch

Always test the new deployment thoroughly:

```bash
# Functional tests
curl http://localhost:8201/health
curl http://localhost:8201/v1/calculate/natal

# Load test (optional)
ab -n 1000 -c 10 http://localhost:8201/health

# Check logs for errors
docker-compose -f docker-compose.production.green.yml logs app-green
```

### 3. Gradual Rollout

For high-risk changes, consider canary deployment:

```nginx
# nginx/conf.d/upstream-canary.conf
upstream nocturna_backend {
    server nocturna-prod-blue-api:8000 weight=9;   # 90% traffic
    server nocturna-prod-green-api:8000 weight=1;  # 10% traffic
}
```

### 4. Database Backups

Backups are automatic before deployment, but verify:

```bash
ls -lh backups/postgres/
```

### 5. Monitor After Switch

Watch logs and metrics for at least 15 minutes after switching:

```bash
# Monitor logs
docker-compose -f docker-compose.production.green.yml logs -f app-green

# Monitor resource usage
docker stats nocturna-prod-green-api
```

### 6. Keep Inactive Slot Ready

Don't remove the inactive slot immediately:

- Keep it running for 1-2 hours after switch
- Allows instant rollback if issues arise
- Stop (don't remove) to save resources

### 7. Document Deployments

Keep a deployment log:

```bash
# deployment-log.md
- 2025-01-06 14:30 - v1.1.0 deployed to green
- 2025-01-06 14:45 - Switched traffic to green
- 2025-01-06 15:00 - Monitoring complete, stopped blue
```

## Advanced Scenarios

### Emergency Maintenance

If both slots need to be down:

```bash
# Switch to maintenance page in nginx
cp nginx/conf.d/upstream-maintenance.conf nginx/conf.d/upstream.conf
docker exec nocturna-nginx nginx -s reload

# Perform maintenance
docker-compose -f docker-compose.production.blue.yml down
# Do maintenance work

# Restart
./scripts/deploy/production-deploy-blue.sh
```

### Scaling

To scale up workers:

```bash
# Edit docker-compose.production.blue.yml
CMD ["uvicorn", "...", "--workers", "8"]  # Increase workers

# Rebuild and deploy
./scripts/deploy/production-deploy-blue.sh --rebuild
```

### Multi-Server Deployment

For multiple servers, use Docker Swarm or Kubernetes:

```bash
# Docker Swarm example
docker stack deploy -c docker-compose.production.blue.yml nocturna-blue
```

## Related Documentation

- [Docker Deployment](docker.md)
- [Deployment Scripts](../../scripts/deploy/README.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
