"""
Test Pydantic schemas
"""
import pytest
from datetime import datetime, date
from uuid import uuid4, UUID
from pydantic import ValidationError

from app.schemas import (
    UserCreate, UserUpdate, UserResponse,
    FieldCreate, FieldUpdate, FieldResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    QuickAddRequest, SearchRequest,
    PaginationParams, DashboardStats,
    TEST_USER_ID
)


class TestUserSchemas:
    """Test User schemas"""
    
    def test_user_create_valid(self):
        """Test valid user creation"""
        user_data = {
            "email_address": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "timezone": "Europe/Berlin"
        }
        
        user = UserCreate(**user_data)
        assert user.email_address == "test@example.com"
        assert user.first_name == "Test"
        assert user.is_active is True
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(email_address="invalid-email")
    
    def test_user_update_partial(self):
        """Test partial user update"""
        update_data = {
            "first_name": "Updated",
            "timezone": "America/New_York"
        }
        
        update = UserUpdate(**update_data)
        assert update.first_name == "Updated"
        assert update.timezone == "America/New_York"
        assert update.last_name is None  # Not provided
    
    def test_weekly_review_day_validation(self):
        """Test weekly review day validation"""
        # Valid day
        user = UserCreate(email_address="test@example.com", weekly_review_day=0)
        assert user.weekly_review_day == 0
        
        # Invalid day
        with pytest.raises(ValidationError):
            UserCreate(email_address="test@example.com", weekly_review_day=7)


class TestFieldSchemas:
    """Test Field schemas"""
    
    def test_field_create_valid(self):
        """Test valid field creation"""
        field_data = {
            "name": "Work",
            "description": "Work-related projects and tasks"
        }
        
        field = FieldCreate(**field_data)
        assert field.name == "Work"
        assert field.description == "Work-related projects and tasks"
    
    def test_field_name_required(self):
        """Test field name is required"""
        with pytest.raises(ValidationError):
            FieldCreate(description="Test")
    
    def test_field_name_too_long(self):
        """Test field name length validation"""
        with pytest.raises(ValidationError):
            FieldCreate(name="a" * 51)  # 51 characters, max is 50


class TestProjectSchemas:
    """Test Project schemas"""
    
    def test_project_create_valid(self):
        """Test valid project creation"""
        project_data = {
            "user_id": TEST_USER_ID,
            "project_name": "Test Project",
            "field_id": 1,
            "do_this_week": True
        }
        
        project = ProjectCreate(**project_data)
        assert project.user_id == TEST_USER_ID
        assert project.project_name == "Test Project"
        assert project.do_this_week is True
    
    def test_project_name_required(self):
        """Test project name is required"""
        with pytest.raises(ValidationError):
            ProjectCreate(user_id=TEST_USER_ID)
    
    def test_project_update_partial(self):
        """Test partial project update"""
        update_data = {
            "project_name": "Updated Project",
            "do_this_week": False
        }
        
        update = ProjectUpdate(**update_data)
        assert update.project_name == "Updated Project"
        assert update.do_this_week is False
        assert update.field_id is None  # Not provided


class TestTaskSchemas:
    """Test Task schemas"""
    
    def test_task_create_valid(self):
        """Test valid task creation"""
        task_data = {
            "user_id": TEST_USER_ID,
            "task_name": "Test Task",
            "project_id": 1,
            "priority": 1,
            "do_today": True
        }
        
        task = TaskCreate(**task_data)
        assert task.user_id == TEST_USER_ID
        assert task.task_name == "Test Task"
        assert task.priority == 1
        assert task.do_today is True
    
    def test_task_priority_validation(self):
        """Test task priority validation"""
        # Valid priorities
        for priority in [1, 2, 3, 4, 5]:
            task = TaskCreate(
                user_id=TEST_USER_ID,
                task_name="Test Task",
                priority=priority
            )
            assert task.priority == priority
        
        # Invalid priorities
        for invalid_priority in [0, 6, -1, 10]:
            with pytest.raises(ValidationError):
                TaskCreate(
                    user_id=TEST_USER_ID,
                    task_name="Test Task",
                    priority=invalid_priority
                )
    
    def test_task_with_due_date(self):
        """Test task with due date"""
        task_data = {
            "user_id": TEST_USER_ID,
            "task_name": "Test Task",
            "do_on_date": date.today()
        }
        
        task = TaskCreate(**task_data)
        assert task.do_on_date == date.today()


class TestCommonSchemas:
    """Test common schemas"""
    
    def test_pagination_params(self):
        """Test pagination parameters"""
        params = PaginationParams(limit=50, offset=100)
        assert params.limit == 50
        assert params.offset == 100
        assert params.order_desc is False
    
    def test_pagination_validation(self):
        """Test pagination validation"""
        # Limit too high
        with pytest.raises(ValidationError):
            PaginationParams(limit=101)
        
        # Limit too low
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)
        
        # Negative offset
        with pytest.raises(ValidationError):
            PaginationParams(offset=-1)
    
    def test_quick_add_request(self):
        """Test quick add request"""
        request_data = {
            "content": "Quick task to add",
            "type": "task",
            "do_today": True,
            "priority": 2
        }
        
        request = QuickAddRequest(**request_data)
        assert request.content == "Quick task to add"
        assert request.type == "task"
        assert request.do_today is True
        assert request.priority == 2
    
    def test_search_request(self):
        """Test search request"""
        search_data = {
            "query": "test search",
            "user_id": TEST_USER_ID,
            "types": ["project", "task"],
            "include_completed": False
        }
        
        search = SearchRequest(**search_data)
        assert search.query == "test search"
        assert search.user_id == TEST_USER_ID
        assert "project" in search.types
        assert "task" in search.types
    
    def test_dashboard_stats(self):
        """Test dashboard stats schema"""
        stats_data = {
            "total_projects": 10,
            "active_projects": 8,
            "completed_projects": 2,
            "total_tasks": 50,
            "pending_tasks": 40,
            "completed_tasks": 10,
            "tasks_today": 5,
            "tasks_this_week": 15,
            "overdue_tasks": 3,
            "completion_rate_7d": 75.5,
            "completion_rate_30d": 68.2
        }
        
        stats = DashboardStats(**stats_data)
        assert stats.total_projects == 10
        assert stats.completion_rate_7d == 75.5


class TestSchemaConstants:
    """Test schema constants"""
    
    def test_test_user_id(self):
        """Test TEST_USER_ID constant"""
        assert TEST_USER_ID == UUID("00000000-0000-0000-0000-000000000001")
        assert str(TEST_USER_ID) == "00000000-0000-0000-0000-000000000001"


class TestSchemaRelationships:
    """Test schema relationships and from_model methods"""
    
    def test_user_response_from_model(self):
        """Test UserResponse.from_model method structure"""
        # This tests the method signature, actual model testing requires DB
        assert hasattr(UserResponse, 'from_model')
        assert callable(UserResponse.from_model)
    
    def test_project_response_from_model(self):
        """Test ProjectResponse.from_model method structure"""
        assert hasattr(ProjectResponse, 'from_model')
        assert callable(ProjectResponse.from_model)
    
    def test_task_response_from_model(self):
        """Test TaskResponse.from_model method structure"""
        assert hasattr(TaskResponse, 'from_model')
        assert callable(TaskResponse.from_model)