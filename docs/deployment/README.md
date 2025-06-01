# Deployment Documentation

This directory contains comprehensive deployment guides for Nocturna Calculations.

## Available Deployment Methods

### 🐳 Docker Deployment (Recommended)

**Best for:** Production environments, service integration, easy setup

- **[Docker Deployment Guide](docker.md)** - Complete containerized deployment
- **Quick Setup:** `make docker-deploy`
- **Features:** Automated setup, health monitoring, service component mode
- **Prerequisites:** Docker 20.10+, Docker Compose 2.0+

### 🐍 Traditional Python Deployment

**Best for:** Development, custom environments, existing infrastructure

- **[Production Deployment Guide](production.md)** - Manual production setup
- **Quick Setup:** `make setup-prod`
- **Features:** Full control, custom configuration, existing infrastructure integration
- **Prerequisites:** Python 3.9+, PostgreSQL, Redis

## Deployment Comparison

| Feature | Docker | Traditional |
|---------|--------|-------------|
| **Setup Complexity** | ⭐⭐⭐⭐⭐ One command | ⭐⭐⭐ Multiple steps |
| **Isolation** | ⭐⭐⭐⭐⭐ Complete | ⭐⭐ Process level |
| **Portability** | ⭐⭐⭐⭐⭐ Any Docker host | ⭐⭐⭐ Python environments |
| **Resource Usage** | ⭐⭐⭐ Container overhead | ⭐⭐⭐⭐⭐ Native |
| **Monitoring** | ⭐⭐⭐⭐⭐ Built-in | ⭐⭐⭐ Manual setup |
| **Scaling** | ⭐⭐⭐⭐⭐ Container orchestration | ⭐⭐⭐ Manual |
| **Updates** | ⭐⭐⭐⭐⭐ Image updates | ⭐⭐⭐ Dependency management |

## Quick Start Matrix

### Development Environment
```bash
# Docker (if you want containerized dev)
make docker-deploy

# Traditional (recommended for development)
make setup-dev
conda activate nocturna-dev
make dev
```

### Production Environment
```bash
# Docker (recommended)
make docker-deploy

# Traditional
make setup-prod
conda activate nocturna-prod
```

### Testing Environment
```bash
# Docker
make docker-up && make docker-setup-production-dry

# Traditional
make setup-test
conda activate nocturna-test
make test-api
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

---

## Next Steps

1. **Choose your deployment method** based on your requirements
2. **Follow the specific guide** for your chosen method
3. **Configure for service integration** with your main backend
4. **Set up monitoring and backups** for production use
5. **Test the integration** with your application

For detailed instructions, see the specific deployment guides:

- 🐳 **[Docker Deployment Guide](docker.md)** - Recommended for most use cases
- 🐍 **[Traditional Deployment Guide](production.md)** - For custom environments 