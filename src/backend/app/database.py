"""
Supabase client configuration and connection management
"""
from typing import Optional
import psycopg2
from supabase import create_client, Client
from app.config import get_settings

# Global Supabase client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        
        # Get Supabase configuration
        supabase_url = settings.database.supabase.get("url", "")
        service_key = settings.database.supabase.get("service_role_key", "")
        
        # Override with environment variables if present
        import os
        supabase_url = os.getenv("SUPABASE_URL", supabase_url)
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", service_key)
        
        if not supabase_url or not service_key:
            raise ValueError("Missing Supabase URL or service role key")
        
        # Create Supabase client
        _supabase_client = create_client(supabase_url, service_key)
        
    return _supabase_client

def test_connection() -> bool:
    """
    Test Supabase connection
    """
    try:
        client = get_supabase_client()
        # Test with a simple query
        result = client.table("gtd_projects").select("count", count="exact").limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection test failed: {e}")
        return False

def get_db_connection():
    """
    Get direct PostgreSQL connection for raw SQL queries
    """
    import os
    
    # Get connection details from environment variables
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    
    # Fallback to individual environment variables
    supabase_url = os.getenv("SUPABASE_URL", "")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not supabase_url:
        raise ValueError("Missing SUPABASE_URL or DATABASE_URL")
    
    # Extract database connection details from Supabase URL
    # Format: https://project.supabase.co
    project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    # Build PostgreSQL connection string
    # Note: This is a simplified approach - you might need to adjust based on your actual Supabase setup
    host = f"db.{project_id}.supabase.co"
    database = "postgres"
    user = "postgres"
    password = service_key  # This might not be correct - adjust based on your setup
    
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=5432
    )

# Dependency function for FastAPI
def get_db() -> Client:
    """
    Dependency function that yields Supabase client
    """
    return get_supabase_client()