# Installation Guide

## Prerequisites
- **WSL** (Windows Subsystem for Linux) with Ubuntu/Debian
- **Conda** or Miniconda installed
- PostgreSQL and Redis (will be installed automatically if missing)

---

## Installation Steps

### 1. Run the Main Setup Script
```bash
python scripts/install_dev.py
```
This will:
- Install PostgreSQL and Redis (if not present).
- Prompt for database credentials (name, user, password, host, port).
- Create a `.env` file with your credentials.
- Set up a Conda environment (`nocturna`) and install dependencies.

**⚠️ Important**: When prompted for PostgreSQL password, you **MUST** provide a non-empty password. Setting an empty password will cause the installation to fail.

### 2. Automatic Dependency Installation
The script calls `install_dependencies.py` to:
- Verify and install required Python packages:
  - `psycopg2-binary` (PostgreSQL)
  - `redis` (Redis client)
  - `alembic` (migrations)
  - `sqlalchemy` (database ORM)
  - `prometheus-client` (metrics)

### 3. Database Setup
- Initializes Alembic for migrations.
- Updates `alembic.ini` with the database URL from `.env`.
- Runs initial migrations.

### 4. Post-Installation Verification
- Check database connection status:
  ```bash
  ./scripts/setup_db.sh status
  ```
- Re-run migrations if needed:
  ```bash
  ./scripts/setup_db.sh migrate
  ```

---

## Post-Setup
- Activate the Conda environment:
  ```bash
  conda activate nocturna
  ```
- Start the application:
  ```bash
  python -m nocturna_calculations.api.app
  ```

---

## Notes
- **PostgreSQL Password Required**: You must provide a non-empty PostgreSQL password during installation. Empty passwords will cause installation failure.
- **Troubleshooting**: Check terminal logs for errors during setup.
- **Manual Override**: To skip interactive prompts, modify `install_dev.py`.

---

## Dependency Management
All Python dependencies are centralized in:
- `scripts/install_dependencies.py` (core packages)
- `requirements.txt` (project-specific packages)