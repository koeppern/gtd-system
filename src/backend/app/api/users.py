"""
User API endpoints with device-specific settings support
"""
from fastapi import APIRouter, HTTPException, Body, Query
from app.database import get_db_connection
import json
from typing import Dict, Any, Optional, Literal
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

DeviceType = Literal["desktop", "tablet", "phone"]

@router.get("/me")
async def get_current_user_info() -> dict:
    """Get current user information"""
    return {"message": "User endpoints not implemented yet"}

@router.get("/me/settings")
async def get_user_settings(
    user_id: str = "00000000-0000-0000-0000-000000000001",
    device: Optional[DeviceType] = None
) -> Dict[str, Any]:
    """
    Get user settings. 
    If device is specified, returns settings for that device only.
    If device is not specified, returns the full settings_json structure.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if device:
            # Get settings for specific device with fallback to defaults
            cursor.execute("""
                SELECT get_user_setting(%s, %s, key) as setting_value, key
                FROM gtd_setting_keys
                ORDER BY category, key
            """, (user_id, device))
            
            results = cursor.fetchall()
            
            # Convert to dictionary
            settings = {}
            for setting_value, key in results:
                # Parse JSONB value
                if setting_value is not None:
                    try:
                        settings[key] = json.loads(setting_value) if isinstance(setting_value, str) else setting_value
                    except (json.JSONDecodeError, TypeError):
                        settings[key] = setting_value
                        
        else:
            # Get full settings structure
            cursor.execute("""
                SELECT settings_json 
                FROM gtd_user_settings 
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result and result[0]:
                settings = result[0]
            else:
                # Return empty structure if no settings exist
                settings = {
                    "desktop": {},
                    "tablet": {},
                    "phone": {}
                }
            
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved settings for user {user_id}, device: {device}")
        return settings
        
    except Exception as e:
        logger.error(f"Error retrieving user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/me/settings/keys")
async def get_available_setting_keys() -> Dict[str, Any]:
    """Get all available setting keys with their metadata"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key, description, data_type, default_value, category
            FROM gtd_setting_keys
            ORDER BY category, key
        """)
        
        results = cursor.fetchall()
        
        # Group by category
        keys_by_category = {}
        for key, description, data_type, default_value, category in results:
            if category not in keys_by_category:
                keys_by_category[category] = []
                
            keys_by_category[category].append({
                "key": key,
                "description": description,
                "data_type": data_type,
                "default_value": default_value
            })
            
        cursor.close()
        conn.close()
        
        return {
            "categories": keys_by_category,
            "total_keys": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving setting keys: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/me/settings/{device}/{setting_key}")
async def get_user_setting(
    device: DeviceType,
    setting_key: str, 
    user_id: str = "00000000-0000-0000-0000-000000000001"
) -> Dict[str, Any]:
    """Get a specific user setting for a device"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use helper function to get setting with fallback to default
        cursor.execute("""
            SELECT get_user_setting(%s, %s, %s) as setting_value
        """, (user_id, device, setting_key))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None or result[0] is None:
            raise HTTPException(status_code=404, detail=f"Setting '{setting_key}' not found for device '{device}'")
            
        # Parse JSONB value
        setting_value = result[0]
        if isinstance(setting_value, str):
            try:
                setting_value = json.loads(setting_value)
            except json.JSONDecodeError:
                pass
                
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