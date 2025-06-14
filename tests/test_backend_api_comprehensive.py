"""
Comprehensive Backend API Tests for GTD Application
Tests all API endpoints with proper mocking and coverage
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add src/backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from app.main import app
from app.database import get_db_connection

client = TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns success"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "gtd-backend"}

class TestUserSettingsAPI:
    """Test user settings endpoints with device-specific support"""
    
    @patch('app.api.users.get_db_connection')
    def test_get_user_settings_all(self, mock_db):
        """Test getting all user settings"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [{"desktop": {"sidebar_open": True}}]
        
        response = client.get("/api/users/me/settings")
        assert response.status_code == 200
        
    @patch('app.api.users.get_db_connection')
    def test_get_user_settings_device_specific(self, mock_db):
        """Test getting device-specific settings"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(True, "sidebar_open")]
        
        response = client.get("/api/users/me/settings?device=desktop")
        assert response.status_code == 200

    @patch('app.api.users.get_db_connection')
    def test_get_setting_keys(self, mock_db):
        """Test getting available setting keys"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("sidebar_open", "Whether sidebar is open", "boolean", True, "ui"),
            ("theme_mode", "Color theme", "string", "light", "ui")
        ]
        
        response = client.get("/api/users/me/settings/keys")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total_keys" in data

    @patch('app.api.users.get_db_connection')
    def test_get_specific_user_setting(self, mock_db):
        """Test getting specific setting for device"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [True]
        
        response = client.get("/api/users/me/settings/desktop/sidebar_open")
        assert response.status_code == 200
        data = response.json()
        assert data["device"] == "desktop"
        assert data["setting_key"] == "sidebar_open"

    @patch('app.api.users.get_db_connection')
    def test_update_user_setting(self, mock_db):
        """Test updating a user setting"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # Setting exists
        
        response = client.put(
            "/api/users/me/settings/desktop/sidebar_open",
            json=False
        )
        assert response.status_code == 200

    @patch('app.api.users.get_db_connection')
    def test_update_device_settings_bulk(self, mock_db):
        """Test updating multiple settings for a device"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("sidebar_open",), ("theme_mode",)]
        
        settings = {
            "sidebar_open": False,
            "theme_mode": "dark"
        }
        
        response = client.put(
            "/api/users/me/settings/desktop",
            json=settings
        )
        assert response.status_code == 200

    @patch('app.api.users.get_db_connection')
    def test_delete_user_setting(self, mock_db):
        """Test deleting (resetting) a user setting"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [{"desktop": {"sidebar_open": False}}]
        
        response = client.delete("/api/users/me/settings/desktop/sidebar_open")
        assert response.status_code == 200

    @patch('app.api.users.get_db_connection')
    def test_reset_all_settings(self, mock_db):
        """Test resetting all user settings"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]
        
        response = client.delete("/api/users/me/settings")
        assert response.status_code == 200

class TestTasksAPI:
    """Test tasks API endpoints"""
    
    @patch('app.api.tasks.get_db_connection')
    def test_get_tasks_list(self, mock_db):
        """Test getting tasks list"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Test Task", "Test Project", "Test Field", 1, False, None)
        ]
        mock_cursor.fetchone.return_value = [100]  # Total count
        
        response = client.get("/api/tasks")
        assert response.status_code == 200

    @patch('app.api.tasks.get_db_connection')
    def test_get_task_by_id(self, mock_db):
        """Test getting specific task"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Test Task", "Test Project", 1, False)
        
        response = client.get("/api/tasks/1")
        assert response.status_code == 200

    @patch('app.api.tasks.get_db_connection')
    def test_create_task(self, mock_db):
        """Test creating a new task"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "New Task", "Project", 1, False)
        
        task_data = {
            "task_name": "New Task",
            "project_id": 1,
            "field_id": 1,
            "priority": 1
        }
        
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 200

    @patch('app.api.tasks.get_db_connection')
    def test_update_task(self, mock_db):
        """Test updating a task"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Updated Task", "Project", 1, False)
        
        update_data = {"task_name": "Updated Task"}
        
        response = client.put("/api/tasks/1", json=update_data)
        assert response.status_code == 200

    @patch('app.api.tasks.get_db_connection')
    def test_delete_task(self, mock_db):
        """Test deleting a task"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        response = client.delete("/api/tasks/1")
        assert response.status_code == 200

    @patch('app.api.tasks.get_db_connection')
    def test_complete_task(self, mock_db):
        """Test completing a task"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Task", "Project", 1, True)
        
        response = client.post("/api/tasks/1/complete")
        assert response.status_code == 200

    @patch('app.api.tasks.get_db_connection')
    def test_get_today_tasks(self, mock_db):
        """Test getting today's tasks"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Today Task", "Project", "Field", 1, True, None)
        ]
        
        response = client.get("/api/tasks/today")
        assert response.status_code == 200

