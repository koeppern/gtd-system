"""
Quick-add API endpoints with Supabase direct connection
"""
from fastapi import APIRouter

router = APIRouter(prefix="/quick-add", tags=["quick-add"])

@router.post("/")
async def quick_add() -> dict:
    """Quick add functionality"""
    return {"message": "Quick-add endpoints not implemented yet"}