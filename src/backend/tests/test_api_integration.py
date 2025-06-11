"""
Comprehensive integration tests with FastAPI TestClient
Tests all API endpoints with proper cleanup
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from uuid import uuid4, UUID
import json
import os

# Set test environment before imports
os.environ["CONFIG_FILE"] = "test_config.yaml"
os.environ["PYTEST_CURRENT_TEST"] = "1"

from app.main import create_app
from app.database import async_session_maker
from app.config import get_settings


# Use fixtures from conftest.py


class TestCORSConfiguration:
    """Test CORS configuration"""
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight request"""
        response = client.options(
            "/api/fields/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"


class TestFieldsAPI:
    """Test Fields API endpoints"""
    
    def test_get_fields(self, client):
        """Test GET /api/fields/"""
        response = client.get("/api/fields/")
        assert response.status_code in [200, 404]  # 404 if no test user configured
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_field(self, client):
        """Test POST /api/fields/"""
        field_data = {
            "name": f"TestField_{uuid4().hex[:8]}",
            "description": "Test field created by integration test"
        }
        
        response = client.post("/api/fields/", json=field_data)
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == field_data["name"]
            assert data["description"] == field_data["description"]
            assert "id" in data
            
            # Cleanup: Delete created field
            client.delete(f"/api/fields/{data['id']}")


class TestProjectsAPI:
    """Test Projects API endpoints"""
    
    def test_get_projects(self, client):
        """Test GET /api/projects/"""
        response = client.get("/api/projects/")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_weekly_projects(self, client):
        """Test GET /api/projects/weekly"""
        response = client.get("/api/projects/weekly")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_project(self, client):
        """Test POST /api/projects/"""
        project_data = {
            "project_name": f"Test Project {uuid4().hex[:8]}",
            "do_this_week": True,
            "keywords": "test, integration",
            "gtd_processes": "test process"
        }
        
        response = client.post("/api/projects/", json=project_data)
        if response.status_code == 200:
            data = response.json()
            assert data["project_name"] == project_data["project_name"]
            assert data["do_this_week"] == project_data["do_this_week"]
            assert "id" in data
            
            # Cleanup: Delete created project
            client.delete(f"/api/projects/{data['id']}")


class TestTasksAPI:
    """Test Tasks API endpoints"""
    
    def test_get_tasks(self, client):
        """Test GET /api/tasks/"""
        response = client.get("/api/tasks/")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_tasks_with_filters(self, client):
        """Test GET /api/tasks/ with filters"""
        params = {
            "limit": 5,
            "do_today": True,
            "do_this_week": False,
            "is_done": False
        }
        
        response = client.get("/api/tasks/", params=params)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 5
    
    def test_get_today_tasks(self, client):
        """Test GET /api/tasks/today"""
        response = client.get("/api/tasks/today")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_task(self, client):
        """Test POST /api/tasks/"""
        task_data = {
            "task_name": f"Test Task {uuid4().hex[:8]}",
            "do_today": True,
            "do_this_week": True,
            "priority": 3,
            "is_reading": False,
            "wait_for": False,
            "postponed": False,
            "reviewed": False
        }
        
        response = client.post("/api/tasks/", json=task_data)
        if response.status_code == 200:
            data = response.json()
            assert data["task_name"] == task_data["task_name"]
            assert data["do_today"] == task_data["do_today"]
            assert data["priority"] == task_data["priority"]
            assert "id" in data
            
            # Cleanup: Delete created task
            client.delete(f"/api/tasks/{data['id']}")


class TestDashboardAPI:
    """Test Dashboard API endpoints"""
    
    def test_get_dashboard_stats(self, client):
        """Test GET /api/dashboard/stats"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            required_keys = [
                "total_tasks", "completed_tasks", "pending_tasks",
                "total_projects", "active_projects", "completed_projects"
            ]
            for key in required_keys:
                assert key in data
                assert isinstance(data[key], int)


class TestSearchAPI:
    """Test Search API endpoints"""
    
    def test_search_tasks(self, client):
        """Test GET /api/search/tasks"""
        response = client.get("/api/search/tasks", params={"q": "test"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_search_projects(self, client):
        """Test GET /api/search/projects"""
        response = client.get("/api/search/projects", params={"q": "test"})
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestQuickAddAPI:
    """Test Quick Add API endpoints"""
    
    def test_parse_text(self, client):
        """Test POST /api/quick-add/parse"""
        text_data = {
            "text": "Call John about the meeting #work @today"
        }
        
        response = client.post("/api/quick-add/parse", json=text_data)
        if response.status_code == 200:
            data = response.json()
            assert "suggested_task" in data
            assert "suggested_project" in data
            assert "suggested_field" in data


class TestUserAPI:
    """Test User API endpoints"""
    
    def test_get_current_user(self, client):
        """Test GET /api/users/me"""
        response = client.get("/api/users/me")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "email_address" in data
            assert "first_name" in data
    
    def test_get_user_stats(self, client):
        """Test GET /api/users/me/stats"""
        response = client.get("/api/users/me/stats")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_tasks" in data
            assert "total_projects" in data


class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection"""
        async with async_session_maker() as db:
            result = await db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            assert row[0] == 1
    
    @pytest.mark.asyncio
    async def test_database_tables_exist(self):
        """Test that all required tables exist"""
        required_tables = ["gtd_users", "gtd_fields", "gtd_projects", "gtd_tasks"]
        
        async with async_session_maker() as db:
            for table in required_tables:
                result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                assert count >= 0  # Table exists and is queryable


class TestSupabaseConnection:
    """Test Supabase connection if configured"""
    
    def test_supabase_configuration(self):
        """Test if Supabase is properly configured"""
        settings = get_settings()
        database_url = settings.database_url_asyncpg
        
        # Check if using Supabase (PostgreSQL) or SQLite
        if "postgresql" in database_url:
            # Supabase/PostgreSQL configuration
            assert "supabase.co" in database_url or "localhost" in database_url
        else:
            # SQLite configuration
            assert "sqlite" in database_url
    
    @pytest.mark.asyncio
    async def test_database_performance(self):
        """Test basic database performance"""
        import time
        
        start_time = time.time()
        async with async_session_maker() as db:
            await db.execute(text("SELECT COUNT(*) FROM gtd_users"))
        end_time = time.time()
        
        # Query should complete within reasonable time
        assert (end_time - start_time) < 1.0  # Less than 1 second


class TestDataConsistency:
    """Test data consistency and relationships"""
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self):
        """Test that foreign key relationships work properly"""
        async with async_session_maker() as db:
            # Test user-project relationship
            result = await db.execute(text("""
                SELECT COUNT(*) FROM gtd_projects p 
                LEFT JOIN gtd_users u ON p.user_id = u.id 
                WHERE u.id IS NULL
            """))
            orphaned_projects = result.fetchone()[0]
            assert orphaned_projects == 0
            
            # Test user-task relationship
            result = await db.execute(text("""
                SELECT COUNT(*) FROM gtd_tasks t 
                LEFT JOIN gtd_users u ON t.user_id = u.id 
                WHERE u.id IS NULL
            """))
            orphaned_tasks = result.fetchone()[0]
            assert orphaned_tasks == 0


def test_health_check(client):
    """Test application health"""
    # Test if the application starts properly
    response = client.get("/docs")
    assert response.status_code in [200, 404]  # 404 if docs disabled in production


if __name__ == "__main__":
    pytest.main([__file__, "-v"])