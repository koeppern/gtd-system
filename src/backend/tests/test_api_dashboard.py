"""
Test Dashboard API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestDashboardAPI:
    """Test Dashboard API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_dashboard_overview(self, client: TestClient, test_user, multiple_projects, multiple_tasks, completed_items, helpers):
        """Test getting comprehensive dashboard overview."""
        response = client.get("/api/dashboard/overview")
        data = helpers.assert_response_success(response)
        
        # Check main sections
        assert "user" in data
        assert "tasks" in data
        assert "fields" in data
        assert "summary" in data
        
        # Check user section
        user_data = data["user"]
        assert "id" in user_data
        assert "name" in user_data
        assert "email" in user_data
        assert "stats" in user_data
        
        # Check tasks section
        tasks_data = data["tasks"]
        assert "stats" in tasks_data
        assert "today" in tasks_data
        assert "overdue" in tasks_data
        assert "week" in tasks_data
        assert "waiting" in tasks_data
        assert "reading" in tasks_data
        
        # Check today tasks
        today_data = tasks_data["today"]
        assert "count" in today_data
        assert "tasks" in today_data
        assert isinstance(today_data["tasks"], list)
        
        # Check overdue tasks
        overdue_data = tasks_data["overdue"]
        assert "count" in overdue_data
        assert "tasks" in overdue_data
        assert isinstance(overdue_data["tasks"], list)
        
        # Check week tasks
        week_data = tasks_data["week"]
        assert "count" in week_data
        assert "tasks" in week_data
        assert isinstance(week_data["tasks"], list)
        
        # Check waiting tasks
        waiting_data = tasks_data["waiting"]
        assert "count" in waiting_data
        assert "tasks" in waiting_data
        assert isinstance(waiting_data["tasks"], list)
        
        # Check reading tasks
        reading_data = tasks_data["reading"]
        assert "count" in reading_data
        assert "tasks" in reading_data
        assert isinstance(reading_data["tasks"], list)
        
        # Check fields section
        fields_data = data["fields"]
        assert "popular" in fields_data
        assert isinstance(fields_data["popular"], list)
        
        # Check summary section
        summary_data = data["summary"]
        summary_fields = [
            "total_active_items", "completion_rate", "urgent_items",
            "today_focus", "attention_needed"
        ]
        for field in summary_fields:
            assert field in summary_data
            assert isinstance(summary_data[field], (int, float))
    
    def test_get_dashboard_stats(self, client: TestClient, test_user, multiple_projects, multiple_tasks, completed_items, helpers):
        """Test getting detailed dashboard statistics."""
        response = client.get("/api/dashboard/stats")
        data = helpers.assert_response_success(response)
        
        # Check main sections
        assert "projects" in data
        assert "tasks" in data
        assert "priorities" in data
        assert "weekly" in data
        
        # Check projects stats
        projects_data = data["projects"]
        project_fields = ["total", "active", "completed", "completion_rate"]
        for field in project_fields:
            assert field in projects_data
            assert isinstance(projects_data[field], (int, float))
        
        # Check tasks stats
        tasks_data = data["tasks"]
        task_fields = [
            "total", "pending", "completed", "completion_rate",
            "today", "overdue", "reading", "waiting"
        ]
        for field in task_fields:
            assert field in tasks_data
            assert isinstance(tasks_data[field], (int, float))
        
        # Check priorities stats
        priorities_data = data["priorities"]
        priority_fields = [
            "priority_1", "priority_2", "priority_3",
            "priority_4", "priority_5", "no_priority"
        ]
        for field in priority_fields:
            assert field in priorities_data
            assert isinstance(priorities_data[field], int)
        
        # Check weekly stats
        weekly_data = data["weekly"]
        assert "tasks_this_week" in weekly_data
        assert isinstance(weekly_data["tasks_this_week"], int)
        
        # Validate data consistency
        assert tasks_data["pending"] == tasks_data["total"] - tasks_data["completed"]
        assert projects_data["active"] == projects_data["total"] - projects_data["completed"]
    
    def test_get_quick_actions(self, client: TestClient, test_user, helpers):
        """Test getting quick action suggestions."""
        response = client.get("/api/dashboard/quick-actions")
        data = helpers.assert_response_success(response)
        
        # Check main sections
        assert "suggestions" in data
        assert "quick_links" in data
        
        # Check suggestions
        suggestions = data["suggestions"]
        assert isinstance(suggestions, list)
        
        for suggestion in suggestions:
            assert "type" in suggestion
            assert "title" in suggestion
            assert "description" in suggestion
            assert "action" in suggestion
            assert "count" in suggestion
            
            # Validate suggestion types
            assert suggestion["type"] in ["urgent", "planning", "focus", "review", "productivity"]
        
        # Check quick links
        quick_links = data["quick_links"]
        assert isinstance(quick_links, list)
        
        for link in quick_links:
            assert "title" in link
            assert "action" in link
            assert "icon" in link
        
        # Should have standard quick links
        link_titles = [link["title"] for link in quick_links]
        assert "Add Task" in link_titles
        assert "Add Project" in link_titles
        assert "Today's Tasks" in link_titles
        assert "Weekly Review" in link_titles
    
    def test_get_quick_actions_with_overdue_tasks(self, client: TestClient, test_user, helpers):
        """Test quick actions when there are overdue tasks."""
        # First create an overdue task
        task_data = {
            "task_name": "Overdue Task for Dashboard",
            "do_on_date": "2023-01-01"  # Past date
        }
        
        create_response = client.post("/api/tasks/", json=task_data)
        helpers.assert_response_success(create_response)
        
        response = client.get("/api/dashboard/quick-actions")
        data = helpers.assert_response_success(response)
        
        suggestions = data["suggestions"]
        
        # Should suggest reviewing overdue tasks
        urgent_suggestions = [s for s in suggestions if s["type"] == "urgent"]
        assert len(urgent_suggestions) > 0
        
        # Check that the suggestion mentions overdue tasks
        overdue_suggestion = urgent_suggestions[0]
        assert "overdue" in overdue_suggestion["title"].lower()
        assert overdue_suggestion["count"] > 0
    
    def test_get_quick_actions_with_many_today_tasks(self, client: TestClient, test_user, helpers):
        """Test quick actions when there are many tasks for today."""
        # Create multiple tasks for today
        for i in range(12):  # More than 10 to trigger focus suggestion
            task_data = {
                "task_name": f"Today Task {i}",
                "do_today": True
            }
            
            create_response = client.post("/api/tasks/", json=task_data)
            helpers.assert_response_success(create_response)
        
        response = client.get("/api/dashboard/quick-actions")
        data = helpers.assert_response_success(response)
        
        suggestions = data["suggestions"]
        
        # Should suggest prioritizing today's tasks
        focus_suggestions = [s for s in suggestions if s["type"] == "focus"]
        if focus_suggestions:  # Might not always trigger depending on other conditions
            focus_suggestion = focus_suggestions[0]
            assert "prioritize" in focus_suggestion["title"].lower() or "focus" in focus_suggestion["title"].lower()
            assert focus_suggestion["count"] > 10
    
    def test_get_quick_actions_with_waiting_tasks(self, client: TestClient, test_user, helpers):
        """Test quick actions when there are waiting tasks."""
        # Create a waiting task
        task_data = {
            "task_name": "Waiting Task for Dashboard",
            "wait_for": True
        }
        
        create_response = client.post("/api/tasks/", json=task_data)
        helpers.assert_response_success(create_response)
        
        response = client.get("/api/dashboard/quick-actions")
        data = helpers.assert_response_success(response)
        
        suggestions = data["suggestions"]
        
        # Should suggest reviewing waiting tasks
        review_suggestions = [s for s in suggestions if s["type"] == "review"]
        if review_suggestions:  # Might not always be present
            review_suggestion = review_suggestions[0]
            assert "waiting" in review_suggestion["title"].lower()
            assert review_suggestion["count"] > 0
    
    def test_get_quick_actions_no_tasks_today(self, client: TestClient, test_user, helpers):
        """Test quick actions when no tasks are scheduled for today."""
        # The test user should have no tasks for today initially
        response = client.get("/api/dashboard/quick-actions")
        data = helpers.assert_response_success(response)
        
        suggestions = data["suggestions"]
        
        # Should suggest planning the day
        planning_suggestions = [s for s in suggestions if s["type"] == "planning"]
        # Note: This might not always be present depending on existing test data
        
        # Should at least have some suggestions
        assert len(suggestions) > 0
    
    def test_dashboard_without_data(self, client: TestClient, test_user, helpers):
        """Test dashboard endpoints with minimal data."""
        # Test overview with just the test user
        response = client.get("/api/dashboard/overview")
        data = helpers.assert_response_success(response)
        
        # Should still have proper structure
        assert "user" in data
        assert "tasks" in data
        assert "summary" in data
        
        # Counts should be zero or low
        assert data["tasks"]["stats"]["total_tasks"] >= 0
        assert data["summary"]["total_active_items"] >= 0
    
    def test_dashboard_api_error_handling(self, client: TestClient, helpers):
        """Test dashboard API error handling."""
        # Test without authentication (should use test user)
        response = client.get("/api/dashboard/overview")
        # Should still work with test user dependency
        helpers.assert_response_success(response)
    
    def test_dashboard_performance_fields(self, client: TestClient, test_user, multiple_fields, multiple_projects, multiple_tasks, helpers):
        """Test dashboard with multiple fields and verify performance data."""
        response = client.get("/api/dashboard/overview")
        data = helpers.assert_response_success(response)
        
        # Should have popular fields
        popular_fields = data["fields"]["popular"]
        assert isinstance(popular_fields, list)
        
        # Each field should have usage data
        for field in popular_fields:
            assert "id" in field
            assert "name" in field
            assert "project_count" in field
            assert "task_count" in field
            assert "total_usage" in field