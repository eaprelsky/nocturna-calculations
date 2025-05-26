"""
Database migration script
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from alembic.config import Config
from alembic import command

def run_migrations():
    """Run database migrations"""
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    run_migrations() 