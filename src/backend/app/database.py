"""
Supabase client configuration and connection management
"""
from typing import Optional
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

# Dependency function for FastAPI
def get_db() -> Client:
    """
    Dependency function that yields Supabase client
    """
    return get_supabase_client()