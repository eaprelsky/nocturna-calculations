# Service Token Management Guide

## Overview

Service tokens provide secure, long-lived authentication for backend-to-backend integration with the Nocturna Calculations API. This guide covers the complete process from setup to usage.

## Prerequisites

- ✅ Database setup and migrations applied (`alembic upgrade head`)
- ✅ Admin user created
- ✅ API server running (`make dev`)
- ✅ Environment activated (`conda activate nocturna-dev`)

## Quick Start

### 1. Create Admin User (If Not Done)

```bash
# Create your first admin user
make admin-create

# Verify admin creation
make admin-list
```

### 2. Create Service Token

```bash
# Create 30-day service token (default)
make service-token-create

# Create custom duration token
make service-token-create-custom DAYS=90

# Create eternal token (never expires - use with caution)
make service-token-create-eternal
```

### 3. Get Your Token

The `create` command will display your JWT token:

```
🔐 SERVICE TOKEN:
--------------------------------------------------------------------------------
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZGZlNzI3Yy1jZjA0LTQwNjEtOTE2Yy0wNzQ1ZTk4NjMyNGYiLCJ0eXBlIjoic2VydmljZSIsInNjb3BlIjoiY2FsY3VsYXRpb25zIiwidG9rZW5faWQiOiJjOWRmMGJhMi02ZjhkLTQwM2ItOTFjMi1mZWE2YzIxYTg3ZTEiLCJleHAiOjE3NTE4ODY1NDd9.EuDouOSdbQ6ksGjSaCD1XA_MZ4vjvF2TUgdtIQ2otJ8
--------------------------------------------------------------------------------
```

**Copy this token** - you'll need it for API authentication.

### 4. Use Your Token

```bash
# Set environment variable
export NOCTURNA_SERVICE_TOKEN="your_token_here"

# Test API call
curl -H "Authorization: Bearer $NOCTURNA_SERVICE_TOKEN" \
     http://localhost:8000/api/charts
```

## Detailed Process

### Step 1: Admin User Setup

Service tokens can only be created by admin users. If you don't have an admin user:

```bash
# Interactive admin creation
python scripts/create_admin.py create
```

You'll be prompted for:
- Email address
- Username
- First name (optional)
- Last name (optional)
- Password (hidden input)

**Verify admin creation:**
```bash
python scripts/create_admin.py list
```

### Step 2: Service Token Creation

#### Using Make Commands (Recommended)

```bash
# Standard 30-day token
make service-token-create

# Custom duration (example: 90 days)
make service-token-create-custom DAYS=90

# Eternal token (never expires)
make service-token-create-eternal
```

#### Using Script Directly

```bash
# Standard token
python scripts/manage_service_tokens.py create

# Custom duration
python scripts/manage_service_tokens.py create --days 90

# Custom scope
python scripts/manage_service_tokens.py create --scope "calculations,admin"

# Eternal token
python scripts/manage_service_tokens.py create --eternal
```

#### Token Creation Output

When successful, you'll see:

```
✅ Service token created successfully!

Token ID:     c9df0ba2-6f8d-403b-91c2-fea6c21a87e1
Scope:        calculations
Expires:      2025-07-07 11:09:07 (30 days)
Created by:   admin@example.com

🔐 SERVICE TOKEN:
--------------------------------------------------------------------------------
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZGZlNzI3Yy1jZjA0LTQwNjEtOTE2Yy0wNzQ1ZTk4NjMyNGYiLCJ0eXBlIjoic2VydmljZSIsInNjb3BlIjoiY2FsY3VsYXRpb25zIiwidG9rZW5faWQiOiJjOWRmMGJhMi02ZjhkLTQwM2ItOTFjMi1mZWE2YzIxYTg3ZTEiLCJleHAiOjE3NTE4ODY1NDd9.EuDouOSdbQ6ksGjSaCD1XA_MZ4vjvF2TUgdtIQ2otJ8
--------------------------------------------------------------------------------

💡 Usage in your application:
   export NOCTURNA_SERVICE_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Important:** Copy the JWT token from between the dashes - this is what you'll use for authentication.

### Step 3: Token Management

#### List All Tokens

```bash
# Using Make
make service-token-list

