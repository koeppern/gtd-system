"""
Generic CRUD base class
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from sqlalchemy import and_, or_, desc, asc, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.models.base import Base

# Type variables
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD operations base class"""
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    async def get(
        self,
        db: AsyncSession,
        id: Union[int, UUID],
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Get a single record by ID
        
        Args:
            db: Database session
            id: Record ID
            include_deleted: Include soft-deleted records
            
        Returns:
            Model instance or None
        """
        query = select(self.model).where(self.model.id == id)
        
        # Filter out soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_desc: Order descending if True
            include_deleted: Include soft-deleted records
            filters: Additional filters to apply
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        # Filter out soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))
        elif hasattr(self.model, 'created_at'):
            # Default ordering by creation date
            query = query.order_by(desc(self.model.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(
        self,
        db: AsyncSession,
        *,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records with optional filtering
        
        Args:
            db: Database session
            include_deleted: Include soft-deleted records
            filters: Additional filters to apply
            
        Returns:
            Number of matching records
        """
        query = select(func.count(self.model.id))
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        # Filter out soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await db.execute(query)
        return result.scalar()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Create a new record
        
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created model instance
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record
        
        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Pydantic schema or dict with update data
            
        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        id: Union[int, UUID],
        hard_delete: bool = False
    ) -> Optional[ModelType]:
        """
        Delete a record (soft delete by default)
        
        Args:
            db: Database session
            id: Record ID
            hard_delete: Permanently delete if True, soft delete if False
            
        Returns:
            Deleted model instance or None if not found
        """
        db_obj = await self.get(db=db, id=id)
        if not db_obj:
            return None
        
        if hard_delete or not hasattr(db_obj, 'deleted_at'):
            # Hard delete
            await db.delete(db_obj)
        else:
            # Soft delete
            db_obj.soft_delete()
        
        await db.commit()
        return db_obj
    
    async def restore(
        self,
        db: AsyncSession,
        *,
        id: Union[int, UUID]
    ) -> Optional[ModelType]:
        """
        Restore a soft-deleted record
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Restored model instance or None if not found
        """
        db_obj = await self.get(db=db, id=id, include_deleted=True)
        if not db_obj or not hasattr(db_obj, 'deleted_at') or not db_obj.is_deleted:
            return None
        
        db_obj.restore()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Search records across multiple fields
        
        Args:
            db: Database session
            query: Search query string
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Include soft-deleted records
            
        Returns:
            List of matching model instances
        """
        search_query = select(self.model)
        
        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                field_attr = getattr(self.model, field)
                search_conditions.append(field_attr.ilike(f"%{query}%"))
        
        if search_conditions:
            search_query = search_query.where(or_(*search_conditions))
        
        # Filter out soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            search_query = search_query.where(self.model.deleted_at.is_(None))
        
        # Apply pagination
        search_query = search_query.offset(skip).limit(limit)
        
        result = await db.execute(search_query)
        return result.scalars().all()
    
    async def exists(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Any],
        include_deleted: bool = False
    ) -> bool:
        """
        Check if a record exists with given filters
        
        Args:
            db: Database session
            filters: Filters to apply
            include_deleted: Include soft-deleted records
            
        Returns:
            True if record exists, False otherwise
        """
        query = select(self.model.id)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        # Filter out soft-deleted records unless requested
        if not include_deleted and hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))
        
        query = query.limit(1)
        result = await db.execute(query)
        return result.first() is not None
    
    async def bulk_update(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Any],
        update_data: Dict[str, Any]
    ) -> int:
        """
        Bulk update records matching filters
        
        Args:
            db: Database session
            filters: Filters to identify records to update
            update_data: Data to update
            
        Returns:
            Number of updated records
        """
        query = update(self.model)
        
        # Apply filters
        conditions = []
        for field, value in filters.items():
            if hasattr(self.model, field):
                conditions.append(getattr(self.model, field) == value)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.values(**update_data)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount
    
    async def bulk_delete(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Any],
        hard_delete: bool = False
    ) -> int:
        """
        Bulk delete records matching filters
        
        Args:
            db: Database session
            filters: Filters to identify records to delete
            hard_delete: Permanently delete if True, soft delete if False
            
        Returns:
            Number of deleted records
        """
        if hard_delete or not hasattr(self.model, 'deleted_at'):
            # Hard delete
            query = delete(self.model)
            
            # Apply filters
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    conditions.append(getattr(self.model, field) == value)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await db.execute(query)
            await db.commit()
            return result.rowcount
        else:
            # Soft delete - update deleted_at timestamp
            return await self.bulk_update(
                db=db,
                filters=filters,
                update_data={"deleted_at": func.now()}
            )