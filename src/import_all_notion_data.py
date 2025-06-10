#!/usr/bin/env python3
"""
Import all Notion data for Johannes Köppern
This script imports both projects and tasks with the correct user ID
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.dirname(__file__))

from etl_projects import GTDProjectsETL, find_gtd_projects_csv
from etl_tasks import GTDTasksETL, find_gtd_tasks_csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Johannes Köppern's user ID
JOHANNES_USER_ID = "00000000-0000-0000-0000-000000000001"

def import_all_data():
    """Import all Notion data for Johannes"""
    load_dotenv()
    
    # Override the user ID to use Johannes' ID
    os.environ["DEFAULT_USER_ID"] = JOHANNES_USER_ID
    
    logger.info("="*60)
    logger.info("Starting complete Notion import for Johannes Köppern")
    logger.info(f"User ID: {JOHANNES_USER_ID}")
    logger.info(f"Email: johannes.koeppern@googlemail.com")
    logger.info("="*60)
    
    try:
        # Step 1: Import Projects
        logger.info("\n📁 STEP 1: Importing GTD Projects...")
        logger.info("-"*40)
        
        csv_file = find_gtd_projects_csv()
        logger.info(f"Found projects CSV: {csv_file}")
        
        projects_etl = GTDProjectsETL(user_id=JOHANNES_USER_ID)
        projects_etl.run_etl(csv_file, truncate=True, force=True)
        
        logger.info("✅ Projects import completed!")
        
        # Step 2: Import Tasks
        logger.info("\n📋 STEP 2: Importing GTD Tasks...")
        logger.info("-"*40)
        
        csv_file = find_gtd_tasks_csv()
        logger.info(f"Found tasks CSV: {csv_file}")
        
        tasks_etl = GTDTasksETL(user_id=JOHANNES_USER_ID)
        tasks_etl.run_tasks_etl(csv_file, truncate=True, force=True)
        
        logger.info("✅ Tasks import completed!")
        
        # Step 3: Verify the import
        logger.info("\n📊 STEP 3: Verifying import results...")
        logger.info("-"*40)
        
        verify_import_results()
        
        logger.info("\n🎉 ALL IMPORTS COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        raise

def verify_import_results():
    """Verify the import was successful"""
    from supabase import create_client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Check user
        user_result = supabase.table("gtd_users").select("*").eq("id", JOHANNES_USER_ID).execute()
        if user_result.data:
            user = user_result.data[0]
            logger.info(f"✅ User: {user['first_name']} {user['last_name']} ({user['email_address']})")
        else:
            logger.error("❌ User not found!")
            return
        
        # Check projects
        projects_result = supabase.table("gtd_projects").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
        logger.info(f"✅ Projects imported: {projects_result.count}")
        
        # Check completed projects
        completed_projects = supabase.table("gtd_projects").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).not_.is_("done_at", "null").execute()
        logger.info(f"   - Completed projects: {completed_projects.count}")
        
        # Check tasks
        tasks_result = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
        logger.info(f"✅ Tasks imported: {tasks_result.count}")
        
        # Check completed tasks
        completed_tasks = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).not_.is_("done_at", "null").execute()
        logger.info(f"   - Completed tasks: {completed_tasks.count}")
        
        # Check project-task mappings
        mapped_tasks = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).not_.is_("project_id", "null").execute()
        logger.info(f"   - Tasks linked to projects: {mapped_tasks.count}")
        
        # Show user dashboard
        dashboard_result = supabase.table("gtd_user_dashboard").select("*").eq("user_id", JOHANNES_USER_ID).execute()
        if dashboard_result.data:
            dashboard = dashboard_result.data[0]
            logger.info("\n📈 User Dashboard Summary:")
            logger.info(f"   Total Projects: {dashboard['total_projects']} ({dashboard['completed_projects']} completed)")
            logger.info(f"   Total Tasks: {dashboard['total_tasks']} ({dashboard['completed_tasks']} completed)")
            logger.info(f"   Tasks for Today: {dashboard['tasks_today']}")
            logger.info(f"   Tasks This Week: {dashboard['tasks_this_week']}")
        
        # Show sample data
        logger.info("\n📝 Sample Projects (showing 3):")
        sample_projects = supabase.table("gtd_projects_with_fields").select("project_name, field_name, is_done").eq("user_id", JOHANNES_USER_ID).limit(3).execute()
        for i, project in enumerate(sample_projects.data, 1):
            status = "✓" if project['is_done'] else "○"
            field = project['field_name'] or "No Field"
            logger.info(f"   {i}. {status} {project['project_name']} [{field}]")
        
        logger.info("\n✏️ Sample Tasks (showing 3):")
        sample_tasks = supabase.table("gtd_tasks_with_details").select("task_name, project_name, is_done").eq("user_id", JOHANNES_USER_ID).limit(3).execute()
        for i, task in enumerate(sample_tasks.data, 1):
            status = "✓" if task['is_done'] else "○"
            project = task['project_name'] or "No Project"
            logger.info(f"   {i}. {status} {task['task_name'][:50]}... [Project: {project[:30]}...]")
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise

if __name__ == "__main__":
    import_all_data()