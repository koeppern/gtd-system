"""
Task model - represents GTD tasks
"""
from datetime import datetime, date, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import String, Text, Boolean, Integer, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Task(BaseModel):
    """
    Task model matching gtd_tasks table
    """
    __tablename__ = "gtd_tasks"
    
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
    
    # Core task information
    task_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True
    )
    
    # Project relationship
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("gtd_projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    project_reference: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # GTD status flags
    done_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    do_today: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    do_this_week: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    is_reading: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    wait_for: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    postponed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    reviewed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Dates and timing
    do_on_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True
    )
    
    last_edited: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    date_of_creation: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Field/category relationship
    field_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("gtd_fields.id"),
        nullable=True,
        index=True
    )
    
    # Additional task properties
    priority: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )
    
    time_expenditure: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    knowledge_db_entry: Mapped[Optional[str]] = mapped_column(
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
        back_populates="tasks"
    )
    
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="tasks"
    )
    
    field: Mapped[Optional["Field"]] = relationship(
        "Field",
        back_populates="tasks"
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name={self.task_name[:50]})>"
    
    @property
    def is_done(self) -> bool:
        """Check if task is completed"""
        return self.done_at is not None
    
    @property
    def is_active(self) -> bool:
        """Check if task is active (not deleted and not done)"""
        return not self.is_deleted and not self.is_done
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.do_on_date or self.is_done:
            return False
        return self.do_on_date < date.today()
    
    @property
    def is_due_today(self) -> bool:
        """Check if task is due today"""
        if not self.do_on_date:
            return False
        return self.do_on_date == date.today()
    
    @property
    def is_due_this_week(self) -> bool:
        """Check if task is due this week"""
        if not self.do_on_date:
            return False
        today = date.today()
        # Calculate days until end of week (Sunday)
        days_until_sunday = 6 - today.weekday()
        end_of_week = today + timedelta(days=days_until_sunday)
        return today <= self.do_on_date <= end_of_week
    
    def complete(self) -> None:
        """Mark task as completed"""
        self.done_at = datetime.utcnow()
    
    def reopen(self) -> None:
        """Reopen a completed task"""
        self.done_at = None
    
    def set_priority(self, priority: int) -> None:
        """Set task priority (1=highest, 5=lowest)"""
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
        self.priority = priority