class TestProjectsAPI:
    """Test projects API endpoints"""
    
    @patch('app.api.projects.get_db_connection')
    def test_get_projects_list(self, mock_db):
        """Test getting projects list"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Test Project", "Test Field", False, 5)
        ]
        mock_cursor.fetchone.return_value = [50]  # Total count
        
        response = client.get("/api/projects")
        assert response.status_code == 200

    @patch('app.api.projects.get_db_connection')
    def test_get_project_by_id(self, mock_db):
        """Test getting specific project"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Test Project", "Field", False)
        
        response = client.get("/api/projects/1")
        assert response.status_code == 200

    @patch('app.api.projects.get_db_connection')
    def test_create_project(self, mock_db):
        """Test creating a new project"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "New Project", "Field", False)
        
        project_data = {
            "project_name": "New Project",
            "field_id": 1,
            "description": "Test project"
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 200

    @patch('app.api.projects.get_db_connection')
    def test_complete_project(self, mock_db):
        """Test completing a project"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Project", "Field", True)
        
        response = client.post("/api/projects/1/complete")
        assert response.status_code == 200

class TestFieldsAPI:
    """Test fields API endpoints"""
    
    @patch('app.api.fields.get_db_connection')
    def test_get_fields_list(self, mock_db):
        """Test getting fields list"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Test Field", "Description")
        ]
        
        response = client.get("/api/fields")
        assert response.status_code == 200

class TestDashboardAPI:
    """Test dashboard API endpoints"""
    
    @patch('app.api.dashboard.get_db_connection')
    def test_get_dashboard_stats(self, mock_db):
        """Test getting dashboard statistics"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock different queries for dashboard stats
        mock_cursor.fetchone.side_effect = [
            [10],   # total_tasks
            [3],    # completed_today
            [5],    # overdue_tasks
            [15],   # total_projects
            [2],    # completed_projects
        ]
        
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "completed_today" in data

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('app.api.users.get_db_connection')
    def test_database_connection_error(self, mock_db):
        """Test handling database connection errors"""
        mock_db.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/users/me/settings")
        assert response.status_code == 500

    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    @patch('app.api.users.get_db_connection')
    def test_invalid_setting_key(self, mock_db):
        """Test updating invalid setting key"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # No setting found
        
        response = client.put(
            "/api/users/me/settings/desktop/invalid_key",
            json=True
        )
        assert response.status_code == 400

    def test_invalid_device_type(self):
        """Test using invalid device type"""
        response = client.get("/api/users/me/settings/invalid_device/sidebar_open")
        assert response.status_code == 422  # Validation error

class TestDatabaseFunctions:
    """Test database utility functions"""
    
    @patch('app.database.psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}):
            result = get_db_connection()
            assert result == mock_conn

    @patch('app.database.psycopg2.connect')
    def test_get_db_connection_failure(self, mock_connect):
        """Test database connection failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}):
            with pytest.raises(Exception):
                get_db_connection()

class TestDataValidation:
    """Test data validation and sanitization"""
    
    def test_task_creation_validation(self):
        """Test task creation with invalid data"""
        invalid_task = {
            "task_name": "",  # Empty name
            "priority": 10,   # Invalid priority range
        }
        
        response = client.post("/api/tasks", json=invalid_task)
        # Should handle validation appropriately
        assert response.status_code in [400, 422]

    def test_project_creation_validation(self):
        """Test project creation with invalid data"""
        invalid_project = {
            "project_name": "",  # Empty name
            "field_id": "invalid"  # Invalid field_id type
        }
        
        response = client.post("/api/projects", json=invalid_project)
        assert response.status_code in [400, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])