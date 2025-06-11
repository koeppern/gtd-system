#!/usr/bin/env python3
"""
Test configuration loading
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
import os

print("🔧 Testing Configuration")
print("=" * 30)
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {Path(__file__).parent.parent}")

try:
    settings = get_settings()
    print(f"✅ Settings loaded successfully")
    print(f"Environment: {settings.app.environment}")
    print(f"Default user ID: {settings.gtd.default_user_id}")
    print(f"Database URL: {settings.database_url_asyncpg}")
except Exception as e:
    print(f"❌ Failed to load settings: {e}")
    import traceback
    traceback.print_exc()