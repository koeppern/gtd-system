"""
Task Pydantic schemas
"""
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import Field, field_validator

from .common import BaseSchema, TimestampMixin, SoftDeleteMixin, PaginatedResponse
from .field import FieldSummary
from .project import ProjectSummary
from .user import UserSummary


class TaskBase(BaseSchema):
    """Base task schema"""
    
    task_name: str = Field(..., min_length=1, description="Task name")
    project_id: Optional[int] = Field(None, description="Project ID")
    project_reference: Optional[str] = Field(None, description="Project reference from import")
    
    # GTD status flags
    do_today: bool = Field(False, description="Scheduled for today")
    do_this_week: bool = Field(False, description="Scheduled for this week")
    is_reading: bool = Field(False, description="Is a reading task")
    wait_for: bool = Field(False, description="Waiting for someone/something")
    postponed: bool = Field(False, description="Postponed task")
    reviewed: bool = Field(False, description="Has been reviewed")
    
    # Scheduling
    do_on_date: Optional[date] = Field(None, description="Scheduled date")
    
    # Additional properties
    field_id: Optional[int] = Field(None, description="Field/category ID")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    time_expenditure: Optional[str] = Field(None, description="Estimated time")
    url: Optional[str] = Field(None, description="Related URL")
    knowledge_db_entry: Optional[str] = Field(None, description="Knowledge database reference")
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Priority must be between 1 (highest) and 5 (lowest)")
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    
    user_id: UUID = Field(..., description="User ID (owner)")
    
    # Optional import metadata
    notion_export_row: Optional[int] = Field(None, description="Original Notion row number")
    source_file: Optional[str] = Field(None, description="Source import file")
    last_edited: Optional[datetime] = Field(None, description="Last edited timestamp")
    date_of_creation: Optional[datetime] = Field(None, description="Original creation date")


class TaskUpdate(BaseSchema):
    """Schema for updating task (all fields optional)"""
    
    task_name: Optional[str] = Field(None, min_length=1, description="Task name")
    project_id: Optional[int] = Field(None, description="Project ID")
    
    # GTD status flags
    do_today: Optional[bool] = Field(None, description="Scheduled for today")
    do_this_week: Optional[bool] = Field(None, description="Scheduled for this week")
    is_reading: Optional[bool] = Field(None, description="Is a reading task")
    wait_for: Optional[bool] = Field(None, description="Waiting for someone/something")
    postponed: Optional[bool] = Field(None, description="Postponed task")
    reviewed: Optional[bool] = Field(None, description="Has been reviewed")
    
    # Scheduling
    do_on_date: Optional[date] = Field(None, description="Scheduled date")
    
    # Additional properties
    field_id: Optional[int] = Field(None, description="Field/category ID")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    time_expenditure: Optional[str] = Field(None, description="Estimated time")
    url: Optional[str] = Field(None, description="Related URL")
    knowledge_db_entry: Optional[str] = Field(None, description="Knowledge database reference")
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Priority must be between 1 (highest) and 5 (lowest)")
        return v


class TaskSummary(BaseSchema):
    """Minimal task information for relationships"""
    
    id: int = Field(..., description="Task ID")
    task_name: str = Field(..., description="Task name")
    project_id: Optional[int] = Field(None, description="Project ID")
    is_done: bool = Field(..., description="Is task completed")
    done_at: Optional[datetime] = Field(None, description="Completion timestamp")
    do_today: bool = Field(..., description="Scheduled for today")
    do_this_week: bool = Field(..., description="Scheduled for this week")
    priority: Optional[int] = Field(None, description="Priority")


class TaskResponse(TaskBase, TimestampMixin, SoftDeleteMixin):
    """Complete task response schema"""
    
    id: int = Field(..., description="Task ID")
    user_id: UUID = Field(..., description="User ID (owner)")
    
    # Completion tracking
    done_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Import and edit metadata
    notion_export_row: Optional[int] = Field(None, description="Original Notion row number")
    source_file: Optional[str] = Field(None, description="Source import file")
    last_edited: Optional[datetime] = Field(None, description="Last edited timestamp")
    date_of_creation: Optional[datetime] = Field(None, description="Original creation date")
    
    # Computed fields
    is_done: bool = Field(..., description="Is task completed")
    is_active: bool = Field(..., description="Is task active (not deleted, not done)")
    is_overdue: bool = Field(..., description="Is task overdue")
    is_due_today: bool = Field(..., description="Is task due today")
    is_due_this_week: bool = Field(..., description="Is task due this week")
    
    # Related data (optional includes)
    user: Optional[UserSummary] = Field(None, description="Task owner")
    project: Optional[ProjectSummary] = Field(None, description="Associated project")
    field: Optional[FieldSummary] = Field(None, description="Task field/category")
    
    @classmethod
    def from_model(cls, task_model, include_user: bool = False, include_project: bool = False, include_field: bool = False) -> "TaskResponse":
        """Create response from SQLAlchemy model"""
        data = {
            "id": task_model.id,
            "user_id": task_model.user_id,
            "task_name": task_model.task_name,
            "project_id": task_model.project_id,
            "project_reference": task_model.project_reference,
            "do_today": task_model.do_today,
            "do_this_week": task_model.do_this_week,
            "is_reading": task_model.is_reading,
            "wait_for": task_model.wait_for,
            "postponed": task_model.postponed,
            "reviewed": task_model.reviewed,
            "do_on_date": task_model.do_on_date,
            "field_id": task_model.field_id,
            "priority": task_model.priority,
            "time_expenditure": task_model.time_expenditure,
            "url": task_model.url,
            "knowledge_db_entry": task_model.knowledge_db_entry,
            "done_at": task_model.done_at,
            "notion_export_row": task_model.notion_export_row,
            "source_file": task_model.source_file,
            "last_edited": task_model.last_edited,
            "date_of_creation": task_model.date_of_creation,
            "created_at": task_model.created_at,
            "updated_at": task_model.updated_at,
            "deleted_at": task_model.deleted_at,
            "is_done": task_model.is_done,
            "is_active": task_model.is_active,
            "is_overdue": task_model.is_overdue,
            "is_due_today": task_model.is_due_today,
            "is_due_this_week": task_model.is_due_this_week,
        }
        
        # Include related data if requested
        if include_user and hasattr(task_model, 'user') and task_model.user:
            data["user"] = UserSummary.from_model(task_model.user)
        
        if include_project and hasattr(task_model, 'project') and task_model.project:
            data["project"] = ProjectSummary.from_model(task_model.project)
        
        if include_field and hasattr(task_model, 'field') and task_model.field:
            data["field"] = FieldSummary.from_model(task_model.field)
        
        return cls(**data)


