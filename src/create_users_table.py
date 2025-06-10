#!/usr/bin/env python3
"""
Create GTD Users table and update existing tables to use UUID foreign keys
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_users_table():
    """Create GTD users table and update existing tables"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not all([supabase_url, supabase_key]):
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # SQL script to create users table and update existing tables
    sql_script = """
    -- =========================================
    -- 1. Create GTD Users table
    -- =========================================
    
    CREATE TABLE IF NOT EXISTS gtd_users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        
        -- Basic user information
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email_address VARCHAR(255) UNIQUE NOT NULL,
        
        -- User preferences
        timezone VARCHAR(50) DEFAULT 'UTC',
        date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
        time_format VARCHAR(10) DEFAULT '24h',
        
        -- GTD-specific settings
        default_field_id INTEGER REFERENCES gtd_fields(id) DEFAULT 1, -- Default to 'Private'
        weekly_review_day INTEGER DEFAULT 0, -- 0=Sunday, 1=Monday, etc.
        
        -- Account status
        is_active BOOLEAN DEFAULT TRUE,
        email_verified BOOLEAN DEFAULT FALSE,
        
        -- Metadata
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        last_login_at TIMESTAMP,
        deleted_at TIMESTAMP
    );
    
    -- =========================================
    -- 2. Create indexes for users table
    -- =========================================
    
    CREATE INDEX IF NOT EXISTS idx_gtd_users_email ON gtd_users(email_address);
    CREATE INDEX IF NOT EXISTS idx_gtd_users_active ON gtd_users(is_active);
    CREATE INDEX IF NOT EXISTS idx_gtd_users_created ON gtd_users(created_at);
    
    -- =========================================
    -- 3. Add trigger for auto-update updated_at
    -- =========================================
    
    CREATE OR REPLACE FUNCTION update_gtd_users_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS trigger_gtd_users_updated_at ON gtd_users;
    
    CREATE TRIGGER trigger_gtd_users_updated_at
        BEFORE UPDATE ON gtd_users
        FOR EACH ROW
        EXECUTE FUNCTION update_gtd_users_updated_at();
    
    -- =========================================
    -- 4. Update existing tables to use proper UUID foreign keys
    -- =========================================
    
    -- Note: We're keeping the existing user_id columns as UUID
    -- but adding proper foreign key constraints
    
    -- Add foreign key constraint to gtd_projects
    DO $$ 
    BEGIN
        -- Check if foreign key constraint doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_gtd_projects_user_id' 
            AND table_name = 'gtd_projects'
        ) THEN
            ALTER TABLE gtd_projects 
            ADD CONSTRAINT fk_gtd_projects_user_id 
            FOREIGN KEY (user_id) REFERENCES gtd_users(id) ON DELETE CASCADE;
        END IF;
    END $$;
    
    -- Add foreign key constraint to gtd_tasks
    DO $$ 
    BEGIN
        -- Check if foreign key constraint doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_gtd_tasks_user_id' 
            AND table_name = 'gtd_tasks'
        ) THEN
            ALTER TABLE gtd_tasks 
            ADD CONSTRAINT fk_gtd_tasks_user_id 
            FOREIGN KEY (user_id) REFERENCES gtd_users(id) ON DELETE CASCADE;
        END IF;
    END $$;
    
    -- =========================================
    -- 5. Create enhanced views with user information
    -- =========================================
    
    -- Enhanced projects view with user info
    CREATE OR REPLACE VIEW gtd_projects_with_user_details AS
    SELECT 
        p.*,
        f.name as field_name,
        f.description as field_description,
        u.first_name,
        u.last_name,
        u.email_address,
        CASE WHEN p.done_at IS NOT NULL THEN true ELSE false END as is_done
    FROM gtd_projects p
    LEFT JOIN gtd_fields f ON p.field_id = f.id
    LEFT JOIN gtd_users u ON p.user_id = u.id;
    
    -- Enhanced tasks view with user info
    CREATE OR REPLACE VIEW gtd_tasks_with_user_details AS
    SELECT 
        t.*,
        p.project_name,
        p.readings as project_readings,
        f.name as field_name,
        f.description as field_description,
        u.first_name,
        u.last_name,
        u.email_address,
        CASE WHEN t.done_at IS NOT NULL THEN true ELSE false END as is_done
    FROM gtd_tasks t
    LEFT JOIN gtd_projects p ON t.project_id = p.id
    LEFT JOIN gtd_fields f ON t.field_id = f.id
    LEFT JOIN gtd_users u ON t.user_id = u.id;
    
    -- User dashboard summary
    CREATE OR REPLACE VIEW gtd_user_dashboard AS
    SELECT 
        u.id as user_id,
        u.first_name,
        u.last_name,
        u.email_address,
        
        -- Project statistics
        COUNT(DISTINCT p.id) as total_projects,
        COUNT(DISTINCT CASE WHEN p.done_at IS NOT NULL THEN p.id END) as completed_projects,
        COUNT(DISTINCT CASE WHEN p.done_at IS NULL THEN p.id END) as active_projects,
        
        -- Task statistics
        COUNT(DISTINCT t.id) as total_tasks,
        COUNT(DISTINCT CASE WHEN t.done_at IS NOT NULL THEN t.id END) as completed_tasks,
        COUNT(DISTINCT CASE WHEN t.done_at IS NULL THEN t.id END) as pending_tasks,
        COUNT(DISTINCT CASE WHEN t.do_today = true AND t.done_at IS NULL THEN t.id END) as tasks_today,
        COUNT(DISTINCT CASE WHEN t.do_this_week = true AND t.done_at IS NULL THEN t.id END) as tasks_this_week,
        
        -- User activity
        u.last_login_at,
        u.created_at as user_since
        
    FROM gtd_users u
    LEFT JOIN gtd_projects p ON u.id = p.user_id AND p.deleted_at IS NULL
    LEFT JOIN gtd_tasks t ON u.id = t.user_id AND t.deleted_at IS NULL
    WHERE u.deleted_at IS NULL
    GROUP BY u.id, u.first_name, u.last_name, u.email_address, u.last_login_at, u.created_at;
    """
    
    try:
        logger.info("Creating GTD users table and updating foreign key constraints...")
        
        # Execute the SQL script
        # Note: Supabase Python client doesn't support multi-statement execution directly
        # We'll need to execute each statement separately or use a different approach
        
        # For now, let's log the SQL and recommend manual execution
        logger.info("SQL script prepared. Please execute the following in Supabase SQL Editor:")
        print("\n" + "="*60)
        print("EXECUTE THIS SQL IN SUPABASE SQL EDITOR:")
        print("="*60)
        print(sql_script)
        print("="*60)
        
        # Test if we can at least connect and check existing tables
        result = supabase.table("gtd_projects").select("id").limit(1).execute()
        logger.info("✓ Successfully connected to Supabase")
        logger.info("✓ Existing tables are accessible")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

