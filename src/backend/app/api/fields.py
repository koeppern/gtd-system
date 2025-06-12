"""
Fields API endpoints with Supabase direct connection
"""
from fastapi import APIRouter

router = APIRouter(prefix="/fields", tags=["fields"])

@router.get("/")
async def get_fields() -> dict:
    """Get all fields"""
    return {"message": "Fields endpoints not implemented yet"}