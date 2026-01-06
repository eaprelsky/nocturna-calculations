# Admin Setup Guide - Nocturna Calculations

## Overview

Nocturna Calculations includes a role-based admin system where certain users can have administrative privileges (`is_superuser = True`). This guide explains how to set up and manage admin users.

## Prerequisites

- Database must be set up and migrations applied
- You should have your environment activated (`conda activate nocturna-dev`)
- PostgreSQL should be running

## Quick Start

### 1. Create Your First Admin User

```bash
# Using Make (recommended)
make admin-create

# Or directly
python scripts/create_admin.py create
```

This will interactively prompt you for:
- Email address
- Username  
- First name (optional)
- Last name (optional)
- Password (hidden input)

### 2. Verify Admin Creation

```bash
# List all admin users
make admin-list

# Or directly
python scripts/create_admin.py list
```

## Admin Management Commands

### Using Make Commands (Recommended)

```bash
# Create new admin user
make admin-create

# Promote existing user to admin
make admin-promote  

# List all admin users
make admin-list
```

### Using Script Directly

```bash
# Create new admin user
python scripts/create_admin.py create

# Promote existing user to admin  
python scripts/create_admin.py promote

# List all admin users
python scripts/create_admin.py list

# Non-interactive usage
python scripts/create_admin.py [create|promote|list]
```

## Getting Bearer Token for External API Access

### 1. Login to Get Bearer Token

Once you have created your admin user, you need to login to get a bearer token for API access:

```bash
# Using curl (replace with your admin credentials)
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=your_admin_password"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 900
}
```

### 2. Use the Bearer Token

Copy the `access_token` from the response and use it in your API requests:

