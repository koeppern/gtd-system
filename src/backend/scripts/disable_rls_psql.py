#!/usr/bin/env python3
"""
Script to disable RLS on GTD tables using psql command
"""
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings


def disable_rls_with_psql():
    """Disable RLS on all GTD tables using psql"""
    
    # List of GTD tables to disable RLS on
    tables = [
        'gtd_projects',
        'gtd_tasks', 
        'gtd_fields',
        'gtd_users'
    ]
    
    print("🔧 Disabling RLS on GTD Tables (via psql)")
    print("=" * 45)
    
    settings = get_settings()
    db_url = settings.database_url_asyncpg
    
    # Convert asyncpg URL to standard postgresql URL for psql
    if db_url.startswith("postgresql+asyncpg://"):
        psql_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        psql_url = db_url
    
    print(f"Database URL: {psql_url}")
    print(f"Environment: {settings.app.environment}")
    print()
    
    success_count = 0
    
    for table in tables:
        print(f"Disabling RLS on table: {table}")
        
        try:
            # Construct the SQL command
            sql_command = f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"
            
            # Execute psql command
            cmd = ["psql", psql_url, "-c", sql_command]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  ✓ Successfully disabled RLS on {table}")
                success_count += 1
            else:
                print(f"  ✗ Failed to disable RLS on {table}")
                if result.stderr:
                    print(f"    Error: {result.stderr.strip()}")
                if result.stdout:
                    print(f"    Output: {result.stdout.strip()}")
                    
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout while processing {table}")
        except FileNotFoundError:
            print(f"  ✗ psql command not found. Please install PostgreSQL client tools.")
            print("    On Ubuntu/Debian: sudo apt-get install postgresql-client")
            print("    On macOS: brew install postgresql")
            print("    On Windows: Download from https://www.postgresql.org/download/windows/")
            break
        except Exception as e:
            print(f"  ✗ Unexpected error for {table}: {e}")
    
    print()
    print(f"RLS disabling complete! Successfully processed {success_count}/{len(tables)} tables.")
    
    if success_count > 0:
        print()
        print("⚠️  IMPORTANT SECURITY NOTICE:")
        print("   RLS has been temporarily disabled for testing purposes.")
        print("   Remember to re-enable RLS after testing is complete.")
        print("   Use the enable_rls.py script to re-enable RLS.")
    
    return success_count == len(tables)


def main():
    """Main function"""
    success = disable_rls_with_psql()
    
    if success:
        print("\n💡 Next steps:")
        print("  1. Run your FastAPI backend tests")
        print("  2. Re-enable RLS when testing is complete:")
        print("     python scripts/enable_rls.py")
    else:
        print("\n💡 Alternative manual approach:")
        print("  1. Open Supabase Dashboard -> SQL Editor")
        print("  2. Execute these SQL commands:")
        for table in ['gtd_projects', 'gtd_tasks', 'gtd_fields', 'gtd_users']:
            print(f"     ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)