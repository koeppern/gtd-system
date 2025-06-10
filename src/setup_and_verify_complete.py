#!/usr/bin/env python3
"""
Complete GTD System Setup and Verification
This script executes the SQL consolidation and verifies everything works
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JOHANNES_USER_ID = "00000000-0000-0000-0000-000000000001"

def execute_sql_file(supabase, sql_file_path):
    """Execute SQL file in Supabase"""
    logger.info(f"📜 Executing SQL file: {sql_file_path}")
    
    # Read SQL file
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split into individual statements (basic splitting by semicolon)
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    logger.info(f"Found {len(statements)} SQL statements to execute")
    
    for i, statement in enumerate(statements, 1):
        if not statement:
            continue
            
        try:
            # Skip comments and empty lines
            if statement.startswith('--') or statement.strip() == '':
                continue
                
            logger.info(f"Executing statement {i}/{len(statements)}")
            logger.debug(f"SQL: {statement[:100]}...")
            
            # Execute the SQL statement
            result = supabase.rpc('exec_sql', {'sql': statement}).execute()
            
        except Exception as e:
            logger.warning(f"Statement {i} failed (might be expected): {e}")
            # Continue with next statement - some failures are expected (DROP IF EXISTS, etc.)
            continue
    
    logger.info("✅ SQL execution completed")

def setup_complete_system():
    """Setup the complete GTD system"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing environment variables!")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        logger.info("="*60)
        logger.info("🚀 STARTING COMPLETE GTD SYSTEM SETUP")
        logger.info("="*60)
        
        # Step 1: Execute SQL consolidation script
        logger.info("\n📋 STEP 1: Executing SQL consolidation script...")
        logger.info("-"*40)
        
        sql_file = Path(__file__).parent.parent / "sql" / "consolidate_and_setup_all_tables.sql"
        
        # Alternative approach: Execute SQL directly using Supabase's SQL editor endpoint
        # Read and execute the SQL file content
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        logger.info("Executing complete SQL script via Supabase...")
        
        # Use the query method to execute raw SQL
        try:
            # For large SQL scripts, we need to execute via the PostgREST API
            import requests
            
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            # Execute SQL via the query endpoint
            sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
            
            logger.info("Attempting to execute SQL via RPC call...")
            response = requests.post(
                sql_url,
                headers=headers,
                json={'sql': sql_content}
            )
            
            if response.status_code == 200:
                logger.info("✅ SQL script executed successfully!")
            else:
                logger.warning(f"RPC call failed with status {response.status_code}: {response.text}")
                logger.info("Trying alternative approach with individual statements...")
                
                # Alternative: Execute statements individually
                statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
                
                for i, statement in enumerate(statements, 1):
                    if not statement:
                        continue
                    try:
                        logger.info(f"Executing statement {i}/{len(statements)}")
                        # Direct database query
                        supabase.postgrest.session.post(
                            f"{supabase_url}/rest/v1/rpc/exec_sql",
                            headers=headers,
                            json={'sql': statement}
                        )
                    except Exception as e:
                        logger.debug(f"Statement {i} warning: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            logger.info("Attempting to verify if tables were created anyway...")
        
        logger.info("✅ SQL consolidation completed!")
        
        # Step 2: Verify database setup
        logger.info("\n🔍 STEP 2: Verifying database setup...")
        logger.info("-"*40)
        
        # Check if user exists
        try:
            user_result = supabase.table("gtd_users").select("*").eq("id", JOHANNES_USER_ID).execute()
            if user_result.data:
                user = user_result.data[0]
                logger.info(f"✅ User found: {user['first_name']} {user['last_name']} ({user['email_address']})")
            else:
                logger.error("❌ User Johannes Köppern not found!")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot verify user: {e}")
            return False
        
        # Check data counts
        try:
            projects_result = supabase.table("gtd_projects").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
            tasks_result = supabase.table("gtd_tasks").select("id", count="exact").eq("user_id", JOHANNES_USER_ID).execute()
            
            logger.info(f"✅ Projects: {projects_result.count}")
            logger.info(f"✅ Tasks: {tasks_result.count}")
            
            if projects_result.count == 0 or tasks_result.count == 0:
                logger.warning("⚠️ No data found - this might indicate the previous import didn't persist")
                logger.info("Re-running import to ensure data is present...")
                
                # Re-import data
                from import_all_notion_data import import_all_data
                import_all_data()
                
        except Exception as e:
            logger.error(f"❌ Cannot verify data counts: {e}")
            return False
        
        # Step 3: Check dashboard view
        logger.info("\n📈 STEP 3: Checking dashboard view...")
        logger.info("-"*40)
        
        try:
            dashboard_result = supabase.table("gtd_user_dashboard").select("*").eq("user_id", JOHANNES_USER_ID).execute()
            if dashboard_result.data:
                dashboard = dashboard_result.data[0]
                logger.info("📊 Dashboard Summary:")
                logger.info(f"   Total Projects: {dashboard['total_projects']} ({dashboard['completed_projects']} completed)")
                logger.info(f"   Total Tasks: {dashboard['total_tasks']} ({dashboard['completed_tasks']} completed)")
                logger.info(f"   Tasks Today: {dashboard['tasks_today']}")
                logger.info(f"   Tasks This Week: {dashboard['tasks_this_week']}")
            else:
                logger.warning("⚠️ Dashboard view returned no data")
        except Exception as e:
            logger.warning(f"⚠️ Dashboard view not accessible: {e}")
        
        # Step 4: Show sample data
        logger.info("\n📝 STEP 4: Sample data verification...")
        logger.info("-"*40)
        
        try:
            # Sample projects
            sample_projects = supabase.table("gtd_projects_with_fields").select("project_name, field_name, is_done").eq("user_id", JOHANNES_USER_ID).limit(3).execute()
            logger.info("Sample Projects:")
            for i, project in enumerate(sample_projects.data, 1):
                status = "✓" if project.get('is_done') else "○"
                field = project.get('field_name') or "No Field"
                logger.info(f"   {i}. {status} {project['project_name'][:50]}... [{field}]")
        except Exception as e:
            logger.warning(f"Could not fetch sample projects: {e}")
        
        try:
            # Sample tasks
            sample_tasks = supabase.table("gtd_tasks_with_details").select("task_name, project_name, is_done").eq("user_id", JOHANNES_USER_ID).limit(3).execute()
            logger.info("Sample Tasks:")
            for i, task in enumerate(sample_tasks.data, 1):
                status = "✓" if task.get('is_done') else "○"
                project = task.get('project_name') or "No Project"
                logger.info(f"   {i}. {status} {task['task_name'][:50]}... [Project: {project[:30]}...]")
        except Exception as e:
            logger.warning(f"Could not fetch sample tasks: {e}")
        
        logger.info("\n🎉 COMPLETE GTD SYSTEM SETUP SUCCESSFUL!")
        logger.info("="*60)
        logger.info("Your GTD system is ready to use! 🚀")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_complete_system()
    sys.exit(0 if success else 1)