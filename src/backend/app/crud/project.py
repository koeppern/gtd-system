"""
Project CRUD operations
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectFilters


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """CRUD operations for Project model"""
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ProjectFilters] = None
    ) -> List[Project]:
        """
        Get projects for a specific user with optional filters
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional project filters
            
        Returns:
            List of project instances
        """
        query = select(Project).where(
            Project.user_id == user_id,
            Project.deleted_at.is_(None) if not (filters and filters.include_deleted) else True
        )
        
        # Apply filters
        if filters:
            if filters.field_id is not None:
                query = query.where(Project.field_id == filters.field_id)
            
            if filters.is_done is not None:
                if filters.is_done:
                    query = query.where(Project.done_at.isnot(None))
                else:
                    query = query.where(Project.done_at.is_(None))
            
            if filters.do_this_week is not None:
                query = query.where(Project.do_this_week == filters.do_this_week)
            
            if filters.has_tasks is not None:
                from app.models.task import Task
                if filters.has_tasks:
                    query = query.where(
                        Project.id.in_(
                            select(Task.project_id).where(
                                Task.project_id.isnot(None),
                                Task.deleted_at.is_(None)
                            ).distinct()
                        )
                    )
                else:
                    query = query.where(
                        Project.id.notin_(
                            select(Task.project_id).where(
                                Task.project_id.isnot(None),
                                Task.deleted_at.is_(None)
                            ).distinct()
                        )
                    )
            
            if filters.completed_after:
                query = query.where(Project.done_at >= filters.completed_after)
            
            if filters.completed_before:
                query = query.where(Project.done_at <= filters.completed_before)
            
            if filters.created_after:
                query = query.where(Project.created_at >= filters.created_after)
            
            if filters.created_before:
                query = query.where(Project.created_at <= filters.created_before)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Project.project_name.ilike(search_term),
                        Project.keywords.ilike(search_term),
                        Project.readings.ilike(search_term)
                    )
                )
        
        # Order by creation date (newest first) by default
        query = query.order_by(desc(Project.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active_projects(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get active (not completed, not deleted) projects for a user
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active project instances
        """
        query = select(Project).where(
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
            Project.done_at.is_(None)
        ).order_by(desc(Project.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_weekly_projects(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> List[Project]:
        """
        Get projects scheduled for this week
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of weekly project instances
        """
        query = select(Project).where(
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
            Project.done_at.is_(None),
            Project.do_this_week == True
        ).order_by(desc(Project.updated_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def complete_project(
        self,
        db: AsyncSession,
        *,
        project: Project,
        completion_time: Optional[datetime] = None,
        auto_complete_tasks: bool = False
    ) -> Project:
        """
        Mark a project as completed
        
        Args:
            db: Database session
            project: Project instance
            completion_time: Optional completion timestamp
            auto_complete_tasks: Also complete all active tasks
            
        Returns:
            Updated project instance
        """
        project.done_at = completion_time or datetime.utcnow()
        
        if auto_complete_tasks:
            from app.models.task import Task
            # Complete all active tasks in this project
            await db.execute(
                Task.__table__.update()
                .where(
                    and_(
                        Task.project_id == project.id,
                        Task.deleted_at.is_(None),
                        Task.done_at.is_(None)
                    )
                )
                .values(done_at=project.done_at)
            )
        
        await db.commit()
        await db.refresh(project)
        return project
    
    async def reopen_project(
        self,
        db: AsyncSession,
        *,
        project: Project
    ) -> Project:
        """
        Reopen a completed project
        
        Args:
            db: Database session
            project: Project instance
            
        Returns:
            Updated project instance
        """
        project.done_at = None
        await db.commit()
        await db.refresh(project)
        return project
    
    async def get_project_with_task_stats(
        self,
        db: AsyncSession,
        *,
        project_id: int
    ) -> Optional[dict]:
        """
        Get project with task statistics
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Project data with task statistics or None
        """
        project = await self.get(db=db, id=project_id)
        if not project:
            return None
        
        from app.models.task import Task
        
        # Count tasks
        task_total = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.deleted_at.is_(None)
                )
            )
        )
        
        task_completed = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.isnot(None)
                )
            )
        )
        
        # Count priority tasks
        high_priority_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.priority.in_([1, 2])
                )
            )
        )
        
        # Count overdue tasks
        from datetime import date
        overdue_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.do_on_date < date.today()
                )
            )
        )
        
        return {
            "project": project,
            "task_count": task_total or 0,
            "completed_tasks": task_completed or 0,
            "pending_tasks": (task_total or 0) - (task_completed or 0),
            "high_priority_tasks": high_priority_tasks or 0,
            "overdue_tasks": overdue_tasks or 0,
            "completion_percentage": (
                (task_completed / task_total * 100) 
                if task_total and task_completed 
                else 0.0
            )
        }
    
    async def search_projects(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Project]:
        """
        Search projects by name, keywords, and content
        
        Args:
            db: Database session
            user_id: User ID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching project instances
        """
        search_term = f"%{query}%"
        search_query = select(Project).where(
            and_(
                Project.user_id == user_id,
                Project.deleted_at.is_(None),
                or_(
                    Project.project_name.ilike(search_term),
                    Project.keywords.ilike(search_term),
                    Project.readings.ilike(search_term),
                    Project.gtd_processes.ilike(search_term)
                )
            )
        ).order_by(desc(Project.updated_at)).offset(skip).limit(limit)
        
        result = await db.execute(search_query)
        return result.scalars().all()
    
    async def get_projects_by_field(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        field_id: int,
        include_completed: bool = False
    ) -> List[Project]:
        """
        Get projects in a specific field
        
        Args:
            db: Database session
            user_id: User ID
            field_id: Field ID
            include_completed: Include completed projects
            
        Returns:
            List of project instances
        """
        query = select(Project).where(
            and_(
                Project.user_id == user_id,
                Project.field_id == field_id,
                Project.deleted_at.is_(None)
            )
        )
        
        if not include_completed:
            query = query.where(Project.done_at.is_(None))
        
        query = query.order_by(desc(Project.created_at))
        
        result = await db.execute(query)
        return result.scalars().all()


# Create instance
crud_project = CRUDProject(Project)