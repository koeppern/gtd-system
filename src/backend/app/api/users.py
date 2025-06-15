"""
User API endpoints with device-specific settings support
"""
from fastapi import APIRouter, HTTPException, Body, Query, Depends
from app.database import get_supabase_client
from app.dependencies import get_current_user
from supabase import Client
import json
from typing import Dict, Any, Optional, Literal
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

DeviceType = Literal["desktop", "tablet", "phone"]

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current user information"""
    return {
        "user_id": current_user.get("user_id") or current_user.get("sub"),
        "email": current_user.get("email"),
        "role": current_user.get("role", "authenticated")
    }

@router.get("/me/settings")
async def get_user_settings(
    device: Optional[DeviceType] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get user settings. 
    If device is specified, returns settings for that device only.
    If device is not specified, returns the full settings_json structure.
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        
        if device:
            # Get all setting keys
            setting_keys_result = supabase.table("gtd_setting_keys").select("key, default_value").execute()
            
            # Get user settings
            user_settings_result = supabase.table("gtd_user_settings").select("settings_json").eq("user_id", user_id).execute()
            
            user_device_settings = {}
            if user_settings_result.data:
                settings_json = user_settings_result.data[0].get("settings_json", {})
                user_device_settings = settings_json.get(device, {})
            
            # Merge with defaults
            settings = {}
            for setting_key_info in setting_keys_result.data:
                key = setting_key_info["key"]
                default_value = setting_key_info["default_value"]
                settings[key] = user_device_settings.get(key, default_value)
                        
        else:
            # Get full settings structure
            user_settings_result = supabase.table("gtd_user_settings").select("settings_json").eq("user_id", user_id).execute()
            
            if user_settings_result.data and user_settings_result.data[0].get("settings_json"):
                settings = user_settings_result.data[0]["settings_json"]
            else:
                # Return empty structure if no settings exist
                settings = {
                    "desktop": {},
                    "tablet": {},
                    "phone": {}
                }
        
        logger.info(f"Retrieved settings for user {user_id}, device: {device}")
        return settings
        
    except Exception as e:
        logger.error(f"Error retrieving user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/me/settings/keys")
async def get_available_setting_keys(
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get all available setting keys with their metadata"""
    try:
        result = supabase.table("gtd_setting_keys").select("key, description, data_type, default_value, category").order("category, key").execute()
        
        # Group by category
        keys_by_category = {}
        for item in result.data:
            category = item["category"]
            if category not in keys_by_category:
                keys_by_category[category] = []
                
            keys_by_category[category].append({
                "key": item["key"],
                "description": item["description"],
                "data_type": item["data_type"],
                "default_value": item["default_value"]
            })
        
        return {
            "categories": keys_by_category,
            "total_keys": len(result.data)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving setting keys: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/me/settings/{device}/{setting_key}")
async def get_user_setting(
    device: DeviceType,
    setting_key: str, 
    user_id: str = "00000000-0000-0000-0000-000000000001",
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get a specific user setting for a device"""
    try:
        # First, check if the setting key exists
        setting_key_result = supabase.table("gtd_setting_keys").select("*").eq("key", setting_key).execute()
        
        if not setting_key_result.data:
            raise HTTPException(status_code=404, detail=f"Setting key '{setting_key}' not found")
        
        setting_key_info = setting_key_result.data[0]
        default_value = setting_key_info.get("default_value")
        
        # Get user settings
        user_settings_result = supabase.table("gtd_user_settings").select("settings_json").eq("user_id", user_id).execute()
        
        setting_value = default_value  # Default fallback
        
        if user_settings_result.data:
            settings_json = user_settings_result.data[0].get("settings_json", {})
            device_settings = settings_json.get(device, {})
            if setting_key in device_settings:
                setting_value = device_settings[setting_key]
        
        return {
            "device": device,
            "setting_key": setting_key,
            "setting_value": setting_value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user setting '{setting_key}' for device '{device}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/me/settings/{device}/{setting_key}")
async def update_user_setting(
    device: DeviceType,
    setting_key: str,
    setting_value: Any = Body(...),
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, Any]:
    """Update or create a user setting for a specific device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate setting key exists
        cursor.execute("SELECT 1 FROM gtd_setting_keys WHERE key = %s", (setting_key,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"Invalid setting key: {setting_key}")
        
        # Use helper function to set the setting
        cursor.execute("""
            SELECT set_user_setting(%s, %s, %s, %s)
        """, (user_id, device, setting_key, json.dumps(setting_value)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Updated setting '{setting_key}' for user {user_id}, device: {device}")
        
        return {
            "device": device,
            "setting_key": setting_key,
            "setting_value": setting_value,
            "message": "Setting updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user setting '{setting_key}' for device '{device}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/me/settings/{device}")
async def update_device_settings(
    device: DeviceType,
    settings: Dict[str, Any] = Body(...),
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, Any]:
    """Update multiple settings for a specific device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate all setting keys exist
        valid_keys = set()
        cursor.execute("SELECT key FROM gtd_setting_keys")
        for (key,) in cursor.fetchall():
            valid_keys.add(key)
            
        invalid_keys = set(settings.keys()) - valid_keys
        if invalid_keys:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid setting keys: {', '.join(invalid_keys)}"
            )
        
        # Update each setting
        updated_count = 0
        for setting_key, setting_value in settings.items():
            cursor.execute("""
                SELECT set_user_setting(%s, %s, %s, %s)
            """, (user_id, device, setting_key, json.dumps(setting_value)))
            updated_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Updated {updated_count} settings for user {user_id}, device: {device}")
        
        return {
            "device": device,
            "updated_count": updated_count,
            "settings": settings,
            "message": f"Updated {updated_count} settings successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device settings for '{device}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/me/settings/{device}/{setting_key}")
async def delete_user_setting(
    device: DeviceType,
    setting_key: str,
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, str]:
    """Delete a user setting for a specific device (resets to default)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current settings
        cursor.execute("""
            SELECT settings_json 
            FROM gtd_user_settings 
            WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            raise HTTPException(status_code=404, detail=f"No settings found for user")
            
        settings_json = result[0]
        
        # Remove the specific setting from the device category
        if device in settings_json and setting_key in settings_json[device]:
            # Create updated settings
            updated_settings = dict(settings_json)
            if device in updated_settings:
                updated_settings[device] = dict(updated_settings[device])
                del updated_settings[device][setting_key]
                
                # Update in database
                cursor.execute("""
                    UPDATE gtd_user_settings 
                    SET settings_json = %s, updated_at = NOW()
                    WHERE user_id = %s
                """, (json.dumps(updated_settings), user_id))
                
                conn.commit()
                
                logger.info(f"Deleted setting '{setting_key}' for user {user_id}, device: {device}")
                message = f"Setting '{setting_key}' deleted successfully (reset to default)"
            else:
                message = f"Setting '{setting_key}' was already using default value"
        else:
            message = f"Setting '{setting_key}' was already using default value"
            
        cursor.close()
        conn.close()
        
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user setting '{setting_key}' for device '{device}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/me/settings")
async def reset_all_user_settings(
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, str]:
    """Reset all user settings to defaults"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM gtd_user_settings 
            WHERE user_id = %s
            RETURNING user_id
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if result:
            logger.info(f"Reset all settings for user {user_id}")
            return {"message": "All settings reset to defaults successfully"}
        else:
            return {"message": "No settings found to reset"}
        
    except Exception as e:
        logger.error(f"Error resetting user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/me/stats")
async def get_user_stats() -> dict:
    """Get user statistics (placeholder)"""
    return {
        "total_tasks": 0,
        "completed_tasks": 0,
        "total_projects": 0,
        "completed_projects": 0
    }