#!/usr/bin/env python3
"""
Check users in the database
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine


async def check_users():
    """Check all users in the database"""
    print("👥 Checking Users in Database")
    print("=" * 30)
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, first_name, last_name, email_address FROM gtd_users"))
        users = result.fetchall()
        
        if not users:
            print("❌ No users found in database")
        else:
            print(f"✅ Found {len(users)} user(s):")
            for user in users:
                print(f"  - ID: {user[0]} | Name: {user[1]} {user[2]} | Email: {user[3]}")


if __name__ == "__main__":
    asyncio.run(check_users())