```bash
# Example API call with bearer token
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 3. Token Refresh

Access tokens expire (default: 15 minutes). Use the refresh token to get a new access token:

```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token_here"}'
```

## API Endpoints for Admin

### Check Current User Info
```http
GET /api/auth/me
Authorization: Bearer <token>
```

Response includes `is_superuser` field:
```json
{
  "id": "uuid",
  "email": "admin@example.com", 
  "username": "admin",
  "first_name": "Admin",
  "last_name": "User",
  "is_superuser": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Verify Admin Access
```http
GET /api/auth/admin/verify
Authorization: Bearer <admin-token>
```

Success (200):
```json
{
  "is_admin": true,
  "user_id": "uuid",
  "email": "admin@example.com",
  "username": "admin" 
}
```

Forbidden (403):
```json
{
  "detail": "Admin privileges required"
}
```

## Database Fields

The `users` table includes these admin-related fields:

- `is_active` (Boolean): User account is active
- `is_superuser` (Boolean): User has admin privileges

## Security Considerations

### Production Setup

1. **Strong Passwords**: Ensure admin accounts use strong, unique passwords
2. **Limited Admin Accounts**: Only create admin accounts for users who need them
3. **Regular Auditing**: Periodically review admin users with `make admin-list`
4. **Environment Variables**: Ensure `SECRET_KEY` is set to a secure value in production

### Admin Authentication Flow

1. Admin logs in normally via `/api/auth/login`
2. Frontend checks `/api/auth/me` to see if user has `is_superuser: true`
3. Admin features can verify access via `/api/auth/admin/verify`
4. All admin endpoints should use `get_current_admin_user` dependency

## Troubleshooting

### "Failed to connect to database"
- Ensure PostgreSQL is running: `make services-start`
- Check your `.env` file has correct `DATABASE_URL`
- Verify you're in the correct conda environment

### "User already exists"
- Check existing users: `make admin-list`
- Use `make admin-promote` to promote existing user instead

### "No Nocturna environment active"
- Activate your environment: `conda activate nocturna-dev`
- Or set up environment: `make setup-dev`

### "401 Unauthorized" when getting token
- Verify your admin credentials are correct
- Ensure the API server is running: `make dev-server`
- Check that you're using the correct login endpoint URL
- Verify the admin user was created successfully: `make admin-list`

### "Token expired" errors
- Access tokens expire after 15 minutes by default
- Use the refresh token to get a new access token
- For long-running scripts, implement token refresh logic

## Service Token System (Recommended for Production)

For production deployments and backend integration, we recommend using **service tokens** instead of login-based authentication. Service tokens provide:

- ✅ **Long-lived authentication** (30-365 days or eternal)
- ✅ **Automatic token refresh** via client library
- ✅ **No interactive login required**
- ✅ **Secure token management**
- ✅ **Audit trail and usage tracking**

### 1. Create Service Token

```bash
# Create 30-day service token
make service-token-create

# Create 90-day service token
make service-token-create-custom DAYS=90

# Create eternal token (never expires - use with caution)
make service-token-create-eternal
```

### 2. Use Service Token in Your Application

#### Environment Variable Setup
```bash
# Add to your .env file
export NOCTURNA_SERVICE_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
export NOCTURNA_API_URL="http://localhost:8000"
```

#### Python Client (Recommended)
```python
from nocturna_calculations.client import NocturnaClient

# Client with automatic token refresh
client = NocturnaClient(
    service_token=os.getenv("NOCTURNA_SERVICE_TOKEN"),
    api_url=os.getenv("NOCTURNA_API_URL"),
    auto_refresh=True  # Handles token refresh automatically
)

# Make API calls - client handles authentication
result = client.calculate_planetary_positions(
    date="2024-01-01",
    time="12:00:00",
    latitude=55.7558,
    longitude=37.6173,
    timezone="Europe/Moscow"
)
```

#### Manual Token Refresh
```python
import requests
import os

# For custom implementations
service_token = os.getenv("NOCTURNA_SERVICE_TOKEN")

# Get fresh access token
response = requests.post(
    f"{os.getenv('NOCTURNA_API_URL')}/api/auth/service-token/refresh",
    headers={"Authorization": f"Bearer {service_token}"}
)

access_token = response.json()["access_token"]

# Use access token for API calls
headers = {"Authorization": f"Bearer {access_token}"}
```

### 3. Service Token Management

```bash
# List all service tokens
make service-token-list

# Check token validity
make service-token-check TOKEN="your_token_here"

# Revoke a token
make service-token-revoke TOKEN_ID="token_id_here"
```

### 4. Token Refresh Architecture

The service token system uses a **two-tier approach**:

1. **Service Token** (long-lived): Stored in environment, used for authentication
2. **Access Token** (short-lived): Generated on-demand, used for API calls

```mermaid
graph LR
    A[Service Token<br/>30-365 days] --> B[Refresh Endpoint]
    B --> C[Access Token<br/>15 minutes]
    C --> D[API Calls]
    
    E[Client Library] --> F[Auto-Refresh Logic]
    F --> B
```

This provides the **security of short-lived tokens** with the **convenience of long-lived authentication**.

## Next Steps

After setting up authentication, you might want to:

1. **Service Tokens**: Set up service tokens for production backend integration
2. **Client Library**: Use the Python client library for automatic token management
3. **Admin Endpoints**: Add admin-only API endpoints using the `get_current_admin_user` dependency
4. **Frontend Admin UI**: Build admin dashboard in your frontend application
5. **User Management**: Add endpoints for admins to manage other users
6. **System Monitoring**: Add admin endpoints for system health and metrics

## Example: Adding Admin-Only Endpoint

```python
from fastapi import Depends
from nocturna_calculations.api.routers.auth import get_current_admin_user

@router.get("/admin/users")
async def list_all_users(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to list all users"""
    users = db.query(User).all()
    return users
```

## Support

If you encounter issues with admin setup:

1. Check the logs for detailed error messages
2. Verify your database connection
3. Ensure all migrations are applied: `make db-migrate`
4. Contact the development team with specific error messages 