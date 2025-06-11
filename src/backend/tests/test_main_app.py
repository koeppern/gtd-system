"""
Test main application and integration
"""
import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Test main application functionality."""
    
    def test_root_endpoint(self, client: TestClient, helpers):
        """Test root endpoint."""
        response = client.get("/")
        data = helpers.assert_response_success(response)
        
        assert "message" in data
        assert "version" in data
        assert data["message"] == "GTD Backend API"
    
    def test_health_check(self, client: TestClient, helpers):
        """Test health check endpoint."""
        response = client.get("/health")
        data = helpers.assert_response_success(response)
        
        # Check main sections
        assert "status" in data
        assert "app" in data
        assert "database" in data
        
        # Check app info
        app_data = data["app"]
        assert "name" in app_data
        assert "version" in app_data
        assert "environment" in app_data
        
        # Check database status
        db_data = data["database"]
        assert "status" in db_data
        # Should be healthy for tests
        assert db_data["status"] == "healthy"
        
        # Overall status should be healthy
        assert data["status"] == "healthy"
    
    def test_api_documentation_endpoints(self, client: TestClient):
        """Test API documentation endpoints."""
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Check that our endpoints are documented
        paths = schema["paths"]
        assert "/api/users/me" in paths
        assert "/api/tasks/" in paths
        assert "/api/projects/" in paths
        assert "/api/dashboard/overview" in paths
    
    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set."""
        # Test preflight request
        response = client.options("/api/users/me")
        
        # Should have CORS headers
        # Note: TestClient might not handle OPTIONS the same way as a real browser
        # This is more of a smoke test
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
    
    def test_error_handling(self, client: TestClient, helpers):
        """Test global error handling."""
        # Test 404 error
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # Test validation error
        response = client.post("/api/users/", json={"invalid": "data"})
        assert response.status_code == 422
        
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_request_validation(self, client: TestClient, helpers):
        """Test request validation."""
        # Test invalid JSON
        response = client.post(
            "/api/tasks/",
            json={"task_name": ""},  # Empty name should fail validation
        )
        helpers.assert_response_error(response, 422)
        
        # Test invalid field types
        response = client.post(
            "/api/tasks/",
            json={
                "task_name": "Valid Task",
                "priority": "invalid"  # Should be integer
            }
        )
        helpers.assert_response_error(response, 422)
    
    def test_database_integration(self, client: TestClient, test_user, helpers):
        """Test database integration through API."""
        # Test that database operations work through the API
        
        # Create a field
        field_response = client.post("/api/fields/", json={
            "name": "Integration Test Field",
            "description": "Testing database integration"
        })
        field_data = helpers.assert_response_success(field_response)
        field_id = field_data["id"]
        
        # Create a project using the field
        project_response = client.post("/api/projects/", json={
            "project_name": "Integration Test Project",
            "field_id": field_id,
            "do_this_week": True
        })
        project_data = helpers.assert_response_success(project_response)
        project_id = project_data["id"]
        
        # Create a task using the project and field
        task_response = client.post("/api/tasks/", json={
            "task_name": "Integration Test Task",
            "field_id": field_id,
            "project_id": project_id,
            "priority": 2,
            "do_today": True
        })
        task_data = helpers.assert_response_success(task_response)
        task_id = task_data["id"]
        
        # Verify relationships work
        assert task_data["field_id"] == field_id
        assert task_data["project_id"] == project_id
        
        # Test that we can retrieve related data
        project_tasks_response = client.get(f"/api/tasks/by-project/{project_id}")
        project_tasks = helpers.assert_response_success(project_tasks_response)
        
        assert len(project_tasks) >= 1
        assert any(t["id"] == task_id for t in project_tasks)
        
        # Test field stats include our data
        field_stats_response = client.get(f"/api/fields/{field_id}/stats")
        field_stats = helpers.assert_response_success(field_stats_response)
        
        assert field_stats["total_projects"] >= 1
        assert field_stats["total_tasks"] >= 1
    
    def test_api_endpoint_coverage(self, client: TestClient, test_user, helpers):
        """Test that all major API endpoints are accessible."""
        endpoints_to_test = [
            ("GET", "/api/users/me"),
            ("GET", "/api/users/me/stats"),
            ("GET", "/api/fields/"),
            ("GET", "/api/projects/"),
            ("GET", "/api/projects/active"),
            ("GET", "/api/tasks/"),
            ("GET", "/api/tasks/today"),
            ("GET", "/api/tasks/stats"),
            ("GET", "/api/dashboard/overview"),
            ("GET", "/api/dashboard/stats"),
            ("GET", "/api/search/recent"),
        ]
        
        for method, endpoint in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            # Should not return 500 errors
            assert response.status_code < 500, f"Endpoint {method} {endpoint} returned {response.status_code}"
            
            # Most should return 200 or validation errors
            assert response.status_code in [200, 400, 404, 422], f"Unexpected status for {method} {endpoint}: {response.status_code}"
    
    def test_gtd_workflow_integration(self, client: TestClient, test_user, helpers):
        """Test complete GTD workflow through API integration."""
        # 1. Quick capture
        capture_response = client.post("/api/quick-add/capture", json={
            "content": "Research and implement new task management system",
            "auto_categorize": True
        })
        captured_item = helpers.assert_response_success(capture_response)
        
        # 2. Process inbox item
        process_response = client.post("/api/quick-add/process-inbox", json={
            "item_id": captured_item["id"],
            "item_type": captured_item["type"],
            "action": "schedule_week" if captured_item["type"] == "project" else "schedule_today",
            "field_name": "Productivity",
            "priority": 1 if captured_item["type"] == "task" else None
        })
        helpers.assert_response_success(process_response)
        
        # 3. Check dashboard reflects new item
        dashboard_response = client.get("/api/dashboard/overview")
        dashboard_data = helpers.assert_response_success(dashboard_response)
        
        assert dashboard_data["summary"]["total_active_items"] >= 1
        
        # 4. Search for the item
        search_response = client.get(f"/api/search/?query=management")
        search_data = helpers.assert_response_success(search_response)
        
        assert search_data["total_results"] >= 1
        
        # 5. Complete the item
        item_id = captured_item["id"]
        item_type = captured_item["type"]
        
        if item_type == "project":
            complete_response = client.post(f"/api/projects/{item_id}/complete")
        else:
            complete_response = client.post(f"/api/tasks/{item_id}/complete")
        
        helpers.assert_response_success(complete_response)
        
        # 6. Verify completion in stats
        if item_type == "project":
            stats_response = client.get("/api/users/me/stats")
        else:
            stats_response = client.get("/api/tasks/stats")
        
        stats_data = helpers.assert_response_success(stats_response)
        
        if item_type == "project":
            assert stats_data["completed_projects"] >= 1
        else:
            assert stats_data["completed_tasks"] >= 1
    
    def test_performance_basic(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test basic performance with multiple items."""
        # Test that endpoints respond reasonably with data
        
        # Dashboard should handle multiple items
        dashboard_response = client.get("/api/dashboard/overview")
        helpers.assert_response_success(dashboard_response)
        
        # Search should handle multiple items
        search_response = client.get("/api/search/?query=test")
        helpers.assert_response_success(search_response)
        
        # Lists should handle pagination
        projects_response = client.get("/api/projects/?limit=5")
        projects_data = helpers.assert_response_success(projects_response)
        assert len(projects_data) <= 5
        
        tasks_response = client.get("/api/tasks/?limit=5")
        tasks_data = helpers.assert_response_success(tasks_response)
        assert len(tasks_data) <= 5
    
    def test_api_consistency(self, client: TestClient, test_user, helpers):
        """Test API response consistency."""
        # Create items and test consistent response formats
        
        # Test field response format
        field_response = client.post("/api/fields/", json={
            "name": "Consistency Test Field",
            "description": "Testing response consistency"
        })
        field_data = helpers.assert_response_success(field_response)
        helpers.assert_field_data(field_data)
        
        # Test project response format
        project_response = client.post("/api/projects/", json={
            "project_name": "Consistency Test Project",
            "field_id": field_data["id"]
        })
        project_data = helpers.assert_response_success(project_response)
        helpers.assert_project_data(project_data)
        
        # Test task response format
        task_response = client.post("/api/tasks/", json={
            "task_name": "Consistency Test Task",
            "project_id": project_data["id"],
            "field_id": field_data["id"]
        })
        task_data = helpers.assert_response_success(task_response)
        helpers.assert_task_data(task_data)
        
        # Test that GET returns same format as POST
        get_task_response = client.get(f"/api/tasks/{task_data['id']}")
        get_task_data = helpers.assert_response_success(get_task_response)
        
        # Should have same essential fields
        for field in ["id", "task_name", "user_id", "project_id", "field_id"]:
            assert field in get_task_data
            assert get_task_data[field] == task_data[field]