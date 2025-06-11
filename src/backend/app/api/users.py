"""
User API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.dependencies import get_db, get_test_user_directly
from app.crud.user import crud_user
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserStats

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_test_user_directly)
) -> UserResponse:
    """
    Get current user information
    
    Returns:
        UserResponse: Current user data
    """
    return UserResponse.from_model(current_user)


@router.get("/me/stats", response_model=UserStats)
async def get_current_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> UserStats:
    """
    Get current user statistics
    
    Returns:
        UserStats: User statistics including projects and tasks counts
    """
    stats = await crud_user.get_user_stats(db=db, user_id=current_user.id)
    return UserStats(**stats)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> UserResponse:
    """
    Update current user information
    
    Args:
        user_update: User update data
        
    Returns:
        UserResponse: Updated user data
    """
    try:
        updated_user = await crud_user.update(
            db=db, 
            db_obj=current_user, 
            obj_in=user_update
        )
        return UserResponse.from_model(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me/email")
async def update_user_email(
    new_email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Update user email address
    
    Args:
        new_email: New email address
        
    Returns:
        dict: Success message
    """
    try:
        await crud_user.update_email(
            db=db,
            user=current_user,
            new_email=new_email
        )
        return {"message": "Email updated successfully. Please verify your new email."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/me/verify-email")
async def verify_user_email(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Mark user email as verified
    
    Returns:
        dict: Success message
    """
    await crud_user.verify_email(db=db, user=current_user)
    return {"message": "Email verified successfully"}


@router.post("/me/activate")
async def activate_user_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Activate user account
    
    Returns:
        dict: Success message
    """
    await crud_user.activate(db=db, user=current_user)
    return {"message": "Account activated successfully"}


@router.post("/me/deactivate")
async def deactivate_user_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Deactivate user account
    
    Returns:
        dict: Success message
    """
    await crud_user.deactivate(db=db, user=current_user)
    return {"message": "Account deactivated successfully"}


# Admin endpoints (for future use)
@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create a new user (admin only)
    
    Args:
        user_create: User creation data
        
    Returns:
        UserResponse: Created user data
    """
    try:
        user = await crud_user.create(db=db, obj_in=user_create)
        return UserResponse.from_model(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get user by ID (admin only)
    
    Args:
        user_id: User ID
        
    Returns:
        UserResponse: User data
    """
    user = await crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_model(user)


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> UserStats:
    """
    Get user statistics by ID (admin only)
    
    Args:
        user_id: User ID
        
    Returns:
        UserStats: User statistics
    """
    # Check if user exists
    user = await crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    stats = await crud_user.get_user_stats(db=db, user_id=user_id)
    return UserStats(**stats)