"""
Common Pydantic schemas and utilities
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# Type variable for generic responses
T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SoftDeleteMixin(BaseModel):
    """Mixin for soft delete functionality"""
    
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None


class PaginationParams(BaseSchema):
    """Pagination parameters for list endpoints"""
    
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")
    order_by: Optional[str] = Field(None, description="Field to order by")
    order_desc: bool = Field(False, description="Order descending")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper"""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Items skipped")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        limit: int,
        offset: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response"""
        return cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0,
        )


class ErrorDetail(BaseSchema):
    """Error detail schema"""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseSchema):
    """Standardized error response"""
    
    success: bool = Field(False, description="Success status")
    error: ErrorDetail = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class SuccessResponse(BaseSchema):
    """Standardized success response"""
    
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class CompletionRequest(BaseSchema):
    """Request to mark something as completed"""
    
    completed_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Completion timestamp"
    )
    notes: Optional[str] = Field(None, description="Completion notes")


class QuickAddRequest(BaseSchema):
    """Quick add request for GTD capture"""
    
    content: str = Field(..., min_length=1, max_length=1000, description="Content to capture")
    type: Optional[str] = Field("task", description="Type: task or project")
    field: Optional[str] = Field(None, description="Field/category name")
    project_name: Optional[str] = Field(None, description="Project name for tasks")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    do_today: bool = Field(False, description="Schedule for today")
    do_this_week: bool = Field(False, description="Schedule for this week")


class SearchRequest(BaseSchema):
    """Search request across projects and tasks"""
    
    query: str = Field(..., min_length=1, description="Search query")
    types: List[str] = Field(["project", "task"], description="Types to search: project, task")
    field_id: Optional[int] = Field(None, description="Filter by field ID")
    user_id: UUID = Field(..., description="User ID for search")
    include_completed: bool = Field(False, description="Include completed items")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")


class SearchResult(BaseSchema):
    """Individual search result"""
    
    id: int = Field(..., description="Item ID")
    type: str = Field(..., description="Type: project or task")
    title: str = Field(..., description="Item title/name")
    description: Optional[str] = Field(None, description="Item description")
    field_name: Optional[str] = Field(None, description="Field/category name")
    is_completed: bool = Field(..., description="Whether item is completed")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    relevance_score: float = Field(..., description="Search relevance (0-1)")


class SearchResponse(BaseSchema):
    """Search response with results"""
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total results found")
    search_time_ms: float = Field(..., description="Search time in milliseconds")


# Constants for testing
TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class DashboardStats(BaseSchema):
    """Dashboard statistics"""
    
    total_projects: int = Field(..., description="Total projects")
    active_projects: int = Field(..., description="Active projects")
    completed_projects: int = Field(..., description="Completed projects")
    
    total_tasks: int = Field(..., description="Total tasks")
    pending_tasks: int = Field(..., description="Pending tasks")
    completed_tasks: int = Field(..., description="Completed tasks")
    
    tasks_today: int = Field(..., description="Tasks due today")
    tasks_this_week: int = Field(..., description="Tasks due this week")
    overdue_tasks: int = Field(..., description="Overdue tasks")
    
    completion_rate_7d: float = Field(..., description="7-day completion rate percentage")
    completion_rate_30d: float = Field(..., description="30-day completion rate percentage")