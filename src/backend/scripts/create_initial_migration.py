#!/usr/bin/env python3
"""
Create initial Alembic migration for the GTD database schema
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from app.config import get_settings


def create_initial_migration():
    """Create the initial Alembic migration"""
    # Get alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Update the database URL in alembic config
    settings = get_settings()
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url_asyncpg)
    
    print("Creating initial migration...")
    
    # Generate the migration
    command.revision(
        alembic_cfg,
        autogenerate=True,
        message="Initial GTD schema with users, fields, projects, and tasks"
    )
    
    print("✓ Initial migration created")
    print("\nTo apply the migration, run:")
    print("  alembic upgrade head")
    print("\nOr use the init_db.py script to set up everything at once:")
    print("  python scripts/init_db.py")


if __name__ == "__main__":
    create_initial_migration()