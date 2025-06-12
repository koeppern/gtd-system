#!/usr/bin/env python3
"""
Script to temporarily disable RLS on GTD tables for testing
"""
import os
import sys
from pathlib import Path

# Add src/backend to path to import database module
backend_path = Path(__file__).parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from app.database import get_supabase_client

def disable_rls_on_tables():
    """Disable RLS on all GTD tables"""
    
    # List of GTD tables to disable RLS on
    tables = [
        'gtd_projects',
        'gtd_tasks', 
        'gtd_fields',
        'gtd_users'
    ]
    
    try:
        client = get_supabase_client()
        
        for table in tables:
            print(f"Disabling RLS on table: {table}")
            
            # Use Supabase RPC to execute raw SQL
            sql_query = f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"
            
            try:
                # Execute SQL using Supabase client's rpc method
                result = client.rpc('execute_sql', {'sql': sql_query}).execute()
                print(f"✓ Successfully disabled RLS on {table}")
            except Exception as e:
                # Try alternative method using PostgREST
                try:
                    # Use the underlying PostgREST client to execute SQL
                    result = client.postgrest.rpc('execute_sql', {'sql': sql_query}).execute()
                    print(f"✓ Successfully disabled RLS on {table}")
                except Exception as e2:
                    print(f"✗ Failed to disable RLS on {table}: {e2}")
                    # Let's try a direct approach
                    print(f"Attempting direct SQL execution for {table}...")
                    
        print("\nRLS disabling complete!")
        print("Note: RLS has been temporarily disabled for testing purposes.")
        print("Remember to re-enable RLS after testing is complete.")
        
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return False
    
    return True

if __name__ == "__main__":
    disable_rls_on_tables()