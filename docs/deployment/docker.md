# Docker Deployment Guide

This guide explains how to deploy Nocturna Calculations as a containerized service using Docker and Docker Compose.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Service Component Mode](#service-component-mode)
- [Deployment Steps](#deployment-steps)
- [Management Commands](#management-commands)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Production Considerations](#production-considerations)
- [Integration with Main Backend](#integration-with-main-backend)

## Overview

The Docker deployment provides:

- **🐳 Containerized Application**: API server running in an isolated environment
- **🗄️ PostgreSQL Database**: Persistent data storage with automatic backups
- **🚀 Redis Cache**: High-performance caching and rate limiting
- **🔧 Automated Setup**: One-command deployment with migrations and admin setup
- **📊 Health Monitoring**: Built-in health checks and status monitoring
- **🔒 Security**: Non-root containers, encrypted connections, and secure defaults

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nocturna API  │◄──►│   PostgreSQL     │    │     Redis       │
│   (FastAPI)     │    │   Database       │    │     Cache       │
│   Port: 8000    │    │   Port: 5432     │    │   Port: 6379    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Your Main      │
│  Backend        │
│  (via API)      │
└─────────────────┘
```

## Prerequisites

### System Requirements

- **Docker**: Version 20.10+ 
- **Docker Compose**: Version 2.0+
- **Available Ports**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis)
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 10GB disk space

### Installation

#### Ubuntu/Debian
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

### Verification

```bash
# Check Docker installation
docker --version
docker-compose --version

# Test Docker
docker run hello-world
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd nocturna-calculations

# Check Docker prerequisites
make docker-check

# Setup environment
make docker-setup
```

### 2. Configure Environment

Edit the `.env` file created in the previous step:

```bash
# Generate secure keys
openssl rand -hex 32  # Use output for SECRET_KEY

# Edit configuration
nano .env
```

**Required changes in `.env**:**
```bash
# Replace these values
SECRET_KEY=your_generated_32_char_secret_key
ADMIN_PASSWORD=your_secure_admin_password
POSTGRES_PASSWORD=your_secure_database_password

# Update CORS origins for your domains
CORS_ORIGINS=["https://your-backend.com","https://your-frontend.com"]
```

### 3. Deploy

```bash
# Complete deployment (builds, starts, migrates, configures)
make docker-deploy
```

### 4. Verify Deployment

```bash
# Check service status
make docker-status

# Check logs
make docker-logs

# Test API
curl http://localhost:8000/health
```

## Configuration

### Environment Variables

The service is configured via environment variables in the `.env` file:

#### Security Configuration
```bash
SECRET_KEY=your_jwt_secret_key                    # JWT signing key
ADMIN_PASSWORD=your_admin_password                # Initial admin password
POSTGRES_PASSWORD=your_database_password          # Database password
```

#### Service Component Settings
```bash
ALLOW_USER_REGISTRATION=false                     # Disable new registrations
REGISTRATION_REQUIRES_APPROVAL=true               # Require approval
MAX_USERS_LIMIT=100                               # Limit user count
```

#### Integration Settings
```bash
CORS_ORIGINS=["https://your-backend.com"]         # Allowed origins
SERVICE_TOKEN=                                    # Generated during setup
```

#### Performance Settings
```bash
RATE_LIMIT_DEFAULT=1000                           # Requests per hour
RATE_LIMIT_PREMIUM=10000                          # Premium rate limit
CACHE_TTL=3600                                    # Cache expiry (seconds)
```

### Custom Configuration

For advanced configuration, modify `docker-compose.yml`:

```yaml
services:
  app:
    environment:
      # Add custom environment variables
      - CUSTOM_SETTING=value
    volumes:
      # Mount custom config files
      - ./custom-config.yaml:/app/config/custom.yaml
```

## Service Component Mode

The Docker deployment configures Nocturna as a **service component** for integration with your main backend:

### Features

- **🚫 Disabled Registration**: No new user signups
- **👤 Admin User**: System administration access
- **🔑 Service Token**: API access for your backend
- **🔒 Secure Defaults**: Production-ready security settings

### Users Created

1. **Admin User**
   - Email: `admin@nocturna.service`
   - Purpose: System administration
   - Access: Web interface + full API

2. **Service User**
   - Email: `service@nocturna.internal`
   - Purpose: Backend integration
   - Access: API only via long-lived token

### Token Management

The service user receives a **30-day JWT token** for API access:

```bash
# View deployment summary with token
cat deployment_summary.json

# The token allows your backend to make API calls:
curl -H "Authorization: Bearer YOUR_SERVICE_TOKEN" \
     http://localhost:8000/api/v1/calculations
```

## Deployment Steps

### Step-by-Step Deployment

#### 1. Preparation
```bash
# Clone repository
git clone <repository-url>
cd nocturna-calculations

# Verify Docker installation
make docker-check
```

#### 2. Environment Setup
```bash
# Create .env file from template
make docker-setup

# Generate secure secret key
openssl rand -hex 32

# Edit .env file
nano .env
```

#### 3. Build and Start Services
```bash
# Build Docker image
make docker-build

# Start all services
make docker-up

# Check status
make docker-status
```

#### 4. Database Setup
```bash
# Run migrations
make docker-migrate

# Setup admin user and service token
make docker-setup-production
```

#### 5. Verification
```bash
# Check logs
make docker-logs

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/calculations/health
```

### One-Command Deployment

For automated deployment:

```bash
# Complete setup in one command
make docker-deploy
```

This runs all steps automatically.

## Management Commands

### Service Management

```bash
# Start services
make docker-up

# Stop services  
make docker-down

# Restart services
make docker-restart

# View status
make docker-status
```

### Logs and Debugging

```bash
# View all service logs
make docker-logs

# View API logs only
make docker-logs-api

# Follow logs in real-time
docker-compose logs -f

# Open shell in API container
make docker-shell
```

### Database Operations

```bash
# Run migrations
make docker-migrate

# Connect to database
docker-compose exec db psql -U postgres -d nocturna

# Backup database
docker-compose exec db pg_dump -U postgres nocturna > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres nocturna < backup.sql
```

### User Management

```bash
# Create additional admin user
docker-compose exec app python scripts/create_admin.py create

# List admin users
docker-compose exec app python scripts/create_admin.py list

# Setup production (admin + service user)
make docker-setup-production
```

### Maintenance

```bash
# Clean up Docker resources
make docker-clean

# Update images
docker-compose pull
make docker-restart

# View resource usage
docker stats
```

## Monitoring & Troubleshooting

### Health Checks

The deployment includes automatic health monitoring:

```bash
# Check service health
curl http://localhost:8000/health

# Detailed health status
curl http://localhost:8000/api/v1/health

# Docker health status
docker-compose ps
```

### Common Issues

#### Services Won't Start

```bash
# Check logs for errors
make docker-logs

# Verify environment file
cat .env

# Check port conflicts
sudo netstat -tulpn | grep -E ':(8000|5432|6379)'

# Restart with fresh containers
make docker-clean
make docker-deploy
```

#### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose logs db

# Verify database is ready
docker-compose exec db pg_isready -U postgres

# Reset database (⚠️ destroys data)
docker-compose down -v
docker-compose up -d db
make docker-migrate
```

#### API Authentication Issues

```bash
# Regenerate service token
make docker-setup-production

# Check admin user
docker-compose exec app python scripts/create_admin.py list

# Verify JWT secret is set
docker-compose exec app printenv SECRET_KEY
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Container metrics
docker-compose top

# API metrics (if enabled)
curl http://localhost:8000/metrics
```

### Log Analysis

```bash
# Error logs only
docker-compose logs | grep ERROR

# API request logs
docker-compose logs app | grep -E '(GET|POST|PUT|DELETE)'

# Database activity
docker-compose logs db | tail -n 100
```

## Production Considerations

### Security

#### Network Security
```yaml
# docker-compose.yml modifications for production
services:
  app:
    # Only expose API port
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only
  
  db:
    # Remove external port access
    # ports: []  # Database not accessible externally
  
  redis:
    # Remove external port access
    # ports: []  # Redis not accessible externally
```

#### SSL/TLS Configuration

For HTTPS, use a reverse proxy:

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Environment Security

```bash
# Secure .env file permissions
chmod 600 .env
chown root:root .env

# Use Docker secrets for sensitive data
docker secret create postgres_password /path/to/password/file
```

### Scalability

#### Horizontal Scaling

```yaml
# docker-compose.yml for multiple API instances
services:
  app:
    deploy:
      replicas: 3
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

#### Resource Limits

```yaml
# docker-compose.yml with resource limits
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Backup Strategy

#### Automated Backups

```bash
# Create backup script
cat << 'EOF' > backup.sh
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T db pg_dump -U postgres nocturna > "$BACKUP_DIR/nocturna_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/nocturna_$DATE.sql"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "nocturna_*.sql.gz" -mtime +30 -delete
EOF

# Make executable
chmod +x backup.sh

# Schedule with cron
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### Monitoring Setup

#### Prometheus Metrics

```yaml
# docker-compose.yml with monitoring
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Integration with Main Backend

### API Authentication

Your main backend should use the service token for API calls:

```python
# Python example
import requests

SERVICE_TOKEN = "your_service_token_from_deployment_summary"

headers = {
    "Authorization": f"Bearer {SERVICE_TOKEN}",
    "Content-Type": "application/json"
}

# Make API call
response = requests.post(
    "http://nocturna-api:8000/api/v1/calculations",
    headers=headers,
    json={
        "date": "2024-01-01T12:00:00Z",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "calculations": ["positions", "aspects"]
    }
)

result = response.json()
```

### Service Discovery

In Docker networks, services can communicate by name:

```yaml
# Your main backend docker-compose.yml
services:
  main-backend:
    environment:
      - NOCTURNA_API_URL=http://nocturna-api:8000
    networks:
      - nocturna_nocturna-network

networks:
  nocturna_nocturna-network:
    external: true
```

### Health Checks

Monitor the Nocturna service from your backend:

```python
# Health check example
def check_nocturna_health():
    try:
        response = requests.get(
            "http://nocturna-api:8000/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False
```

### Error Handling

Implement proper error handling for API calls:

```python
def make_calculation_request(data):
    try:
        response = requests.post(
            f"{NOCTURNA_API_URL}/api/v1/calculations",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Rate limited
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code == 401:
            # Invalid token
            raise AuthenticationError("Invalid service token")
        else:
            # Other errors
            raise APIError(f"API error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        raise TimeoutError("Nocturna API timeout")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Cannot connect to Nocturna API")
```

---

## Summary

The Docker deployment provides a production-ready Nocturna Calculations service with:

✅ **One-command deployment**  
✅ **Secure service component mode**  
✅ **Automated admin and service user setup**  
✅ **Health monitoring and logging**  
✅ **Easy integration with your main backend**  
✅ **Production security defaults**  

For support and troubleshooting, check the logs with `make docker-logs` and refer to the [main documentation](../README.md). 