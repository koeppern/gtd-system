"""
Field model - represents GTD fields/categories (Private, Work, etc.)
"""
from typing import Optional, List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Field(BaseModel):
    """
    Field model matching gtd_fields table
    Represents categories like "Private", "Work", etc.
    """
    __tablename__ = "gtd_fields"
    
    # Field name (unique)
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Optional description
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="field",
        lazy="dynamic"
    )
    
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="field",
        lazy="dynamic"
    )
    
    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name={self.name})>"
    
    @property
    def project_count(self) -> int:
        """Get number of projects in this field"""
        return self.projects.filter_by(deleted_at=None).count()
    
    @property
    def task_count(self) -> int:
        """Get number of tasks in this field"""
        return self.tasks.filter_by(deleted_at=None).count()