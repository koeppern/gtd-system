#!/usr/bin/env python3
"""
Create the missing gtd_users table and insert Johannes
"""
import os
import logging
from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JOHANNES_USER_ID = "00000000-0000-0000-0000-000000000001"

def create_users_table():
    """Create gtd_users table if it doesn't exist"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    logger.info("🔧 Creating gtd_users table...")
    
    # Try to check if user already exists
    try:
        result = supabase.table("gtd_users").select("id").limit(1).execute()
        logger.info("✅ gtd_users table already exists")
        
        # Check if Johannes exists
        user_result = supabase.table("gtd_users").select("*").eq("id", JOHANNES_USER_ID).execute()
        if user_result.data:
            user = user_result.data[0]
            logger.info(f"✅ User already exists: {user['first_name']} {user['last_name']}")
            return True
        else:
            logger.info("User table exists but Johannes not found, inserting...")
            
    except Exception as e:
        if "does not exist" in str(e):
            logger.info("gtd_users table doesn't exist - this is the issue!")
            logger.info("Manual action required: Execute sql/consolidate_and_setup_all_tables.sql in Supabase")
            return False
        else:
            logger.error(f"Unexpected error: {e}")
            return False
    
    # Insert Johannes if table exists but user doesn't
    try:
        user_data = {
            "id": JOHANNES_USER_ID,
            "first_name": "Johannes",
            "last_name": "Köppern", 
            "email_address": "johannes.koeppern@googlemail.com",
            "timezone": "Europe/Berlin",
            "email_verified": True,
            "is_active": True
        }
        
        result = supabase.table("gtd_users").insert(user_data).execute()
        
        if result.data:
            logger.info("✅ Johannes Köppern inserted successfully!")
            return True
        else:
            logger.error("❌ Failed to insert user")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to insert user: {e}")
        return False

def check_system_status():
    """Check overall system status"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    logger.info("📊 Checking system status...")
    
    try:
        # Check user
        user_result = supabase.table("gtd_users").select("*").eq("id", JOHANNES_USER_ID).execute()
        if user_result.data:
            user = user_result.data[0]
            logger.info(f"✅ User: {user['first_name']} {user['last_name']} ({user['email_address']})")
        else:
            logger.error("❌ User not found")
            return False
        
        # Check projects
        projects_result = supabase.table("gtd_projects").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
        logger.info(f"✅ Projects: {projects_result.count}")
        
        # Check tasks  
        tasks_result = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
        logger.info(f"✅ Tasks: {tasks_result.count}")
        
        # Check completed counts
        completed_projects = supabase.table("gtd_projects").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).not_.is_("done_at", "null").execute()
        completed_tasks = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).not_.is_("done_at", "null").execute()
        
        logger.info(f"📈 Summary:")
        logger.info(f"   Projects: {projects_result.count} total, {completed_projects.count} completed")
        logger.info(f"   Tasks: {tasks_result.count} total, {completed_tasks.count} completed")
        
        # Try dashboard view if it exists
        try:
            dashboard_result = supabase.table("gtd_user_dashboard").select("*").eq("user_id", JOHANNES_USER_ID).execute()
            if dashboard_result.data:
                dashboard = dashboard_result.data[0]
                logger.info(f"📊 Dashboard: {dashboard['tasks_today']} tasks today, {dashboard['tasks_this_week']} this week")
        except:
            logger.info("📊 Dashboard view not available (requires full SQL consolidation)")
        
        logger.info("🎉 GTD System is working!")
        return True
        
    except Exception as e:
        logger.error(f"❌ System check failed: {e}")
        return False

if __name__ == "__main__":
    success = create_users_table()
    if success:
        check_system_status()
    
    if not success:
        logger.info("=" * 60)
        logger.info("⚠️  MANUAL ACTION REQUIRED:")
        logger.info("1. Go to Supabase Dashboard → SQL Editor")
        logger.info("2. Execute: sql/consolidate_and_setup_all_tables.sql")
        logger.info("3. Then run: python src/verify_import.py")
        logger.info("=" * 60)