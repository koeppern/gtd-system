"""
Test Field API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestFieldAPI:
    """Test Field API endpoints."""
    
    def test_get_fields(self, client: TestClient, test_user, multiple_fields, helpers):
        """Test getting all fields."""
        response = client.get("/api/fields/")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) >= len(multiple_fields)
        
        for field_data in data:
            helpers.assert_field_data(field_data)
    
    def test_get_fields_with_pagination(self, client: TestClient, test_user, multiple_fields, helpers):
        """Test getting fields with pagination."""
        # Test with limit
        response = client.get("/api/fields/?skip=0&limit=2")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) <= 2
    
    def test_get_fields_with_stats(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting fields with usage statistics."""
        response = client.get("/api/fields/with-stats")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        for field_data in data:
            # Check field data
            helpers.assert_field_data(field_data)
            
            # Check stats fields
            stats_fields = [
                "total_projects", "active_projects", "completed_projects",
                "total_tasks", "active_tasks", "completed_tasks",
                "completion_rate_projects", "completion_rate_tasks"
            ]
            for field in stats_fields:
                assert field in field_data
                assert isinstance(field_data[field], (int, float))
    
    def test_get_popular_fields(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting popular fields by usage."""
        response = client.get("/api/fields/popular?limit=3")
        data = helpers.assert_response_success(response)
        
        assert isinstance(data, list)
        assert len(data) <= 3
        
        for field_data in data:
            helpers.assert_field_data(field_data)
            # Check usage fields
            assert "project_count" in field_data
            assert "task_count" in field_data
            assert "total_usage" in field_data
    
    def test_get_field_by_id(self, client: TestClient, test_user, test_field, helpers):
        """Test getting field by ID."""
        response = client.get(f"/api/fields/{test_field.id}")
        data = helpers.assert_response_success(response)
        helpers.assert_field_data(data, expected_name="Test Field")
        assert data["id"] == test_field.id
    
    def test_get_field_by_id_not_found(self, client: TestClient, test_user, helpers):
        """Test getting non-existent field."""
        response = client.get("/api/fields/999999")
        helpers.assert_response_error(response, 404)
    
    def test_get_field_stats(self, client: TestClient, test_user, test_field, helpers):
        """Test getting field statistics."""
        response = client.get(f"/api/fields/{test_field.id}/stats")
        data = helpers.assert_response_success(response)
        
        stats_fields = [
            "total_projects", "active_projects", "completed_projects",
            "total_tasks", "active_tasks", "completed_tasks",
            "completion_rate_projects", "completion_rate_tasks"
        ]
        for field in stats_fields:
            assert field in data
            assert isinstance(data[field], (int, float))
    
    def test_create_field(self, client: TestClient, test_user, helpers):
        """Test creating a new field."""
        field_data = {
            "name": "New Field",
            "description": "A newly created field"
        }
        
        response = client.post("/api/fields/", json=field_data)
        data = helpers.assert_response_success(response, 200)
        helpers.assert_field_data(data, expected_name="New Field")
        assert data["description"] == "A newly created field"
    
    def test_create_field_duplicate_name(self, client: TestClient, test_user, test_field, helpers):
        """Test creating field with duplicate name."""
        field_data = {
            "name": "Test Field",  # Same as test_field
            "description": "Duplicate field"
        }
        
        response = client.post("/api/fields/", json=field_data)
        data = helpers.assert_response_error(response, 400)
        assert "already exists" in data["detail"]
    
    def test_update_field(self, client: TestClient, test_user, test_field, helpers):
        """Test updating a field."""
        update_data = {
            "name": "Updated Field",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/fields/{test_field.id}", json=update_data)
        data = helpers.assert_response_success(response)
        helpers.assert_field_data(data, expected_name="Updated Field")
        assert data["description"] == "Updated description"
    
    def test_update_field_not_found(self, client: TestClient, test_user, helpers):
        """Test updating non-existent field."""
        update_data = {
            "name": "Non-existent Field"
        }
        
        response = client.put("/api/fields/999999", json=update_data)
        helpers.assert_response_error(response, 404)
    
    def test_delete_field_soft(self, client: TestClient, test_user, test_field, helpers):
        """Test soft deleting a field."""
        response = client.delete(f"/api/fields/{test_field.id}")
        data = helpers.assert_response_success(response)
        assert "soft deleted" in data["message"]
    
    def test_delete_field_hard(self, client: TestClient, test_user, test_field, helpers):
        """Test hard deleting a field."""
        response = client.delete(f"/api/fields/{test_field.id}?hard_delete=true")
        data = helpers.assert_response_success(response)
        assert "permanently deleted" in data["message"]
    
    def test_delete_field_not_found(self, client: TestClient, test_user, helpers):
        """Test deleting non-existent field."""
        response = client.delete("/api/fields/999999")
        helpers.assert_response_error(response, 404)
    
    def test_restore_field(self, client: TestClient, test_user, helpers):
        """Test restoring a soft-deleted field."""
        # First create and soft delete a field
        field_data = {
            "name": "Field to Restore",
            "description": "This field will be deleted and restored"
        }
        
        create_response = client.post("/api/fields/", json=field_data)
        field_data = helpers.assert_response_success(create_response)
        field_id = field_data["id"]
        
        # Soft delete it
        delete_response = client.delete(f"/api/fields/{field_id}")
        helpers.assert_response_success(delete_response)
        
        # Restore it
        restore_response = client.post(f"/api/fields/{field_id}/restore")
        data = helpers.assert_response_success(restore_response)
        helpers.assert_field_data(data, expected_name="Field to Restore")
    
    def test_get_field_by_name(self, client: TestClient, test_user, test_field, helpers):
        """Test getting field by name."""
        response = client.get(f"/api/fields/name/{test_field.name}")
        data = helpers.assert_response_success(response)
        helpers.assert_field_data(data, expected_name="Test Field")
    
    def test_get_field_by_name_not_found(self, client: TestClient, test_user, helpers):
        """Test getting field by non-existent name."""
        response = client.get("/api/fields/name/NonExistentField")
        helpers.assert_response_error(response, 404)
    
    def test_get_or_create_field(self, client: TestClient, test_user, helpers):
        """Test get or create field functionality."""
        # Test creating new field
        response = client.post(
            "/api/fields/get-or-create",
            params={
                "field_name": "Auto Created Field",
                "description": "Automatically created field"
            }
        )
        data = helpers.assert_response_success(response)
        helpers.assert_field_data(data, expected_name="Auto Created Field")
        
        # Test getting existing field (should return same field)
        response2 = client.post(
            "/api/fields/get-or-create",
            params={"field_name": "Auto Created Field"}
        )
        data2 = helpers.assert_response_success(response2)
        assert data["id"] == data2["id"]  # Should be the same field
    
    def test_field_api_validation_errors(self, client: TestClient, test_user, helpers):
        """Test API validation errors."""
        # Test missing required fields
        response = client.post("/api/fields/", json={})
        helpers.assert_response_error(response, 422)
        
        # Test invalid field name (empty string)
        field_data = {
            "name": "",
            "description": "Invalid field"
        }
        response = client.post("/api/fields/", json=field_data)
        helpers.assert_response_error(response, 422)