def insert_sample_user():
    """Insert a sample user for testing"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    default_user_id = os.getenv("DEFAULT_USER_ID")
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Check if users table exists and is accessible
        result = supabase.table("gtd_users").select("id").limit(1).execute()
        logger.info("✓ GTD users table is accessible")
        
        # Insert sample user with the DEFAULT_USER_ID
        sample_user = {
            "id": default_user_id,
            "first_name": "John",
            "last_name": "Doe", 
            "email_address": "john.doe@example.com",
            "timezone": "Europe/Berlin",
            "email_verified": True
        }
        
        # Try to insert (will fail if user already exists)
        try:
            result = supabase.table("gtd_users").insert(sample_user).execute()
            logger.info(f"✓ Sample user created with ID: {default_user_id}")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.info(f"✓ User with ID {default_user_id} already exists")
            else:
                raise e
        
        return True
        
    except Exception as e:
        logger.error(f"Error inserting sample user: {e}")
        return False

def test_user_relationships():
    """Test the foreign key relationships"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    default_user_id = os.getenv("DEFAULT_USER_ID")
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        logger.info("Testing user relationships...")
        
        # Test user dashboard view
        result = supabase.table("gtd_user_dashboard").select("*").eq("user_id", default_user_id).execute()
        if result.data:
            user_stats = result.data[0]
            logger.info(f"✓ User Dashboard for {user_stats['first_name']} {user_stats['last_name']}:")
            logger.info(f"  - Total Projects: {user_stats['total_projects']}")
            logger.info(f"  - Completed Projects: {user_stats['completed_projects']}")
            logger.info(f"  - Total Tasks: {user_stats['total_tasks']}")
            logger.info(f"  - Completed Tasks: {user_stats['completed_tasks']}")
            logger.info(f"  - Tasks Today: {user_stats['tasks_today']}")
        
        # Test projects with user details
        result = supabase.table("gtd_projects_with_user_details").select("project_name, first_name, last_name").eq("user_id", default_user_id).limit(3).execute()
        if result.data:
            logger.info(f"✓ Sample Projects with User Info:")
            for project in result.data:
                logger.info(f"  - {project['project_name']} (Owner: {project['first_name']} {project['last_name']})")
        
        # Test tasks with user details  
        result = supabase.table("gtd_tasks_with_user_details").select("task_name, first_name, last_name").eq("user_id", default_user_id).limit(3).execute()
        if result.data:
            logger.info(f"✓ Sample Tasks with User Info:")
            for task in result.data:
                logger.info(f"  - {task['task_name'][:50]}... (Owner: {task['first_name']} {task['last_name']})")
        
        logger.info("✓ All relationship tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing relationships: {e}")
        return False

def main():
    """Main execution function"""
    logger.info("Starting GTD Users table creation...")
    
    try:
        # Step 1: Create users table (SQL output)
        if create_users_table():
            logger.info("✓ Step 1: Users table SQL generated")
        else:
            logger.error("✗ Step 1: Failed to generate users table SQL")
            return False
        
        # Wait for user to execute SQL manually
        input("\nPlease execute the SQL above in Supabase SQL Editor, then press Enter to continue...")
        
        # Step 2: Insert sample user
        if insert_sample_user():
            logger.info("✓ Step 2: Sample user created/verified")
        else:
            logger.error("✗ Step 2: Failed to create sample user")
            return False
        
        # Step 3: Test relationships
        if test_user_relationships():
            logger.info("✓ Step 3: User relationships tested successfully")
        else:
            logger.error("✗ Step 3: Failed to test user relationships")
            return False
        
        logger.info("🎉 GTD Users table setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)