"""
Pydantic schemas for GTD API
"""
from .common import (
    BaseSchema,
    TimestampMixin,
    SoftDeleteMixin,
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
    QuickAddRequest,
    SearchRequest,
    SearchResult,
    SearchResponse,
    DashboardStats,
    CompletionRequest,
    TEST_USER_ID,
)
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserSummary,
)
from .field import (
    FieldBase,
    FieldCreate,
    FieldUpdate,
    FieldResponse,
    FieldSummary,
)
from .project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectSummary,
    ProjectListResponse,
    ProjectFilters,
)
from .task import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskSummary,
    TaskListResponse,
    TaskFilters,
)

__all__ = [
    # Common
    "BaseSchema",
    "TimestampMixin", 
    "SoftDeleteMixin",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "QuickAddRequest",
    "SearchRequest",
    "SearchResult",
    "SearchResponse",
    "DashboardStats",
    "CompletionRequest",
    "TEST_USER_ID",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserSummary",
    # Field
    "FieldBase",
    "FieldCreate",
    "FieldUpdate",
    "FieldResponse",
    "FieldSummary",
    # Project
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectSummary",
    "ProjectListResponse",
    "ProjectFilters",
    # Task
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskSummary",
    "TaskListResponse",
    "TaskFilters",
]