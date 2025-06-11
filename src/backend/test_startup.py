"""
Quick test to verify backend startup
"""
import asyncio
import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_startup():
    """Test basic imports and configuration loading"""
    try:
        print("Testing imports...")
        
        # Test config loading
        from app.config import get_settings
        settings = get_settings()
        print(f"✓ Config loaded: {settings.app.name} v{settings.app.version}")
        
        # Test database import
        from app.database import async_session_maker
        print("✓ Database module imported")
        
        # Test CRUD imports
        from app.crud.user import crud_user
        from app.crud.field import crud_field
        from app.crud.project import crud_project
        from app.crud.task import crud_task
        print("✓ CRUD modules imported")
        
        # Test API imports
        from app.api import users, fields, projects, tasks, dashboard, search, quick_add
        print("✓ API modules imported")
        
        # Test main app
        from app.main import app
        print("✓ FastAPI app created")
        
        print("\n🎉 All imports successful! Backend is ready to start.")
        print(f"Run: python run.py")
        print(f"API docs will be at: http://{settings.app.host}:{settings.app.port}/docs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_startup())
    sys.exit(0 if success else 1)