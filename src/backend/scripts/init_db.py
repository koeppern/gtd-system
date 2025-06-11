#!/usr/bin/env python3
"""
Initialize database - create tables and run migrations
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.database import engine
from app.models.base import Base
from app.config import get_settings


async def create_tables():
    """Create all tables using SQLAlchemy"""
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import User, Field, Project, Task
        
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✓ Tables created successfully")


async def check_database_connection():
    """Check if we can connect to the database"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def init_default_fields():
    """Initialize default GTD fields"""
    from app.database import async_session_maker
    from app.crud.field import crud_field
    from app.schemas.field import FieldCreate
    
    default_fields = ["Private", "Work", "Unsorted"]
    
    async with async_session_maker() as db:
        for field_name in default_fields:
            # Check if field exists
            existing = await crud_field.get_by_name(db, name=field_name)
            if not existing:
                field_create = FieldCreate(
                    name=field_name,
                    description=f"Default {field_name} field"
                )
                await crud_field.create(db, obj_in=field_create)
                print(f"✓ Created field: {field_name}")
            else:
                print(f"- Field already exists: {field_name}")
        
        await db.commit()


def run_alembic_upgrade():
    """Run Alembic migrations"""
    alembic_cfg = Config("alembic.ini")
    
    # Update the database URL in alembic config
    settings = get_settings()
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url_asyncpg)
    
    print("Running Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    print("✓ Migrations completed")


async def main():
    """Main initialization function"""
    print("🚀 Initializing GTD Backend Database")
    print("=" * 50)
    
    # Check database connection
    if not await check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        return False
    
    # Create tables
    await create_tables()
    
    # Initialize default fields
    print("\nInitializing default fields...")
    await init_default_fields()
    
    print("\n✅ Database initialization complete!")
    print("\nYou can now:")
    print("- Run the backend: python run.py")
    print("- Create new migrations: alembic revision --autogenerate -m 'description'")
    print("- Apply migrations: alembic upgrade head")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)