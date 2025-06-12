#!/usr/bin/env python3
"""
Script to temporarily disable RLS on GTD tables for testing purposes
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


async def disable_rls_on_tables():
    """Disable RLS on all GTD tables"""
    
    # List of GTD tables to disable RLS on
    tables = [
        'gtd_projects',
        'gtd_tasks', 
        'gtd_fields',
        'gtd_users'
    ]
    
    print("🔧 Disabling RLS on GTD Tables")
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
                print(f"Disabling RLS on table: {table}")
                
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
                        if not current_rls:
                            print(f"  ℹ️  RLS already disabled on {table}")
                            success_count += 1
                            continue
                    
                    # Disable RLS
                    disable_query = text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
                    await conn.execute(disable_query)
                    
                    # Commit the transaction
                    await conn.commit()
                    
                    print(f"  ✓ Successfully disabled RLS on {table}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ✗ Failed to disable RLS on {table}: {e}")
                    # Continue with other tables
                    continue
            
            print()
            print(f"RLS disabling complete! Successfully processed {success_count}/{len(tables)} tables.")
            
            if success_count > 0:
                print()
                print("⚠️  IMPORTANT SECURITY NOTICE:")
                print("   RLS has been temporarily disabled for testing purposes.")
                print("   Remember to re-enable RLS after testing is complete.")
                print("   Use the enable_rls.py script to re-enable RLS.")
                
        return success_count == len(tables)
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


async def main():
    """Main function"""
    success = await disable_rls_on_tables()
    
    if success:
        print("\n💡 Next steps:")
        print("  1. Run your FastAPI backend tests")
        print("  2. Re-enable RLS when testing is complete:")
        print("     python scripts/enable_rls.py")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)