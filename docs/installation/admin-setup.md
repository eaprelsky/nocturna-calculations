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

## Next Steps

After creating admin users, you might want to:

1. **Create Admin Endpoints**: Add admin-only API endpoints using the `get_current_admin_user` dependency
2. **Frontend Admin UI**: Build admin dashboard in your frontend application
3. **User Management**: Add endpoints for admins to manage other users
4. **System Monitoring**: Add admin endpoints for system health and metrics

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