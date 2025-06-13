#!/usr/bin/env python3
"""
Debug Supabase connectivity and analyze the 400 Bad Request issue.
"""
import os
import sys
sys.path.append('/mnt/c/python/gtd/src/backend')

from app.config import get_settings
from app.database import get_db_client
import asyncio

async def debug_supabase():
    """Debug Supabase connectivity issues"""
    print("=== Supabase Debug Script ===")
    
    # Get configuration
    settings = get_settings()
    print(f"✓ Loaded config from: {settings}")
    print(f"✓ Database URL: {settings.database.supabase['url']}")
    print(f"✓ Service Role Key: {settings.database.supabase['service_role_key'][:20]}...")
    print(f"✓ Default User ID: {settings.gtd.default_user_id}")
    
    # Get Supabase client
    try:
        supabase = get_db_client()
        print("✓ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return
    
    # Test 1: Basic table list (should work with service role)
    print("\n=== Test 1: Basic Health Check ===")
    try:
        # Try a very basic query
        result = supabase.table("gtd_users").select("id").limit(1).execute()
        print(f"✓ Basic query succeeded: {len(result.data)} rows returned")
    except Exception as e:
        print(f"❌ Basic query failed: {e}")
        print(f"   Type: {type(e)}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response}")
        if hasattr(e, 'status_code'):
            print(f"   Status: {e.status_code}")
    
    # Test 2: Check if RLS is the issue
    print("\n=== Test 2: Test Different Tables ===")
    tables = ["gtd_users", "gtd_fields", "gtd_projects", "gtd_tasks"]
    
    for table in tables:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"✓ {table}: {len(result.data)} rows")
        except Exception as e:
            print(f"❌ {table}: {str(e)[:100]}...")
    
    # Test 3: Check specific task query that's failing
    print("\n=== Test 3: Reproduce Exact Failing Query ===")
    try:
        query = supabase.table("gtd_tasks").select("*")
        query = query.eq("user_id", settings.gtd.default_user_id)
        query = query.is_("deleted_at", "null")
        query = query.is_("done_at", "null")
        query = query.eq("do_today", "false")
        query = query.eq("do_this_week", "false")
        query = query.range(0, 9)  # offset=0, limit=10
        
        print(f"Query URL would be: {query}")
        result = query.execute()
        print(f"✓ Task query succeeded: {len(result.data)} rows")
        
    except Exception as e:
        print(f"❌ Task query failed: {e}")
        print(f"   Full error: {str(e)}")
    
    # Test 4: Test without user filtering  
    print("\n=== Test 4: Test Without User Filter ===")
    try:
        result = supabase.table("gtd_tasks").select("*").limit(1).execute()
        print(f"✓ No user filter: {len(result.data)} rows")
    except Exception as e:
        print(f"❌ No user filter failed: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(debug_supabase())