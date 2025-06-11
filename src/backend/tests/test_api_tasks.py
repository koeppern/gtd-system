"""
Test Task API endpoints with GTD workflow
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date


class TestTaskAPI:
    """Test Task API endpoints."""
    
    def test_get_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test getting all tasks."""
        response = client.get("/api/tasks/")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) >= len(multiple_tasks)
        
        for task_data in data:
            helpers.assert_task_data(task_data)
    
    def test_get_tasks_with_filters(self, client: TestClient, test_user, multiple_tasks, multiple_projects, helpers):
        """Test getting tasks with various filters."""
        # Test project filter
        project_id = multiple_projects[0].id
        response = client.get(f"/api/tasks/?project_id={project_id}")
        data = helpers.assert_response_success(response)
        
        for task_data in data:
            assert task_data["project_id"] == project_id
        
        # Test priority filter
        response = client.get("/api/tasks/?priority=1")
        data = helpers.assert_response_success(response)
        
        for task_data in data:
            assert task_data["priority"] == 1
        
        # Test today tasks filter
        response = client.get("/api/tasks/?do_today=true")
        data = helpers.assert_response_success(response)
        
        for task_data in data:
            assert task_data["do_today"] is True
        
        # Test reading tasks filter
        response = client.get("/api/tasks/?is_reading=true")
        data = helpers.assert_response_success(response)
        
        for task_data in data:
            assert task_data["is_reading"] is True
        
        # Test waiting tasks filter
        response = client.get("/api/tasks/?wait_for=true")
        data = helpers.assert_response_success(response)
        
        for task_data in data:
            assert task_data["wait_for"] is True
    
    def test_get_today_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test getting today's tasks."""
        response = client.get("/api/tasks/today")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for task_data in data:
            helpers.assert_task_data(task_data)
            # Should be either marked for today or due today
            assert task_data["do_today"] is True or task_data["do_on_date"] == str(date.today())
    
    def test_get_week_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test getting this week's tasks."""
        response = client.get("/api/tasks/week")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for task_data in data:
            helpers.assert_task_data(task_data)
            # Should be marked for this week or due this week
            assert task_data["do_this_week"] is True or task_data["do_on_date"] is not None
    
    def test_get_overdue_tasks(self, client: TestClient, test_user, helpers):
        """Test getting overdue tasks."""
        # First create a task with past due date
        task_data = {
            "task_name": "Overdue Task",
            "do_on_date": "2023-01-01"  # Past date
        }
        
        create_response = client.post("/api/tasks/", json=task_data)
        helpers.assert_response_success(create_response)
        
        response = client.get("/api/tasks/overdue")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        # Should find the overdue task we created
        found_overdue = any(task["task_name"] == "Overdue Task" for task in data)
        assert found_overdue
    
    def test_get_waiting_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test getting waiting tasks."""
        response = client.get("/api/tasks/waiting")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for task_data in data:
            helpers.assert_task_data(task_data)
            assert task_data["wait_for"] is True
    
    def test_get_reading_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test getting reading tasks."""
        response = client.get("/api/tasks/reading")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for task_data in data:
            helpers.assert_task_data(task_data)
            assert task_data["is_reading"] is True
    
    def test_get_task_stats(self, client: TestClient, test_user, multiple_tasks, completed_items, helpers):
        """Test getting task statistics."""
        response = client.get("/api/tasks/stats")
        data = helpers.assert_response_success(response)
        
        # Check required stat fields
        required_fields = [
            "total_tasks", "completed_tasks", "pending_tasks", "completion_rate",
            "tasks_today", "overdue_tasks", "priority_1", "priority_2", "priority_3",
            "priority_4", "priority_5", "no_priority", "reading_tasks", "waiting_tasks"
        ]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], (int, float))
        
        # Validate data consistency
        assert data["pending_tasks"] == data["total_tasks"] - data["completed_tasks"]
    
    def test_get_tasks_by_project(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting tasks by project."""
        project_id = multiple_projects[0].id
        response = client.get(f"/api/tasks/by-project/{project_id}")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for task_data in data:
            helpers.assert_task_data(task_data)
            assert task_data["project_id"] == project_id
    
    def test_search_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test searching tasks."""
        response = client.get("/api/tasks/search?query=authentication")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        # Should find tasks with "authentication" in name
        found_relevant = any("authentication" in task["task_name"].lower() for task in data)
        assert found_relevant
    
    def test_get_task_by_id(self, client: TestClient, test_user, test_task, helpers):
        """Test getting task by ID."""
        response = client.get(f"/api/tasks/{test_task.id}")
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data, expected_name="Test Task")
        assert data["id"] == test_task.id
    
    def test_get_task_by_id_not_found(self, client: TestClient, test_user, helpers):
        """Test getting non-existent task."""
        response = client.get("/api/tasks/999999")
        helpers.assert_response_error(response, 404)
    
    def test_create_task(self, client: TestClient, test_user, test_field, test_project, helpers):
        """Test creating a new task."""
        task_data = {
            "task_name": "New Task",
            "field_id": test_field.id,
            "project_id": test_project.id,
            "priority": 2,
            "do_today": True,
            "is_reading": False
        }
        
        response = client.post("/api/tasks/", json=task_data)
        data = helpers.assert_response_success(response, 200)
        helpers.assert_task_data(data, expected_name="New Task")
        assert data["field_id"] == test_field.id
        assert data["project_id"] == test_project.id
        assert data["priority"] == 2
        assert data["do_today"] is True
    
    def test_update_task(self, client: TestClient, test_user, test_task, helpers):
        """Test updating a task."""
        update_data = {
            "task_name": "Updated Task",
            "priority": 1,
            "do_today": True,
            "is_reading": True
        }
        
        response = client.put(f"/api/tasks/{test_task.id}", json=update_data)
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data, expected_name="Updated Task")
        assert data["priority"] == 1
        assert data["do_today"] is True
        assert data["is_reading"] is True
    
    def test_update_task_not_found(self, client: TestClient, test_user, helpers):
        """Test updating non-existent task."""
        update_data = {
            "task_name": "Non-existent Task"
        }
        
        response = client.put("/api/tasks/999999", json=update_data)
        helpers.assert_response_error(response, 404)
    
    def test_complete_task(self, client: TestClient, test_user, test_task, helpers):
        """Test completing a task."""
        response = client.post(f"/api/tasks/{test_task.id}/complete")
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data)
        assert data["done_at"] is not None
    
    def test_complete_task_with_timestamp(self, client: TestClient, test_user, test_task, helpers):
        """Test completing a task with custom timestamp."""
        completion_time = "2023-12-01T10:00:00"
        
        response = client.post(
            f"/api/tasks/{test_task.id}/complete",
            json=completion_time
        )
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data)
        assert data["done_at"] is not None
    
    def test_complete_task_already_completed(self, client: TestClient, test_user, completed_items, helpers):
        """Test completing an already completed task."""
        task_id = completed_items["tasks"][0].id
        
        response = client.post(f"/api/tasks/{task_id}/complete")
        helpers.assert_response_error(response, 400)
    
    def test_reopen_task(self, client: TestClient, test_user, completed_items, helpers):
        """Test reopening a completed task."""
        task_id = completed_items["tasks"][0].id
        
        response = client.post(f"/api/tasks/{task_id}/reopen")
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data)
        assert data["done_at"] is None
    
    def test_reopen_task_not_completed(self, client: TestClient, test_user, test_task, helpers):
        """Test reopening a task that isn't completed."""
        response = client.post(f"/api/tasks/{test_task.id}/reopen")
        helpers.assert_response_error(response, 400)
    
    def test_schedule_task_for_today(self, client: TestClient, test_user, test_task, helpers):
        """Test scheduling task for today."""
        response = client.post(f"/api/tasks/{test_task.id}/schedule-today")
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data)
        assert data["do_today"] is True
        assert data["do_on_date"] == str(date.today())
    
    def test_schedule_task_for_week(self, client: TestClient, test_user, test_task, helpers):
        """Test scheduling task for this week."""
        response = client.post(f"/api/tasks/{test_task.id}/schedule-week")
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data)
        assert data["do_this_week"] is True
    
    def test_set_task_priority(self, client: TestClient, test_user, test_task, helpers):
        """Test setting task priority."""
        response = client.post(f"/api/tasks/{test_task.id}/set-priority", json=1)
        data = helpers.assert_response_success(response)
        helpers.assert_task_data(data)
        assert data["priority"] == 1
    
    def test_set_task_priority_invalid(self, client: TestClient, test_user, test_task, helpers):
        """Test setting invalid task priority."""
        response = client.post(f"/api/tasks/{test_task.id}/set-priority", json=6)  # Invalid priority
        helpers.assert_response_error(response, 422)  # Validation error
    
    def test_bulk_complete_tasks(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test bulk completing multiple tasks."""
        # Get some incomplete task IDs
        task_ids = [task.id for task in multiple_tasks[:3] if not task.done_at]
        
        response = client.post("/api/tasks/bulk-complete", json=task_ids)
        data = helpers.assert_response_success(response)
        
        assert "completed_count" in data
        assert data["completed_count"] >= 0
        assert "message" in data
    
    def test_bulk_complete_tasks_empty_list(self, client: TestClient, test_user, helpers):
        """Test bulk completing with empty task list."""
        response = client.post("/api/tasks/bulk-complete", json=[])
        helpers.assert_response_error(response, 400)
    
    def test_delete_task_soft(self, client: TestClient, test_user, test_task, helpers):
        """Test soft deleting a task."""
        response = client.delete(f"/api/tasks/{test_task.id}")
        data = helpers.assert_response_success(response)
        assert "soft deleted" in data["message"]
    
    def test_delete_task_hard(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test hard deleting a task."""
        task_id = multiple_tasks[-1].id  # Use last task to avoid affecting other tests
        
        response = client.delete(f"/api/tasks/{task_id}?hard_delete=true")
        data = helpers.assert_response_success(response)
        assert "permanently deleted" in data["message"]
    
    def test_delete_task_not_found(self, client: TestClient, test_user, helpers):
        """Test deleting non-existent task."""
        response = client.delete("/api/tasks/999999")
        helpers.assert_response_error(response, 404)
    
    def test_restore_task(self, client: TestClient, test_user, helpers):
        """Test restoring a soft-deleted task."""
        # First create and soft delete a task
        task_data = {
            "task_name": "Task to Restore"
        }
        
        create_response = client.post("/api/tasks/", json=task_data)
        task_data = helpers.assert_response_success(create_response)
        task_id = task_data["id"]
        
        # Soft delete it
        delete_response = client.delete(f"/api/tasks/{task_id}")
        helpers.assert_response_success(delete_response)
        
        # Restore it
        restore_response = client.post(f"/api/tasks/{task_id}/restore")
        data = helpers.assert_response_success(restore_response)
        helpers.assert_task_data(data, expected_name="Task to Restore")
    
    def test_task_gtd_workflow(self, client: TestClient, test_user, helpers):
        """Test complete GTD workflow for tasks."""
        # 1. Create task
        task_data = {
            "task_name": "GTD Workflow Test Task",
            "priority": 3
        }
        
        create_response = client.post("/api/tasks/", json=task_data)
        task = helpers.assert_response_success(create_response)
        task_id = task["id"]
        
        # 2. Schedule for today
        schedule_response = client.post(f"/api/tasks/{task_id}/schedule-today")
        scheduled_task = helpers.assert_response_success(schedule_response)
        assert scheduled_task["do_today"] is True
        
        # 3. Set high priority
        priority_response = client.post(f"/api/tasks/{task_id}/set-priority", json=1)
        priority_task = helpers.assert_response_success(priority_response)
        assert priority_task["priority"] == 1
        
        # 4. Update to reading task
        update_response = client.put(
            f"/api/tasks/{task_id}",
            json={"is_reading": True}
        )
        updated_task = helpers.assert_response_success(update_response)
        assert updated_task["is_reading"] is True
        
        # 5. Complete task
        complete_response = client.post(f"/api/tasks/{task_id}/complete")
        completed_task = helpers.assert_response_success(complete_response)
        assert completed_task["done_at"] is not None
        
        # 6. Reopen task
        reopen_response = client.post(f"/api/tasks/{task_id}/reopen")
        reopened_task = helpers.assert_response_success(reopen_response)
        assert reopened_task["done_at"] is None
        
        # 7. Delete task
        delete_response = client.delete(f"/api/tasks/{task_id}")
        helpers.assert_response_success(delete_response)
    
    def test_task_api_validation_errors(self, client: TestClient, test_user, helpers):
        """Test API validation errors."""
        # Test missing required fields
        response = client.post("/api/tasks/", json={})
        helpers.assert_response_error(response, 422)
        
        # Test invalid task name (empty string)
        task_data = {
            "task_name": ""
        }
        response = client.post("/api/tasks/", json=task_data)
        helpers.assert_response_error(response, 422)
        
        # Test invalid priority
        task_data = {
            "task_name": "Test Task",
            "priority": 10  # Invalid priority (should be 1-5)
        }
        response = client.post("/api/tasks/", json=task_data)
        helpers.assert_response_error(response, 422)
    
    def test_task_pagination(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test task pagination."""
        # Test with limit
        response = client.get("/api/tasks/?skip=0&limit=3")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) <= 3
        
        # Test with skip
        response = client.get("/api/tasks/?skip=2&limit=3")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) <= 3