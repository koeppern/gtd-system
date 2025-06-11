#!/usr/bin/env python3
"""
Run script for GTD Backend Application
"""
import sys
import os
import uvicorn

# Add app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print(f"Starting GTD Backend on {settings.server.host}:{settings.server.port}")
    print(f"Environment: {settings.app.environment}")
    print(f"Debug mode: {settings.app.debug}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.app.debug,
        access_log=True,
        log_level="info" if not settings.app.debug else "debug"
    )