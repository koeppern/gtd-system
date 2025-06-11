"""
Integration tests with test data using existing fixtures
"""
import pytest
import os

# Set test environment
os.environ["CONFIG_FILE"] = "test_config.yaml"
os.environ["PYTEST_CURRENT_TEST"] = "1"


class TestAPIWithTestData:
    """Test API endpoints with pre-created test data"""
    
    @pytest.mark.asyncio
    async def test_fields_api(self, client, multiple_fields):
        """Test fields API with test data"""
        # Test GET /api/fields/
        response = client.get("/api/fields/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(multiple_fields)
        
        # Test that we can find our test fields
        field_names = [field.name for field in multiple_fields]
        response_names = [item["name"] for item in data]
        for name in field_names:
            assert name in response_names
    
    @pytest.mark.asyncio 
    async def test_projects_api(self, client, multiple_projects):
        """Test projects API with test data"""
        # Test GET /api/projects/
        response = client.get("/api/projects/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(multiple_projects)
        
        # Test GET /api/projects/weekly
        response = client.get("/api/projects/weekly")
        assert response.status_code == 200
        weekly_data = response.json()
        assert isinstance(weekly_data, list)
    
    @pytest.mark.asyncio
    async def test_tasks_api(self, client, multiple_tasks):
        """Test tasks API with test data"""
        # Test GET /api/tasks/
        response = client.get("/api/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(multiple_tasks)
        
        # Test GET /api/tasks/today
        response = client.get("/api/tasks/today")
        assert response.status_code == 200
        today_data = response.json()
        assert isinstance(today_data, list)
        
        # Test filtering
        response = client.get("/api/tasks/", params={"do_today": True})
        assert response.status_code == 200
        filtered_data = response.json()
        assert isinstance(filtered_data, list)
    
    @pytest.mark.asyncio
    async def test_dashboard_api(self, client, multiple_projects, multiple_tasks):
        """Test dashboard API with test data"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        required_fields = [
            "total_tasks", "completed_tasks", "pending_tasks",
            "total_projects", "active_projects", "completed_projects"
        ]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], int)
            assert data[field] >= 0
    
    @pytest.mark.asyncio
    async def test_search_api(self, client, multiple_projects, multiple_tasks):
        """Test search API with test data"""
        # Search for tasks
        response = client.get("/api/search/tasks", params={"q": "test"})
        assert response.status_code == 200
        task_results = response.json()
        assert isinstance(task_results, list)
        
        # Search for projects
        response = client.get("/api/search/projects", params={"q": "Development"})
        assert response.status_code == 200
        project_results = response.json()
        assert isinstance(project_results, list)
    
    @pytest.mark.asyncio
    async def test_user_api(self, client, test_user):
        """Test user API with test data"""
        response = client.get("/api/users/me")
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "email_address" in data
        assert data["email_address"] == test_user.email_address
        
        # Test user stats
        response = client.get("/api/users/me/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "total_tasks" in stats
        assert "total_projects" in stats


class TestCRUDOperations:
    """Test CRUD operations with proper cleanup"""
    
    @pytest.mark.asyncio
    async def test_create_and_delete_field(self, client):
        """Test creating and deleting a field"""
        # Create field
        field_data = {
            "name": f"TestField_{pytest.current_test_id}",
            "description": "Test field for CRUD test"
        }
        
        response = client.post("/api/fields/", json=field_data)
        assert response.status_code == 200
        created_field = response.json()
        assert created_field["name"] == field_data["name"]
        field_id = created_field["id"]
        
        # Verify field exists
        response = client.get(f"/api/fields/{field_id}")
        assert response.status_code == 200
        
        # Delete field
        response = client.delete(f"/api/fields/{field_id}")
        assert response.status_code == 200
        
        # Verify field is deleted
        response = client.get(f"/api/fields/{field_id}")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_and_delete_project(self, client, test_field):
        """Test creating and deleting a project"""
        # Create project
        project_data = {
            "project_name": f"TestProject_{pytest.current_test_id}",
            "field_id": test_field.id,
            "do_this_week": True,
            "keywords": "test, crud"
        }
        
        response = client.post("/api/projects/", json=project_data)
        assert response.status_code == 200
        created_project = response.json()
        assert created_project["project_name"] == project_data["project_name"]
        project_id = created_project["id"]
        
        # Delete project
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_create_and_delete_task(self, client, test_field, test_project):
        """Test creating and deleting a task"""
        # Create task
        task_data = {
            "task_name": f"TestTask_{pytest.current_test_id}",
            "field_id": test_field.id,
            "project_id": test_project.id,
            "priority": 3,
            "do_today": True,
            "do_this_week": True
        }
        
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200
        created_task = response.json()
        assert created_task["task_name"] == task_data["task_name"]
        task_id = created_task["id"]
        
        # Delete task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200


class TestDataValidation:
    """Test data validation and error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_field_creation(self, client):
        """Test creating field with invalid data"""
        # Missing required field
        response = client.post("/api/fields/", json={"description": "Missing name"})
        assert response.status_code == 422
        
        # Empty name
        response = client.post("/api/fields/", json={"name": "", "description": "Empty name"})
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_task_creation(self, client):
        """Test creating task with invalid data"""
        # Missing required field
        response = client.post("/api/tasks/", json={"priority": 1})
        assert response.status_code == 422
        
        # Invalid priority
        response = client.post("/api/tasks/", json={
            "task_name": "Test",
            "priority": 10  # Should be 1-5
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_nonexistent_resource_access(self, client):
        """Test accessing non-existent resources"""
        # Non-existent field
        response = client.get("/api/fields/99999")
        assert response.status_code == 404
        
        # Non-existent project
        response = client.get("/api/projects/99999") 
        assert response.status_code == 404
        
        # Non-existent task
        response = client.get("/api/tasks/99999")
        assert response.status_code == 404


@pytest.fixture(autouse=True)
def add_test_id(request):
    """Add unique test ID to pytest for cleanup"""
    import uuid
    pytest.current_test_id = str(uuid.uuid4())[:8]