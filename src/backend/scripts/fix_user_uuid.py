#!/usr/bin/env python3
"""
Fix the user UUID format in the database
"""
import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine


async def fix_user_uuid():
    """Delete the incorrectly formatted user and create a new one with proper UUID"""
    print("🔧 Fixing User UUID Format")
    print("=" * 30)
    
    async with engine.begin() as conn:
        # Delete the incorrectly formatted user
        await conn.execute(text("DELETE FROM gtd_users WHERE id='00000000000000000000000000000001'"))
        print("✓ Deleted incorrectly formatted user")
        
        # Insert user with proper UUID format
        user_uuid = "00000000-0000-0000-0000-000000000001"
        await conn.execute(text("""
            INSERT INTO gtd_users (
                id, first_name, last_name, email_address, timezone, 
                date_format, time_format, weekly_review_day, is_active, email_verified
            ) VALUES (:id, :first_name, :last_name, :email_address, :timezone, :date_format, :time_format, :weekly_review_day, :is_active, :email_verified)
        """), {
            "id": user_uuid,
            "first_name": "Test",
            "last_name": "User", 
            "email_address": "test@example.com",
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "time_format": "24h",
            "weekly_review_day": 0,
            "is_active": True,
            "email_verified": True
        })
        print(f"✅ Created user with proper UUID: {user_uuid}")


async def main():
    try:
        await fix_user_uuid()
        print("\n✅ User UUID format fixed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error fixing user UUID: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)