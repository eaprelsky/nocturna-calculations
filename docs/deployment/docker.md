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
- [Token Management](#token-management)
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

## Token Management

### Overview

The service token is a **JWT token with 30-day expiration** that allows your main backend to authenticate with the Nocturna API. When it expires, your backend will start receiving `401 Unauthorized` responses.

### 🚨 Token Expiration Symptoms

```python
# Your backend will receive these responses:
{
    "detail": "Token has expired",
    "status_code": 401
}
```

**Signs of token expiration:**
- 401 Unauthorized errors from Nocturna API
- Authentication failures in your backend logs
- Failed astrological calculations
- Service disruption for users

### 🔍 Checking Token Status

#### Quick Status Check
```bash
# Check if token is expiring soon
make docker-token-check
```

#### Manual Token Inspection
```python
# In your backend code, check token expiration
import jwt
from datetime import datetime

def check_token_expiration(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = payload.get('exp')
        
        if exp_timestamp:
            exp_date = datetime.fromtimestamp(exp_timestamp)
            days_until_expiry = (exp_date - datetime.now()).days
            
            print(f"Token expires on: {exp_date}")
            print(f"Days until expiry: {days_until_expiry}")
            
            return days_until_expiry
    except jwt.DecodeError:
        print("Invalid token format")
        return 0

# Usage
SERVICE_TOKEN = "your_current_token"
days_left = check_token_expiration(SERVICE_TOKEN)

if days_left < 7:
    print("⚠️ Token expires soon - renewal needed!")
```

### 🔄 Token Renewal Options

#### Option 1: Automatic Renewal (Recommended for Production)
```bash
# Renew token if expiring within 7 days
make docker-token-renew

# Force renewal regardless of expiration
make docker-token-force-renew
```

#### Option 2: Eternal Tokens (For Lazy Admins! 😄)
For internal deployments with nginx/firewall protection:

```bash
# Generate eternal token (never expires)
make docker-token-eternal
```

**Perfect for:**
- 🏠 **Internal deployments** with nginx reverse proxy
- 🔒 **Firewall-protected** environments
- 😴 **Lazy admins** who don't want monthly renewals
- 🛡️ **Corporate networks** with restricted access

**Security Requirements:**
- ⚠️ **Block external access** via nginx/firewall
- 🌐 **IP whitelisting** for additional security  
- 📊 **Monitor logs** for suspicious activity
- 🔄 **Rotate if compromised**

#### Option 3: Custom Duration Tokens
```bash
# Generate 1-year token
make docker-token-custom DAYS=365

# Generate 5-year token  
make docker-token-custom DAYS=1825

# Generate 10-year token
make docker-token-custom DAYS=3650
```

#### Option 4: Manual Renewal
```bash
# Regenerate all production credentials
make docker-setup-production

# Get the new token
cat deployment_summary.json
```

### 🤖 Automated Token Renewal

#### Cron-based Renewal
```bash
# Create renewal script
cat << 'EOF' > /usr/local/bin/renew_nocturna_token.sh
#!/bin/bash
cd /path/to/nocturna-calculations

# Check and renew token if needed
make docker-token-renew > /var/log/nocturna_token_renewal.log 2>&1

# Optionally restart your main backend if token was renewed
if grep -q "Token renewal complete" /var/log/nocturna_token_renewal.log; then
    # systemctl restart your-main-backend
    echo "Token renewed - consider restarting your backend"
fi
EOF

# Make executable
chmod +x /usr/local/bin/renew_nocturna_token.sh

# Schedule weekly renewal check
echo "0 2 * * 1 /usr/local/bin/renew_nocturna_token.sh" | crontab -
```

#### Docker Compose Healthcheck-based Renewal
```yaml
# Add to docker-compose.yml
services:
  token-monitor:
    build: .
    command: >
      sh -c "
        while true; do
          sleep 86400; # Check daily
          python scripts/renew_service_token.py --days-before-expiry 7
        done
      "
    depends_on:
      - app
    restart: unless-stopped
```

### 🔧 Backend Integration for Token Management

#### Error Handling with Automatic Retry
```python
import requests
import time
from datetime import datetime, timedelta

class NocturnaAPIClient:
    def __init__(self, api_url, service_token):
        self.api_url = api_url
        self.service_token = service_token
        self.token_expires_at = self._decode_token_expiry(service_token)
    
    def _decode_token_expiry(self, token):
        """Decode token to get expiration time"""
        try:
            import jwt
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
        except:
            pass
        return None
    
    def _is_token_expiring_soon(self, days_threshold=7):
        """Check if token expires within threshold"""
        if not self.token_expires_at:
            return True
        
        return (self.token_expires_at - datetime.now()).days <= days_threshold
    
    def _notify_token_expiry(self):
        """Notify administrators about token expiry"""
        # Implement your notification system here
        print(f"⚠️ Nocturna service token expires on {self.token_expires_at}")
        # send_email_alert()
        # post_to_slack()
        # create_monitoring_alert()
    
    def make_api_call(self, endpoint, data=None, max_retries=1):
        """Make API call with token expiry handling"""
        
        # Check if token is expiring soon
        if self._is_token_expiring_soon():
            self._notify_token_expiry()
        
        headers = {
            "Authorization": f"Bearer {self.service_token}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 401:
                    error_detail = response.json().get('detail', '')
                    if 'expired' in error_detail.lower():
                        if attempt < max_retries:
                            # Token expired - you could implement auto-renewal here
                            # or just notify and fail
                            raise TokenExpiredError(
                                "Service token has expired. Please renew with: "
                                "make docker-token-renew"
                            )
                        else:
                            raise TokenExpiredError("Service token expired after retry")
                    else:
                        raise AuthenticationError(f"Authentication failed: {error_detail}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise TimeoutError("Nocturna API timeout after retries")
            
            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise ConnectionError("Cannot connect to Nocturna API after retries")

# Custom exceptions
class TokenExpiredError(Exception):
    pass

class AuthenticationError(Exception):
    pass

# Usage
client = NocturnaAPIClient(
    api_url="http://nocturna-api:8000/api/v1",
    service_token=SERVICE_TOKEN
)

try:
    result = client.make_api_call("/calculations", calculation_data)
except TokenExpiredError as e:
    # Handle token expiry - notify admins, log error, etc.
    logger.error(f"Nocturna token expired: {e}")
    # Optionally implement automatic renewal here
except AuthenticationError as e:
    logger.error(f"Nocturna authentication error: {e}")
```

### 📊 Monitoring Token Health

#### Prometheus Metrics
```python
# Add to your backend monitoring
from prometheus_client import Gauge, Counter

nocturna_token_days_until_expiry = Gauge(
    'nocturna_token_days_until_expiry',
    'Days until Nocturna service token expires'
)

nocturna_token_expired_errors = Counter(
    'nocturna_token_expired_errors_total',
    'Number of token expiry errors'
)

# Update metrics periodically
def update_token_metrics():
    days_left = check_token_expiration(SERVICE_TOKEN)
    nocturna_token_days_until_expiry.set(days_left or 0)
```

#### Health Check Endpoint
```python
# Add to your backend health check
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check Nocturna token
    try:
        days_left = check_token_expiration(SERVICE_TOKEN)
        if days_left is None:
            health_status["services"]["nocturna_token"] = "unknown"
        elif days_left <= 0:
            health_status["services"]["nocturna_token"] = "expired"
            health_status["status"] = "degraded"
        elif days_left <= 7:
            health_status["services"]["nocturna_token"] = "expiring_soon"
            health_status["status"] = "warning"
        else:
            health_status["services"]["nocturna_token"] = "healthy"
    except Exception:
        health_status["services"]["nocturna_token"] = "error"
        health_status["status"] = "degraded"
    
    return health_status
```

### 🔄 Token Renewal Best Practices

1. **Proactive Renewal**: Renew tokens before they expire (7-14 days before)
2. **Monitoring**: Set up alerts for token expiry
3. **Automation**: Use cron jobs or monitoring systems for automatic renewal
4. **Logging**: Log all token renewal activities
5. **Testing**: Test your renewal process in staging first
6. **Backup Plan**: Have manual renewal procedures documented
7. **Security**: Treat new tokens as secrets - rotate them securely

### 🚨 Emergency Token Recovery

If your token expires unexpectedly:

```bash
# 1. Immediate renewal
make docker-token-force-renew

# 2. Get the new token immediately
docker-compose exec app python scripts/renew_service_token.py --force

# 3. Update your backend configuration
# Update SERVICE_TOKEN environment variable in your backend

# 4. Restart your backend service
# systemctl restart your-backend-service

# 5. Verify connectivity
curl -H "Authorization: Bearer NEW_TOKEN" \
     http://localhost:8000/api/v1/health
```

The token management system ensures your service integration remains secure while providing multiple options for renewal and monitoring to prevent service disruptions.

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

### 😴 Lazy Admin Setup (Eternal Tokens + Nginx)

For admins who want to set it up once and forget about monthly token renewals:

#### Step 1: Generate Eternal Token
```bash
# Generate eternal service token
make docker-token-eternal

# Get the eternal token
cat deployment_summary.json
```

#### Step 2: Configure Nginx Protection
```nginx
# /etc/nginx/sites-available/nocturna
server {
    listen 80;
    server_name nocturna.internal.company.com;
    
    # Restrict to internal networks only
    allow 10.0.0.0/8;      # Internal corporate network
    allow 172.16.0.0/12;   # Docker networks
    allow 192.168.0.0/16;  # Local networks
    deny all;              # Block everything else
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Optional: Additional security headers
        proxy_set_header X-Frame-Options DENY;
        proxy_set_header X-Content-Type-Options nosniff;
    }
}
```

#### Step 3: Update docker-compose.yml (Optional)
```yaml
services:
  app:
    ports:
      # Bind only to localhost (nginx will proxy)
      - "127.0.0.1:8000:8000"
    # Remove external port exposure:
    # - "8000:8000"  # Delete this line
```

#### Step 4: Firewall Rules (Additional Security)
```bash
# Allow only nginx to access the API port
sudo ufw allow from 127.0.0.1 to any port 8000
sudo ufw deny 8000

# Allow nginx
sudo ufw allow 'Nginx Full'
```

#### Step 5: Update Your Backend
```python
# Your backend with eternal token
class NocturnaClient:
    def __init__(self):
        # Eternal token - no expiry monitoring needed!
        self.api_url = "http://nocturna.internal.company.com"
        self.headers = {
            "Authorization": f"Bearer {ETERNAL_SERVICE_TOKEN}",
            "Content-Type": "application/json"
        }
        
    def calculate_chart(self, birth_data):
        # No token expiry concerns! 🎉
        response = requests.post(
            f"{self.api_url}/api/v1/calculations/planetary-positions",
            headers=self.headers,
            json=birth_data
        )
        return response.json()
```

#### Benefits of Lazy Admin Setup:
- 😴 **No monthly renewals** - set it and forget it
- 🔒 **Secure** - nginx + firewall protection  
- 🚀 **Simple** - no token monitoring needed
- 🛡️ **Internal only** - no external exposure
- 🎯 **Perfect for corporate environments**

#### Monitoring (Optional but Recommended):
```bash
# Check eternal token status
make docker-token-check

# Should show: "♾️ Eternal token - no expiration concerns!"
```

---

## Summary

The Docker deployment provides a production-ready Nocturna Calculations service with:

✅ **One-command deployment**  
✅ **Secure service component mode**  
✅ **Automated admin and service user setup**  
✅ **Comprehensive token management**  
✅ **Health monitoring and logging**  
✅ **Easy integration with your main backend**  
✅ **Production security defaults**  

For support and troubleshooting, check the logs with `make docker-logs` and refer to the [main documentation](../README.md). 