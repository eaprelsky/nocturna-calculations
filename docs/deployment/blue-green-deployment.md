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
./scripts/deploy.sh blue
```

This will:
- Ensure shared infrastructure (database, Redis, network)
- Run database migrations
- Start blue application on port 18200
- Wait for health check

#### 3. Check Deployment Status

```bash
# Check status of all instances
./scripts/status.sh
```

Now blue is running: `Blue:18200`

### Updating Production (Zero Downtime)

#### Scenario: Blue is Active, Deploying to Green

**Step 1: Deploy New Version to Green**

```bash
# Deploy new version to green slot
./scripts/deploy.sh green
```

This will:
- Build new Docker image
- Start green container on port 18201
- Use existing database and Redis (shared with blue)
- Wait for health check to pass

**Step 2: Test Green Deployment**

```bash
# Test health endpoint
curl http://localhost:18201/health

# Test API endpoints
curl http://localhost:18201/v1/calculate/natal \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1990-01-01T12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173
  }'

# Check logs
docker-compose -f docker-compose.green.yml logs -f
```

**Step 3: Switch Traffic to Green**

```bash
# Switch to route traffic to green
./scripts/switch.sh green
```

This will:
- Verify green is healthy
- Update metadata file (.current-env)
- Update nginx configuration if available
- Reload nginx (no downtime)

Now green is active: `Green:18201`

**Step 4: Monitor Green**

```bash
# Check status
./scripts/status.sh

# Monitor logs
docker-compose -f docker-compose.green.yml logs -f

# Check metrics
watch -n 5 'curl -s http://localhost:18201/health | jq'
```

**Step 5a: Success - Stop Blue**

If everything works:

```bash
# Stop blue (but don't remove, keep for potential rollback)
docker-compose -f docker-compose.blue.yml down
```

**Step 5b: Issues - Rollback to Blue**

If issues detected:

```bash
# Instant rollback to blue
./scripts/rollback.sh
```

Traffic immediately returns to blue (no service interruption).

### Next Update Cycle

#### Scenario: Green is Active, Deploying to Blue

**Update Blue with New Version**

```bash
# Deploy new version to blue slot
./scripts/deploy.sh blue
```

**Test and Switch**

```bash
# Test blue
curl http://localhost:18200/health

# Switch traffic to blue
./scripts/switch.sh blue

# Stop green if successful
docker-compose -f docker-compose.green.yml down
```

## Commands Reference

### Deployment Commands

```bash
# Deploy to blue
./scripts/deploy.sh blue [--rebuild]

# Deploy to green
./scripts/deploy.sh green [--rebuild]

# Deploy to staging
./scripts/deploy.sh staging [--rebuild]

# Auto-deploy to inactive instance
./scripts/deploy.sh auto

# Switch traffic to specific instance
./scripts/switch.sh [blue|green]

# Rollback to previous instance
./scripts/rollback.sh

# Check deployment status
./scripts/status.sh
```

### Monitoring Commands

```bash
# Check status
./scripts/status.sh

# View logs
docker-compose -f docker-compose.blue.yml logs -f
docker-compose -f docker-compose.green.yml logs -f

# Test endpoints
curl http://localhost:18200/health  # Blue
curl http://localhost:18201/health  # Green
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
docker-compose -f docker-compose.green.yml logs

# Check database connection
docker exec nocturna-postgres pg_isready

# Check if port is already in use
netstat -an | grep 18201

# Rebuild if needed
./scripts/deploy.sh green --rebuild
```

### Traffic Switch Fails

**Symptoms:**
```bash
Error: Could not verify traffic switch
```

**Solution:**
```bash
# Check instance is healthy
curl http://localhost:18200/health  # or 18201 for green

# Check status
./scripts/status.sh

# Try manual switch
./scripts/switch.sh blue  # or green

# Check metadata file
cat .current-env
```

### Database Connection Errors

**Symptoms:**
```
Could not connect to database
```

**Solution:**
```bash
# Ensure shared infrastructure is running
docker-compose -f docker-compose.shared.yml up -d

# Check database health
docker exec nocturna-postgres pg_isready

# Check database logs
docker logs nocturna-postgres
```

### Both Slots Consuming Resources

**Issue:** Both blue and green running simultaneously

**Solution:**
```bash
# Stop inactive slot after successful switch
docker-compose -f docker-compose.blue.yml down
# OR
docker-compose -f docker-compose.green.yml down
```

## Rollback Strategies

### Instant Rollback (Same Version)

If the new deployment has issues but database is compatible:

```bash
# Immediate rollback
./scripts/rollback.sh
```

Response time: ~5 seconds

### Full Rollback (Previous Version)

If you need to revert to a previous version:

```bash
# Deploy old version to inactive slot
./scripts/deploy.sh blue

# Switch traffic
./scripts/switch.sh blue
```

### Database Rollback

If migrations need to be reverted:

```bash
# Stop application
docker-compose -f docker-compose.blue.yml down
docker-compose -f docker-compose.green.yml down

# Restore database from backup (if you have backups configured)
# docker exec -i nocturna-postgres psql -U user dbname < backup.sql

# Deploy old version
./scripts/deploy.sh blue
```

## Best Practices

### 1. Version Management

Deploy to specific instances:

```bash
# Deploy to blue
./scripts/deploy.sh blue

# Deploy to green
./scripts/deploy.sh green

# Auto-deploy to inactive instance
./scripts/deploy.sh auto
```

### 2. Testing Before Switch

Always test the new deployment thoroughly:

```bash
# Functional tests
curl http://localhost:18201/health
curl http://localhost:18201/v1/calculate/natal

# Load test (optional)
ab -n 1000 -c 10 http://localhost:18201/health

# Check logs for errors
docker-compose -f docker-compose.green.yml logs
```

### 3. Monitoring

Check deployment status regularly:

```bash
# Check overall status
./scripts/status.sh

# Monitor active instance
watch -n 5 './scripts/status.sh'
```

### 4. Database Backups

Ensure you have database backup strategy in place:

```bash
# Manual backup example
docker exec nocturna-postgres pg_dump -U user dbname > backup_$(date +%Y%m%d).sql
```

### 5. Monitor After Switch

Watch logs and metrics for at least 15 minutes after switching:

```bash
# Monitor logs
docker-compose -f docker-compose.green.yml logs -f

# Check status
./scripts/status.sh

# Monitor resource usage
docker stats
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
# Stop both instances
docker-compose -f docker-compose.blue.yml down
docker-compose -f docker-compose.green.yml down

# Perform maintenance
# Do maintenance work

# Restart
./scripts/deploy.sh blue
```

### Scaling

To scale up workers:

```bash
# Edit docker-compose.blue.yml
# Modify WORKERS environment variable or command

# Rebuild and deploy
./scripts/deploy.sh blue --rebuild
```

### Multi-Server Deployment

For multiple servers, use Docker Swarm or Kubernetes:

```bash
# Docker Swarm example
docker stack deploy -c docker-compose.blue.yml nocturna-blue
```

## Related Documentation

- [Docker Deployment](docker.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
