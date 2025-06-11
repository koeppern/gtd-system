"""
Test Project API endpoints with GTD workflow
"""
import pytest
from fastapi.testclient import TestClient


class TestProjectAPI:
    """Test Project API endpoints."""
    
    def test_get_projects(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test getting all projects."""
        response = client.get("/api/projects/")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) >= len(multiple_projects)
        
        for project_data in data:
            helpers.assert_project_data(project_data)
    
    def test_get_projects_with_filters(self, client: TestClient, test_user, multiple_projects, multiple_fields, helpers):
        """Test getting projects with various filters."""
        # Test field filter
        field_id = multiple_fields[0].id
        response = client.get(f"/api/projects/?field_id={field_id}")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for project_data in data:
            assert project_data["field_id"] == field_id
        
        # Test weekly projects filter
        response = client.get("/api/projects/?do_this_week=true")
        data = helpers.assert_response_success(response)
        
        for project_data in data:
            assert project_data["do_this_week"] is True
        
        # Test search filter
        response = client.get("/api/projects/?search=Backend")
        data = helpers.assert_response_success(response)
        
        assert len(data) >= 1  # Should find "Backend Development"
    
    def test_get_active_projects(self, client: TestClient, test_user, multiple_projects, completed_items, helpers):
        """Test getting active projects only."""
        response = client.get("/api/projects/active")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for project_data in data:
            helpers.assert_project_data(project_data)
            assert project_data["done_at"] is None  # Should be incomplete
    
    def test_get_weekly_projects(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test getting weekly projects."""
        response = client.get("/api/projects/weekly")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for project_data in data:
            helpers.assert_project_data(project_data)
            assert project_data["do_this_week"] is True
    
    def test_get_projects_by_field(self, client: TestClient, test_user, multiple_projects, multiple_fields, helpers):
        """Test getting projects by field."""
        field_id = multiple_fields[0].id
        response = client.get(f"/api/projects/by-field/{field_id}")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for project_data in data:
            helpers.assert_project_data(project_data)
            assert project_data["field_id"] == field_id
    
    def test_search_projects(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test searching projects."""
        response = client.get("/api/projects/search?query=Development")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        # Should find projects with "Development" in name or keywords
        found_relevant = any("development" in project["project_name"].lower() for project in data)
        assert found_relevant
    
    def test_get_project_by_id(self, client: TestClient, test_user, test_project, helpers):
        """Test getting project by ID."""
        response = client.get(f"/api/projects/{test_project.id}")
        data = helpers.assert_response_success(response)
        helpers.assert_project_data(data, expected_name="Test Project")
        assert data["id"] == test_project.id
    
    def test_get_project_by_id_not_found(self, client: TestClient, test_user, helpers):
        """Test getting non-existent project."""
        response = client.get("/api/projects/999999")
        helpers.assert_response_error(response, 404)
    
    def test_get_project_with_stats(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting project with task statistics."""
        project_id = multiple_projects[0].id
        response = client.get(f"/api/projects/{project_id}/with-stats")
        data = helpers.assert_response_success(response)
        
        # Check project data
        helpers.assert_project_data(data)
        
        # Check stats fields
        stats_fields = [
            "task_count", "completed_tasks", "pending_tasks",
            "high_priority_tasks", "overdue_tasks", "completion_percentage"
        ]
        for field in stats_fields:
            assert field in data
            assert isinstance(data[field], (int, float))
    
    def test_create_project(self, client: TestClient, test_user, test_field, helpers):
        """Test creating a new project."""
        project_data = {
            "project_name": "New Project",
            "field_id": test_field.id,
            "keywords": "new, project, test",
            "do_this_week": True
        }
        
        response = client.post("/api/projects/", json=project_data)
        data = helpers.assert_response_success(response, 200)
        helpers.assert_project_data(data, expected_name="New Project")
        assert data["field_id"] == test_field.id
        assert data["do_this_week"] is True
    
    def test_update_project(self, client: TestClient, test_user, test_project, helpers):
        """Test updating a project."""
        update_data = {
            "project_name": "Updated Project",
            "keywords": "updated, test",
            "do_this_week": True
        }
        
        response = client.put(f"/api/projects/{test_project.id}", json=update_data)
        data = helpers.assert_response_success(response)
        helpers.assert_project_data(data, expected_name="Updated Project")
        assert data["keywords"] == "updated, test"
        assert data["do_this_week"] is True
    
    def test_update_project_not_found(self, client: TestClient, test_user, helpers):
        """Test updating non-existent project."""
        update_data = {
            "project_name": "Non-existent Project"
        }
        
        response = client.put("/api/projects/999999", json=update_data)
        helpers.assert_response_error(response, 404)
    
    def test_complete_project(self, client: TestClient, test_user, test_project, helpers):
        """Test completing a project."""
        response = client.post(f"/api/projects/{test_project.id}/complete")
        data = helpers.assert_response_success(response)
        helpers.assert_project_data(data)
        assert data["done_at"] is not None
    
    def test_complete_project_with_tasks(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test completing a project and auto-completing tasks."""
        project_id = multiple_projects[0].id
        
        response = client.post(f"/api/projects/{project_id}/complete?auto_complete_tasks=true")
        data = helpers.assert_response_success(response)
        helpers.assert_project_data(data)
        assert data["done_at"] is not None
    
    def test_complete_project_already_completed(self, client: TestClient, test_user, completed_items, helpers):
        """Test completing an already completed project."""
        project_id = completed_items["projects"][0].id
        
        response = client.post(f"/api/projects/{project_id}/complete")
        helpers.assert_response_error(response, 400)
    
    def test_reopen_project(self, client: TestClient, test_user, completed_items, helpers):
        """Test reopening a completed project."""
        project_id = completed_items["projects"][0].id
        
        response = client.post(f"/api/projects/{project_id}/reopen")
        data = helpers.assert_response_success(response)
        helpers.assert_project_data(data)
        assert data["done_at"] is None
    
    def test_reopen_project_not_completed(self, client: TestClient, test_user, test_project, helpers):
        """Test reopening a project that isn't completed."""
        response = client.post(f"/api/projects/{test_project.id}/reopen")
        helpers.assert_response_error(response, 400)
    
    def test_delete_project_soft(self, client: TestClient, test_user, test_project, helpers):
        """Test soft deleting a project."""
        response = client.delete(f"/api/projects/{test_project.id}")
        data = helpers.assert_response_success(response)
        assert "soft deleted" in data["message"]
    
    def test_delete_project_hard(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test hard deleting a project."""
        project_id = multiple_projects[-1].id  # Use last project to avoid affecting other tests
        
        response = client.delete(f"/api/projects/{project_id}?hard_delete=true")
        data = helpers.assert_response_success(response)
        assert "permanently deleted" in data["message"]
    
    def test_delete_project_not_found(self, client: TestClient, test_user, helpers):
        """Test deleting non-existent project."""
        response = client.delete("/api/projects/999999")
        helpers.assert_response_error(response, 404)
    
    def test_restore_project(self, client: TestClient, test_user, test_field, helpers):
        """Test restoring a soft-deleted project."""
        # First create and soft delete a project
        project_data = {
            "project_name": "Project to Restore",
            "field_id": test_field.id
        }
        
        create_response = client.post("/api/projects/", json=project_data)
        project_data = helpers.assert_response_success(create_response)
        project_id = project_data["id"]
        
        # Soft delete it
        delete_response = client.delete(f"/api/projects/{project_id}")
        helpers.assert_response_success(delete_response)
        
        # Restore it
        restore_response = client.post(f"/api/projects/{project_id}/restore")
        data = helpers.assert_response_success(restore_response)
        helpers.assert_project_data(data, expected_name="Project to Restore")
    
    def test_project_gtd_workflow(self, client: TestClient, test_user, test_field, helpers):
        """Test complete GTD workflow for projects."""
        # 1. Create project
        project_data = {
            "project_name": "GTD Workflow Test",
            "field_id": test_field.id,
            "do_this_week": False
        }
        
        create_response = client.post("/api/projects/", json=project_data)
        project = helpers.assert_response_success(create_response)
        project_id = project["id"]
        
        # 2. Update to weekly
        update_response = client.put(
            f"/api/projects/{project_id}",
            json={"do_this_week": True}
        )
        updated_project = helpers.assert_response_success(update_response)
        assert updated_project["do_this_week"] is True
        
        # 3. Complete project
        complete_response = client.post(f"/api/projects/{project_id}/complete")
        completed_project = helpers.assert_response_success(complete_response)
        assert completed_project["done_at"] is not None
        
        # 4. Reopen project
        reopen_response = client.post(f"/api/projects/{project_id}/reopen")
        reopened_project = helpers.assert_response_success(reopen_response)
        assert reopened_project["done_at"] is None
        
        # 5. Delete project
        delete_response = client.delete(f"/api/projects/{project_id}")
        helpers.assert_response_success(delete_response)
    
    def test_project_api_validation_errors(self, client: TestClient, test_user, helpers):
        """Test API validation errors."""
        # Test missing required fields
        response = client.post("/api/projects/", json={})
        helpers.assert_response_error(response, 422)
        
        # Test invalid project name (empty string)
        project_data = {
            "project_name": "",
            "field_id": 1
        }
        response = client.post("/api/projects/", json=project_data)
        helpers.assert_response_error(response, 422)
    
    def test_project_pagination(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test project pagination."""
        # Test with limit
        response = client.get("/api/projects/?skip=0&limit=2")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) <= 2
        
        # Test with skip
        response = client.get("/api/projects/?skip=1&limit=2")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) <= 2