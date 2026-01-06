# Database Initialization Scripts

This directory contains SQL scripts that are automatically executed when the PostgreSQL container starts for the first time.

## How it works

- Scripts in this directory are mounted to `/docker-entrypoint-initdb.d/` in the PostgreSQL container
- PostgreSQL automatically executes `.sql` and `.sh` files in alphabetical order during initialization
- This only happens when the database is created for the first time (when the data volume is empty)

## Usage

Place any initialization scripts here:

```
scripts/db_init/
├── 01-create-extensions.sql    # Create required PostgreSQL extensions
├── 02-create-users.sql         # Create additional database users
├── 03-setup-permissions.sql    # Set up permissions
└── 99-seed-data.sql           # Insert initial data (optional)
```

## Example Scripts

### Create Extensions (01-create-extensions.sql)
```sql
-- Create required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

### Create Read-Only User (02-create-readonly-user.sql)
```sql
-- Create read-only user for reporting/monitoring
CREATE USER nocturna_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE nocturna TO nocturna_readonly;
GRANT USAGE ON SCHEMA public TO nocturna_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO nocturna_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO nocturna_readonly;
```

## Notes

- **Security**: Be careful with passwords in SQL files. Consider using environment variables.
- **Ordering**: Files are executed in alphabetical order. Use numeric prefixes to control execution order.
- **One-time only**: These scripts only run during initial database creation.
- **Logs**: Check container logs if scripts fail: `docker-compose logs db`

## Current Status

This directory is currently empty. Add initialization scripts as needed for your deployment.

The main database schema and migrations are handled by Alembic through the application, not through these initialization scripts. 