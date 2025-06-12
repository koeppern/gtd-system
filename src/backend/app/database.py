"""
Database configuration and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings

# Initialize engine and session factory on import
def _init_database():
    """Initialize database engine and session factory with fallback support"""
    settings = get_settings()
    database_url = settings.database_url_asyncpg
    
    # For development, provide more resilient connection handling
    engine_kwargs = {
        "echo": settings.app.debug,
        "future": True,
        "pool_pre_ping": True,
    }
    
    # Use NullPool for serverless environments or when connection might be unreliable
    if settings.app.environment == "production" or "postgresql" in database_url:
        engine_kwargs["poolclass"] = NullPool
    
    # Add connection timeout and retry settings for PostgreSQL
    if "postgresql" in database_url:
        # Extract project ID for server settings if using pooler
        server_settings = {"application_name": "gtd_backend"}
        if "pooler.supabase.com" in database_url:
            # For pooler connections, we need to specify the project
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(database_url)
            if parsed.query:
                query_params = parse_qs(parsed.query)
                if "options" in query_params:
                    options = query_params["options"][0]
                    if "project=" in options:
                        project_id = options.split("project=")[1]
                        server_settings["options"] = f"-c search_path=public"
                        
        engine_kwargs["connect_args"] = {
            "server_settings": server_settings,
            "ssl": "require",  # Enable SSL for Supabase pooler
            "command_timeout": 10,
            "timeout": 30,
        }
    
    # Create async engine
    engine = create_async_engine(database_url, **engine_kwargs)
    
    # Create async session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    return engine, async_session_maker

# Initialize database components
engine, async_session_maker = _init_database()

# Import models to ensure they are registered with Base
from app.models.base import Base
from app.models import User, Field, Project, Task


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()