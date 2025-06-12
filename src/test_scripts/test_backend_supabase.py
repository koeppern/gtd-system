#!/usr/bin/env python3
"""
Test script to verify FastAPI backend connection to Supabase.
Displays connection type (IPv4/IPv6), project/task counts, and sample data.
"""

import socket
import sys
import os
import asyncio
from typing import Optional

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

# Use the production database from .env
# Load .env file from project root
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from fastapi.testclient import TestClient
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def test_direct_database_connection():
    """Test direct database connection using environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        return None, None
    
    try:
        # Create async engine
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            await conn.commit()
        
        return engine, database_url
    except Exception as e:
        print(f"Direct database connection failed: {e}")
        return None, None

def get_connection_type(database_url: str) -> str:
    """Determine if we're using IPv4 or IPv6 for Supabase connection."""
    try:
        url_parts = urllib.parse.urlparse(database_url)
        hostname = url_parts.hostname
        
        if hostname:
            # Get address info
            addr_info = socket.getaddrinfo(hostname, None)
            
            # Check the first result
            if addr_info:
                family = addr_info[0][0]
                if family == socket.AF_INET:
                    return f"IPv4 (Host: {hostname})"
                elif family == socket.AF_INET6:
                    return f"IPv6 (Host: {hostname})"
        
        return "Unknown"
    except Exception as e:
        return f"Error detecting: {e}"

async def fetch_data_directly(engine):
    """Fetch data directly from database."""
    try:
        async with engine.begin() as conn:
            # Get projects
            result = await conn.execute(text("""
                SELECT id, name, done_at, created_at 
                FROM gtd_projects 
                ORDER BY created_at DESC 
                LIMIT 4
            """))
            projects = result.fetchall()
            
            # Get total project count
            count_result = await conn.execute(text("SELECT COUNT(*) FROM gtd_projects"))
            project_count = count_result.scalar()
            
            # Get tasks
            result = await conn.execute(text("""
                SELECT id, name, done_at, created_at 
                FROM gtd_tasks 
                ORDER BY created_at DESC 
                LIMIT 4
            """))
            tasks = result.fetchall()
            
            # Get total task count
            count_result = await conn.execute(text("SELECT COUNT(*) FROM gtd_tasks"))
            task_count = count_result.scalar()
            
            return {
                "projects": projects,
                "project_count": project_count,
                "tasks": tasks,
                "task_count": task_count
            }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

async def main():
    print("=== FastAPI Backend Supabase Test ===\n")
    
    # Test direct database connection
    engine, database_url = await test_direct_database_connection()
    
    if engine and database_url:
        # Display connection type
        connection_type = get_connection_type(database_url)
        print(f"Connection Type: {connection_type}\n")
        
        # Fetch data directly
        data = await fetch_data_directly(engine)
        
        if data:
            # Display projects
            print("--- Projects ---")
            print(f"Total Projects: {data['project_count']}")
            
            if data['projects']:
                print("\nFirst 4 Projects:")
                for project in data['projects']:
                    status = "✓" if project.done_at else "○"
                    print(f"  {status} {project.name}")
            
            # Display tasks
            print("\n--- Tasks ---")
            print(f"Total Tasks: {data['task_count']}")
            
            if data['tasks']:
                print("\nFirst 4 Tasks:")
                for task in data['tasks']:
                    status = "✓" if task.done_at else "○"
                    print(f"  {status} {task.name}")
        
        # Cleanup
        await engine.dispose()
    else:
        print("Failed to establish database connection")
        print("\nTrying FastAPI TestClient as fallback...\n")
        
        # Fallback to TestClient
        from app.main import app
        client = TestClient(app)
        
        # Test projects endpoint
        print("--- Projects (via API) ---")
        try:
            response = client.get("/api/projects/")
            if response.status_code == 200:
                projects = response.json()
                print(f"Total Projects: {len(projects)}")
                
                if projects:
                    print("\nFirst 4 Projects:")
                    for project in projects[:4]:
                        print(f"  • {project['name']}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main())