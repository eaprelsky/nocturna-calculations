# Deployment Documentation

This directory contains comprehensive deployment guides for Nocturna Calculations.

## Available Deployment Methods

### 🐳 Docker Deployment (Recommended)

**Best for:** Production environments, service integration, easy setup

- **[Docker Deployment Guide](docker.md)** - Complete containerized deployment
- **[Blue-Green Deployment](blue-green-deployment.md)** - Zero-downtime production updates
- **Quick Setup:** `./scripts/deploy.sh staging` (staging) or `./scripts/deploy.sh blue` (production)
- **Features:** Automated setup, health monitoring, blue-green deployment, multi-layer caching
- **Prerequisites:** Docker 20.10+, Docker Compose 2.0+

### 📦 Deployment Environments

We support three deployment environments:

1. **Staging** - Single instance for testing (`docker-compose.staging.yml`)
2. **Production Blue** - Active production slot (`docker-compose.production.blue.yml`)
3. **Production Green** - Standby production slot for zero-downtime updates (`docker-compose.production.green.yml`)

### 🐍 Traditional Python Deployment

**Best for:** Development, custom environments, existing infrastructure

- **[Production Deployment Guide](production.md)** - Manual production setup
- **Quick Setup:** `make setup-prod`
- **Features:** Full control, custom configuration, existing infrastructure integration
- **Prerequisites:** Python 3.9+, PostgreSQL, Redis

## Deployment Comparison

| Feature | Docker (Blue-Green) | Docker (Basic) | Traditional |
|---------|---------------------|----------------|-------------|
| **Setup Complexity** | ⭐⭐⭐⭐ Automated scripts | ⭐⭐⭐⭐⭐ One command | ⭐⭐⭐ Multiple steps |
| **Zero Downtime** | ⭐⭐⭐⭐⭐ Blue-green switch | ⭐ Manual restart | ⭐ Manual restart |
| **Rollback Speed** | ⭐⭐⭐⭐⭐ Instant (~5s) | ⭐⭐ Rebuild required | ⭐⭐ Rebuild required |
| **Isolation** | ⭐⭐⭐⭐⭐ Complete | ⭐⭐⭐⭐⭐ Complete | ⭐⭐ Process level |
| **Portability** | ⭐⭐⭐⭐⭐ Any Docker host | ⭐⭐⭐⭐⭐ Any Docker host | ⭐⭐⭐ Python environments |
| **Resource Usage** | ⭐⭐ Dual slots | ⭐⭐⭐ Container overhead | ⭐⭐⭐⭐⭐ Native |
| **Build Speed** | ⭐⭐⭐⭐⭐ Multi-layer cache | ⭐⭐⭐⭐ Basic cache | ⭐⭐⭐ Dependency management |
| **Production Ready** | ⭐⭐⭐⭐⭐ Enterprise-grade | ⭐⭐⭐⭐ Good | ⭐⭐⭐ Manual setup |

## Quick Start Matrix

### Staging Environment
```bash
# Prepare configuration
cp config/staging.env.example config/staging.env
vim config/staging.env  # Edit with your values

# Deploy staging
./scripts/deploy.sh staging

# Access: http://localhost:8100
```

### Production Environment (Blue-Green)
```bash
# Prepare configuration
cp config/production.env.example config/production.env
vim config/production.env  # Edit with your values

# Initial deployment (blue slot)
./scripts/deploy.sh blue

# Check status
./scripts/status.sh

# Zero-downtime update workflow:
# 1. Deploy to green
./scripts/deploy.sh green

# 2. Test green
curl http://localhost:18201/health

# 3. Switch traffic
./scripts/switch.sh green

# 4. Rollback if needed
./scripts/rollback.sh
```

### Development Environment
```bash
# Docker (development mode)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# Traditional (recommended for development)
make setup-dev
conda activate nocturna-dev
make dev
```

## Service Integration Architecture

### As a Service Component

Nocturna is designed to be deployed as a **service component** that integrates with your main backend:

```
┌─────────────────┐    API calls    ┌──────────────────┐
│   Your Main     │◄──────────────►│  Nocturna API    │
│   Backend       │  (JWT token)    │  (Calculations)  │
│                 │                 │                  │
└─────────────────┘                 └──────────────────┘
         │                                   │
         │ User requests                     │ Database
         ▼                                   ▼
┌─────────────────┐                 ┌──────────────────┐
│   Frontend      │                 │   PostgreSQL     │
│   Application   │                 │   + Redis        │
└─────────────────┘                 └──────────────────┘
```

### Configuration for Service Mode

Both deployment methods support service component configuration:

