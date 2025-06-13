#!/usr/bin/env python3
"""
Test all API calls that the frontend makes to ensure backend compatibility.
Can run with either TestClient (embedded) or against a real running server.
"""
import sys
import os
import argparse
import json
from typing import Dict, Any, List
import requests
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

# For TestClient mode
from fastapi.testclient import TestClient
from app.main import app


class APITester:
    def __init__(self, use_test_client: bool = True, base_url: str = "http://localhost:8000"):
        self.use_test_client = use_test_client
        self.base_url = base_url
        self.client = TestClient(app) if use_test_client else None
        self.results = []
        
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request using either TestClient or real HTTP"""
        url = endpoint if self.use_test_client else f"{self.base_url}{endpoint}"
        
        try:
            if self.use_test_client:
                # Use TestClient
                response = getattr(self.client, method.lower())(url, **kwargs)
            else:
                # Use real HTTP
                response = getattr(requests, method.lower())(url, **kwargs)
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.status_code < 400 else None,
                "error": response.text if response.status_code >= 400 else None,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "status_code": 500,
                "data": None,
                "error": str(e),
                "headers": {}
            }
    
    def test_endpoint(self, name: str, method: str, endpoint: str, **kwargs):
        """Test a single endpoint and record results"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"Method: {method} {endpoint}")
        if kwargs:
            print(f"Params: {kwargs}")
        
        start_time = datetime.now()
        result = self.make_request(method, endpoint, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()
        
        status_icon = "✅" if result["status_code"] < 400 else "❌"
        print(f"{status_icon} Status: {result['status_code']} ({duration:.3f}s)")
        
        if result["data"]:
            print(f"Response: {json.dumps(result['data'], indent=2)[:200]}...")
        elif result["error"]:
            print(f"Error: {result['error'][:200]}...")
        
        self.results.append({
            "name": name,
            "endpoint": endpoint,
            "method": method,
            "status": result["status_code"],
            "success": result["status_code"] < 400,
            "duration": duration,
            "error": result["error"]
        })
        
        return result
    
    def run_all_tests(self):
        """Run all frontend API tests based on actual frontend usage"""
        print(f"\n{'#'*60}")
        print(f"# Frontend API Compatibility Test")
        print(f"# Mode: {'TestClient (Embedded)' if self.use_test_client else f'Real Server ({self.base_url})'}")
        print(f"{'#'*60}")
        
        # 1. Dashboard Stats (page.tsx)
        self.test_endpoint(
            "Dashboard Statistics",
            "GET",
            "/api/dashboard/stats"
        )
        
        # 2. Today's Tasks (page.tsx)
        self.test_endpoint(
            "Today's Tasks",
            "GET", 
            "/api/tasks/today"
        )
        
        # 3. Weekly Projects (page.tsx)
        self.test_endpoint(
            "Weekly Projects",
            "GET",
            "/api/projects/weekly"
        )
        
        # 4. Inbox Tasks (page.tsx)
        self.test_endpoint(
            "Inbox Tasks (No Project)",
            "GET",
            "/api/tasks",
            params={
                "limit": 10,
                "do_today": "false",
                "do_this_week": "false", 
                "is_done": "false"
            }
        )
        
        # 5. All Projects (used in task forms)
        self.test_endpoint(
            "All Projects",
            "GET",
            "/api/projects"
        )
        
        # 6. All Fields (used in project forms)
        self.test_endpoint(
            "All Fields",
            "GET",
            "/api/fields"
        )
        
        # 7. Active Projects (projects page)
        self.test_endpoint(
            "Active Projects",
            "GET",
            "/api/projects/active"
        )
        
        # 8. Task Statistics
        self.test_endpoint(
            "Task Statistics",
            "GET",
            "/api/tasks/stats"
        )
        
        # 9. Waiting Tasks
        self.test_endpoint(
            "Waiting Tasks",
            "GET",
            "/api/tasks/waiting"
        )
        
        # 10. Reading Tasks
        self.test_endpoint(
            "Reading Tasks",
            "GET",
            "/api/tasks/reading"
        )
        
        # 11. Tasks for specific project (if any projects exist)
        projects_result = self.make_request("GET", "/api/projects", params={"limit": 1})
        if projects_result["data"] and len(projects_result["data"]) > 0:
            project_id = projects_result["data"][0]["id"]
            self.test_endpoint(
                f"Tasks for Project {project_id}",
                "GET",
                f"/api/tasks/by-project/{project_id}"
            )
        
        # 12. Search Tasks
        self.test_endpoint(
            "Search Tasks",
            "GET",
            "/api/tasks/search",
            params={"q": "test"}
        )
        
        # 13. Weekly Review Endpoints
        self.test_endpoint(
            "Tasks Needing Review",
            "GET",
            "/api/weekly-review/tasks-to-review"
        )
        
        self.test_endpoint(
            "Projects Needing Review", 
            "GET",
            "/api/weekly-review/projects-to-review"
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'#'*60}")
        print("# Test Summary")
        print(f"{'#'*60}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n{'='*60}")
            print("Failed Tests:")
            print(f"{'='*60}")
            for result in self.results:
                if not result["success"]:
                    print(f"\n❌ {result['name']}")
                    print(f"   Endpoint: {result['method']} {result['endpoint']}")
                    print(f"   Status: {result['status']}")
                    if result["error"]:
                        print(f"   Error: {result['error'][:100]}...")
        
        # Performance summary
        print(f"\n{'='*60}")
        print("Performance Summary:")
        print(f"{'='*60}")
        avg_duration = sum(r["duration"] for r in self.results) / len(self.results)
        slowest = max(self.results, key=lambda r: r["duration"])
        print(f"Average Response Time: {avg_duration:.3f}s")
        print(f"Slowest Endpoint: {slowest['name']} ({slowest['duration']:.3f}s)")


def main():
    parser = argparse.ArgumentParser(description="Test frontend API compatibility")
    parser.add_argument(
        "--mode",
        choices=["test", "real"],
        default="test",
        help="Use 'test' for TestClient or 'real' for actual server"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for real server mode (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    use_test_client = args.mode == "test"
    
    # Create tester and run
    tester = APITester(use_test_client=use_test_client, base_url=args.url)
    
    try:
        tester.run_all_tests()
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1
    
    # Return exit code based on results
    failed_count = sum(1 for r in tester.results if not r["success"])
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())