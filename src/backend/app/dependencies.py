"""
FastAPI dependencies for database, authentication, and other services
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import async_session_maker
from app.config import get_settings
from app.crud.user import crud_user
from app.models.user import User

# Security scheme for JWT authentication
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency
    
    Yields:
        AsyncSession: Database session
        
    Raises:
        HTTPException: If database is not available
    """
    try:
        async with async_session_maker() as session:
            # Test the connection before yielding
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            yield session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {str(e)}"
        )


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        db: Database session
        credentials: JWT token from Authorization header
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # TODO: Implement JWT token validation
    # For now, return the test user
    settings = get_settings()
    test_user_id = UUID(settings.gtd.default_user_id)
    
    user = await crud_user.get(db=db, id=test_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_test_user_directly(db: AsyncSession = Depends(get_db)) -> User:
    """
    Get test user directly for development/testing
    Used when authentication is not yet implemented
    
    Args:
        db: Database session
        
    Returns:
        User: Test user instance
        
    Raises:
        HTTPException: If test user not found
    """
    settings = get_settings()
    test_user_id = UUID(settings.gtd.default_user_id)
    
    user = await crud_user.get(db=db, id=test_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test user {test_user_id} not found in database"
        )
    
    return user