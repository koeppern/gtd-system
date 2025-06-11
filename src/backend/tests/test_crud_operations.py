"""
Test CRUD operations directly
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from app.crud.user import crud_user
from app.crud.field import crud_field
from app.crud.project import crud_project
from app.crud.task import crud_task
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.field import FieldCreate, FieldUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.task import TaskCreate, TaskUpdate


class TestCRUDOperations:
    """Test CRUD operations directly."""
    
    async def test_user_crud(self, db_session: AsyncSession):
        """Test User CRUD operations."""
        # Create
        user_data = UserCreate(
            name="CRUD Test User",
            email_address="crud@example.com",
            is_active=True,
            email_verified=False
        )
        user = await crud_user.create(db=db_session, obj_in=user_data)
        
        assert user.name == "CRUD Test User"
        assert user.email_address == "crud@example.com"
        assert user.is_active is True
        assert user.email_verified is False
        
        # Read
        retrieved_user = await crud_user.get(db=db_session, id=user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.name == user.name
        
        # Update
        update_data = UserUpdate(name="Updated CRUD User", is_active=False)
        updated_user = await crud_user.update(db=db_session, db_obj=user, obj_in=update_data)
        
        assert updated_user.name == "Updated CRUD User"
        assert updated_user.is_active is False
        assert updated_user.email_address == "crud@example.com"  # Unchanged
        
        # Test get by email
        user_by_email = await crud_user.get_by_email(db=db_session, email="crud@example.com")
        assert user_by_email is not None
        assert user_by_email.id == user.id
        
        # Test user stats
        stats = await crud_user.get_user_stats(db=db_session, user_id=user.id)
        assert "total_projects" in stats
        assert "total_tasks" in stats
        assert stats["total_projects"] == 0  # No projects created yet
        assert stats["total_tasks"] == 0     # No tasks created yet
        
        # Delete
        deleted_user = await crud_user.delete(db=db_session, id=user.id)
        assert deleted_user is not None
        
        # Verify soft delete
        deleted_user_check = await crud_user.get(db=db_session, id=user.id)
        assert deleted_user_check is None  # Should not be found
        
        # But should be found with include_deleted
        deleted_user_with_deleted = await crud_user.get(db=db_session, id=user.id, include_deleted=True)
        assert deleted_user_with_deleted is not None
        assert deleted_user_with_deleted.is_deleted is True
    
    async def test_field_crud(self, db_session: AsyncSession):
        """Test Field CRUD operations."""
        # Create
        field_data = FieldCreate(
            name="CRUD Test Field",
            description="A field for testing CRUD operations"
        )
        field = await crud_field.create(db=db_session, obj_in=field_data)
        
        assert field.name == "CRUD Test Field"
        assert field.description == "A field for testing CRUD operations"
        
        # Read
        retrieved_field = await crud_field.get(db=db_session, id=field.id)
        assert retrieved_field is not None
        assert retrieved_field.id == field.id
        assert retrieved_field.name == field.name
        
        # Update
        update_data = FieldUpdate(
            name="Updated CRUD Field",
            description="Updated description"
        )
        updated_field = await crud_field.update(db=db_session, db_obj=field, obj_in=update_data)
        
        assert updated_field.name == "Updated CRUD Field"
        assert updated_field.description == "Updated description"
        
        # Test get by name
        field_by_name = await crud_field.get_by_name(db=db_session, name="Updated CRUD Field")
        assert field_by_name is not None
        assert field_by_name.id == field.id
        
        # Test get or create (existing)
        existing_field = await crud_field.get_or_create_by_name(
            db=db_session, 
            name="Updated CRUD Field"
        )
        assert existing_field.id == field.id
        
        # Test get or create (new)
        new_field = await crud_field.get_or_create_by_name(
            db=db_session,
            name="Auto Created Field",
            description="Auto created description"
        )
        assert new_field.id != field.id
        assert new_field.name == "Auto Created Field"
        
        # Test field stats
        stats = await crud_field.get_field_stats(db=db_session, field_id=field.id)
        assert "total_projects" in stats
        assert "total_tasks" in stats
        assert stats["total_projects"] == 0  # No projects using this field
        assert stats["total_tasks"] == 0     # No tasks using this field
        
        # Delete
        deleted_field = await crud_field.delete(db=db_session, id=field.id)
        assert deleted_field is not None
    
    async def test_project_crud(self, db_session: AsyncSession, test_user, test_field):
        """Test Project CRUD operations."""
        # Create
        project_data = ProjectCreate(
            user_id=test_user.id,
            project_name="CRUD Test Project",
            field_id=test_field.id,
            keywords="crud, test, project",
            do_this_week=True
        )
        project = await crud_project.create(db=db_session, obj_in=project_data)
        
        assert project.project_name == "CRUD Test Project"
        assert project.user_id == test_user.id
        assert project.field_id == test_field.id
        assert project.keywords == "crud, test, project"
        assert project.do_this_week is True
        assert project.done_at is None
        
        # Read
        retrieved_project = await crud_project.get(db=db_session, id=project.id)
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        assert retrieved_project.project_name == project.project_name
        
        # Update
        update_data = ProjectUpdate(
            project_name="Updated CRUD Project",
            keywords="updated, crud, test",
            do_this_week=False
        )
        updated_project = await crud_project.update(db=db_session, db_obj=project, obj_in=update_data)
        
        assert updated_project.project_name == "Updated CRUD Project"
        assert updated_project.keywords == "updated, crud, test"
        assert updated_project.do_this_week is False
        assert updated_project.field_id == test_field.id  # Unchanged
        
        # Test get by user
        user_projects = await crud_project.get_by_user(
            db=db_session,
            user_id=test_user.id,
            skip=0,
            limit=10
        )
        assert len(user_projects) >= 1
        assert any(p.id == project.id for p in user_projects)
        
        # Test get active projects
        active_projects = await crud_project.get_active_projects(
            db=db_session,
            user_id=test_user.id
        )
        assert len(active_projects) >= 1
        assert any(p.id == project.id for p in active_projects)
        
        # Test search projects
        search_results = await crud_project.search_projects(
            db=db_session,
            user_id=test_user.id,
            query="CRUD"
        )
        assert len(search_results) >= 1
        assert any(p.id == project.id for p in search_results)
        
        # Test complete project
        completed_project = await crud_project.complete_project(
            db=db_session,
            project=project
        )
        assert completed_project.done_at is not None
        
        # Test reopen project
        reopened_project = await crud_project.reopen_project(
            db=db_session,
            project=completed_project
        )
        assert reopened_project.done_at is None
        
        # Test get project with stats
        project_stats = await crud_project.get_project_with_task_stats(
            db=db_session,
            project_id=project.id
        )
        assert project_stats is not None
        assert "project" in project_stats
        assert "task_count" in project_stats
        assert project_stats["task_count"] == 0  # No tasks created yet
        
        # Delete
        deleted_project = await crud_project.delete(db=db_session, id=project.id)
        assert deleted_project is not None
    
    async def test_task_crud(self, db_session: AsyncSession, test_user, test_field, test_project):
        """Test Task CRUD operations."""
        # Create
        task_data = TaskCreate(
            user_id=test_user.id,
            task_name="CRUD Test Task",
            field_id=test_field.id,
            project_id=test_project.id,
            priority=2,
            do_today=True,
            do_this_week=False,
            is_reading=False,
            wait_for=False,
            postponed=False
        )
        task = await crud_task.create(db=db_session, obj_in=task_data)
        
        assert task.task_name == "CRUD Test Task"
        assert task.user_id == test_user.id
        assert task.field_id == test_field.id
        assert task.project_id == test_project.id
        assert task.priority == 2
        assert task.do_today is True
        assert task.done_at is None
        
        # Read
        retrieved_task = await crud_task.get(db=db_session, id=task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.task_name == task.task_name
        
        # Update
        update_data = TaskUpdate(
            task_name="Updated CRUD Task",
            priority=1,
            is_reading=True,
            wait_for=True
        )
        updated_task = await crud_task.update(db=db_session, db_obj=task, obj_in=update_data)
        
        assert updated_task.task_name == "Updated CRUD Task"
        assert updated_task.priority == 1
        assert updated_task.is_reading is True
        assert updated_task.wait_for is True
        assert updated_task.do_today is True  # Unchanged
        
        # Test get by user
        user_tasks = await crud_task.get_by_user(
            db=db_session,
            user_id=test_user.id,
            skip=0,
            limit=10
        )
        assert len(user_tasks) >= 1
        assert any(t.id == task.id for t in user_tasks)
        
        # Test get today tasks
        today_tasks = await crud_task.get_today_tasks(
            db=db_session,
            user_id=test_user.id
        )
        assert len(today_tasks) >= 1
        assert any(t.id == task.id for t in today_tasks)
        
        # Test get waiting tasks
        waiting_tasks = await crud_task.get_waiting_tasks(
            db=db_session,
            user_id=test_user.id
        )
        assert len(waiting_tasks) >= 1
        assert any(t.id == task.id for t in waiting_tasks)
        
        # Test get reading tasks
        reading_tasks = await crud_task.get_reading_tasks(
            db=db_session,
            user_id=test_user.id
        )
        assert len(reading_tasks) >= 1
        assert any(t.id == task.id for t in reading_tasks)
        
        # Test search tasks
        search_results = await crud_task.search_tasks(
            db=db_session,
            user_id=test_user.id,
            query="CRUD"
        )
        assert len(search_results) >= 1
        assert any(t.id == task.id for t in search_results)
        
        # Test schedule for today
        scheduled_task = await crud_task.schedule_for_today(db=db_session, task=task)
        assert scheduled_task.do_today is True
        assert scheduled_task.do_on_date == date.today()
        
        # Test schedule for week
        week_scheduled_task = await crud_task.schedule_for_week(db=db_session, task=task)
        assert week_scheduled_task.do_this_week is True
        
        # Test set priority
        priority_task = await crud_task.set_priority(db=db_session, task=task, priority=5)
        assert priority_task.priority == 5
        
        # Test invalid priority
        with pytest.raises(ValueError):
            await crud_task.set_priority(db=db_session, task=task, priority=10)
        
        # Test complete task
        completed_task = await crud_task.complete_task(db=db_session, task=task)
        assert completed_task.done_at is not None
        
        # Test reopen task
        reopened_task = await crud_task.reopen_task(db=db_session, task=completed_task)
        assert reopened_task.done_at is None
        
        # Test task stats
        stats = await crud_task.get_task_stats(db=db_session, user_id=test_user.id)
        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "pending_tasks" in stats
        assert stats["total_tasks"] >= 1
        
        # Test bulk complete
        # Create another task for bulk operations
        task2_data = TaskCreate(
            user_id=test_user.id,
            task_name="Bulk Test Task",
            priority=3
        )
        task2 = await crud_task.create(db=db_session, obj_in=task2_data)
        
        # Bulk complete both tasks
        completed_count = await crud_task.bulk_complete_tasks(
            db=db_session,
            task_ids=[task.id, task2.id],
            user_id=test_user.id
        )
        assert completed_count >= 1  # At least one should be completed
        
        # Delete
        deleted_task = await crud_task.delete(db=db_session, id=task.id)
        assert deleted_task is not None
    
    async def test_crud_base_operations(self, db_session: AsyncSession, test_user):
        """Test base CRUD operations."""
        # Test count
        user_count = await crud_user.count(db=db_session)
        assert user_count >= 1  # At least test_user exists
        
        # Test get_multi
        users = await crud_user.get_multi(db=db_session, skip=0, limit=10)
        assert len(users) >= 1
        assert any(u.id == test_user.id for u in users)
        
        # Test get_multi with ordering
        users_ordered = await crud_user.get_multi(
            db=db_session,
            order_by="created_at",
            order_desc=True
        )
        assert len(users_ordered) >= 1
        
        # Test exists
        user_exists = await crud_user.exists(
            db=db_session,
            filters={"id": test_user.id}
        )
        assert user_exists is True
        
        # Test exists with non-existent data
        fake_exists = await crud_user.exists(
            db=db_session,
            filters={"email_address": "nonexistent@example.com"}
        )
        assert fake_exists is False
        
        # Test search
        search_results = await crud_user.search(
            db=db_session,
            query="Test",
            search_fields=["name", "email_address"]
        )
        assert len(search_results) >= 1  # Should find test_user
    
    async def test_soft_delete_and_restore(self, db_session: AsyncSession, test_user):
        """Test soft delete and restore functionality."""
        # Create a field to test with
        field_data = FieldCreate(
            name="Soft Delete Test Field",
            description="Field to test soft delete"
        )
        field = await crud_field.create(db=db_session, obj_in=field_data)
        
        # Soft delete
        deleted_field = await crud_field.delete(db=db_session, id=field.id, hard_delete=False)
        assert deleted_field is not None
        assert deleted_field.is_deleted is True
        
        # Should not be found in normal queries
        not_found = await crud_field.get(db=db_session, id=field.id)
        assert not_found is None
        
        # Should be found with include_deleted
        found_deleted = await crud_field.get(db=db_session, id=field.id, include_deleted=True)
        assert found_deleted is not None
        assert found_deleted.is_deleted is True
        
        # Restore
        restored_field = await crud_field.restore(db=db_session, id=field.id)
        assert restored_field is not None
        assert restored_field.is_deleted is False
        
        # Should be found in normal queries again
        found_restored = await crud_field.get(db=db_session, id=field.id)
        assert found_restored is not None
        assert found_restored.is_deleted is False
    
    async def test_crud_error_handling(self, db_session: AsyncSession):
        """Test CRUD error handling."""
        # Test creating user with duplicate email
        user_data1 = UserCreate(
            name="User 1",
            email_address="duplicate@example.com"
        )
        user1 = await crud_user.create(db=db_session, obj_in=user_data1)
        
        # Try to create another user with same email
        user_data2 = UserCreate(
            name="User 2",
            email_address="duplicate@example.com"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            await crud_user.create(db=db_session, obj_in=user_data2)
        
        # Test creating field with duplicate name
        field_data1 = FieldCreate(name="Duplicate Field")
        field1 = await crud_field.create(db=db_session, obj_in=field_data1)
        
        field_data2 = FieldCreate(name="Duplicate Field")
        
        with pytest.raises(ValueError, match="already exists"):
            await crud_field.create(db=db_session, obj_in=field_data2)