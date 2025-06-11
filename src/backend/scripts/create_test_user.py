#!/usr/bin/env python3
"""
Create a test user for development
"""
import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import async_session_maker
from app.crud.user import crud_user
from app.schemas.user import UserCreate


async def create_test_user():
    """Create a test user with the expected ID from the frontend"""
    user_uuid = uuid.UUID("00000000-0000-0000-0000-000000000001")  # The ID used in frontend config
    
    async with async_session_maker() as db:
        # Check if user already exists
        existing_user = await crud_user.get(db, id=user_uuid)
        if existing_user:
            print(f"✓ Test user already exists: {existing_user.email_address}")
            return existing_user
        
        # Create test user manually using SQLAlchemy model since UserCreate doesn't support id
        from app.models.user import User
        user = User(
            id=user_uuid,
            first_name="Test",
            last_name="User",
            email_address="test@example.com",
            timezone="UTC",
            date_format="YYYY-MM-DD",
            time_format="24h",
            weekly_review_day=0,  # Sunday
            is_active=True,
            email_verified=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        print(f"✅ Created test user: {user.email_address} (ID: {user.id})")
        return user


async def main():
    print("🧪 Creating Test User for Development")
    print("=" * 40)
    
    try:
        user = await create_test_user()
        print(f"\n✅ Test user ready!")
        print(f"Email: {user.email_address}")
        print(f"ID: {user.id}")
        return True
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)