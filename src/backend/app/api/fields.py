"""
Field API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_test_user_directly
from app.crud.field import crud_field
from app.models.user import User
from app.schemas.field import FieldResponse, FieldCreate, FieldUpdate, FieldWithStats

router = APIRouter(prefix="/fields", tags=["fields"])


@router.get("/", response_model=List[FieldResponse])
async def get_fields(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[FieldResponse]:
    """
    Get all fields with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[FieldResponse]: List of field data
    """
    fields = await crud_field.get_multi(db=db, skip=skip, limit=limit)
    return [FieldResponse.from_model(field) for field in fields]


@router.get("/with-stats", response_model=List[FieldWithStats])
async def get_fields_with_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[FieldWithStats]:
    """
    Get all fields with usage statistics
    
    Returns:
        List[FieldWithStats]: List of fields with statistics
    """
    fields_with_stats = await crud_field.get_all_with_stats(db=db)
    return [FieldWithStats(**field_data) for field_data in fields_with_stats]


@router.get("/popular", response_model=List[FieldWithStats])
async def get_popular_fields(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of fields to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> List[FieldWithStats]:
    """
    Get most popular fields by usage
    
    Args:
        limit: Maximum number of fields to return
        
    Returns:
        List[FieldWithStats]: List of popular fields with usage counts
    """
    popular_fields = await crud_field.get_popular_fields(db=db, limit=limit)
    return [FieldWithStats(**field_data) for field_data in popular_fields]


@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> FieldResponse:
    """
    Get field by ID
    
    Args:
        field_id: Field ID
        
    Returns:
        FieldResponse: Field data
    """
    field = await crud_field.get(db=db, id=field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    return FieldResponse.from_model(field)


@router.get("/{field_id}/stats")
async def get_field_stats(
    field_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Get field usage statistics
    
    Args:
        field_id: Field ID
        
    Returns:
        dict: Field statistics
    """
    # Check if field exists
    field = await crud_field.get(db=db, id=field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    stats = await crud_field.get_field_stats(db=db, field_id=field_id)
    return stats


@router.post("/", response_model=FieldResponse)
async def create_field(
    field_create: FieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> FieldResponse:
    """
    Create a new field
    
    Args:
        field_create: Field creation data
        
    Returns:
        FieldResponse: Created field data
    """
    try:
        field = await crud_field.create(db=db, obj_in=field_create)
        return FieldResponse.from_model(field)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: int,
    field_update: FieldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> FieldResponse:
    """
    Update a field
    
    Args:
        field_id: Field ID
        field_update: Field update data
        
    Returns:
        FieldResponse: Updated field data
    """
    field = await crud_field.get(db=db, id=field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    updated_field = await crud_field.update(
        db=db, 
        db_obj=field, 
        obj_in=field_update
    )
    return FieldResponse.from_model(updated_field)


@router.delete("/{field_id}")
async def delete_field(
    field_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the field"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> dict:
    """
    Delete a field (soft delete by default)
    
    Args:
        field_id: Field ID
        hard_delete: Permanently delete if True, soft delete if False
        
    Returns:
        dict: Success message
    """
    field = await crud_field.delete(db=db, id=field_id, hard_delete=hard_delete)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    action = "permanently deleted" if hard_delete else "soft deleted"
    return {"message": f"Field {action} successfully"}


@router.post("/{field_id}/restore", response_model=FieldResponse)
async def restore_field(
    field_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> FieldResponse:
    """
    Restore a soft-deleted field
    
    Args:
        field_id: Field ID
        
    Returns:
        FieldResponse: Restored field data
    """
    field = await crud_field.restore(db=db, id=field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found or not deleted"
        )
    
    return FieldResponse.from_model(field)


@router.get("/name/{field_name}", response_model=FieldResponse)
async def get_field_by_name(
    field_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> FieldResponse:
    """
    Get field by name
    
    Args:
        field_name: Field name
        
    Returns:
        FieldResponse: Field data
    """
    field = await crud_field.get_by_name(db=db, name=field_name)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    return FieldResponse.from_model(field)


@router.post("/get-or-create", response_model=FieldResponse)
async def get_or_create_field(
    field_name: str,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_test_user_directly)
) -> FieldResponse:
    """
    Get field by name or create if it doesn't exist
    
    Args:
        field_name: Field name
        description: Optional field description
        
    Returns:
        FieldResponse: Field data (existing or newly created)
    """
    field = await crud_field.get_or_create_by_name(
        db=db, 
        name=field_name, 
        description=description
    )
    return FieldResponse.from_model(field)