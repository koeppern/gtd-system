"""
User API endpoints with Supabase direct connection
"""
from fastapi import APIRouter, HTTPException, Body
from app.database import get_db_connection
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_current_user_info() -> dict:
    """Get current user information"""
    return {"message": "User endpoints not implemented yet"}

@router.get("/me/settings")
async def get_user_settings(user_id: str = "00000000-0000-0000-0000-000000000001") -> Dict[str, Any]:
    """Get all user settings as a dictionary"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all settings for the user
        cursor.execute("""
            SELECT setting_key, setting_value 
            FROM gtd_user_settings 
            WHERE user_id = %s
        """, (user_id,))
        
        results = cursor.fetchall()
        
        # Convert to dictionary
        settings = {}
        for setting_key, setting_value in results:
            settings[setting_key] = setting_value
            
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(settings)} settings for user {user_id}")
        return settings
        
    except Exception as e:
        logger.error(f"Error retrieving user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/me/settings/{setting_key}")
async def get_user_setting(
    setting_key: str, 
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, Any]:
    """Get a specific user setting"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT setting_value 
            FROM gtd_user_settings 
            WHERE user_id = %s AND setting_key = %s
        """, (user_id, setting_key))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Setting '{setting_key}' not found")
            
        return {setting_key: result[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user setting '{setting_key}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/me/settings/{setting_key}")
async def update_user_setting(
    setting_key: str,
    setting_value: Dict[str, Any] = Body(...),
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, Any]:
    """Update or create a user setting"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use PostgreSQL UPSERT (INSERT ... ON CONFLICT)
        cursor.execute("""
            INSERT INTO gtd_user_settings (user_id, setting_key, setting_value)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, setting_key)
            DO UPDATE SET 
                setting_value = EXCLUDED.setting_value,
                updated_at = NOW()
            RETURNING setting_key, setting_value, updated_at
        """, (user_id, setting_key, json.dumps(setting_value)))
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Updated setting '{setting_key}' for user {user_id}")
        
        return {
            "setting_key": result[0],
            "setting_value": result[1],
            "updated_at": result[2].isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating user setting '{setting_key}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/me/settings/{setting_key}")
async def delete_user_setting(
    setting_key: str,
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, str]:
    """Delete a user setting"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM gtd_user_settings 
            WHERE user_id = %s AND setting_key = %s
            RETURNING setting_key
        """, (user_id, setting_key))
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Setting '{setting_key}' not found")
            
        logger.info(f"Deleted setting '{setting_key}' for user {user_id}")
        return {"message": f"Setting '{setting_key}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user setting '{setting_key}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")