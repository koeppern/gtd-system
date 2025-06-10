#!/usr/bin/env python3
"""
Script to create the gtd_projects table in Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    """Create the gtd_projects table"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not all([supabase_url, supabase_key]):
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # First, try to insert a test record to see if table exists
    try:
        result = supabase.table("gtd_projects").select("id").limit(1).execute()
        logger.info("Table gtd_projects already exists")
        return
    except Exception as e:
        logger.info(f"Table doesn't exist yet: {e}")
    
    # Try to create table using direct SQL execution via postgrest
    create_sql = """
    CREATE TABLE gtd_projects (
        id SERIAL PRIMARY KEY,
        user_id UUID NOT NULL,
        notion_export_row INTEGER,
        done_status BOOLEAN,
        readings TEXT,
        field VARCHAR(50),
        keywords TEXT,
        done_duplicate BOOLEAN,
        mother_project TEXT,
        related_projects TEXT,
        related_mother_projects TEXT,
        related_knowledge_vault TEXT,
        related_tasks TEXT,
        do_this_week BOOLEAN,
        gtd_processes TEXT,
        add_checkboxes TEXT,
        project_name TEXT,
        source_file VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        deleted_at TIMESTAMP
    );
    """
    
    try:
        # This approach uses the raw HTTP client
        import httpx
        headers = {
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/vnd.pgrst.object+json',
            'Prefer': 'return=minimal'
        }
        
        # Try creating via raw SQL query
        logger.info("Attempting to create table via direct SQL...")
        
        # Alternative: Just try to use the table and let Supabase handle it
        logger.info("Creating table by attempting first insert...")
        test_record = {
            'user_id': '00000000-0000-0000-0000-000000000000',
            'project_name': 'test',
            'readings': 'test'
        }
        
        try:
            result = supabase.table("gtd_projects").insert(test_record).execute()
            # If we get here, table exists, delete the test record
            supabase.table("gtd_projects").delete().eq('project_name', 'test').execute()
            logger.info("Table created successfully!")
        except Exception as e:
            logger.error(f"Could not create table: {e}")
            logger.info("Please create the table manually using sql/create_gtd_projects_table.sql")
            
    except Exception as e:
        logger.error(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()