#!/usr/bin/env python3
"""
Quick verification script after SQL consolidation
Run this after executing sql/consolidate_and_setup_all_tables.sql in Supabase
"""
import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JOHANNES_USER_ID = "00000000-0000-0000-0000-000000000001"

def verify_setup():
    """Quick verification that everything is working"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing environment variables!")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        logger.info("🔍 Checking database setup...")
        
        # Check user
        user_result = supabase.table("gtd_users").select("*").eq("id", JOHANNES_USER_ID).execute()
        if user_result.data:
            user = user_result.data[0]
            logger.info(f"✅ User: {user['first_name']} {user['last_name']} ({user['email_address']})")
        else:
            logger.error("❌ User Johannes Köppern not found!")
            return False
        
        # Check tables and counts
        projects_result = supabase.table("gtd_projects").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
        tasks_result = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
        
        logger.info(f"✅ Projects: {projects_result.count}")
        logger.info(f"✅ Tasks: {tasks_result.count}")
        
        # Check dashboard view
        dashboard_result = supabase.table("gtd_user_dashboard").select("*").eq("user_id", JOHANNES_USER_ID).execute()
        if dashboard_result.data:
            dashboard = dashboard_result.data[0]
            logger.info("📈 Dashboard Summary:")
            logger.info(f"   Total Projects: {dashboard['total_projects']} ({dashboard['completed_projects']} completed)")
            logger.info(f"   Total Tasks: {dashboard['total_tasks']} ({dashboard['completed_tasks']} completed)")
            logger.info(f"   Tasks Today: {dashboard['tasks_today']}")
            logger.info(f"   Tasks This Week: {dashboard['tasks_this_week']}")
        
        logger.info("🎉 Verification successful! Your GTD system is ready.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_setup()
    sys.exit(0 if success else 1)