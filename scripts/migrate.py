"""
Database migration script
"""
import os
import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from nocturna_calculations.api.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if database is accessible"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_current_revision():
    """Get current database revision"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get current revision: {e}")
        return None

def run_migrations():
    """Run database migrations"""
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot proceed with migrations due to database connection issues")
        sys.exit(1)
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Get current revision
    current_rev = get_current_revision()
    logger.info(f"Current database revision: {current_rev}")
    
    # Get available revisions
    script = ScriptDirectory.from_config(alembic_cfg)
    head_rev = script.get_current_head()
    logger.info(f"Latest available revision: {head_rev}")
    
    if current_rev == head_rev:
        logger.info("Database is up to date")
        return
    
    try:
        # Run migrations
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 