- **Disabled user registration** - Your main backend manages users
- **Admin access** - For system administration
- **Service token** - Long-lived token for backend API access
- **Rate limiting** - Configurable per your needs
- **CORS setup** - For your specific domains

## Environment Configuration

### Docker Environment Variables

Set in `.env` file:
```bash
# Security
SECRET_KEY=your_32_char_secret
ADMIN_PASSWORD=secure_admin_password
POSTGRES_PASSWORD=secure_db_password

# Service Component Mode
ALLOW_USER_REGISTRATION=false
MAX_USERS_LIMIT=100

# Integration
CORS_ORIGINS=["https://your-backend.com"]
```

### Traditional Environment Variables

Set in Conda environment or system:
```bash
export DATABASE_URL="postgresql://user:pass@localhost/nocturna"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your_secret_key"
```

## Security Considerations

### Production Security Checklist

- [ ] **Strong secrets** - Generate secure SECRET_KEY and passwords
- [ ] **Network isolation** - Use internal networks where possible
- [ ] **HTTPS/TLS** - Set up reverse proxy with SSL certificates
- [ ] **Firewall rules** - Restrict access to necessary ports only
- [ ] **User management** - Disable registration, use service tokens
- [ ] **Updates** - Keep dependencies and base images updated
- [ ] **Monitoring** - Set up logging and health monitoring
- [ ] **Backups** - Regular database and configuration backups

### Docker Security

- Non-root container execution
- Multi-stage builds for minimal attack surface
- Health checks for service monitoring
- Secret management via environment variables
- Network isolation between services

### Traditional Security

- Virtual environment isolation
- System user with minimal privileges
- Service management with systemd
- Log rotation and monitoring
- Database connection security

## Monitoring and Maintenance

### Health Checks

```bash
# Docker
curl http://localhost:8000/health
make docker-status

# Traditional  
curl http://localhost:8000/health
systemctl status nocturna-api
```

### Logs

```bash
# Docker
make docker-logs
docker-compose logs -f app

# Traditional
tail -f /var/log/nocturna/api.log
journalctl -u nocturna-api -f
```

### Updates

```bash
# Docker
docker-compose pull
make docker-restart

# Traditional
conda activate nocturna-prod
pip install --upgrade nocturna-calculations
systemctl restart nocturna-api
```

## Troubleshooting

### Common Issues

1. **Port conflicts** - Check if ports 8000, 5432, 6379 are available
2. **Database connection** - Verify PostgreSQL is running and accessible
3. **Redis connection** - Ensure Redis is running and accessible
4. **JWT errors** - Check SECRET_KEY is set and consistent
5. **CORS issues** - Verify CORS_ORIGINS includes your frontend domain

### Getting Help

- **Docker logs:** `make docker-logs`
- **Service status:** `make docker-status` or `systemctl status`
- **Configuration check:** Review `.env` file or environment variables
- **API health:** `curl http://localhost:8000/health`

### Debug Mode

```bash
# Docker
docker-compose exec app python -c "from nocturna_calculations.api.config import settings; print(settings)"

# Traditional
python -c "from nocturna_calculations.api.config import settings; print(settings)"
```

## Multi-Layer Docker Build Strategy

Our Dockerfile uses an optimized multi-stage build with three distinct layers for maximum caching efficiency:

### Layer 1: Base OS (Cached Long-Term)
- Operating system packages
- System dependencies
- Rarely changes (~once per month)
- **Rebuild time:** 5 minutes

### Layer 2: Python Dependencies (Cached Medium-Term)
- Python packages from `requirements.txt`
- Changes when dependencies update (~weekly)
- **Rebuild time:** 2 minutes

### Layer 3: Application Code (Changes Frequently)
- Your application code
- Changes with every deployment (~daily)
- **Rebuild time:** 5 seconds

### Benefits
- **Fast rebuilds:** Only application layer rebuilds on code changes (5 seconds)
- **Efficient CI/CD:** Cache reuse across builds
- **Bandwidth savings:** Download base layers once

---

## Next Steps

1. **Choose your deployment method** based on your requirements
2. **Follow the specific guide** for your chosen method
3. **Configure for service integration** with your main backend
4. **Set up monitoring and backups** for production use
5. **Test the integration** with your application

For detailed instructions, see the specific deployment guides:

- 🐳 **[Docker Deployment Guide](docker.md)** - Recommended for most use cases
- 🔄 **[Blue-Green Deployment](blue-green-deployment.md)** - Zero-downtime production updates
- 🐍 **[Traditional Deployment Guide](production.md)** - For custom environments 