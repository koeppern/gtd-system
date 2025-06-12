#!/usr/bin/env python3
"""
Test the FastAPI endpoints directly using requests
"""

import requests
import time
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the backend server in background"""
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent / "backend"
    
    # Start server
    process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    return process

def test_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    # Test health/root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"Root endpoint failed: {e}")
    
    # Test projects endpoint
    try:
        response = requests.get(f"{base_url}/api/projects/", timeout=10)
        print(f"Projects endpoint: {response.status_code}")
        if response.status_code == 200:
            projects = response.json()
            print(f"Found {len(projects)} projects")
            if projects:
                print("First project:", projects[0].get('name', 'Unknown'))
        else:
            print(f"Projects error: {response.text}")
    except Exception as e:
        print(f"Projects endpoint failed: {e}")
    
    # Test tasks endpoint  
    try:
        response = requests.get(f"{base_url}/api/tasks/", timeout=10)
        print(f"Tasks endpoint: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"Found {len(tasks)} tasks")
            if tasks:
                print("First task:", tasks[0].get('name', 'Unknown'))
        else:
            print(f"Tasks error: {response.text}")
    except Exception as e:
        print(f"Tasks endpoint failed: {e}")

def main():
    print("=== Direct API Test ===\n")
    
    print("Starting backend server...")
    process = start_backend()
    
    try:
        print("Testing endpoints...\n")
        test_endpoints()
    finally:
        print("\nStopping backend server...")
        process.terminate()
        process.wait()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()