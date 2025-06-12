"""
Search API endpoints with Supabase direct connection
"""
from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
async def search() -> dict:
    """Search across projects and tasks"""
    return {"message": "Search endpoints not implemented yet"}