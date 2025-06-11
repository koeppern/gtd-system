"""
Test User API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestUserAPI:
    """Test User API endpoints."""
    
    def test_get_current_user_info(self, client: TestClient, test_user, helpers):
        """Test getting current user information."""
        response = client.get("/api/users/me")
        data = helpers.assert_response_success(response)
        helpers.assert_user_data(data)
        assert data["email_address"] == "test@example.com"
    
    def test_get_current_user_stats(self, client: TestClient, test_user, helpers):
        """Test getting current user statistics."""
        response = client.get("/api/users/me/stats")
        data = helpers.assert_response_success(response)
        
        # Check required stat fields
        required_fields = [
            "total_projects", "active_projects", "completed_projects",
            "total_tasks", "pending_tasks", "completed_tasks",
            "tasks_today", "tasks_this_week"
        ]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], int)
    
    def test_update_current_user(self, client: TestClient, test_user, helpers):
        """Test updating current user information."""
        update_data = {
            "name": "Updated Test User",
            "is_active": True
        }
        
        response = client.put("/api/users/me", json=update_data)
        data = helpers.assert_response_success(response)
        helpers.assert_user_data(data, expected_name="Updated Test User")
    
    def test_update_user_email(self, client: TestClient, test_user, helpers):
        """Test updating user email address."""
        response = client.put(
            "/api/users/me/email",
            params={"new_email": "newemail@example.com"}
        )
        data = helpers.assert_response_success(response)
        assert "message" in data
        assert "updated successfully" in data["message"]
    
    def test_update_user_email_duplicate(self, client: TestClient, test_user, helpers):
        """Test updating user email to existing email."""
        # Try to update to same email
        response = client.put(
            "/api/users/me/email",
            params={"new_email": "test@example.com"}
        )
        data = helpers.assert_response_error(response, 400)
        assert "already in use" in data["detail"]
    
    def test_verify_user_email(self, client: TestClient, test_user, helpers):
        """Test verifying user email."""
        response = client.post("/api/users/me/verify-email")
        data = helpers.assert_response_success(response)
        assert "verified successfully" in data["message"]
    
    def test_activate_user_account(self, client: TestClient, test_user, helpers):
        """Test activating user account."""
        response = client.post("/api/users/me/activate")
        data = helpers.assert_response_success(response)
        assert "activated successfully" in data["message"]
    
    def test_deactivate_user_account(self, client: TestClient, test_user, helpers):
        """Test deactivating user account."""
        response = client.post("/api/users/me/deactivate")
        data = helpers.assert_response_success(response)
        assert "deactivated successfully" in data["message"]
    
    def test_create_user(self, client: TestClient, helpers):
        """Test creating a new user (admin endpoint)."""
        user_data = {
            "name": "New User",
            "email_address": "newuser@example.com",
            "is_active": True,
            "email_verified": False
        }
        
        response = client.post("/api/users/", json=user_data)
        data = helpers.assert_response_success(response, 200)
        helpers.assert_user_data(data, expected_name="New User")
        assert data["email_address"] == "newuser@example.com"
    
    def test_create_user_duplicate_email(self, client: TestClient, test_user, helpers):
        """Test creating user with duplicate email."""
        user_data = {
            "name": "Duplicate User",
            "email_address": "test@example.com",  # Same as test_user
            "is_active": True,
            "email_verified": False
        }
        
        response = client.post("/api/users/", json=user_data)
        data = helpers.assert_response_error(response, 400)
        assert "already exists" in data["detail"]
    
    def test_get_user_by_id(self, client: TestClient, test_user, helpers):
        """Test getting user by ID (admin endpoint)."""
        response = client.get(f"/api/users/{test_user.id}")
        data = helpers.assert_response_success(response)
        helpers.assert_user_data(data)
        assert data["id"] == str(test_user.id)
    
    def test_get_user_by_id_not_found(self, client: TestClient, helpers):
        """Test getting non-existent user by ID."""
        fake_uuid = "00000000-1111-2222-3333-444444444444"
        response = client.get(f"/api/users/{fake_uuid}")
        helpers.assert_response_error(response, 404)
    
    def test_get_user_stats_by_id(self, client: TestClient, test_user, helpers):
        """Test getting user statistics by ID (admin endpoint)."""
        response = client.get(f"/api/users/{test_user.id}/stats")
        data = helpers.assert_response_success(response)
        
        # Check required stat fields
        required_fields = [
            "total_projects", "active_projects", "completed_projects",
            "total_tasks", "pending_tasks", "completed_tasks",
            "tasks_today", "tasks_this_week"
        ]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], int)
    
    def test_get_user_stats_by_id_not_found(self, client: TestClient, helpers):
        """Test getting stats for non-existent user."""
        fake_uuid = "00000000-1111-2222-3333-444444444444"
        response = client.get(f"/api/users/{fake_uuid}/stats")
        helpers.assert_response_error(response, 404)
    
    def test_user_api_validation_errors(self, client: TestClient, helpers):
        """Test API validation errors."""
        # Test invalid email format
        user_data = {
            "name": "Test User",
            "email_address": "invalid-email",  # Invalid format
            "is_active": True
        }
        
        response = client.post("/api/users/", json=user_data)
        helpers.assert_response_error(response, 422)
        
        # Test missing required fields
        response = client.post("/api/users/", json={})
        helpers.assert_response_error(response, 422)
    
    def test_user_api_with_projects_and_tasks(self, client: TestClient, multiple_projects, multiple_tasks, completed_items, helpers):
        """Test user stats with real data."""
        response = client.get("/api/users/me/stats")
        data = helpers.assert_response_success(response)
        
        # Should have projects and tasks
        assert data["total_projects"] > 0
        assert data["total_tasks"] > 0
        assert data["completed_projects"] > 0
        assert data["completed_tasks"] > 0
        
        # Active counts should be total - completed
        assert data["active_projects"] == data["total_projects"] - data["completed_projects"]
        assert data["pending_tasks"] == data["total_tasks"] - data["completed_tasks"]