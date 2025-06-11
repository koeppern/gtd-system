"""
Task CRUD operations
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilters


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """CRUD operations for Task model"""
    
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[TaskFilters] = None
    ) -> List[Task]:
        """
        Get tasks for a specific user with optional filters
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional task filters
            
        Returns:
            List of task instances
        """
        query = select(Task).where(
            Task.user_id == user_id,
            Task.deleted_at.is_(None) if not (filters and filters.include_deleted) else True
        )
        
        # Apply filters
        if filters:
            if filters.project_id is not None:
                query = query.where(Task.project_id == filters.project_id)
            
            if filters.field_id is not None:
                query = query.where(Task.field_id == filters.field_id)
            
            if filters.is_done is not None:
                if filters.is_done:
                    query = query.where(Task.done_at.isnot(None))
                else:
                    query = query.where(Task.done_at.is_(None))
            
            # GTD status filters
            if filters.do_today is not None:
                query = query.where(Task.do_today == filters.do_today)
            
            if filters.do_this_week is not None:
                query = query.where(Task.do_this_week == filters.do_this_week)
            
            if filters.is_reading is not None:
                query = query.where(Task.is_reading == filters.is_reading)
            
            if filters.wait_for is not None:
                query = query.where(Task.wait_for == filters.wait_for)
            
            if filters.postponed is not None:
                query = query.where(Task.postponed == filters.postponed)
            
            if filters.reviewed is not None:
                query = query.where(Task.reviewed == filters.reviewed)
            
            # Priority filters
            if filters.priority is not None:
                query = query.where(Task.priority == filters.priority)
            
            if filters.priority_min is not None:
                query = query.where(Task.priority >= filters.priority_min)
            
            if filters.priority_max is not None:
                query = query.where(Task.priority <= filters.priority_max)
            
            # Date filters
            if filters.due_date is not None:
                query = query.where(Task.do_on_date == filters.due_date)
            
            if filters.due_before is not None:
                query = query.where(Task.do_on_date <= filters.due_before)
            
            if filters.due_after is not None:
                query = query.where(Task.do_on_date >= filters.due_after)
            
            if filters.overdue is not None:
                today = date.today()
                if filters.overdue:
                    query = query.where(
                        and_(
                            Task.do_on_date < today,
                            Task.done_at.is_(None)
                        )
                    )
                else:
                    query = query.where(
                        or_(
                            Task.do_on_date >= today,
                            Task.do_on_date.is_(None),
                            Task.done_at.isnot(None)
                        )
                    )
            
            if filters.completed_after:
                query = query.where(Task.done_at >= filters.completed_after)
            
            if filters.completed_before:
                query = query.where(Task.done_at <= filters.completed_before)
            
            if filters.created_after:
                query = query.where(Task.created_at >= filters.created_after)
            
            if filters.created_before:
                query = query.where(Task.created_at <= filters.created_before)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(Task.task_name.ilike(search_term))
        
        # Default ordering: priority (high first), then due date, then creation date
        query = query.order_by(
            asc(Task.priority.nullslast()),
            asc(Task.do_on_date.nullslast()),
            desc(Task.created_at)
        )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_today_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> List[Task]:
        """
        Get tasks scheduled for today
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of today's task instances
        """
        today = date.today()
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.done_at.is_(None),
                or_(
                    Task.do_today == True,
                    Task.do_on_date == today
                )
            )
        ).order_by(asc(Task.priority.nullslast()), desc(Task.created_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_week_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> List[Task]:
        """
        Get tasks scheduled for this week
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of this week's task instances
        """
        today = date.today()
        # Calculate end of week (Sunday)
        days_until_sunday = 6 - today.weekday()
        end_of_week = today + timedelta(days=days_until_sunday)
        
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.done_at.is_(None),
                or_(
                    Task.do_this_week == True,
                    and_(
                        Task.do_on_date >= today,
                        Task.do_on_date <= end_of_week
                    )
                )
            )
        ).order_by(asc(Task.priority.nullslast()), asc(Task.do_on_date.nullslast()))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_overdue_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> List[Task]:
        """
        Get overdue tasks
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of overdue task instances
        """
        today = date.today()
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.done_at.is_(None),
                Task.do_on_date < today
            )
        ).order_by(asc(Task.do_on_date), asc(Task.priority.nullslast()))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_waiting_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> List[Task]:
        """
        Get tasks waiting for someone/something
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of waiting task instances
        """
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.done_at.is_(None),
                Task.wait_for == True
            )
        ).order_by(desc(Task.created_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_reading_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> List[Task]:
        """
        Get reading tasks
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of reading task instances
        """
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.done_at.is_(None),
                Task.is_reading == True
            )
        ).order_by(desc(Task.created_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def complete_task(
        self,
        db: AsyncSession,
        *,
        task: Task,
        completion_time: Optional[datetime] = None
    ) -> Task:
        """
        Mark a task as completed
        
        Args:
            db: Database session
            task: Task instance
            completion_time: Optional completion timestamp
            
        Returns:
            Updated task instance
        """
        task.done_at = completion_time or datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        return task
    
    async def reopen_task(
        self,
        db: AsyncSession,
        *,
        task: Task
    ) -> Task:
        """
        Reopen a completed task
        
        Args:
            db: Database session
            task: Task instance
            
        Returns:
            Updated task instance
        """
        task.done_at = None
        await db.commit()
        await db.refresh(task)
        return task
    
    async def schedule_for_today(
        self,
        db: AsyncSession,
        *,
        task: Task
    ) -> Task:
        """
        Schedule task for today
        
        Args:
            db: Database session
            task: Task instance
            
        Returns:
            Updated task instance
        """
        task.do_today = True
        task.do_on_date = date.today()
        await db.commit()
        await db.refresh(task)
        return task
    
    async def schedule_for_week(
        self,
        db: AsyncSession,
        *,
        task: Task
    ) -> Task:
        """
        Schedule task for this week
        
        Args:
            db: Database session
            task: Task instance
            
        Returns:
            Updated task instance
        """
        task.do_this_week = True
        await db.commit()
        await db.refresh(task)
        return task
    
    async def set_priority(
        self,
        db: AsyncSession,
        *,
        task: Task,
        priority: int
    ) -> Task:
        """
        Set task priority
        
        Args:
            db: Database session
            task: Task instance
            priority: Priority level (1-5)
            
        Returns:
            Updated task instance
        """
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 (highest) and 5 (lowest)")
        
        task.priority = priority
        await db.commit()
        await db.refresh(task)
        return task
    
    async def search_tasks(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Task]:
        """
        Search tasks by name
        
        Args:
            db: Database session
            user_id: User ID
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching task instances
        """
        search_term = f"%{query}%"
        search_query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
                Task.task_name.ilike(search_term)
            )
        ).order_by(desc(Task.updated_at)).offset(skip).limit(limit)
        
        result = await db.execute(search_query)
        return result.scalars().all()
    
    async def get_tasks_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: int,
        include_completed: bool = False
    ) -> List[Task]:
        """
        Get tasks for a specific project
        
        Args:
            db: Database session
            project_id: Project ID
            include_completed: Include completed tasks
            
        Returns:
            List of task instances
        """
        query = select(Task).where(
            and_(
                Task.project_id == project_id,
                Task.deleted_at.is_(None)
            )
        )
        
        if not include_completed:
            query = query.where(Task.done_at.is_(None))
        
        query = query.order_by(
            asc(Task.priority.nullslast()),
            asc(Task.do_on_date.nullslast()),
            desc(Task.created_at)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_task_stats(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> dict:
        """
        Get comprehensive task statistics for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with task statistics
        """
        today = date.today()
        
        # Total tasks
        total_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(Task.user_id == user_id, Task.deleted_at.is_(None))
            )
        )
        
        # Completed tasks
        completed_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.isnot(None)
                )
            )
        )
        
        # Today's tasks
        tasks_today = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    or_(Task.do_today == True, Task.do_on_date == today)
                )
            )
        )
        
        # Overdue tasks
        overdue_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.do_on_date < today
                )
            )
        )
        
        # Priority distribution
        priority_counts = {}
        for priority in [1, 2, 3, 4, 5]:
            count = await db.scalar(
                select(func.count(Task.id)).where(
                    and_(
                        Task.user_id == user_id,
                        Task.deleted_at.is_(None),
                        Task.done_at.is_(None),
                        Task.priority == priority
                    )
                )
            )
            priority_counts[f"priority_{priority}"] = count or 0
        
        # No priority tasks
        no_priority = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.priority.is_(None)
                )
            )
        )
        
        # GTD workflow stats
        reading_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.is_reading == True
                )
            )
        )
        
        waiting_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.wait_for == True
                )
            )
        )
        
        return {
            "total_tasks": total_tasks or 0,
            "completed_tasks": completed_tasks or 0,
            "pending_tasks": (total_tasks or 0) - (completed_tasks or 0),
            "completion_rate": (
                (completed_tasks / total_tasks * 100) 
                if total_tasks and completed_tasks 
                else 0.0
            ),
            "tasks_today": tasks_today or 0,
            "overdue_tasks": overdue_tasks or 0,
            **priority_counts,
            "no_priority": no_priority or 0,
            "reading_tasks": reading_tasks or 0,
            "waiting_tasks": waiting_tasks or 0,
        }
    
    async def bulk_complete_tasks(
        self,
        db: AsyncSession,
        *,
        task_ids: List[int],
        user_id: UUID,
        completion_time: Optional[datetime] = None
    ) -> int:
        """
        Bulk complete multiple tasks
        
        Args:
            db: Database session
            task_ids: List of task IDs
            user_id: User ID (for security)
            completion_time: Optional completion timestamp
            
        Returns:
            Number of tasks completed
        """
        completion_timestamp = completion_time or datetime.utcnow()
        
        result = await db.execute(
            Task.__table__.update()
            .where(
                and_(
                    Task.id.in_(task_ids),
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None)
                )
            )
            .values(done_at=completion_timestamp)
        )
        
        await db.commit()
        return result.rowcount


# Create instance
crud_task = CRUDTask(Task)