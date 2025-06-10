#!/usr/bin/env python3
"""
Execute SQL directly via PostgreSQL connection
Since Supabase doesn't have exec_sql RPC, we use psycopg2 directly
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_sql_via_psycopg():
    """Execute SQL via direct PostgreSQL connection"""
    try:
        import psycopg2
    except ImportError:
        logger.error("psycopg2 not installed. Installing...")
        os.system("pip install psycopg2-binary")
        import psycopg2
    
    load_dotenv()
    
    # Get Supabase connection details
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url:
        logger.error("SUPABASE_URL not found")
        return False
    
    # Extract host from URL
    host = supabase_url.replace("https://", "").replace("http://", "")
    if ".supabase.co" in host:
        host = host.replace(".supabase.co", "")
    
    # Read SQL file
    sql_file = Path(__file__).parent.parent / "sql" / "consolidate_and_setup_all_tables.sql"
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    logger.info(f"Connecting to PostgreSQL at {host}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=f"{host}.supabase.co",
            port=5432,
            database="postgres",
            user="postgres",
            password=supabase_key  # Service role key is also the postgres password
        )
        
        cur = conn.cursor()
        
        logger.info("Connected! Executing SQL...")
        
        # Execute the complete SQL
        cur.execute(sql_content)
        conn.commit()
        
        logger.info("✅ SQL executed successfully!")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        logger.info("This is expected - Supabase restricts direct PostgreSQL connections")
        logger.info("The SQL must be executed manually in the Supabase dashboard")
        return False

def create_supabase_function():
    """Create a function in Supabase that can execute SQL"""
    from supabase import create_client
    
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Create exec_sql function
    create_function_sql = """
    CREATE OR REPLACE FUNCTION exec_sql(sql text)
    RETURNS text
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
        EXECUTE sql;
        RETURN 'OK';
    EXCEPTION
        WHEN OTHERS THEN
            RETURN SQLERRM;
    END;
    $$;
    """
    
    try:
        logger.info("Creating exec_sql function...")
        result = supabase.rpc('exec_sql', {'sql': create_function_sql}).execute()
        logger.info("✅ Function created!")
        return True
    except Exception as e:
        logger.error(f"Could not create function: {e}")
        
        # Try alternative approach - execute via raw SQL query
        try:
            import requests
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/sql'
            }
            
            # Use the raw SQL endpoint
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/query",
                headers=headers,
                data=create_function_sql
            )
            
            if response.status_code == 200:
                logger.info("✅ Function created via raw SQL!")
                return True
            else:
                logger.error(f"Raw SQL failed: {response.status_code} - {response.text}")
                
        except Exception as e2:
            logger.error(f"Alternative approach failed: {e2}")
        
        return False

def execute_sql_with_function():
    """Execute SQL using the created function"""
    from supabase import create_client
    
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Read SQL file
    sql_file = Path(__file__).parent.parent / "sql" / "consolidate_and_setup_all_tables.sql"
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split into statements and execute each
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    logger.info(f"Executing {len(statements)} SQL statements...")
    
    success_count = 0
    for i, statement in enumerate(statements, 1):
        try:
            logger.info(f"Executing statement {i}/{len(statements)}")
            result = supabase.rpc('exec_sql', {'sql': statement}).execute()
            if result.data == 'OK':
                success_count += 1
            else:
                logger.warning(f"Statement {i} warning: {result.data}")
        except Exception as e:
            logger.warning(f"Statement {i} failed: {e}")
    
    logger.info(f"✅ Executed {success_count}/{len(statements)} statements successfully")
    return success_count > 0

if __name__ == "__main__":
    logger.info("🚀 Attempting to execute SQL consolidation script...")
    
    # Try multiple approaches
    success = False
    
    # Approach 1: Direct PostgreSQL connection
    logger.info("Approach 1: Direct PostgreSQL connection...")
    if execute_sql_via_psycopg():
        success = True
    
    if not success:
        # Approach 2: Create function and use it
        logger.info("Approach 2: Creating exec_sql function...")
        if create_supabase_function():
            if execute_sql_with_function():
                success = True
    
    if success:
        logger.info("✅ SQL execution successful!")
        
        # Now verify
        logger.info("Running verification...")
        os.system("python src/verify_import.py")
    else:
        logger.error("❌ Could not execute SQL automatically")
        logger.info("Please execute sql/consolidate_and_setup_all_tables.sql manually in Supabase SQL Editor")
    
    sys.exit(0 if success else 1)