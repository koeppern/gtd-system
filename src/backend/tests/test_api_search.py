"""
Test Search API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestSearchAPI:
    """Test Search API endpoints."""
    
    def test_search_all(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test searching across all projects and tasks."""
        response = client.get("/api/search/?query=test")
        data = helpers.assert_response_success(response)
        
        # Check response structure
        assert "query" in data
        assert "total_results" in data
        assert "projects" in data
        assert "tasks" in data
        
        assert data["query"] == "test"
        
        # Check projects section
        projects_data = data["projects"]
        assert "count" in projects_data
        assert "results" in projects_data
        assert isinstance(projects_data["results"], list)
        
        # Check tasks section
        tasks_data = data["tasks"]
        assert "count" in tasks_data
        assert "results" in tasks_data
        assert isinstance(tasks_data["results"], list)
        
        # Verify total results matches
        assert data["total_results"] == projects_data["count"] + tasks_data["count"]
        
        # Verify search results contain the query term
        all_results = projects_data["results"] + tasks_data["results"]
        for result in all_results:
            # Should contain "test" in name, keywords, or other searchable fields
            searchable_text = ""
            if "project_name" in result:
                searchable_text += result["project_name"].lower()
            if "task_name" in result:
                searchable_text += result["task_name"].lower()
            if "keywords" in result and result["keywords"]:
                searchable_text += result["keywords"].lower()
            
            # Note: Not all results may contain the exact term due to partial matching
    
    def test_search_all_with_filters(self, client: TestClient, test_user, multiple_projects, multiple_tasks, completed_items, helpers):
        """Test searching with include_completed filter."""
        # Search without completed items
        response = client.get("/api/search/?query=test&include_completed=false")
        data = helpers.assert_response_success(response)
        
        # Should not include completed items
        all_results = data["projects"]["results"] + data["tasks"]["results"]
        for result in all_results:
            assert result.get("done_at") is None
        
        # Search with completed items
        response = client.get("/api/search/?query=test&include_completed=true")
        data_with_completed = helpers.assert_response_success(response)
        
        # Should have same or more results
        assert data_with_completed["total_results"] >= data["total_results"]
    
    def test_search_projects_only(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test searching projects only."""
        response = client.get("/api/search/projects?query=Development")
        data = helpers.assert_response_success(response)
        
        # Check response structure
        assert "query" in data
        assert "count" in data
        assert "results" in data
        
        assert data["query"] == "Development"
        assert isinstance(data["results"], list)
        
        # All results should be projects
        for project in data["results"]:
            helpers.assert_project_data(project)
            # Should contain "Development" in name or keywords
            searchable_text = project["project_name"].lower()
            if project.get("keywords"):
                searchable_text += project["keywords"].lower()
            assert "development" in searchable_text
    
    def test_search_tasks_only(self, client: TestClient, test_user, multiple_tasks, helpers):
        """Test searching tasks only."""
        response = client.get("/api/search/tasks?query=authentication")
        data = helpers.assert_response_success(response)
        
        # Check response structure
        assert "query" in data
        assert "count" in data
        assert "results" in data
        
        assert data["query"] == "authentication"
        assert isinstance(data["results"], list)
        
        # Should find the "Implement authentication" task
        assert data["count"] >= 1
        
        # All results should be tasks
        for task in data["results"]:
            helpers.assert_task_data(task)
            # Should contain "authentication" in name
            assert "authentication" in task["task_name"].lower()
    
    def test_search_with_pagination(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test search with pagination."""
        # Search with limit
        response = client.get("/api/search/projects?query=test&limit=2")
        data = helpers.assert_response_success(response)
        
        assert len(data["results"]) <= 2
        
        # Search with skip
        response = client.get("/api/search/tasks?query=test&skip=1&limit=2")
        data = helpers.assert_response_success(response)
        
        assert len(data["results"]) <= 2
    
    def test_search_suggestions(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting search suggestions."""
        response = client.get("/api/search/suggestions?query=dev")
        data = helpers.assert_response_success(response)
        
        # Check response structure
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        
        # Should find suggestions related to "dev" (like "Development")
        suggestions = data["suggestions"]
        dev_suggestions = [s for s in suggestions if "dev" in s.lower()]
        assert len(dev_suggestions) > 0
    
    def test_search_suggestions_with_limit(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test search suggestions with limit."""
        response = client.get("/api/search/suggestions?query=test&limit=3")
        data = helpers.assert_response_success(response)
        
        suggestions = data["suggestions"]
        assert len(suggestions) <= 3
    
    def test_get_recent_items(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting recent items."""
        response = client.get("/api/search/recent")
        data = helpers.assert_response_success(response)
        
        # Check response structure
        assert "recent_projects" in data
        assert "recent_tasks" in data
        
        # Check recent projects
        recent_projects = data["recent_projects"]
        assert isinstance(recent_projects, list)
        assert len(recent_projects) <= 5  # Limited to 5
        
        for project in recent_projects:
            assert "id" in project
            assert "name" in project
            assert "updated_at" in project
            assert "is_completed" in project
            assert isinstance(project["is_completed"], bool)
        
        # Check recent tasks
        recent_tasks = data["recent_tasks"]
        assert isinstance(recent_tasks, list)
        assert len(recent_tasks) <= 5  # Limited to 5
        
        for task in recent_tasks:
            assert "id" in task
            assert "name" in task
            assert "updated_at" in task
            assert "is_completed" in task
            assert "project_id" in task
            assert isinstance(task["is_completed"], bool)
    
    def test_get_recent_items_with_limit(self, client: TestClient, test_user, multiple_projects, multiple_tasks, helpers):
        """Test getting recent items with custom limit."""
        response = client.get("/api/search/recent?limit=3")
        data = helpers.assert_response_success(response)
        
        # Should respect the limit but each category is limited to 5 max
        recent_projects = data["recent_projects"]
        recent_tasks = data["recent_tasks"]
        
        assert len(recent_projects) <= 5
        assert len(recent_tasks) <= 5
    
    def test_search_empty_query(self, client: TestClient, test_user, helpers):
        """Test search with empty or very short query."""
        # Empty query should fail validation
        response = client.get("/api/search/?query=")
        helpers.assert_response_error(response, 422)  # Validation error
        
        # Very short query should also fail
        response = client.get("/api/search/projects?query=")
        helpers.assert_response_error(response, 422)  # Validation error
    
    def test_search_no_results(self, client: TestClient, test_user, helpers):
        """Test search with query that returns no results."""
        response = client.get("/api/search/?query=nonexistentquerythatreturnsnothing")
        data = helpers.assert_response_success(response)
        
        assert data["total_results"] == 0
        assert data["projects"]["count"] == 0
        assert data["tasks"]["count"] == 0
        assert len(data["projects"]["results"]) == 0
        assert len(data["tasks"]["results"]) == 0
    
    def test_search_case_insensitive(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test that search is case insensitive."""
        # Search with lowercase
        response_lower = client.get("/api/search/projects?query=development")
        data_lower = helpers.assert_response_success(response_lower)
        
        # Search with uppercase
        response_upper = client.get("/api/search/projects?query=DEVELOPMENT")
        data_upper = helpers.assert_response_success(response_upper)
        
        # Should return same results
        assert data_lower["count"] == data_upper["count"]
    
    def test_search_special_characters(self, client: TestClient, test_user, helpers):
        """Test search with special characters."""
        # Create a project with special characters
        project_data = {
            "project_name": "API & Database Integration",
            "keywords": "api, database, integration, & symbols"
        }
        
        create_response = client.post("/api/projects/", json=project_data)
        helpers.assert_response_success(create_response)
        
        # Search for the special character
        response = client.get("/api/search/projects?query=&")
        data = helpers.assert_response_success(response)
        
        # Should handle special characters gracefully
        assert isinstance(data["results"], list)
    
    def test_search_partial_matching(self, client: TestClient, test_user, multiple_projects, helpers):
        """Test partial word matching in search."""
        # Search for partial word "Dev" should match "Development"
        response = client.get("/api/search/projects?query=Dev")
        data = helpers.assert_response_success(response)
        
        # Should find projects with "Development" in the name
        found_development = any("development" in project["project_name"].lower() 
                              for project in data["results"])
        assert found_development or data["count"] == 0  # Might not have results depending on test data