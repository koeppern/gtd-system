"""
User CRUD operations
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model"""
    
    async def get_by_email(
        self,
        db: AsyncSession,
        *,
        email: str
    ) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            db: Database session
            email: Email address
            
        Returns:
            User instance or None
        """
        query = select(User).where(
            User.email_address == email,
            User.deleted_at.is_(None)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate
    ) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            obj_in: User creation schema
            
        Returns:
            Created user instance
        """
        # Check if email already exists
        existing_user = await self.get_by_email(db=db, email=obj_in.email_address)
        if existing_user:
            raise ValueError(f"User with email {obj_in.email_address} already exists")
        
        return await super().create(db=db, obj_in=obj_in)
    
    async def update_email(
        self,
        db: AsyncSession,
        *,
        user: User,
        new_email: str
    ) -> User:
        """
        Update user email address
        
        Args:
            db: Database session
            user: User instance
            new_email: New email address
            
        Returns:
            Updated user instance
        """
        # Check if new email already exists
        existing_user = await self.get_by_email(db=db, email=new_email)
        if existing_user and existing_user.id != user.id:
            raise ValueError(f"Email {new_email} is already in use")
        
        user.email_address = new_email
        user.email_verified = False  # Require re-verification
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def verify_email(
        self,
        db: AsyncSession,
        *,
        user: User
    ) -> User:
        """
        Mark user email as verified
        
        Args:
            db: Database session
            user: User instance
            
        Returns:
            Updated user instance
        """
        user.email_verified = True
        await db.commit()
        await db.refresh(user)
        return user
    
    async def activate(
        self,
        db: AsyncSession,
        *,
        user: User
    ) -> User:
        """
        Activate user account
        
        Args:
            db: Database session
            user: User instance
            
        Returns:
            Updated user instance
        """
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        return user
    
    async def deactivate(
        self,
        db: AsyncSession,
        *,
        user: User
    ) -> User:
        """
        Deactivate user account
        
        Args:
            db: Database session
            user: User instance
            
        Returns:
            Updated user instance
        """
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return user
    
    async def update_last_login(
        self,
        db: AsyncSession,
        *,
        user: User
    ) -> User:
        """
        Update user's last login timestamp
        
        Args:
            db: Database session
            user: User instance
            
        Returns:
            Updated user instance
        """
        from datetime import datetime
        
        user.last_login_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user
    
    async def get_user_stats(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> dict:
        """
        Get user statistics (projects, tasks, etc.)
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
        """
        from sqlalchemy import func, and_
        from app.models.project import Project
        from app.models.task import Task
        
        # Count projects
        project_total = await db.scalar(
            select(func.count(Project.id)).where(
                and_(
                    Project.user_id == user_id,
                    Project.deleted_at.is_(None)
                )
            )
        )
        
        project_completed = await db.scalar(
            select(func.count(Project.id)).where(
                and_(
                    Project.user_id == user_id,
                    Project.deleted_at.is_(None),
                    Project.done_at.isnot(None)
                )
            )
        )
        
        # Count tasks
        task_total = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None)
                )
            )
        )
        
        task_completed = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.isnot(None)
                )
            )
        )
        
        # Count today's tasks
        from datetime import date
        tasks_today = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.do_today == True
                )
            )
        )
        
        # Count this week's tasks
        tasks_this_week = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    Task.done_at.is_(None),
                    Task.do_this_week == True
                )
            )
        )
        
        return {
            "total_projects": project_total or 0,
            "active_projects": (project_total or 0) - (project_completed or 0),
            "completed_projects": project_completed or 0,
            "total_tasks": task_total or 0,
            "pending_tasks": (task_total or 0) - (task_completed or 0),
            "completed_tasks": task_completed or 0,
            "tasks_today": tasks_today or 0,
            "tasks_this_week": tasks_this_week or 0,
        }


# Create instance
crud_user = CRUDUser(User)