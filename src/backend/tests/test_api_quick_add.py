"""
Test Quick-add API endpoints for GTD workflow
"""
import pytest
from fastapi.testclient import TestClient


class TestQuickAddAPI:
    """Test Quick-add API endpoints."""
    
    def test_quick_add_task_basic(self, client: TestClient, test_user, helpers):
        """Test basic quick add task functionality."""
        task_data = {
            "task_name": "Quick Task Test"
        }
        
        response = client.post("/api/quick-add/task", json=task_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_task_data(data, expected_name="Quick Task Test")
        assert data["task_name"] == "Quick Task Test"
    
    def test_quick_add_task_with_all_options(self, client: TestClient, test_user, helpers):
        """Test quick add task with all options."""
        task_data = {
            "task_name": "Comprehensive Quick Task",
            "project_name": "Quick Project",
            "field_name": "Quick Field",
            "priority": 2,
            "do_today": True,
            "do_this_week": False,
            "is_reading": True,
            "wait_for": False
        }
        
        response = client.post("/api/quick-add/task", json=task_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_task_data(data, expected_name="Comprehensive Quick Task")
        assert data["priority"] == 2
        assert data["do_today"] is True
        assert data["do_this_week"] is False
        assert data["is_reading"] is True
        assert data["wait_for"] is False
        assert data["project_id"] is not None  # Should have created project
        assert data["field_id"] is not None   # Should have created field
    
    def test_quick_add_task_with_existing_project(self, client: TestClient, test_user, test_project, helpers):
        """Test quick add task with existing project."""
        task_data = {
            "task_name": "Task for Existing Project",
            "project_name": test_project.project_name  # Use existing project name
        }
        
        response = client.post("/api/quick-add/task", json=task_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_task_data(data, expected_name="Task for Existing Project")
        assert data["project_id"] == test_project.id
    
    def test_quick_add_task_with_existing_field(self, client: TestClient, test_user, test_field, helpers):
        """Test quick add task with existing field."""
        task_data = {
            "task_name": "Task for Existing Field",
            "field_name": test_field.name  # Use existing field name
        }
        
        response = client.post("/api/quick-add/task", json=task_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_task_data(data, expected_name="Task for Existing Field")
        assert data["field_id"] == test_field.id
    
    def test_quick_add_task_invalid_priority(self, client: TestClient, test_user, helpers):
        """Test quick add task with invalid priority."""
        task_data = {
            "task_name": "Invalid Priority Task",
            "priority": 10  # Invalid priority
        }
        
        response = client.post("/api/quick-add/task", json=task_data)
        helpers.assert_response_error(response, 422)  # Validation error
    
    def test_quick_add_project_basic(self, client: TestClient, test_user, helpers):
        """Test basic quick add project functionality."""
        project_data = {
            "project_name": "Quick Project Test"
        }
        
        response = client.post("/api/quick-add/project", json=project_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_project_data(data, expected_name="Quick Project Test")
        assert data["project_name"] == "Quick Project Test"
    
    def test_quick_add_project_with_all_options(self, client: TestClient, test_user, helpers):
        """Test quick add project with all options."""
        project_data = {
            "project_name": "Comprehensive Quick Project",
            "field_name": "Quick Project Field",
            "do_this_week": True,
            "keywords": "quick, test, project"
        }
        
        response = client.post("/api/quick-add/project", json=project_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_project_data(data, expected_name="Comprehensive Quick Project")
        assert data["do_this_week"] is True
        assert data["keywords"] == "quick, test, project"
        assert data["field_id"] is not None  # Should have created field
    
    def test_quick_add_project_with_existing_field(self, client: TestClient, test_user, test_field, helpers):
        """Test quick add project with existing field."""
        project_data = {
            "project_name": "Project for Existing Field",
            "field_name": test_field.name  # Use existing field name
        }
        
        response = client.post("/api/quick-add/project", json=project_data)
        data = helpers.assert_response_success(response)
        
        helpers.assert_project_data(data, expected_name="Project for Existing Field")
        assert data["field_id"] == test_field.id
    
    def test_quick_capture_as_task(self, client: TestClient, test_user, helpers):
        """Test quick capture that gets categorized as a task."""
        capture_data = {
            "content": "Call John about the meeting tomorrow",
            "auto_categorize": True
        }
        
        response = client.post("/api/quick-add/capture", json=capture_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "task"
        assert "id" in data
        assert "name" in data
        assert data["message"] == "Content captured as task"
        assert "call john" in data["name"].lower()
    
    def test_quick_capture_as_project(self, client: TestClient, test_user, helpers):
        """Test quick capture that gets categorized as a project."""
        capture_data = {
            "content": "Complete the quarterly business review project with comprehensive analysis and strategic recommendations for the upcoming fiscal year",
            "auto_categorize": True
        }
        
        response = client.post("/api/quick-add/capture", json=capture_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "project"
        assert "id" in data
        assert "name" in data
        assert data["message"] == "Content captured as project"
        assert "quarterly business review" in data["name"].lower()
    
    def test_quick_capture_without_auto_categorize(self, client: TestClient, test_user, helpers):
        """Test quick capture without auto categorization."""
        capture_data = {
            "content": "Something to capture",
            "auto_categorize": False
        }
        
        response = client.post("/api/quick-add/capture", json=capture_data)
        data = helpers.assert_response_success(response)
        
        # Should default to task when auto_categorize is False
        assert data["type"] == "task"
        assert "id" in data
        assert "name" in data
        assert data["message"] == "Content captured as task"
    
    def test_quick_capture_project_keywords(self, client: TestClient, test_user, helpers):
        """Test quick capture with project keywords."""
        capture_data = {
            "content": "New PROJECT for client management and goal achievement",
            "auto_categorize": True
        }
        
        response = client.post("/api/quick-add/capture", json=capture_data)
        data = helpers.assert_response_success(response)
        
        # Should be categorized as project due to "PROJECT" and "goal" keywords
        assert data["type"] == "project"
    
    def test_quick_capture_task_keywords(self, client: TestClient, test_user, helpers):
        """Test quick capture with task keywords."""
        capture_data = {
            "content": "Call client and email the report",
            "auto_categorize": True
        }
        
        response = client.post("/api/quick-add/capture", json=capture_data)
        data = helpers.assert_response_success(response)
        
        # Should be categorized as task due to "call" and "email" keywords
        assert data["type"] == "task"
    
    def test_process_inbox_item_task_schedule_today(self, client: TestClient, test_user, helpers):
        """Test processing inbox item - schedule task for today."""
        # First create a task
        task_data = {
            "task_name": "Inbox Task to Process"
        }
        
        create_response = client.post("/api/quick-add/task", json=task_data)
        task = helpers.assert_response_success(create_response)
        task_id = task["id"]
        
        # Process it - schedule for today
        process_data = {
            "item_id": task_id,
            "item_type": "task",
            "action": "schedule_today"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "task"
        assert data["id"] == task_id
        assert "schedule_today" in data["message"]
        
        # Verify the task was updated
        verify_response = client.get(f"/api/tasks/{task_id}")
        updated_task = helpers.assert_response_success(verify_response)
        assert updated_task["do_today"] is True
    
    def test_process_inbox_item_task_assign_project(self, client: TestClient, test_user, helpers):
        """Test processing inbox item - assign task to project."""
        # First create a task
        task_data = {
            "task_name": "Task to Assign to Project"
        }
        
        create_response = client.post("/api/quick-add/task", json=task_data)
        task = helpers.assert_response_success(create_response)
        task_id = task["id"]
        
        # Process it - assign to project
        process_data = {
            "item_id": task_id,
            "item_type": "task",
            "action": "assign_project",
            "project_name": "New Inbox Project",
            "field_name": "Inbox Field",
            "priority": 2
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "task"
        assert data["id"] == task_id
        assert "assign_project" in data["message"]
        
        # Verify the task was updated
        verify_response = client.get(f"/api/tasks/{task_id}")
        updated_task = helpers.assert_response_success(verify_response)
        assert updated_task["project_id"] is not None
        assert updated_task["field_id"] is not None
        assert updated_task["priority"] == 2
    
    def test_process_inbox_item_task_mark_reading(self, client: TestClient, test_user, helpers):
        """Test processing inbox item - mark task as reading."""
        # First create a task
        task_data = {
            "task_name": "Task to Mark as Reading"
        }
        
        create_response = client.post("/api/quick-add/task", json=task_data)
        task = helpers.assert_response_success(create_response)
        task_id = task["id"]
        
        # Process it - mark as reading
        process_data = {
            "item_id": task_id,
            "item_type": "task",
            "action": "mark_reading"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "task"
        assert data["id"] == task_id
        
        # Verify the task was updated
        verify_response = client.get(f"/api/tasks/{task_id}")
        updated_task = helpers.assert_response_success(verify_response)
        assert updated_task["is_reading"] is True
    
    def test_process_inbox_item_task_mark_waiting(self, client: TestClient, test_user, helpers):
        """Test processing inbox item - mark task as waiting."""
        # First create a task
        task_data = {
            "task_name": "Task to Mark as Waiting"
        }
        
        create_response = client.post("/api/quick-add/task", json=task_data)
        task = helpers.assert_response_success(create_response)
        task_id = task["id"]
        
        # Process it - mark as waiting
        process_data = {
            "item_id": task_id,
            "item_type": "task",
            "action": "mark_waiting"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "task"
        assert data["id"] == task_id
        
        # Verify the task was updated
        verify_response = client.get(f"/api/tasks/{task_id}")
        updated_task = helpers.assert_response_success(verify_response)
        assert updated_task["wait_for"] is True
    
    def test_process_inbox_item_project_schedule_week(self, client: TestClient, test_user, helpers):
        """Test processing inbox item - schedule project for week."""
        # First create a project
        project_data = {
            "project_name": "Project to Schedule for Week"
        }
        
        create_response = client.post("/api/quick-add/project", json=project_data)
        project = helpers.assert_response_success(create_response)
        project_id = project["id"]
        
        # Process it - schedule for week
        process_data = {
            "item_id": project_id,
            "item_type": "project",
            "action": "schedule_week",
            "field_name": "Weekly Projects"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert data["type"] == "project"
        assert data["id"] == project_id
        
        # Verify the project was updated
        verify_response = client.get(f"/api/projects/{project_id}")
        updated_project = helpers.assert_response_success(verify_response)
        assert updated_project["do_this_week"] is True
        assert updated_project["field_id"] is not None
    
    def test_process_inbox_item_delete(self, client: TestClient, test_user, helpers):
        """Test processing inbox item - delete item."""
        # First create a task
        task_data = {
            "task_name": "Task to Delete"
        }
        
        create_response = client.post("/api/quick-add/task", json=task_data)
        task = helpers.assert_response_success(create_response)
        task_id = task["id"]
        
        # Process it - delete
        process_data = {
            "item_id": task_id,
            "item_type": "task",
            "action": "delete"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert "deleted successfully" in data["message"]
        
        # Verify the task was deleted
        verify_response = client.get(f"/api/tasks/{task_id}")
        helpers.assert_response_error(verify_response, 404)
    
    def test_process_inbox_item_not_found(self, client: TestClient, test_user, helpers):
        """Test processing non-existent inbox item."""
        process_data = {
            "item_id": 999999,
            "item_type": "task",
            "action": "schedule_today"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert "error" in data
        assert "not found" in data["error"].lower()
    
    def test_process_inbox_item_invalid_type(self, client: TestClient, test_user, helpers):
        """Test processing inbox item with invalid type."""
        process_data = {
            "item_id": 1,
            "item_type": "invalid_type",
            "action": "schedule_today"
        }
        
        response = client.post("/api/quick-add/process-inbox", json=process_data)
        data = helpers.assert_response_success(response)
        
        assert "error" in data
        assert "invalid item type" in data["error"].lower()
    
    def test_quick_add_validation_errors(self, client: TestClient, test_user, helpers):
        """Test validation errors in quick add endpoints."""
        # Test missing task name
        response = client.post("/api/quick-add/task", json={})
        helpers.assert_response_error(response, 422)
        
        # Test missing project name
        response = client.post("/api/quick-add/project", json={})
        helpers.assert_response_error(response, 422)
        
        # Test missing content for capture
        response = client.post("/api/quick-add/capture", json={})
        helpers.assert_response_error(response, 422)
        
        # Test empty content for capture
        response = client.post("/api/quick-add/capture", json={"content": ""})
        helpers.assert_response_error(response, 422)
    
    def test_gtd_inbox_workflow(self, client: TestClient, test_user, helpers):
        """Test complete GTD inbox processing workflow."""
        # 1. Capture something
        capture_data = {
            "content": "Research new productivity tools and write a comprehensive comparison report",
            "auto_categorize": True
        }
        
        capture_response = client.post("/api/quick-add/capture", json=capture_data)
        captured_item = helpers.assert_response_success(capture_response)
        
        # Should be categorized as project due to length and complexity
        item_id = captured_item["id"]
        item_type = captured_item["type"]
        
        # 2. Process the captured item
        process_data = {
            "item_id": item_id,
            "item_type": item_type,
            "action": "schedule_week" if item_type == "project" else "schedule_today",
            "field_name": "Research"
        }
        
        if item_type == "task":
            process_data["priority"] = 2
        
        process_response = client.post("/api/quick-add/process-inbox", json=process_data)
        processed_item = helpers.assert_response_success(process_response)
        
        assert processed_item["type"] == item_type
        assert processed_item["id"] == item_id
        
        # 3. Verify the item was properly processed
        if item_type == "project":
            verify_response = client.get(f"/api/projects/{item_id}")
            updated_item = helpers.assert_response_success(verify_response)
            assert updated_item["do_this_week"] is True
        else:
            verify_response = client.get(f"/api/tasks/{item_id}")
            updated_item = helpers.assert_response_success(verify_response)
            assert updated_item["do_today"] is True
            assert updated_item["priority"] == 2
        
        assert updated_item["field_id"] is not None  # Should have been assigned to "Research" field