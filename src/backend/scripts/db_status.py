#!/usr/bin/env python3
"""
Check database status and show table information
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine
from app.config import get_settings


async def check_database_status():
    """Check database connection and show status"""
    print("🔍 Checking GTD Database Status")
    print("=" * 40)
    
    settings = get_settings()
    print(f"Database URL: {settings.database_url_asyncpg}")
    print(f"Environment: {settings.app.environment}")
    print()
    
    try:
        async with engine.connect() as conn:
            # Test connection
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Database connection: OK")
            
            # Check if tables exist
            inspector = inspect(conn.sync_engine)
            tables = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
            
            expected_tables = ["gtd_users", "gtd_fields", "gtd_projects", "gtd_tasks"]
            
            print("\n📊 Table Status:")
            for table in expected_tables:
                if table in tables:
                    # Get row count
                    count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f"  ✓ {table}: {count} rows")
                else:
                    print(f"  ❌ {table}: NOT FOUND")
            
            # Check for additional tables
            other_tables = [t for t in tables if t not in expected_tables and not t.startswith('alembic_')]
            if other_tables:
                print(f"\n📋 Other tables: {', '.join(other_tables)}")
            
            # Check Alembic version
            if "alembic_version" in tables:
                version_result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                version = version_result.fetchone()
                if version:
                    print(f"\n🔄 Alembic version: {version[0]}")
                else:
                    print("\n🔄 Alembic: No migrations applied")
            else:
                print("\n🔄 Alembic: Not initialized")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    print("\n" + "=" * 40)
    return True


async def show_sample_data():
    """Show sample data from each table"""
    print("\n📋 Sample Data:")
    print("-" * 20)
    
    try:
        async with engine.connect() as conn:
            tables = ["gtd_users", "gtd_fields", "gtd_projects", "gtd_tasks"]
            
            for table in tables:
                try:
                    result = await conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                    rows = await result.fetchall()
                    
                    if rows:
                        print(f"\n{table}:")
                        for i, row in enumerate(rows, 1):
                            print(f"  {i}. ID: {row[0]}")
                    else:
                        print(f"\n{table}: (empty)")
                        
                except Exception as e:
                    print(f"\n{table}: Error - {e}")
                    
    except Exception as e:
        print(f"Error fetching sample data: {e}")


async def main():
    """Main function"""
    success = await check_database_status()
    
    if success:
        await show_sample_data()
        
        print("\n💡 Available commands:")
        print("  python scripts/init_db.py          - Initialize database")
        print("  python scripts/create_initial_migration.py - Create first migration")
        print("  alembic upgrade head               - Apply migrations")
        print("  alembic revision --autogenerate    - Create new migration")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)