# Using script
python scripts/manage_service_tokens.py list
```

Output:
```
Found 2 service token(s):

  ID: c9df0ba2-6f8d-403b-91c2-fea6c21a87e1
  Status: ✅ ACTIVE (29 days left)
  Scope: calculations
  Created: 2025-06-07 11:09:07
  Created by: admin@example.com
  Last used: Never

  ID: 12b3b5cb-0cef-4234-82b0-018b8378d33f
  Status: ⚠️  EXPIRES IN 5 DAYS
  Scope: calculations
  Created: 2025-06-07 11:08:29
  Created by: admin@example.com
  Last used: 2025-06-07 14:30:15
```

#### Check Token Validity

```bash
# Using Make
make service-token-check TOKEN="your_token_here"

# Using script
python scripts/manage_service_tokens.py check "your_token_here"
```

#### Revoke Token

```bash
# Using Make
make service-token-revoke TOKEN_ID="c9df0ba2-6f8d-403b-91c2-fea6c21a87e1"

# Using script
python scripts/manage_service_tokens.py revoke c9df0ba2-6f8d-403b-91c2-fea6c21a87e1
```

## Usage Examples

### Environment Variable Setup

```bash
# Add to your .env file or shell profile
export NOCTURNA_SERVICE_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export NOCTURNA_API_URL="http://localhost:8000"
```

### Python Client (Recommended)

```python
import os
from nocturna_calculations.client import NocturnaClient

# Initialize client with automatic token refresh
client = NocturnaClient(
    service_token=os.getenv("NOCTURNA_SERVICE_TOKEN"),
    api_url=os.getenv("NOCTURNA_API_URL"),
    auto_refresh=True
)

# Make API calls - authentication handled automatically
result = client.calculate_planetary_positions(
    date="2024-01-01",
    time="12:00:00",
    latitude=55.7558,
    longitude=37.6173,
    timezone="Europe/Moscow"
)
```

### Direct HTTP Requests

```bash
# Using curl
curl -H "Authorization: Bearer $NOCTURNA_SERVICE_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/calculations/planetary-positions \
     -d '{
       "date": "2024-01-01",
       "time": "12:00:00",
       "latitude": 55.7558,
       "longitude": 37.6173,
       "timezone": "Europe/Moscow",
       "planets": ["SUN", "MOON", "MERCURY"]
     }'
```

```python
# Using requests
import requests
import os

headers = {
    "Authorization": f"Bearer {os.getenv('NOCTURNA_SERVICE_TOKEN')}",
    "Content-Type": "application/json"
}

response = requests.get(
    "http://localhost:8000/api/charts",
    headers=headers
)
```

## Troubleshooting

### Common Issues

#### 1. "No admin user found"

```bash
# Solution: Create admin user first
make admin-create
```

#### 2. "Failed to connect to database"

```bash
# Check database is running
make services-start

# Check environment
conda activate nocturna-dev

# Check migrations
alembic upgrade head
```

#### 3. "Token not displayed after creation"

The token is only shown once during creation. If you missed it:

```bash
# Create a new token
python scripts/manage_service_tokens.py create

# Revoke the old one if needed
python scripts/manage_service_tokens.py revoke old_token_id
```

#### 4. "401 Unauthorized" with token

```bash
# Check token validity
python scripts/manage_service_tokens.py check "$NOCTURNA_SERVICE_TOKEN"

# Check token format (should start with "eyJ")
echo $NOCTURNA_SERVICE_TOKEN

# Verify API server is running
curl http://localhost:8000/health
```

## Related Documentation

- **[Admin Setup Guide](../installation/admin-setup.md)** - Setting up admin users
- **[Service Integration Guide](service-integration.md)** - Backend integration patterns
- **[API Reference](../api/)** - Complete API documentation
- **[Testing Guide](../testing-guide.md)** - Testing with service tokens

## Support

For additional help:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Review the [API documentation](../api/)
3. Run tests to verify setup: `make test-service-tokens`
4. Contact the development team with specific error messages 