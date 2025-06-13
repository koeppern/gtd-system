#!/usr/bin/env python3
"""
Manual migration for done_at column
This assumes the column has been added manually via Supabase Console
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import get_supabase_client


def main():
    """Migrate done_status to done_at for existing projects"""
    print("🔄 Migrating done_status to done_at...")
    
    db = get_supabase_client()
    
    # Since we can't add the column via Python, we'll simulate the complete migration
    print("📋 Please execute this SQL in Supabase SQL Editor:")
    print()
    print("-- 1. Add done_at column")
    print("ALTER TABLE gtd_projects ADD COLUMN IF NOT EXISTS done_at TIMESTAMP WITH TIME ZONE;")
    print()
    print("-- 2. Migrate existing done projects")
    print("UPDATE gtd_projects")
    print("SET done_at = '1970-01-01 00:00:00+00'::timestamptz")
    print("WHERE done_status = true AND done_at IS NULL;")
    print()
    print("-- 3. Verify migration")
    print("SELECT")
    print("    COUNT(*) as total_projects,")
    print("    COUNT(CASE WHEN done_at IS NOT NULL THEN 1 END) as completed_projects,") 
    print("    COUNT(CASE WHEN done_at IS NULL THEN 1 END) as active_projects")
    print("FROM gtd_projects")
    print("WHERE deleted_at IS NULL;")
    print()
    
    # For now, let's get the current state for verification
    try:
        projects = db.table('gtd_projects').select('done_status', 'project_name').execute()
        
        done_projects = [p for p in projects.data if p['done_status'] == True]
        active_projects = [p for p in projects.data if p['done_status'] == False]
        
        print(f"📊 Current state before migration:")
        print(f"   Total projects: {len(projects.data)}")
        print(f"   ✅ Projects with done_status=True: {len(done_projects)}")
        print(f"   🔄 Projects with done_status=False: {len(active_projects)}")
        print()
        print(f"💡 After running the SQL above, you should have:")
        print(f"   ✅ Completed projects (done_at set): {len(done_projects)}")
        print(f"   🔄 Active projects (done_at null): {len(active_projects)}")
        
    except Exception as e:
        print(f"Error checking current state: {e}")


if __name__ == "__main__":
    main()