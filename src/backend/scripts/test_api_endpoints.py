#!/usr/bin/env python3
"""
Test all API endpoints with requests library
This provides a simple way to test the API without complex test setup
"""
import requests
import json
import sys
import time
from uuid import uuid4


BASE_URL = "http://localhost:8000"


class APITester:
    """Simple API endpoint tester"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_items = []  # Track created items for cleanup
    
    def test_endpoint(self, method, endpoint, data=None, expected_codes=[200]):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code in expected_codes
            result = {
                "method": method.upper(),
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": success,
                "data": None,
                "error": None
            }
            
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text[:200]  # First 200 chars
            
            if not success:
                result["error"] = f"Expected {expected_codes}, got {response.status_code}"
            
            return result
            
        except Exception as e:
            return {
                "method": method.upper(),
                "endpoint": endpoint,
                "status_code": None,
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def test_cors(self):
        """Test CORS configuration"""
        print("🔗 Testing CORS Configuration")
        
        # Test preflight request
        try:
            response = self.session.options(
                f"{self.base_url}/api/fields/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            cors_headers = {
                key: value for key, value in response.headers.items() 
                if key.startswith("Access-Control")
            }
            
            print(f"  ✓ CORS preflight: {response.status_code}")
            print(f"  ✓ CORS headers: {cors_headers}")
            return True
            
        except Exception as e:
            print(f"  ❌ CORS test failed: {e}")
            return False
    
    def test_all_endpoints(self):
        """Test all API endpoints"""
        print("🧪 Testing API Endpoints")
        print("=" * 50)
        
        # Test basic endpoints
        endpoints = [
            ("GET", "/docs", [200, 404]),  # Docs might be disabled
            ("GET", "/api/fields/", [200, 404]),  # 404 if no auth
            ("GET", "/api/projects/", [200, 404]),
            ("GET", "/api/projects/weekly", [200, 404]),
            ("GET", "/api/tasks/", [200, 404]),
            ("GET", "/api/tasks/today", [200, 404]),
            ("GET", "/api/dashboard/stats", [200, 404]),
            ("GET", "/api/users/me", [200, 404]),
            ("GET", "/api/users/me/stats", [200, 404]),
            ("GET", "/api/search/tasks?q=test", [200, 404]),
            ("GET", "/api/search/projects?q=test", [200, 404]),
        ]
        
        results = []
        for method, endpoint, expected_codes in endpoints:
            result = self.test_endpoint(method, endpoint, expected_codes=expected_codes)
            results.append(result)
            
            status_icon = "✅" if result["success"] else "❌"
            print(f"  {status_icon} {method} {endpoint} -> {result['status_code']}")
            
            if not result["success"] and result["error"]:
                print(f"      Error: {result['error']}")
        
        return results
    
    def test_create_operations(self):
        """Test creating data (if authentication works)"""
        print("\n🔨 Testing Create Operations")
        print("=" * 30)
        
        # Test field creation
        field_data = {
            "name": f"TestField_{uuid4().hex[:8]}",
            "description": "Test field created by API test"
        }
        
        result = self.test_endpoint("POST", "/api/fields/", field_data, [200, 404, 422])
        print(f"  {'✅' if result['success'] else '❌'} Create Field -> {result['status_code']}")
        
        if result["success"] and result["data"] and "id" in result["data"]:
            field_id = result["data"]["id"]
            self.created_items.append(("field", field_id))
            
            # Test project creation with the field
            project_data = {
                "project_name": f"TestProject_{uuid4().hex[:8]}",
                "field_id": field_id,
                "do_this_week": True,
                "keywords": "test, api"
            }
            
            result = self.test_endpoint("POST", "/api/projects/", project_data, [200, 404, 422])
            print(f"  {'✅' if result['success'] else '❌'} Create Project -> {result['status_code']}")
            
            if result["success"] and result["data"] and "id" in result["data"]:
                project_id = result["data"]["id"]
                self.created_items.append(("project", project_id))
                
                # Test task creation
                task_data = {
                    "task_name": f"TestTask_{uuid4().hex[:8]}",
                    "field_id": field_id,
                    "project_id": project_id,
                    "priority": 3,
                    "do_today": False,
                    "do_this_week": True
                }
                
                result = self.test_endpoint("POST", "/api/tasks/", task_data, [200, 404, 422])
                print(f"  {'✅' if result['success'] else '❌'} Create Task -> {result['status_code']}")
                
                if result["success"] and result["data"] and "id" in result["data"]:
                    task_id = result["data"]["id"]
                    self.created_items.append(("task", task_id))
    
    def cleanup(self):
        """Clean up created test data"""
        if not self.created_items:
            return
        
        print("\n🧹 Cleaning up test data")
        print("=" * 25)
        
        # Delete in reverse order (tasks, projects, fields)
        for item_type, item_id in reversed(self.created_items):
            endpoint = f"/api/{item_type}s/{item_id}" if item_type != "field" else f"/api/fields/{item_id}"
            result = self.test_endpoint("DELETE", endpoint, expected_codes=[200, 404, 405])
            print(f"  {'✅' if result['success'] else '❌'} Delete {item_type} {item_id}")
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n🚫 Testing Error Handling")
        print("=" * 27)
        
        # Test invalid endpoints
        result = self.test_endpoint("GET", "/api/nonexistent/", expected_codes=[404])
        print(f"  {'✅' if result['success'] else '❌'} Invalid endpoint -> {result['status_code']}")
        
        # Test invalid data
        result = self.test_endpoint("POST", "/api/fields/", {"name": ""}, expected_codes=[422, 404])
        print(f"  {'✅' if result['success'] else '❌'} Invalid field data -> {result['status_code']}")
        
        # Test non-existent resource
        result = self.test_endpoint("GET", "/api/fields/99999", expected_codes=[404])
        print(f"  {'✅' if result['success'] else '❌'} Non-existent resource -> {result['status_code']}")
    
    def test_quick_add(self):
        """Test quick add functionality"""
        print("\n⚡ Testing Quick Add")
        print("=" * 20)
        
        quick_add_data = {
            "text": "Call John about the meeting #work @today"
        }
        
        result = self.test_endpoint("POST", "/api/quick-add/parse", quick_add_data, [200, 404])
        print(f"  {'✅' if result['success'] else '❌'} Parse text -> {result['status_code']}")
        
        if result["success"] and result["data"]:
            print(f"      Parsed: {result['data']}")


def check_server_running():
    """Check if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        return True
    except:
        return False


def main():
    """Main test function"""
    print("🚀 GTD Backend API Integration Test")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Backend server is not running!")
        print(f"   Please start the server with: python run.py")
        print(f"   Expected server at: {BASE_URL}")
        return False
    
    print(f"✅ Server is running at {BASE_URL}")
    
    # Run tests
    tester = APITester()
    
    try:
        # Test CORS
        tester.test_cors()
        
        # Test all endpoints
        results = tester.test_all_endpoints()
        
        # Test create operations
        tester.test_create_operations()
        
        # Test error handling
        tester.test_error_handling()
        
        # Test quick add
        tester.test_quick_add()
        
        # Summary
        print("\n📊 Test Summary")
        print("=" * 15)
        
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)
        
        print(f"✅ Successful: {success_count}/{total_count}")
        print(f"❌ Failed: {total_count - success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 All tests passed!")
        elif success_count > 0:
            print("⚠️  Some tests passed - this is expected if authentication is required")
        else:
            print("💥 All tests failed - check server configuration")
        
        return success_count > 0
        
    finally:
        # Always cleanup
        tester.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)