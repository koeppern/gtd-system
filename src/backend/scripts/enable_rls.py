#!/usr/bin/env python3
"""
Script to re-enable RLS on GTD tables after testing
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings


async def enable_rls_on_tables():
    """Re-enable RLS on all GTD tables"""
    
    # List of GTD tables to enable RLS on
    tables = [
        'gtd_projects',
        'gtd_tasks', 
        'gtd_fields',
        'gtd_users'
    ]
    
    print("🔐 Re-enabling RLS on GTD Tables")
    print("=" * 40)
    
    settings = get_settings()
    print(f"Database URL: {settings.database_url_asyncpg}")
    print(f"Environment: {settings.app.environment}")
    print()
    
    try:
        # Create database engine from settings
        engine = create_async_engine(settings.database_url_asyncpg)
        
        async with engine.connect() as conn:
            # Test connection first
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Database connection: OK")
            print()
            
            success_count = 0
            
            for table in tables:
                print(f"Enabling RLS on table: {table}")
                
                try:
                    # First check if table exists
                    check_query = text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = :table_name
                        )
                    """)
                    
                    exists_result = await conn.execute(check_query, {"table_name": table})
                    table_exists = exists_result.fetchone()[0]
                    
                    if not table_exists:
                        print(f"  ⚠️  Table {table} does not exist - skipping")
                        continue
                    
                    # Check current RLS status
                    rls_check_query = text("""
                        SELECT relrowsecurity 
                        FROM pg_class 
                        WHERE relname = :table_name
                    """)
                    
                    rls_result = await conn.execute(rls_check_query, {"table_name": table})
                    rls_row = rls_result.fetchone()
                    
                    if rls_row:
                        current_rls = rls_row[0]
                        if current_rls:
                            print(f"  ℹ️  RLS already enabled on {table}")
                            success_count += 1
                            continue
                    
                    # Enable RLS
                    enable_query = text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
                    await conn.execute(enable_query)
                    
                    # Commit the transaction
                    await conn.commit()
                    
                    print(f"  ✓ Successfully enabled RLS on {table}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ✗ Failed to enable RLS on {table}: {e}")
                    # Continue with other tables
                    continue
            
            print()
            print(f"RLS enabling complete! Successfully processed {success_count}/{len(tables)} tables.")
            
            if success_count > 0:
                print()
                print("🔐 SECURITY RESTORED:")
                print("   RLS has been re-enabled on GTD tables.")
                print("   Database security policies are now active.")
                
        return success_count == len(tables)
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


async def main():
    """Main function"""
    success = await enable_rls_on_tables()
    
    if success:
        print("\n✅ RLS has been successfully re-enabled on all GTD tables.")
        print("   Your database is now secure for production use.")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)