class TaskFilters(BaseSchema):
    """Filters for task queries"""
    
    project_id: Optional[int] = Field(None, description="Filter by project ID")
    field_id: Optional[int] = Field(None, description="Filter by field ID")
    is_done: Optional[bool] = Field(None, description="Filter by completion status")
    
    # GTD status filters
    do_today: Optional[bool] = Field(None, description="Filter by today's tasks")
    do_this_week: Optional[bool] = Field(None, description="Filter by weekly tasks")
    is_reading: Optional[bool] = Field(None, description="Filter reading tasks")
    wait_for: Optional[bool] = Field(None, description="Filter waiting tasks")
    postponed: Optional[bool] = Field(None, description="Filter postponed tasks")
    reviewed: Optional[bool] = Field(None, description="Filter reviewed tasks")
    
    # Priority filters
    priority: Optional[int] = Field(None, ge=1, le=5, description="Filter by priority")
    priority_min: Optional[int] = Field(None, ge=1, le=5, description="Minimum priority")
    priority_max: Optional[int] = Field(None, ge=1, le=5, description="Maximum priority")
    
    # Date filters
    due_date: Optional[date] = Field(None, description="Filter by due date")
    due_before: Optional[date] = Field(None, description="Due before date")
    due_after: Optional[date] = Field(None, description="Due after date")
    overdue: Optional[bool] = Field(None, description="Filter overdue tasks")
    
    completed_after: Optional[datetime] = Field(None, description="Completed after date")
    completed_before: Optional[datetime] = Field(None, description="Completed before date")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    
    # Text search
    search: Optional[str] = Field(None, description="Search in task name")
    
    # Include deleted items
    include_deleted: bool = Field(False, description="Include soft-deleted tasks")


class TaskListResponse(PaginatedResponse[TaskResponse]):
    """Paginated task list response"""
    
    # Additional metadata for task lists
    total_active: int = Field(0, description="Total active tasks")
    total_completed: int = Field(0, description="Total completed tasks")
    total_overdue: int = Field(0, description="Total overdue tasks")
    completion_rate: float = Field(0.0, description="Overall completion rate")


class TaskCompletion(BaseSchema):
    """Schema for completing a task"""
    
    completed_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Completion timestamp"
    )
    completion_notes: Optional[str] = Field(None, description="Completion notes")


class TaskQuickAdd(BaseSchema):
    """Schema for quick task creation"""
    
    task_name: str = Field(..., min_length=1, description="Task name")
    project_name: Optional[str] = Field(None, description="Project name (auto-link)")
    field_name: Optional[str] = Field(None, description="Field name (auto-link)")
    do_today: bool = Field(False, description="Schedule for today")
    do_this_week: bool = Field(False, description="Schedule for this week")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Priority")
    user_id: UUID = Field(..., description="User ID")


class TaskBatch(BaseSchema):
    """Schema for batch task operations"""
    
    task_ids: List[int] = Field(..., min_items=1, description="Task IDs")
    operation: str = Field(..., description="Operation: complete, delete, update")
    
    # Fields for batch update
    project_id: Optional[int] = Field(None, description="Move to project")
    field_id: Optional[int] = Field(None, description="Change field")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Set priority")
    do_today: Optional[bool] = Field(None, description="Set today flag")
    do_this_week: Optional[bool] = Field(None, description="Set weekly flag")


class TaskStats(BaseSchema):
    """Task statistics"""
    
    # Completion stats
    total_tasks: int = Field(0, description="Total tasks")
    completed_tasks: int = Field(0, description="Completed tasks")
    pending_tasks: int = Field(0, description="Pending tasks")
    completion_rate: float = Field(0.0, description="Completion rate percentage")
    
    # Due date stats
    overdue_tasks: int = Field(0, description="Overdue tasks")
    due_today: int = Field(0, description="Due today")
    due_this_week: int = Field(0, description="Due this week")
    
    # Priority distribution
    priority_1: int = Field(0, description="Priority 1 tasks")
    priority_2: int = Field(0, description="Priority 2 tasks")
    priority_3: int = Field(0, description="Priority 3 tasks")
    priority_4: int = Field(0, description="Priority 4 tasks")
    priority_5: int = Field(0, description="Priority 5 tasks")
    no_priority: int = Field(0, description="Tasks without priority")
    
    # GTD workflow stats
    reading_tasks: int = Field(0, description="Reading tasks")
    waiting_tasks: int = Field(0, description="Waiting tasks")
    postponed_tasks: int = Field(0, description="Postponed tasks")
    
    # Time-based metrics
    avg_completion_time_hours: Optional[float] = Field(None, description="Average completion time in hours")
    tasks_created_today: int = Field(0, description="Tasks created today")
    tasks_completed_today: int = Field(0, description="Tasks completed today")