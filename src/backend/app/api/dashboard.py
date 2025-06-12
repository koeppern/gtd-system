"""
Dashboard API endpoints with Supabase direct connection
"""
from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
async def get_dashboard() -> dict:
    """Get dashboard data"""
    return {"message": "Dashboard endpoints not implemented yet"}