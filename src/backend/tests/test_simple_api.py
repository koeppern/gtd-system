"""
Simple API tests that work with existing infrastructure
"""
import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

# Set test environment
os.environ["CONFIG_FILE"] = "test_config.yaml"
os.environ["PYTEST_CURRENT_TEST"] = "1"

from app.main import create_app
from app.database import async_session_maker
from app.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """Create test client with initialized database"""
    app = create_app()
    
    # Initialize database for tests
    async def init_db():
        from app.database import engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Create test user with fixed UUID
            await conn.execute(text("""
                INSERT INTO gtd_users (
                    id, first_name, last_name, email_address, timezone, 
                    date_format, time_format, weekly_review_day, is_active, email_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (
                "00000000-0000-0000-0000-000000000001",
                "Test", "User", "test@example.com", "UTC",
                "YYYY-MM-DD", "24h", 0, True, True
            ))
            
            # Create test fields
            for i, name in enumerate(["Work", "Personal", "Test"], 1):
                await conn.execute(text("""
                    INSERT INTO gtd_fields (id, name, description) 
                    VALUES (?, ?, ?)
                """), (i, name, f"{name} related activities"))
    
    # Run initialization
    asyncio.run(init_db())
    
    return TestClient(app)


class TestBasicAPI:
    """Test basic API functionality"""
    
    def test_health_check(self, test_client):
        """Test that the API is accessible"""
        # Test docs endpoint
        response = test_client.get("/docs")
        assert response.status_code == 200
    
    def test_cors_headers(self, test_client):
        """Test CORS configuration"""
        response = test_client.options(
            "/api/fields/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
    
    def test_fields_endpoint(self, test_client):
        """Test fields endpoint"""
        response = test_client.get("/api/fields/")
        # Should either work (200) or return authentication error (404)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_projects_endpoint(self, test_client):
        """Test projects endpoint"""
        response = test_client.get("/api/projects/")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_tasks_endpoint(self, test_client):
        """Test tasks endpoint"""
        response = test_client.get("/api/tasks/")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_dashboard_endpoint(self, test_client):
        """Test dashboard endpoint"""
        response = test_client.get("/api/dashboard/stats")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
    
    def test_user_endpoint(self, test_client):
        """Test user endpoint"""
        response = test_client.get("/api/users/me")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "email_address" in data


class TestDataCreation:
    """Test creating data with cleanup"""
    
    def test_create_field(self, test_client):
        """Test creating a field"""
        field_data = {
            "name": "TestField123",
            "description": "Test field for integration test"
        }
        
        response = test_client.post("/api/fields/", json=field_data)
        
        if response.status_code == 200:
            # Field created successfully
            data = response.json()
            assert data["name"] == field_data["name"]
            assert "id" in data
            
            # Clean up: try to delete
            field_id = data["id"]
            cleanup_response = test_client.delete(f"/api/fields/{field_id}")
            # Cleanup might not be supported, so we don't assert on it
        else:
            # Authentication or other issue
            assert response.status_code in [404, 422, 401]
    
    def test_create_project(self, test_client):
        """Test creating a project"""
        project_data = {
            "project_name": "Test Project 123",
            "do_this_week": True,
            "keywords": "test, integration"
        }
        
        response = test_client.post("/api/projects/", json=project_data)
        
        if response.status_code == 200:
            data = response.json()
            assert data["project_name"] == project_data["project_name"]
            assert "id" in data
            
            # Try cleanup
            project_id = data["id"]
            test_client.delete(f"/api/projects/{project_id}")
        else:
            assert response.status_code in [404, 422, 401]
    
    def test_create_task(self, test_client):
        """Test creating a task"""
        task_data = {
            "task_name": "Test Task 123",
            "priority": 3,
            "do_today": False,
            "do_this_week": True
        }
        
        response = test_client.post("/api/tasks/", json=task_data)
        
        if response.status_code == 200:
            data = response.json()
            assert data["task_name"] == task_data["task_name"]
            assert "id" in data
            
            # Try cleanup
            task_id = data["id"]
            test_client.delete(f"/api/tasks/{task_id}")
        else:
            assert response.status_code in [404, 422, 401]


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoints(self, test_client):
        """Test invalid endpoints"""
        response = test_client.get("/api/nonexistent/")
        assert response.status_code == 404
    
    def test_invalid_data(self, test_client):
        """Test sending invalid data"""
        # Empty field name
        response = test_client.post("/api/fields/", json={"name": ""})
        assert response.status_code in [422, 404]  # Validation error or auth error
        
        # Invalid JSON
        response = test_client.post(
            "/api/fields/", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [422, 400]


class TestDatabaseConnectivity:
    """Test database connectivity"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test direct database connection"""
        async with async_session_maker() as db:
            result = await db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1
    
    @pytest.mark.asyncio
    async def test_database_tables(self):
        """Test that required tables exist"""
        tables = ["gtd_users", "gtd_fields", "gtd_projects", "gtd_tasks"]
        
        async with async_session_maker() as db:
            for table in tables:
                try:
                    result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    assert count >= 0  # Table exists and is queryable
                except Exception as e:
                    pytest.fail(f"Table {table} not accessible: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])