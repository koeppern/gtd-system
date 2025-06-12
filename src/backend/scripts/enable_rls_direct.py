#!/usr/bin/env python3
"""
Script to re-enable RLS on GTD tables using direct database connection
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from app.config import get_settings


async def enable_rls_direct():
    """Re-enable RLS on all GTD tables using direct asyncpg connection"""
    
    # List of GTD tables to enable RLS on
    tables = [
        'gtd_projects',
        'gtd_tasks', 
        'gtd_fields',
        'gtd_users'
    ]
    
    print("🔐 Re-enabling RLS on GTD Tables (direct asyncpg)")
    print("=" * 52)
    
    settings = get_settings()
    
    # Get database URL from environment or settings
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = settings.database_url_asyncpg
    
    # Convert SQLAlchemy URL to standard PostgreSQL URL for asyncpg
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Database URL: {db_url[:50]}...")
    print(f"Environment: {settings.app.environment}")
    print()
    
    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✓ Database connection: OK")
        print()
        
        success_count = 0
        
        for table in tables:
            print(f"Processing table: {table}")
            
            try:
                # First check if table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = $1
                    )
                """, table)
                
                if not table_exists:
                    print(f"  ⚠️  Table {table} does not exist - skipping")
                    continue
                
                # Check current RLS status
                rls_enabled = await conn.fetchval("""
                    SELECT relrowsecurity 
                    FROM pg_class 
                    WHERE relname = $1
                """, table)
                
                if rls_enabled is True:
                    print(f"  ℹ️  RLS already enabled on {table}")
                    success_count += 1
                    continue
                
                # Enable RLS
                await conn.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
                
                print(f"  ✓ Successfully enabled RLS on {table}")
                success_count += 1
                
            except Exception as e:
                print(f"  ✗ Failed to enable RLS on {table}: {e}")
                continue
        
        print()
        print(f"RLS enabling complete! Successfully processed {success_count}/{len(tables)} tables.")
        
        if success_count > 0:
            print()
            print("🔐 SECURITY RESTORED:")
            print("   RLS has been re-enabled on GTD tables.")
            print("   Database security policies are now active.")
        
        await conn.close()
        return success_count == len(tables)
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


async def main():
    """Main function"""
    success = await enable_rls_direct()
    
    if success:
        print("\n✅ RLS has been successfully re-enabled on all GTD tables.")
        print("   Your database is now secure for production use.")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)