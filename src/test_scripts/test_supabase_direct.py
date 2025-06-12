#!/usr/bin/env python3
"""
Direct test of Supabase connection
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

async def test_connection():
    database_url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {database_url[:50]}...")
    
    try:
        # Create engine with minimal settings
        engine = create_async_engine(
            database_url,
            echo=True,  # Show SQL queries
            connect_args={
                "ssl": "require",
                "server_settings": {
                    "application_name": "test_script"
                }
            }
        )
        
        # Test query
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT current_database(), current_user"))
            row = result.fetchone()
            print(f"\nConnected successfully!")
            print(f"Database: {row[0]}")
            print(f"User: {row[1]}")
            
            # Test tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('gtd_projects', 'gtd_tasks')
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print(f"\nFound tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
        await engine.dispose()
        
    except Exception as e:
        print(f"\nConnection failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())