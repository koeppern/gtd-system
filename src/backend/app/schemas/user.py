"""
User Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field, EmailStr, field_validator

from .common import BaseSchema, TimestampMixin, SoftDeleteMixin


class UserBase(BaseSchema):
    """Base user schema with core fields"""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    email_address: EmailStr = Field(..., description="Email address")
    timezone: str = Field("Europe/Berlin", description="User timezone")
    date_format: str = Field("DD.MM.YYYY", description="Preferred date format")
    time_format: str = Field("24h", description="Preferred time format (12h/24h)")
    weekly_review_day: int = Field(0, ge=0, le=6, description="Weekly review day (0=Sunday)")
    
    @field_validator("weekly_review_day")
    @classmethod
    def validate_weekly_review_day(cls, v: int) -> int:
        if not 0 <= v <= 6:
            raise ValueError("Weekly review day must be between 0 (Sunday) and 6 (Saturday)")
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    
    # Override to make email required
    email_address: EmailStr = Field(..., description="Email address (required)")
    
    # Additional fields for user creation
    password: Optional[str] = Field(None, min_length=8, description="Password (if not using OAuth)")
    is_active: bool = Field(True, description="User is active")
    email_verified: bool = Field(False, description="Email is verified")


class UserUpdate(BaseSchema):
    """Schema for updating user information (all fields optional)"""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    timezone: Optional[str] = Field(None, description="User timezone")
    date_format: Optional[str] = Field(None, description="Preferred date format")
    time_format: Optional[str] = Field(None, description="Preferred time format")
    weekly_review_day: Optional[int] = Field(None, ge=0, le=6, description="Weekly review day")
    
    @field_validator("weekly_review_day")
    @classmethod
    def validate_weekly_review_day(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 0 <= v <= 6:
            raise ValueError("Weekly review day must be between 0 (Sunday) and 6 (Saturday)")
        return v


class UserSummary(BaseSchema):
    """Minimal user information for relationships"""
    
    id: UUID = Field(..., description="User ID")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email_address: EmailStr = Field(..., description="Email address")
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(part for part in parts if part)
    
    @property
    def display_name(self) -> str:
        """Get display name (full name or email)"""
        return self.full_name or str(self.email_address)
    
    @classmethod
    def from_model(cls, user_model) -> "UserSummary":
        """Create summary from SQLAlchemy model"""
        return cls(
            id=user_model.id,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            email_address=user_model.email_address,
        )


class UserResponse(UserBase, TimestampMixin, SoftDeleteMixin):
    """Complete user response schema"""
    
    id: UUID = Field(..., description="User ID")
    is_active: bool = Field(..., description="User is active")
    email_verified: bool = Field(..., description="Email is verified")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    
    # Computed fields
    full_name: str = Field(..., description="Full name")
    display_name: str = Field(..., description="Display name")
    
    @classmethod
    def from_model(cls, user_model) -> "UserResponse":
        """Create response from SQLAlchemy model"""
        return cls(
            id=user_model.id,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            email_address=user_model.email_address,
            timezone=user_model.timezone,
            date_format=user_model.date_format,
            time_format=user_model.time_format,
            weekly_review_day=user_model.weekly_review_day,
            is_active=user_model.is_active,
            email_verified=user_model.email_verified,
            last_login_at=user_model.last_login_at,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            deleted_at=user_model.deleted_at,
            full_name=user_model.full_name,
            display_name=user_model.display_name,
        )


class UserProfile(UserResponse):
    """Extended user profile with statistics"""
    
    # User statistics
    total_projects: int = Field(0, description="Total number of projects")
    active_projects: int = Field(0, description="Number of active projects")
    completed_projects: int = Field(0, description="Number of completed projects")
    
    total_tasks: int = Field(0, description="Total number of tasks")
    pending_tasks: int = Field(0, description="Number of pending tasks")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    
    tasks_today: int = Field(0, description="Tasks due today")
    tasks_this_week: int = Field(0, description="Tasks due this week")
    
    # Activity tracking
    days_since_last_login: Optional[int] = Field(None, description="Days since last login")
    completion_streak: int = Field(0, description="Current completion streak in days")


class UserSettings(BaseSchema):
    """User settings schema"""
    
    timezone: str = Field(..., description="User timezone")
    date_format: str = Field(..., description="Preferred date format")
    time_format: str = Field(..., description="Preferred time format")
    weekly_review_day: int = Field(..., ge=0, le=6, description="Weekly review day")
    
    # Notification preferences
    email_notifications: bool = Field(True, description="Enable email notifications")
    daily_digest: bool = Field(True, description="Enable daily digest emails")
    weekly_review_reminder: bool = Field(True, description="Enable weekly review reminders")
    
    # UI preferences
    theme: str = Field("light", description="UI theme (light/dark)")
    compact_view: bool = Field(False, description="Use compact list view")
    show_completed: bool = Field(False, description="Show completed items by default")