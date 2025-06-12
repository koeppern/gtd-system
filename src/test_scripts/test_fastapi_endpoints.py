#!/usr/bin/env python3
"""
Test FastAPI endpoints directly with HTTP requests
"""
import requests
import time
import subprocess
import threading
import os
import sys
from datetime import datetime

def start_server():
    """Start FastAPI server in background"""
    try:
        subprocess.run([
            'python', '-m', 'uvicorn', 'app.main:app', 
            '--host', '0.0.0.0', '--port', '8000'
        ], cwd='src/backend', capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        print(f"Server startup error: {e}")

def test_api_endpoints():
    """Test all available API endpoints"""
    base_url = "http://localhost:8000"
    
    print("=== FastAPI Endpoint Tests ===\n")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    print()
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database', {}).get('status')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print()
    
    # Test projects endpoint
    try:
        response = requests.get(f"{base_url}/api/projects/", timeout=10)
        print(f"✅ Projects API: {response.status_code}")
        if response.status_code == 200:
            projects = response.json()
            print(f"   Total projects returned: {len(projects)}")
            if projects:
                print(f"   First project: {projects[0].get('name', 'N/A')}")
                print(f"   Project ID: {projects[0].get('id', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Projects API failed: {e}")
    
    print()
    
    # Test specific project
    try:
        response = requests.get(f"{base_url}/api/projects/1", timeout=10)
        print(f"✅ Single project API: {response.status_code}")
        if response.status_code == 200:
            project = response.json()
            print(f"   Project name: {project.get('name', 'N/A')}")
            print(f"   Field ID: {project.get('field_id', 'N/A')}")
        elif response.status_code == 404:
            print("   Project ID 1 not found (expected)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Single project API failed: {e}")
    
    print()
    
    # Test tasks endpoint
    try:
        response = requests.get(f"{base_url}/api/tasks/", timeout=10)
        print(f"✅ Tasks API: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"   Total tasks returned: {len(tasks)}")
            if tasks:
                print(f"   First task: {tasks[0].get('name', 'N/A')}")
                print(f"   Task ID: {tasks[0].get('id', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Tasks API failed: {e}")
    
    print()
    
    # Test task stats
    try:
        response = requests.get(f"{base_url}/api/tasks/stats", timeout=10)
        print(f"✅ Task stats API: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total tasks: {stats.get('total_tasks', 'N/A')}")
            print(f"   Completed tasks: {stats.get('completed_tasks', 'N/A')}")
            print(f"   Today tasks: {stats.get('today_tasks', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Task stats API failed: {e}")
    
    print()
    
    # Test today's tasks
    try:
        response = requests.get(f"{base_url}/api/tasks/today", timeout=10)
        print(f"✅ Today tasks API: {response.status_code}")
        if response.status_code == 200:
            today_tasks = response.json()
            print(f"   Today's tasks: {len(today_tasks)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Today tasks API failed: {e}")
    
    print()
    
    # Test other stub endpoints
    stub_endpoints = [
        ("/api/users/me", "Users API"),
        ("/api/fields/", "Fields API"),
        ("/api/dashboard/", "Dashboard API"),
        ("/api/search/", "Search API")
    ]
    
    for endpoint, name in stub_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {name}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data.get('message', data)}")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    print("\n=== Test Complete ===")

def main():
    # Change to project root
    os.chdir('/mnt/c/python/gtd')
    
    print("Starting FastAPI server...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("Waiting 4 seconds for server startup...")
    time.sleep(4)
    
    # Test endpoints
    test_api_endpoints()

if __name__ == "__main__":
    main()