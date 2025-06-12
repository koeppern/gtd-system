#!/usr/bin/env python3
"""
Script to temporarily disable RLS on GTD tables using Supabase client
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_supabase_client
from app.config import get_settings


def disable_rls_on_tables():
    """Disable RLS on all GTD tables using Supabase client"""
    
    # List of GTD tables to disable RLS on
    tables = [
        'gtd_projects',
        'gtd_tasks', 
        'gtd_fields',
        'gtd_users'
    ]
    
    print("🔧 Disabling RLS on GTD Tables (via Supabase)")
    print("=" * 50)
    
    settings = get_settings()
    print(f"Supabase URL: {os.getenv('SUPABASE_URL', 'Not set')}")
    print(f"Environment: {settings.app.environment}")
    print()
    
    try:
        # Get Supabase client
        client = get_supabase_client()
        print("✓ Supabase client connection: OK")
        print()
        
        success_count = 0
        
        for table in tables:
            print(f"Processing table: {table}")
            
            try:
                # First check if table exists by trying to query it
                try:
                    result = client.table(table).select("*", count="exact").limit(0).execute()
                    table_exists = True
                    print(f"  ✓ Table {table} exists")
                except Exception as e:
                    print(f"  ⚠️  Table {table} might not exist or is inaccessible: {e}")
                    continue
                
                # Use PostgREST RPC to execute SQL
                try:
                    # Try using the Supabase client's rpc method to execute raw SQL
                    sql_query = f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"
                    
                    # Note: Supabase client doesn't directly support DDL execution
                    # We need to use a custom function or alternative approach
                    print(f"  ℹ️  Attempting to disable RLS on {table}")
                    print(f"  ⚠️  Direct SQL execution via Supabase client is limited")
                    print(f"      SQL needed: {sql_query}")
                    
                    # Alternative: Check if RLS is currently enabled
                    # by attempting operations that would fail with RLS
                    success_count += 1
                    print(f"  ✓ Table {table} processed (SQL execution may be needed manually)")
                    
                except Exception as e:
                    print(f"  ✗ Error processing {table}: {e}")
                    continue
                    
            except Exception as e:
                print(f"  ✗ Failed to process {table}: {e}")
                continue
        
        print()
        print(f"RLS processing complete! Processed {success_count}/{len(tables)} tables.")
        
        if success_count > 0:
            print()
            print("⚠️  MANUAL ACTION REQUIRED:")
            print("   Supabase client cannot execute DDL statements directly.")
            print("   You need to run the following SQL commands manually in Supabase SQL Editor:")
            print()
            for table in tables:
                print(f"   ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
            print()
            print("   Or use psql command line tool with database URL from .env")
            
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False


def main():
    """Main function"""
    success = disable_rls_on_tables()
    
    if success:
        print("\n💡 Alternative approaches:")
        print("  1. Use Supabase SQL Editor in Dashboard")
        print("  2. Use psql command line:")
        print("     psql 'postgresql://postgres.jgf...' -c 'ALTER TABLE gtd_projects DISABLE ROW LEVEL SECURITY;'")
        print("  3. Re-enable RLS when testing is complete:")
        print("     python scripts/enable_rls.py")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)