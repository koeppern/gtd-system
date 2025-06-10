"""
Test SQLAlchemy models
"""
import pytest
from datetime import datetime, date
from uuid import uuid4

from app.models import User, Field, Project, Task


class TestUser:
    """Test User model"""
    
    def test_user_creation(self):
        """Test creating a user"""
        user = User(
            email_address="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        assert user.email_address == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.email_verified is True
    
    def test_user_full_name(self):
        """Test full name property"""
        user = User(
            email_address="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        assert user.full_name == "Test User"
    
    def test_user_display_name(self):
        """Test display name property"""
        # With full name
        user = User(
            email_address="test@example.com",
            first_name="Test",
            last_name="User"
        )
        assert user.display_name == "Test User"
        
        # Without name, should use email
        user2 = User(email_address="test@example.com")
        assert user2.display_name == "test@example.com"


class TestField:
    """Test Field model"""
    
    def test_field_creation(self):
        """Test creating a field"""
        field = Field(
            name="Private",
            description="Personal projects and tasks"
        )
        
        assert field.name == "Private"
        assert field.description == "Personal projects and tasks"
    
    def test_field_repr(self):
        """Test field string representation"""
        field = Field(name="Work")
        field.id = 1
        
        assert repr(field) == "<Field(id=1, name=Work)>"


class TestProject:
    """Test Project model"""
    
    def test_project_creation(self):
        """Test creating a project"""
        user_id = uuid4()
        project = Project(
            user_id=user_id,
            project_name="Test Project",
            do_this_week=True
        )
        
        assert project.user_id == user_id
        assert project.project_name == "Test Project"
        assert project.do_this_week is True
        assert project.is_done is False
        assert project.is_active is True
    
    def test_project_completion(self):
        """Test project completion"""
        project = Project(
            user_id=uuid4(),
            project_name="Test Project"
        )
        
        assert project.is_done is False
        
        project.complete()
        assert project.is_done is True
        assert project.done_at is not None
        
        project.reopen()
        assert project.is_done is False
        assert project.done_at is None
    
    def test_project_soft_delete(self):
        """Test project soft delete"""
        project = Project(
            user_id=uuid4(),
            project_name="Test Project"
        )
        
        assert project.is_deleted is False
        assert project.is_active is True
        
        project.soft_delete()
        assert project.is_deleted is True
        assert project.is_active is False


class TestTask:
    """Test Task model"""
    
    def test_task_creation(self):
        """Test creating a task"""
        user_id = uuid4()
        task = Task(
            user_id=user_id,
            task_name="Test Task",
            do_today=True,
            priority=1
        )
        
        assert task.user_id == user_id
        assert task.task_name == "Test Task"
        assert task.do_today is True
        assert task.priority == 1
        assert task.is_done is False
        assert task.is_active is True
    
    def test_task_completion(self):
        """Test task completion"""
        task = Task(
            user_id=uuid4(),
            task_name="Test Task"
        )
        
        assert task.is_done is False
        
        task.complete()
        assert task.is_done is True
        assert task.done_at is not None
        
        task.reopen()
        assert task.is_done is False
        assert task.done_at is None
    
    def test_task_due_date_checks(self):
        """Test due date checking methods"""
        task = Task(
            user_id=uuid4(),
            task_name="Test Task"
        )
        
        # No due date
        assert task.is_due_today is False
        assert task.is_overdue is False
        
        # Due today
        task.do_on_date = date.today()
        assert task.is_due_today is True
        assert task.is_overdue is False
        
        # Overdue
        from datetime import timedelta
        task.do_on_date = date.today() - timedelta(days=1)
        assert task.is_due_today is False
        assert task.is_overdue is True
        
        # Completed task is not overdue
        task.complete()
        assert task.is_overdue is False
    
    def test_task_priority(self):
        """Test task priority setting"""
        task = Task(
            user_id=uuid4(),
            task_name="Test Task"
        )
        
        task.set_priority(1)
        assert task.priority == 1
        
        task.set_priority(5)
        assert task.priority == 5
        
        # Invalid priority should raise error
        with pytest.raises(ValueError):
            task.set_priority(0)
        
        with pytest.raises(ValueError):
            task.set_priority(6)