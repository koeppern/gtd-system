"""
Field CRUD operations
"""
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.field import Field
from app.schemas.field import FieldCreate, FieldUpdate


class CRUDField(CRUDBase[Field, FieldCreate, FieldUpdate]):
    """CRUD operations for Field model"""
    
    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str
    ) -> Optional[Field]:
        """
        Get field by name
        
        Args:
            db: Database session
            name: Field name
            
        Returns:
            Field instance or None
        """
        query = select(Field).where(
            Field.name == name,
            Field.deleted_at.is_(None)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: FieldCreate
    ) -> Field:
        """
        Create a new field
        
        Args:
            db: Database session
            obj_in: Field creation schema
            
        Returns:
            Created field instance
        """
        # Check if field name already exists
        existing_field = await self.get_by_name(db=db, name=obj_in.name)
        if existing_field:
            raise ValueError(f"Field with name '{obj_in.name}' already exists")
        
        return await super().create(db=db, obj_in=obj_in)
    
    async def get_field_stats(
        self,
        db: AsyncSession,
        *,
        field_id: int
    ) -> dict:
        """
        Get field usage statistics
        
        Args:
            db: Database session
            field_id: Field ID
            
        Returns:
            Dictionary with field statistics
        """
        from app.models.project import Project
        from app.models.task import Task
        
        # Count projects
        project_total = await db.scalar(
            select(func.count(Project.id)).where(
                and_(
                    Project.field_id == field_id,
                    Project.deleted_at.is_(None)
                )
            )
        )
        
        project_completed = await db.scalar(
            select(func.count(Project.id)).where(
                and_(
                    Project.field_id == field_id,
                    Project.deleted_at.is_(None),
                    Project.done_at.isnot(None)
                )
            )
        )
        
        # Count tasks
        task_total = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.field_id == field_id,
                    Task.deleted_at.is_(None)
                )
            )
        )
        
        task_completed = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.field_id == field_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.isnot(None)
                )
            )
        )
        
        return {
            "total_projects": project_total or 0,
            "active_projects": (project_total or 0) - (project_completed or 0),
            "completed_projects": project_completed or 0,
            "total_tasks": task_total or 0,
            "active_tasks": (task_total or 0) - (task_completed or 0),
            "completed_tasks": task_completed or 0,
            "completion_rate_projects": (
                (project_completed / project_total * 100) 
                if project_total and project_completed 
                else 0.0
            ),
            "completion_rate_tasks": (
                (task_completed / task_total * 100) 
                if task_total and task_completed 
                else 0.0
            ),
        }
    
    async def get_all_with_stats(
        self,
        db: AsyncSession
    ) -> List[dict]:
        """
        Get all fields with their usage statistics
        
        Args:
            db: Database session
            
        Returns:
            List of fields with statistics
        """
        fields = await self.get_multi(db=db, limit=1000)
        result = []
        
        for field in fields:
            stats = await self.get_field_stats(db=db, field_id=field.id)
            field_data = {
                "id": field.id,
                "name": field.name,
                "description": field.description,
                "created_at": field.created_at,
                "updated_at": field.updated_at,
                **stats
            }
            result.append(field_data)
        
        return result
    
    async def get_popular_fields(
        self,
        db: AsyncSession,
        *,
        limit: int = 10
    ) -> List[dict]:
        """
        Get most popular fields by usage
        
        Args:
            db: Database session
            limit: Maximum number of fields to return
            
        Returns:
            List of fields sorted by usage
        """
        from app.models.project import Project
        from app.models.task import Task
        
        # Get field usage counts
        field_usage_query = select(
            Field.id,
            Field.name,
            Field.description,
            func.count(Project.id).label('project_count'),
            func.count(Task.id).label('task_count')
        ).select_from(
            Field
        ).outerjoin(
            Project, and_(Project.field_id == Field.id, Project.deleted_at.is_(None))
        ).outerjoin(
            Task, and_(Task.field_id == Field.id, Task.deleted_at.is_(None))
        ).where(
            Field.deleted_at.is_(None)
        ).group_by(
            Field.id, Field.name, Field.description
        ).order_by(
            (func.count(Project.id) + func.count(Task.id)).desc()
        ).limit(limit)
        
        result = await db.execute(field_usage_query)
        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "project_count": row.project_count,
                "task_count": row.task_count,
                "total_usage": row.project_count + row.task_count
            }
            for row in result
        ]
    
    async def get_or_create_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        description: Optional[str] = None
    ) -> Field:
        """
        Get field by name or create if it doesn't exist
        
        Args:
            db: Database session
            name: Field name
            description: Optional field description
            
        Returns:
            Field instance
        """
        field = await self.get_by_name(db=db, name=name)
        if field:
            return field
        
        # Create new field
        field_data = FieldCreate(name=name, description=description)
        return await self.create(db=db, obj_in=field_data)


# Create instance
crud_field = CRUDField(Field)