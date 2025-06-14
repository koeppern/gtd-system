"""
Fields API endpoints with Supabase direct connection
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client

from app.database import get_db
from app.config import get_settings

router = APIRouter(prefix="/fields", tags=["fields"])

@router.get("/")
async def get_fields(
    supabase: Client = Depends(get_db)
) -> List[dict]:
    """Get all fields"""
    try:
        # Query fields from Supabase (no user_id filter as it's a global lookup table)
        result = supabase.table("gtd_fields").select("*").execute()
        
        if not result.data:
            return []
        
        return [{
            "id": field.get("id"),
            "name": field.get("name") or f"Field {field.get('id', 'Unknown')}",
            "field_name": field.get("name"),  # Map 'name' to 'field_name' for consistency
            "description": field.get("description"),
            "created_at": field.get("created_at"),
            "updated_at": field.get("updated_at")
        } for field in result.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fields: {str(e)}"
        )