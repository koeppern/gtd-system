"""
Project model - represents GTD projects
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Project(BaseModel):
    """
    Project model matching gtd_projects table
    """
    __tablename__ = "gtd_projects"
    
    # Foreign key to user
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("gtd_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Notion import tracking
    notion_export_row: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Core project information
    project_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True
    )
    
    readings: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Field/category relationship
    field_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("gtd_fields.id"),
        nullable=True,
        index=True
    )
    
    keywords: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Project relationships and references
    mother_project: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    related_projects: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    related_mother_projects: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    related_knowledge_vault: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    related_tasks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # GTD status and timing
    done_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    do_this_week: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Additional GTD fields
    gtd_processes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    add_checkboxes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Import metadata
    source_file: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="projects"
    )
    
    field: Mapped[Optional["Field"]] = relationship(
        "Field",
        back_populates="projects"
    )
    
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.project_name[:50]})>"
    
    @property
    def is_done(self) -> bool:
        """Check if project is completed"""
        return self.done_at is not None
    
    @property
    def is_active(self) -> bool:
        """Check if project is active (not deleted and not done)"""
        return not self.is_deleted and not self.is_done
    
    @property
    def task_count(self) -> int:
        """Get number of tasks in this project"""
        return self.tasks.filter_by(deleted_at=None).count()
    
    @property
    def completed_task_count(self) -> int:
        """Get number of completed tasks in this project"""
        from .task import Task
        return self.tasks.filter(
            Task.deleted_at.is_(None),
            Task.done_at.isnot(None)
        ).count()
    
    @property
    def completion_percentage(self) -> float:
        """Get project completion percentage based on tasks"""
        total = self.task_count
        if total == 0:
            return 0.0
        completed = self.completed_task_count
        return (completed / total) * 100.0
    
    def complete(self) -> None:
        """Mark project as completed"""
        self.done_at = datetime.utcnow()
    
    def reopen(self) -> None:
        """Reopen a completed project"""
        self.done_at = None