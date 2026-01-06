# Service Integration Guide

This guide explains how to integrate Nocturna Calculations as a **service component** in your backend architecture.

## Table of Contents

- [Overview](#overview)
- [Architecture Patterns](#architecture-patterns)
- [Authentication & Security](#authentication--security)
- [Integration Patterns](#integration-patterns)
- [Error Handling](#error-handling)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Token Management](#token-management)
- [Performance Optimization](#performance-optimization)
- [Production Considerations](#production-considerations)

## Overview

Nocturna can be deployed as a **service component** that provides astrological calculations to your main backend via REST API calls. This pattern offers several advantages:

### Benefits of Service Component Architecture

- **🔗 Separation of Concerns**: Your backend handles user management, Nocturna handles calculations
- **📈 Scalability**: Independent scaling and deployment
- **🔒 Security**: Service-to-service authentication with long-lived tokens
- **🛠️ Maintainability**: Clear API boundaries and responsibilities
- **🚀 Performance**: Dedicated resources for calculation-intensive operations

### Service Component vs. Library

| Aspect | Service Component | Library Integration |
|--------|-------------------|-------------------|
| **Deployment** | Independent service | In-process library |
| **Scaling** | Independent scaling | Scales with main app |
| **Maintenance** | Separate updates | Coupled updates |
| **Network** | HTTP API calls | Direct function calls |
| **Resource Usage** | Dedicated resources | Shared resources |
| **Fault Isolation** | Service boundaries | Shared failure domain |

## Architecture Patterns

### Pattern 1: Microservice Integration

```
┌─────────────────┐    HTTP/REST    ┌──────────────────┐
│   Main Backend  │◄──────────────►│  Nocturna API    │
│   (User Mgmt)   │  Service Token  │  (Calculations)  │
│                 │                 │                  │
└─────────────────┘                 └──────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌──────────────────┐
│   Frontend      │                 │  PostgreSQL +    │
│   Client        │                 │  Redis           │
└─────────────────┘                 └──────────────────┘
```

**Use Case**: Clean separation between user management and calculations

### Pattern 2: API Gateway Integration

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Frontend      │◄──►│   API Gateway    │◄──►│  Main Backend    │
│   Client        │    │   (Routing)      │    │  (User Mgmt)     │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Nocturna API    │
                       │  (Calculations)  │
                       └──────────────────┘
```

**Use Case**: Centralized routing with gateway handling service token management

### Pattern 3: Event-Driven Integration

```
┌─────────────────┐    Events      ┌──────────────────┐
│   Main Backend  │◄──────────────►│   Event Bus      │
│                 │                │  (Redis/RabbitMQ)│
└─────────────────┘                └──────────────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Nocturna API    │
                                   │  (Async Worker)  │
                                   └──────────────────┘
```

**Use Case**: Asynchronous calculation processing with event-driven architecture

## Authentication & Security

### Service Token Authentication

Nocturna service component uses **30-day JWT tokens** for backend-to-backend authentication:

```python
import requests
from datetime import datetime
import jwt

class NocturnaServiceClient:
    def __init__(self, api_url, service_token):
        self.api_url = api_url.rstrip('/')
        self.service_token = service_token
        self.headers = {
            "Authorization": f"Bearer {service_token}",
            "Content-Type": "application/json",
            "User-Agent": "YourApp/1.0 (Nocturna-Integration)"
        }
    
    def health_check(self):
        """Check service health and token validity"""
        try:
            response = requests.get(
                f"{self.api_url}/health",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

### Token Security Best Practices

```python
import os
from cryptography.fernet import Fernet

class SecureTokenManager:
    def __init__(self):
        # Store encryption key in environment
        self.encryption_key = os.getenv('TOKEN_ENCRYPTION_KEY')
        self.fernet = Fernet(self.encryption_key)
    
    def store_token(self, token):
        """Encrypt and store service token"""
        encrypted_token = self.fernet.encrypt(token.encode())
        # Store in secure configuration or vault
        return encrypted_token
    
    def retrieve_token(self):
        """Retrieve and decrypt service token"""
        encrypted_token = self.get_encrypted_token_from_storage()
        return self.fernet.decrypt(encrypted_token).decode()
```

### Environment Configuration

```bash
# .env file for your main backend
NOCTURNA_API_URL=http://nocturna-api:8000
NOCTURNA_SERVICE_TOKEN=your_encrypted_service_token
NOCTURNA_TIMEOUT=30
NOCTURNA_MAX_RETRIES=3
```

## Integration Patterns

### Pattern 1: Synchronous API Calls

```python
class NocturnaClient:
    def __init__(self, api_url, service_token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {service_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def calculate_natal_chart(self, birth_data):
        """Calculate natal chart positions"""
        response = self.session.post(
            f"{self.api_url}/api/v1/calculations/planetary-positions",
            json={
                "date": birth_data["date"],
                "time": birth_data["time"],
                "latitude": birth_data["latitude"],
                "longitude": birth_data["longitude"],
                "timezone": birth_data["timezone"],
                "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS", 
                           "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"],
                "include_retrograde": True,
                "include_speed": True
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def calculate_aspects(self, birth_data, orb_multiplier=1.0):
        """Calculate planetary aspects"""
        response = self.session.post(
            f"{self.api_url}/api/v1/calculations/aspects",
            json={
                **birth_data,
                "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"],
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
                "orb_multiplier": orb_multiplier
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["data"]
```

### Pattern 2: Asynchronous Processing

```python
import asyncio
import aiohttp
from typing import List, Dict

class AsyncNocturnaClient:
    def __init__(self, api_url, service_token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {service_token}"}
    
    async def calculate_multiple_charts(self, birth_data_list: List[Dict]):
        """Calculate multiple charts concurrently"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [
                self._calculate_chart(session, birth_data)
                for birth_data in birth_data_list
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    async def _calculate_chart(self, session, birth_data):
        """Calculate single chart asynchronously"""
        async with session.post(
            f"{self.api_url}/api/v1/calculations/planetary-positions",
            json=birth_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]
            else:
                raise Exception(f"API error: {response.status}")
```

### Pattern 3: Caching Layer

```python
import redis
import json
import hashlib
from datetime import timedelta

class CachedNocturnaClient:
    def __init__(self, api_url, service_token, redis_url):
        self.nocturna = NocturnaClient(api_url, service_token)
        self.redis = redis.from_url(redis_url)
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
    
    def _generate_cache_key(self, endpoint, data):
        """Generate cache key from endpoint and data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(f"{endpoint}:{data_str}".encode())
        return f"nocturna:{hash_obj.hexdigest()}"
    
    def calculate_natal_chart(self, birth_data):
        """Calculate with caching"""
        cache_key = self._generate_cache_key("natal", birth_data)
        
        # Try cache first
        cached_result = self.redis.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Calculate and cache
        result = self.nocturna.calculate_natal_chart(birth_data)
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(result)
        )
        return result
```

## Error Handling

### Comprehensive Error Handling

```python
import requests
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class NocturnaAPIError(Exception):
    """Base exception for Nocturna API errors"""
    pass

class TokenExpiredError(NocturnaAPIError):
    """Raised when service token has expired"""
    pass

class RateLimitError(NocturnaAPIError):
    """Raised when rate limit is exceeded"""
    pass

class ServiceUnavailableError(NocturnaAPIError):
    """Raised when Nocturna service is unavailable"""
    pass

class RobustNocturnaClient:
    def __init__(self, api_url, service_token, max_retries=3):
        self.api_url = api_url
        self.service_token = service_token
        self.max_retries = max_retries
        self.headers = {"Authorization": f"Bearer {service_token}"}
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with retry logic and error handling"""
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method, url,
                    headers=self.headers,
                    timeout=30,
                    **kwargs
                )
                
                # Handle specific HTTP status codes
                if response.status_code == 401:
                    error_detail = response.json().get('error', {}).get('message', '')
                    if 'expired' in error_detail.lower():
                        raise TokenExpiredError(
                            "Service token has expired. "
                            "Please renew with: make docker-token-renew"
                        )
                    else:
                        raise NocturnaAPIError(f"Authentication failed: {error_detail}")
                
                elif response.status_code == 429:
                    if attempt < self.max_retries:
                        # Exponential backoff for rate limiting
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Rate limited, waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded after retries")
                
                elif response.status_code >= 500:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Server error, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ServiceUnavailableError(
                            f"Nocturna service unavailable: {response.status_code}"
                        )
                
                elif response.status_code >= 400:
                    error_data = response.json().get('error', {})
                    raise NocturnaAPIError(
                        f"API error {response.status_code}: {error_data.get('message')}"
                    )
                
                # Success
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    self.logger.warning(f"Timeout, retrying attempt {attempt + 1}")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise NocturnaAPIError("Request timeout after retries")
            
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    self.logger.warning(f"Connection error, retrying attempt {attempt + 1}")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise ServiceUnavailableError("Cannot connect to Nocturna service")
        
        raise NocturnaAPIError("Max retries exceeded")
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise ServiceUnavailableError("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
class ProtectedNocturnaClient(RobustNocturnaClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circuit_breaker = CircuitBreaker()
    
    @CircuitBreaker(failure_threshold=3, timeout=30)
    def calculate_natal_chart(self, birth_data):
        return super().calculate_natal_chart(birth_data)
```

## Monitoring & Health Checks

### Health Check Integration

```python
from fastapi import FastAPI, HTTPException
import jwt
from datetime import datetime

app = FastAPI()

class HealthChecker:
    def __init__(self, nocturna_client):
        self.nocturna_client = nocturna_client
    
    def check_nocturna_service(self):
        """Check Nocturna service health"""
        try:
            # Simple health check
            response = self.nocturna_client.health_check()
            return {
                "status": "healthy" if response else "unhealthy",
                "response_time": self._measure_response_time(),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def check_token_expiration(self):
        """Check service token expiration"""
        try:
            token = self.nocturna_client.service_token
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = payload.get('exp')
            
            if exp_timestamp:
                exp_date = datetime.fromtimestamp(exp_timestamp)
                days_left = (exp_date - datetime.now()).days
                
                if days_left <= 0:
                    return {"status": "expired", "days_left": days_left}
                elif days_left <= 7:
                    return {"status": "expiring_soon", "days_left": days_left}
                else:
                    return {"status": "healthy", "days_left": days_left}
            
            return {"status": "unknown", "error": "No expiration in token"}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

@app.get("/health")
async def health_check():
    """Application health check including Nocturna service"""
    health_checker = HealthChecker(nocturna_client)
    
    service_health = health_checker.check_nocturna_service()
    token_health = health_checker.check_token_expiration()
    
    overall_status = "healthy"
    if (service_health["status"] != "healthy" or 
        token_health["status"] in ["expired", "expiring_soon"]):
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "services": {
            "nocturna_api": service_health,
            "nocturna_token": token_health
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Create metrics
nocturna_requests_total = Counter(
    'nocturna_requests_total',
    'Total Nocturna API requests',
    ['method', 'endpoint', 'status']
)

nocturna_request_duration = Histogram(
    'nocturna_request_duration_seconds',
    'Nocturna API request duration'
)

nocturna_token_days_until_expiry = Gauge(
    'nocturna_token_days_until_expiry',
    'Days until Nocturna service token expires'
)

class MonitoredNocturnaClient(RobustNocturnaClient):
    def _make_request(self, method, endpoint, **kwargs):
        """Override to add monitoring"""
        start_time = time.time()
        
        try:
            response = super()._make_request(method, endpoint, **kwargs)
            status = "success"
            return response
        except Exception as e:
            status = "error"
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            nocturna_request_duration.observe(duration)
            nocturna_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
```

## Token Management

### Automated Token Monitoring

```python
import schedule
import time
import threading

class TokenMonitor:
    def __init__(self, nocturna_client, alert_callback=None):
        self.client = nocturna_client
        self.alert_callback = alert_callback
        self.running = False
    
    def check_token_expiry(self):
        """Check token expiration and alert if needed"""
        try:
            health = HealthChecker(self.client).check_token_expiration()
            days_left = health.get('days_left', 0)
            
            if days_left <= 7 and self.alert_callback:
                self.alert_callback(
                    f"Nocturna service token expires in {days_left} days. "
                    f"Please renew with: make docker-token-renew"
                )
                
        except Exception as e:
            if self.alert_callback:
                self.alert_callback(f"Token monitoring error: {e}")
    
    def start_monitoring(self):
        """Start background token monitoring"""
        if self.running:
            return
        
        # Schedule daily checks
        schedule.every().day.at("09:00").do(self.check_token_expiry)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(3600)  # Check every hour
        
        self.running = True
        monitor_thread = threading.Thread(target=run_scheduler, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
```

### Integration with Configuration Management

```python
class ConfigurableNocturnaClient:
    def __init__(self, config_manager):
        self.config = config_manager
        self._client = None
        self._token_last_updated = None
    
    @property
    def client(self):
        """Get client with current token"""
        current_token = self.config.get('NOCTURNA_SERVICE_TOKEN')
        
        if (self._client is None or 
            self._token_last_updated != current_token):
            self._client = RobustNocturnaClient(
                self.config.get('NOCTURNA_API_URL'),
                current_token
            )
            self._token_last_updated = current_token
        
        return self._client
    
    def refresh_token(self):
        """Refresh token from external source"""
        # This could integrate with your token renewal system
        new_token = self._fetch_new_token_from_nocturna()
        self.config.set('NOCTURNA_SERVICE_TOKEN', new_token)
        self._client = None  # Force recreation
```

## Performance Optimization

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedNocturnaClient:
    def __init__(self, api_url, service_token):
        self.api_url = api_url
        self.session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            "Authorization": f"Bearer {service_token}",
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        })
```

### Batch Processing

```python
async def calculate_charts_batch(self, birth_data_list, batch_size=10):
    """Process charts in batches to avoid overwhelming the service"""
    results = []
    
    for i in range(0, len(birth_data_list), batch_size):
        batch = birth_data_list[i:i + batch_size]
        
        # Process batch concurrently
        batch_results = await self.calculate_multiple_charts(batch)
        results.extend(batch_results)
        
        # Small delay between batches to be respectful
        await asyncio.sleep(0.1)
    
    return results
```

## Production Considerations

### Configuration Management

```python
# config.py
import os
from typing import Optional

class NocturnaConfig:
    def __init__(self):
        self.api_url = os.getenv('NOCTURNA_API_URL', 'http://nocturna-api:8000')
        self.service_token = os.getenv('NOCTURNA_SERVICE_TOKEN')
        self.timeout = int(os.getenv('NOCTURNA_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('NOCTURNA_MAX_RETRIES', '3'))
        self.cache_ttl = int(os.getenv('NOCTURNA_CACHE_TTL', '3600'))
        
        if not self.service_token:
            raise ValueError("NOCTURNA_SERVICE_TOKEN is required")
    
    def validate(self):
        """Validate configuration"""
        if not self.api_url.startswith(('http://', 'https://')):
            raise ValueError("Invalid NOCTURNA_API_URL format")
        
        if self.timeout <= 0:
            raise ValueError("NOCTURNA_TIMEOUT must be positive")
```

### Logging Configuration

```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class LoggingNocturnaClient(RobustNocturnaClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = structlog.get_logger("nocturna.client")
    
    def _make_request(self, method, endpoint, **kwargs):
        """Add structured logging to requests"""
        self.logger.info(
            "nocturna_request_start",
            method=method,
            endpoint=endpoint,
            api_url=self.api_url
        )
        
        start_time = time.time()
        try:
            response = super()._make_request(method, endpoint, **kwargs)
            
            self.logger.info(
                "nocturna_request_success",
                method=method,
                endpoint=endpoint,
                duration=time.time() - start_time,
                status_code=200
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "nocturna_request_error",
                method=method,
                endpoint=endpoint,
                duration=time.time() - start_time,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
```

### Testing Integration

```python
import pytest
from unittest.mock import Mock, patch

class TestNocturnaIntegration:
    @pytest.fixture
    def mock_nocturna_client(self):
        """Mock Nocturna client for testing"""
        with patch('your_app.nocturna.NocturnaClient') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            
            # Configure mock responses
            mock_instance.calculate_natal_chart.return_value = {
                "positions": [
                    {
                        "planet": "SUN",
                        "longitude": 359.5,
                        "sign": "PISCES",
                        "degree": 29
                    }
                ]
            }
            
            yield mock_instance
    
    def test_natal_chart_calculation(self, mock_nocturna_client):
        """Test natal chart calculation with mocked service"""
        # Your test code here
        pass
    
    def test_error_handling(self, mock_nocturna_client):
        """Test error handling"""
        mock_nocturna_client.calculate_natal_chart.side_effect = TokenExpiredError()
        
        # Test that your code handles token expiry correctly
        pass
```

## Summary

This guide covers the essential patterns for integrating Nocturna as a service component:

✅ **Authentication**: Service token management and security  
✅ **Error Handling**: Comprehensive error handling with retries  
✅ **Monitoring**: Health checks and metrics integration  
✅ **Performance**: Connection pooling and batch processing  
✅ **Production**: Configuration, logging, and testing  

For operational details on token management and service deployment, see the [Docker Deployment Guide](../deployment/docker.md).

For API reference and endpoint details, see the [API Specification](../api/specification.md). 