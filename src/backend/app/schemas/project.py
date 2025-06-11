"""
Project Pydantic schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import Field, field_validator

from .common import BaseSchema, TimestampMixin, SoftDeleteMixin, PaginatedResponse
from .field import FieldSummary
from .user import UserSummary


class ProjectBase(BaseSchema):
    """Base project schema"""
    
    project_name: str = Field(..., min_length=1, description="Project name")
    readings: Optional[str] = Field(None, description="Project readings/notes")
    field_id: Optional[int] = Field(None, description="Field/category ID")
    keywords: Optional[str] = Field(None, description="Project keywords")
    
    # GTD relationships (text fields from Notion)
    mother_project: Optional[str] = Field(None, description="Parent project reference")
    related_projects: Optional[str] = Field(None, description="Related projects")
    related_mother_projects: Optional[str] = Field(None, description="Related parent projects")
    related_knowledge_vault: Optional[str] = Field(None, description="Knowledge vault references")
    related_tasks: Optional[str] = Field(None, description="Related tasks reference")
    
    # GTD workflow fields
    do_this_week: bool = Field(False, description="Scheduled for this week")
    gtd_processes: Optional[str] = Field(None, description="GTD processes applied")
    add_checkboxes: Optional[str] = Field(None, description="Checkbox templates")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    
    user_id: UUID = Field(..., description="User ID (owner)")
    
    # Optional import metadata
    notion_export_row: Optional[int] = Field(None, description="Original Notion row number")
    source_file: Optional[str] = Field(None, description="Source import file")


class ProjectUpdate(BaseSchema):
    """Schema for updating project (all fields optional)"""
    
    project_name: Optional[str] = Field(None, min_length=1, description="Project name")
    readings: Optional[str] = Field(None, description="Project readings/notes")
    field_id: Optional[int] = Field(None, description="Field/category ID")
    keywords: Optional[str] = Field(None, description="Project keywords")
    
    # GTD fields
    mother_project: Optional[str] = Field(None, description="Parent project reference")
    related_projects: Optional[str] = Field(None, description="Related projects")
    related_mother_projects: Optional[str] = Field(None, description="Related parent projects")
    related_knowledge_vault: Optional[str] = Field(None, description="Knowledge vault references")
    related_tasks: Optional[str] = Field(None, description="Related tasks reference")
    
    do_this_week: Optional[bool] = Field(None, description="Scheduled for this week")
    gtd_processes: Optional[str] = Field(None, description="GTD processes applied")
    add_checkboxes: Optional[str] = Field(None, description="Checkbox templates")


class ProjectSummary(BaseSchema):
    """Minimal project information for relationships"""
    
    id: int = Field(..., description="Project ID")
    project_name: str = Field(..., description="Project name")
    field_id: Optional[int] = Field(None, description="Field ID")
    is_done: bool = Field(..., description="Is project completed")
    done_at: Optional[datetime] = Field(None, description="Completion timestamp")
    do_this_week: bool = Field(..., description="Scheduled for this week")
    
    @classmethod
    def from_model(cls, project_model) -> "ProjectSummary":
        """Create summary from SQLAlchemy model"""
        return cls(
            id=project_model.id,
            project_name=project_model.project_name,
            field_id=project_model.field_id,
            is_done=project_model.is_done,
            done_at=project_model.done_at,
            do_this_week=project_model.do_this_week,
        )


class ProjectResponse(ProjectBase, TimestampMixin, SoftDeleteMixin):
    """Complete project response schema"""
    
    id: int = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="User ID (owner)")
    
    # Completion tracking
    done_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Import metadata
    notion_export_row: Optional[int] = Field(None, description="Original Notion row number")
    source_file: Optional[str] = Field(None, description="Source import file")
    
    # Computed fields
    is_done: bool = Field(..., description="Is project completed")
    is_active: bool = Field(..., description="Is project active (not deleted, not done)")
    
    # Related data (optional includes)
    user: Optional[UserSummary] = Field(None, description="Project owner")
    field: Optional[FieldSummary] = Field(None, description="Project field/category")
    
    # Statistics
    task_count: int = Field(0, description="Total number of tasks")
    completed_task_count: int = Field(0, description="Number of completed tasks")
    completion_percentage: float = Field(0.0, description="Project completion percentage")
    
    @classmethod
    def from_model(cls, project_model, include_user: bool = False, include_field: bool = False) -> "ProjectResponse":
        """Create response from SQLAlchemy model"""
        data = {
            "id": project_model.id,
            "user_id": project_model.user_id,
            "project_name": project_model.project_name,
            "readings": project_model.readings,
            "field_id": project_model.field_id,
            "keywords": project_model.keywords,
            "mother_project": project_model.mother_project,
            "related_projects": project_model.related_projects,
            "related_mother_projects": project_model.related_mother_projects,
            "related_knowledge_vault": project_model.related_knowledge_vault,
            "related_tasks": project_model.related_tasks,
            "do_this_week": project_model.do_this_week,
            "gtd_processes": project_model.gtd_processes,
            "add_checkboxes": project_model.add_checkboxes,
            "done_at": project_model.done_at,
            "notion_export_row": project_model.notion_export_row,
            "source_file": project_model.source_file,
            "created_at": project_model.created_at,
            "updated_at": project_model.updated_at,
            "deleted_at": project_model.deleted_at,
            "is_done": project_model.is_done,
            "is_active": project_model.is_active,
            "task_count": project_model.task_count,
            "completed_task_count": project_model.completed_task_count,
            "completion_percentage": project_model.completion_percentage,
        }
        
        # Include related data if requested
        if include_user and hasattr(project_model, 'user') and project_model.user:
            data["user"] = UserSummary.from_model(project_model.user)
        
        if include_field and hasattr(project_model, 'field') and project_model.field:
            data["field"] = FieldSummary.from_model(project_model.field)
        
        return cls(**data)


class ProjectFilters(BaseSchema):
    """Filters for project queries"""
    
    field_id: Optional[int] = Field(None, description="Filter by field ID")
    is_done: Optional[bool] = Field(None, description="Filter by completion status")
    do_this_week: Optional[bool] = Field(None, description="Filter by weekly schedule")
    has_tasks: Optional[bool] = Field(None, description="Filter projects with/without tasks")
    
    # Date filters
    completed_after: Optional[datetime] = Field(None, description="Completed after date")
    completed_before: Optional[datetime] = Field(None, description="Completed before date")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    
    # Text search
    search: Optional[str] = Field(None, description="Search in project name and keywords")
    
    # Include deleted items
    include_deleted: bool = Field(False, description="Include soft-deleted projects")


class ProjectListResponse(PaginatedResponse[ProjectResponse]):
    """Paginated project list response"""
    
    # Additional metadata for project lists
    total_active: int = Field(0, description="Total active projects")
    total_completed: int = Field(0, description="Total completed projects")
    completion_rate: float = Field(0.0, description="Overall completion rate")


class ProjectCompletion(BaseSchema):
    """Schema for completing a project"""
    
    completed_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Completion timestamp"
    )
    completion_notes: Optional[str] = Field(None, description="Completion notes")
    auto_complete_tasks: bool = Field(False, description="Also complete all active tasks")


class ProjectArchive(BaseSchema):
    """Schema for archiving a project"""
    
    archive_reason: Optional[str] = Field(None, description="Reason for archiving")
    archive_notes: Optional[str] = Field(None, description="Archive notes")
    archive_tasks: bool = Field(True, description="Also archive all tasks")


class ProjectStats(BaseSchema):
    """Project statistics"""
    
    project_id: int = Field(..., description="Project ID")
    project_name: str = Field(..., description="Project name")
    
    # Task statistics
    total_tasks: int = Field(0, description="Total tasks")
    completed_tasks: int = Field(0, description="Completed tasks")
    pending_tasks: int = Field(0, description="Pending tasks")
    overdue_tasks: int = Field(0, description="Overdue tasks")
    
    # Timeline
    created_at: datetime = Field(..., description="Project creation date")
    first_task_at: Optional[datetime] = Field(None, description="First task created")
    last_activity_at: Optional[datetime] = Field(None, description="Last activity")
    completed_at: Optional[datetime] = Field(None, description="Project completion")
    
    # Metrics
    completion_percentage: float = Field(0.0, description="Completion percentage")
    avg_task_completion_days: Optional[float] = Field(None, description="Average days to complete tasks")
    project_duration_days: Optional[int] = Field(None, description="Project duration in days")


class ProjectWithStats(ProjectResponse):
    """Project response with detailed statistics"""
    
    # Detailed task breakdown
    tasks_today: int = Field(0, description="Tasks scheduled for today")
    tasks_this_week: int = Field(0, description="Tasks scheduled for this week")
    tasks_reading: int = Field(0, description="Reading tasks")
    tasks_waiting: int = Field(0, description="Tasks waiting for something")
    tasks_postponed: int = Field(0, description="Postponed tasks")
    
    # Priority breakdown
    high_priority_tasks: int = Field(0, description="High priority tasks (1-2)")
    medium_priority_tasks: int = Field(0, description="Medium priority tasks (3)")
    low_priority_tasks: int = Field(0, description="Low priority tasks (4-5)")
    
    # Time tracking
    avg_task_completion_days: Optional[float] = Field(None, description="Average days to complete tasks")
    project_duration_days: Optional[int] = Field(None, description="Project duration in days")
    
    # Activity metrics
    last_task_created: Optional[datetime] = Field(None, description="Last task creation")
    last_task_completed: Optional[datetime] = Field(None, description="Last task completion")
    
    @classmethod
    def from_model_with_stats(cls, project_model, stats_data: dict) -> "ProjectWithStats":
        """Create response with stats from SQLAlchemy model and stats dict"""
        # Start with basic project data
        base_data = ProjectResponse.from_model(project_model).__dict__
        
        # Add statistics
        base_data.update(stats_data)
        
        return cls(**base_data)