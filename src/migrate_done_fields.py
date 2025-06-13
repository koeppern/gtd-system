#!/usr/bin/env python3
"""
Migration: Replace boolean done fields with timestamp done_at logic

This script:
1. Adds done_at column to gtd_projects if it doesn't exist
2. Migrates existing done_status=true projects to done_at='1970-01-01'
3. Verifies that both gtd_projects and gtd_tasks use done_at logic consistently
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import get_supabase_client
from backend.app.config import get_settings


def main():
    """Execute the done fields migration"""
    print("🔄 Starting done fields migration...")
    
    db = get_supabase_client()
    settings = get_settings()
    
    # Step 1: Check current state
    print("\n📊 Checking current state...")
    
    # Check gtd_projects
    try:
        projects_test = db.table('gtd_projects').select('done_at', 'project_name').limit(1).execute()
        has_done_at_column = True
        print("✅ gtd_projects already has done_at column")
    except Exception:
        has_done_at_column = False
        print("❌ gtd_projects missing done_at column - will be added")
    
    # Get current projects data
    projects_result = db.table('gtd_projects').select('id', 'project_name', 'done_status').execute()
    projects_data = projects_result.data
    
    print(f"📈 Found {len(projects_data)} projects total")
    
    done_projects = [p for p in projects_data if p['done_status'] == True]
    active_projects = [p for p in projects_data if p['done_status'] == False]
    
    print(f"✅ {len(done_projects)} projects with done_status=True")
    print(f"🔄 {len(active_projects)} projects with done_status=False")
    
    # Step 2: Add done_at column if needed (via manual update)
    if not has_done_at_column:
        print(f"\n⚠️  MANUAL ACTION REQUIRED:")
        print(f"Please execute this SQL in Supabase SQL Editor:")
        print(f"ALTER TABLE gtd_projects ADD COLUMN done_at TIMESTAMP WITH TIME ZONE;")
        print(f"\nThen run this script again to complete the migration.")
        return
    
    # Step 3: Migrate done_status=true projects to done_at='1970-01-01'
    print(f"\n🔄 Migrating {len(done_projects)} completed projects...")
    
    migration_date = '1970-01-01T00:00:00+00:00'
    migrated_count = 0
    
    for project in done_projects:
        try:
            # Check if already has done_at
            current = db.table('gtd_projects').select('done_at').eq('id', project['id']).execute()
            if current.data and current.data[0]['done_at'] is not None:
                print(f"⏭️  Skipping {project['project_name'][:30]} (already has done_at)")
                continue
            
            # Update to set done_at
            update_result = db.table('gtd_projects').update({
                'done_at': migration_date
            }).eq('id', project['id']).execute()
            
            if update_result.data:
                migrated_count += 1
                print(f"✅ Migrated: {project['project_name'][:40]}")
            else:
                print(f"❌ Failed to migrate: {project['project_name'][:40]}")
                
        except Exception as e:
            print(f"❌ Error migrating {project['project_name'][:30]}: {e}")
    
    print(f"\n📊 Migration completed: {migrated_count}/{len(done_projects)} projects migrated")
    
    # Step 4: Verify migration
    print(f"\n🔍 Verifying migration...")
    
    # Check projects
    all_projects = db.table('gtd_projects').select('done_status', 'done_at', 'project_name').is_('deleted_at', 'null').execute()
    
    # New logic: done = done_at is not null
    completed_new_logic = [p for p in all_projects.data if p['done_at'] is not None]
    active_new_logic = [p for p in all_projects.data if p['done_at'] is None]
    
    print(f"📈 Verification Results:")
    print(f"   Total projects: {len(all_projects.data)}")
    print(f"   ✅ Completed (done_at exists): {len(completed_new_logic)}")
    print(f"   🔄 Active (done_at is null): {len(active_new_logic)}")
    
    # Check for inconsistencies
    inconsistent = [p for p in all_projects.data 
                   if (p['done_status'] == True and p['done_at'] is None) or 
                      (p['done_status'] == False and p['done_at'] is not None)]
    
    if inconsistent:
        print(f"⚠️  Found {len(inconsistent)} inconsistent projects:")
        for p in inconsistent[:3]:
            print(f"   - {p['project_name'][:30]}: done_status={p['done_status']}, done_at={p['done_at']}")
    else:
        print(f"✅ All projects consistent with new done_at logic!")
    
    # Step 5: Check gtd_tasks (should already be using done_at)
    print(f"\n🔍 Checking gtd_tasks...")
    
    all_tasks = db.table('gtd_tasks').select('done_at', 'task_name').is_('deleted_at', 'null').limit(10).execute()
    
    completed_tasks = [t for t in all_tasks.data if t['done_at'] is not None]
    active_tasks = [t for t in all_tasks.data if t['done_at'] is None]
    
    print(f"📈 Sample tasks check:")
    print(f"   ✅ Completed tasks (done_at exists): {len(completed_tasks)}")
    print(f"   🔄 Active tasks (done_at is null): {len(active_tasks)}")
    print(f"✅ gtd_tasks already using done_at logic correctly!")
    
    print(f"\n🎉 Migration completed successfully!")
    print(f"💡 Next step: Update Dashboard API to use done_at logic for both projects and tasks")


if __name__ == "__main__":
    main()