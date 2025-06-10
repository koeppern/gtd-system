"""
User model - represents GTD users
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    User model matching gtd_users table
    """
    __tablename__ = "gtd_users"
    
    # Primary key - UUID for multi-tenant support
    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    
    # Basic user information
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    email_address: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    # User preferences
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Europe/Berlin",
        nullable=False
    )
    
    date_format: Mapped[str] = mapped_column(
        String(20),
        default="DD.MM.YYYY",
        nullable=False
    )
    
    time_format: Mapped[str] = mapped_column(
        String(10),
        default="24h",
        nullable=False
    )
    
    # GTD-specific settings
    weekly_review_day: Mapped[int] = mapped_column(
        Integer,
        default=0,  # 0=Sunday, 1=Monday, etc.
        nullable=False
    )
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Activity tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email_address})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(part for part in parts if part)
    
    @property
    def display_name(self) -> str:
        """Get display name (full name or email)"""
        return self.full_name or self.email_address