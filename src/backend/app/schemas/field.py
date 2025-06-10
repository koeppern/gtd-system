"""
Field Pydantic schemas
"""
from typing import Optional
from pydantic import Field

from .common import BaseSchema, TimestampMixin, SoftDeleteMixin


class FieldBase(BaseSchema):
    """Base field schema"""
    
    name: str = Field(..., min_length=1, max_length=50, description="Field name")
    description: Optional[str] = Field(None, description="Field description")


class FieldCreate(FieldBase):
    """Schema for creating a new field"""
    pass


class FieldUpdate(BaseSchema):
    """Schema for updating field (all fields optional)"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Field name")
    description: Optional[str] = Field(None, description="Field description")


class FieldSummary(BaseSchema):
    """Minimal field information for relationships"""
    
    id: int = Field(..., description="Field ID")
    name: str = Field(..., description="Field name")
    description: Optional[str] = Field(None, description="Field description")
    
    @classmethod
    def from_model(cls, field_model) -> "FieldSummary":
        """Create summary from SQLAlchemy model"""
        return cls(
            id=field_model.id,
            name=field_model.name,
            description=field_model.description,
        )


class FieldResponse(FieldBase, TimestampMixin, SoftDeleteMixin):
    """Complete field response schema"""
    
    id: int = Field(..., description="Field ID")
    
    # Statistics
    project_count: int = Field(0, description="Number of projects in this field")
    task_count: int = Field(0, description="Number of tasks in this field")
    active_project_count: int = Field(0, description="Number of active projects")
    active_task_count: int = Field(0, description="Number of active tasks")
    
    @classmethod
    def from_model(cls, field_model) -> "FieldResponse":
        """Create response from SQLAlchemy model"""
        return cls(
            id=field_model.id,
            name=field_model.name,
            description=field_model.description,
            created_at=field_model.created_at,
            updated_at=field_model.updated_at,
            deleted_at=field_model.deleted_at,
            project_count=field_model.project_count,
            task_count=field_model.task_count,
            # These would need to be calculated separately or added to the model
            active_project_count=0,  # TODO: Calculate from model
            active_task_count=0,     # TODO: Calculate from model
        )


class FieldWithStats(FieldResponse):
    """Field with detailed statistics"""
    
    # Completion statistics
    completed_projects: int = Field(0, description="Number of completed projects")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    completion_rate_projects: float = Field(0.0, description="Project completion rate (0-100)")
    completion_rate_tasks: float = Field(0.0, description="Task completion rate (0-100)")
    
    # Recent activity
    projects_this_week: int = Field(0, description="Projects created this week")
    tasks_this_week: int = Field(0, description="Tasks created this week")
    completed_this_week: int = Field(0, description="Items completed this week")


class FieldUsageStats(BaseSchema):
    """Field usage statistics"""
    
    field_id: int = Field(..., description="Field ID")
    field_name: str = Field(..., description="Field name")
    
    # Project statistics
    total_projects: int = Field(0, description="Total projects")
    active_projects: int = Field(0, description="Active projects")
    completed_projects: int = Field(0, description="Completed projects")
    
    # Task statistics  
    total_tasks: int = Field(0, description="Total tasks")
    active_tasks: int = Field(0, description="Active tasks")
    completed_tasks: int = Field(0, description="Completed tasks")
    
    # Productivity metrics
    avg_project_completion_days: Optional[float] = Field(None, description="Average days to complete projects")
    avg_task_completion_days: Optional[float] = Field(None, description="Average days to complete tasks")
    
    # Recent activity (last 30 days)
    recent_projects_created: int = Field(0, description="Projects created in last 30 days")
    recent_tasks_created: int = Field(0, description="Tasks created in last 30 days")
    recent_completions: int = Field(0, description="Items completed in last 30 days")