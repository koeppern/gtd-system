"""
User API endpoints with Supabase direct connection
"""
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_current_user_info() -> dict:
    """Get current user information"""
    return {"message": "User endpoints not implemented yet"}