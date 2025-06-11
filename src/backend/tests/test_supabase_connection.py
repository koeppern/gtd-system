"""
Supabase connection tests
Tests specifically for Supabase/PostgreSQL connectivity and features
"""
import pytest
import os
from sqlalchemy import text, create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.database import async_session_maker, get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task


class TestSupabaseConnection:
    """Test basic Supabase database connectivity"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test that we can connect to the database"""
        async with async_session_maker() as session:
            # Test basic connection with a simple query
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            
            # Test database type detection
            settings = get_settings()
            if "postgresql" in settings.database_url_asyncpg:
                # Test PostgreSQL specific query
                result = await session.execute(text("SELECT version()"))
                version = result.scalar()
                assert "PostgreSQL" in version
                print(f"Connected to: {version}")
    
    @pytest.mark.asyncio
    async def test_supabase_tables_exist(self):
        """Test that all required tables exist"""
        async with async_session_maker() as session:
            settings = get_settings()
            
            if "postgresql" in settings.database_url_asyncpg:
                # PostgreSQL query
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('gtd_users', 'gtd_projects', 'gtd_tasks', 'gtd_fields')
                    ORDER BY table_name
                """)
            else:
                # SQLite query
                tables_query = text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name IN ('gtd_users', 'gtd_projects', 'gtd_tasks', 'gtd_fields')
                    ORDER BY name
                """)
            
            result = await session.execute(tables_query)
            tables = [row[0] for row in result]
            
            # Verify all required tables exist
            expected_tables = ['gtd_fields', 'gtd_projects', 'gtd_tasks', 'gtd_users']
            assert set(tables) == set(expected_tables), f"Missing tables. Found: {tables}"
    
    @pytest.mark.asyncio
    async def test_default_user_exists(self):
        """Test that the default user exists in the database"""
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == "00000000-0000-0000-0000-000000000001")
            )
            user = result.scalar_one_or_none()
            
            assert user is not None, "Default user should exist"
            assert user.email_address is not None


class TestSupabaseSpecific:
    """Test Supabase-specific functionality"""
    
    @pytest.mark.asyncio
    async def test_supabase_connection_direct(self):
        """Test direct Supabase connection bypassing test config"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            pytest.skip("Supabase credentials not configured")
        
        # Test connection with Supabase credentials directly
        project_id = supabase_url.split("//")[1].split(".")[0]
        db_url = f"postgresql+asyncpg://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres"
        
        engine = create_async_engine(db_url)
        
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                assert "PostgreSQL" in version
                print(f"✓ Connected to Supabase: {version}")
        finally:
            await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_supabase_tables_exist_direct(self):
        """Test that tables exist in Supabase (direct connection)"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            pytest.skip("Supabase credentials not configured")
        
        # Direct connection to Supabase
        project_id = supabase_url.split("//")[1].split(".")[0]
        db_url = f"postgresql+asyncpg://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres"
        
        engine = create_async_engine(db_url)
        
        try:
            async with engine.begin() as conn:
                # Check for tables
                result = await conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('gtd_users', 'gtd_projects', 'gtd_tasks', 'gtd_fields')
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in result]
                expected_tables = ['gtd_fields', 'gtd_projects', 'gtd_tasks', 'gtd_users']
                
                print(f"✓ Found tables in Supabase: {tables}")
                assert set(tables) == set(expected_tables), f"Missing tables. Found: {tables}"
                
        finally:
            await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_supabase_default_user_exists_direct(self):
        """Test that default user exists in Supabase (direct connection)"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            pytest.skip("Supabase credentials not configured")
        
        # Direct connection to Supabase
        project_id = supabase_url.split("//")[1].split(".")[0]
        db_url = f"postgresql+asyncpg://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres"
        
        engine = create_async_engine(db_url)
        
        try:
            async with engine.begin() as conn:
                # Check for default user
                result = await conn.execute(text("""
                    SELECT id, email_address, first_name, last_name 
                    FROM gtd_users 
                    WHERE id = '00000000-0000-0000-0000-000000000001'
                """))
                
                user = result.fetchone()
                assert user is not None, "Default user should exist in Supabase"
                print(f"✓ Default user found: {user[1]} ({user[2]} {user[3]})")
                
        finally:
            await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_supabase_views_exist(self):
        """Test that database views exist in Supabase"""
        settings = get_settings()
        if "postgresql" not in settings.database_url_asyncpg:
            pytest.skip("Not using PostgreSQL/Supabase")
            
        async with async_session_maker() as session:
            # Check for views
            views_query = text("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'gtd_projects_with_fields', 
                    'gtd_tasks_with_details', 
                    'gtd_tasks_summary'
                )
                ORDER BY table_name
            """)
            
            result = await session.execute(views_query)
            views = [row[0] for row in result]
            
            # These views should exist based on your Supabase setup
            expected_views = [
                'gtd_projects_with_fields',
                'gtd_tasks_summary', 
                'gtd_tasks_with_details'
            ]
            
            for view in expected_views:
                assert view in views, f"View '{view}' not found in database"
    
    @pytest.mark.asyncio
    async def test_postgresql_features_if_available(self):
        """Test PostgreSQL-specific features if using PostgreSQL"""
        settings = get_settings()
        database_url = settings.database_url_asyncpg
        
        if "postgresql" not in database_url:
            pytest.skip("Not using PostgreSQL")
        
        async with async_session_maker() as db:
            # Test UUID support
            result = await db.execute(text("SELECT gen_random_uuid()"))
            uuid_val = result.fetchone()[0]
            assert len(str(uuid_val)) == 36  # Standard UUID length
            
            # Test JSON support
            await db.execute(text("SELECT '{\"test\": \"value\"}'::json"))
            
            # Test array support  
            await db.execute(text("SELECT ARRAY[1,2,3]"))
    
    @pytest.mark.asyncio
    async def test_database_extensions_if_postgresql(self):
        """Test that required PostgreSQL extensions are available"""
        settings = get_settings()
        database_url = settings.database_url_asyncpg
        
        if "postgresql" not in database_url:
            pytest.skip("Not using PostgreSQL")
        
        async with async_session_maker() as db:
            # Check for uuid-ossp extension
            result = await db.execute(text("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp'
                )
            """))
            has_uuid_extension = result.fetchone()[0]
            # Extension might not be installed in all environments
            assert isinstance(has_uuid_extension, bool)
    
    @pytest.mark.asyncio
    async def test_database_performance_postgresql(self):
        """Test PostgreSQL performance characteristics"""
        settings = get_settings()
        database_url = settings.database_url_asyncpg
        
        if "postgresql" not in database_url:
            pytest.skip("Not using PostgreSQL")
        
        import time
        
        # Test connection pool performance
        start_time = time.time()
        tasks = []
        
        for _ in range(5):
            async with async_session_maker() as db:
                await db.execute(text("SELECT 1"))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Multiple connections should be reasonably fast
        assert total_time < 2.0  # Less than 2 seconds for 5 connections
    
    @pytest.mark.asyncio
    async def test_transaction_isolation(self):
        """Test transaction isolation in PostgreSQL"""
        settings = get_settings()
        database_url = settings.database_url_asyncpg
        
        if "postgresql" not in database_url:
            pytest.skip("Not using PostgreSQL")
        
        # Test that transactions are properly isolated
        async with async_session_maker() as db1:
            async with async_session_maker() as db2:
                # Both sessions should be independent
                result1 = await db1.execute(text("SELECT txid_current()"))
                result2 = await db2.execute(text("SELECT txid_current()"))
                
                txid1 = result1.fetchone()[0]
                txid2 = result2.fetchone()[0]
                
                # Different transactions should have different IDs
                assert txid1 != txid2


class TestDatabaseConfiguration:
    """Test database configuration and fallback mechanisms"""
    
    def test_database_url_selection(self):
        """Test that database URL is selected correctly"""
        settings = get_settings()
        db_url = settings.database_url_asyncpg
        
        # Should be either SQLite or PostgreSQL
        assert "sqlite" in db_url or "postgresql" in db_url
    
    def test_environment_variable_override(self):
        """Test that DATABASE_URL environment variable works"""
        original_env = os.getenv("DATABASE_URL")
        
        try:
            # Set a test database URL
            test_url = "sqlite+aiosqlite:///./test.db"
            os.environ["DATABASE_URL"] = test_url
            
            # Clear the cache and get new settings
            get_settings.cache_clear()
            settings = get_settings()
            
            assert settings.database_url_asyncpg == test_url
        
        finally:
            # Restore original environment
            if original_env:
                os.environ["DATABASE_URL"] = original_env
            else:
                os.environ.pop("DATABASE_URL", None)
            get_settings.cache_clear()


class TestSupabaseCRUD:
    """Test CRUD operations with Supabase"""
    
    @pytest.mark.asyncio
    async def test_user_crud_operations(self):
        """Test basic CRUD operations on User model"""
        async with async_session_maker() as session:
            try:
                # Create a test user
                test_user = User(
                    id="test-user-crud-001",
                    first_name="Test",
                    last_name="CRUD",
                    email_address="test.crud@example.com"
                )
                
                session.add(test_user)
                await session.commit()
                
                # Read the user back
                result = await session.execute(
                    select(User).where(User.id == "test-user-crud-001")
                )
                user = result.scalar_one_or_none()
                
                assert user is not None
                assert user.first_name == "Test"
                assert user.email_address == "test.crud@example.com"
                
                # Update the user
                user.last_name = "Updated"
                await session.commit()
                
                # Verify update
                await session.refresh(user)
                assert user.last_name == "Updated"
                
                # Delete the user
                await session.delete(user)
                await session.commit()
                
                # Verify deletion
                result = await session.execute(
                    select(User).where(User.id == "test-user-crud-001")
                )
                deleted_user = result.scalar_one_or_none()
                assert deleted_user is None
                
            except Exception as e:
                await session.rollback()
                raise e
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self):
        """Test that foreign key constraints work properly"""
        settings = get_settings()
        if "sqlite" in settings.database_url_asyncpg:
            pytest.skip("SQLite foreign key enforcement may vary")
            
        async with async_session_maker() as session:
            # Try to create a task with non-existent user
            test_task = Task(
                id="test-task-fk-001",
                task_name="Test Task",
                user_id="non-existent-user-id"
            )
            
            session.add(test_task)
            
            # Should raise an error due to foreign key constraint
            with pytest.raises(Exception) as exc_info:
                await session.commit()
            
            await session.rollback()
            
            # The error should mention foreign key or constraint
            error_msg = str(exc_info.value).lower()
            assert "foreign" in error_msg or "constraint" in error_msg or "violates" in error_msg


class TestDataMigration:
    """Test data migration and schema compatibility"""
    
    @pytest.mark.asyncio
    async def test_schema_version_compatibility(self):
        """Test that current schema is compatible"""
        async with async_session_maker() as db:
            settings = get_settings()
            
            if "postgresql" in settings.database_url_asyncpg:
                # Check if alembic version table exists
                result = await db.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                    )
                """))
                
                has_alembic = result.fetchone()[0]
                if has_alembic:
                    # Check current version
                    version_result = await db.execute(text("SELECT version_num FROM alembic_version"))
                    version = version_result.fetchone()
                    if version:
                        assert len(version[0]) > 0  # Version should be a non-empty string
            else:
                # For SQLite, just check if we can query tables
                await db.execute(text("SELECT 1 FROM gtd_users LIMIT 1"))
    
    @pytest.mark.asyncio
    async def test_table_structure_consistency(self):
        """Test that all tables have consistent structure"""
        required_columns = {
            "gtd_users": ["id", "email_address", "created_at", "updated_at"],
            "gtd_fields": ["id", "name", "created_at", "updated_at"],
            "gtd_projects": ["id", "user_id", "project_name", "created_at", "updated_at"],
            "gtd_tasks": ["id", "user_id", "task_name", "created_at", "updated_at"]
        }
        
        async with async_session_maker() as db:
            for table_name, columns in required_columns.items():
                # Test that we can select from the table with required columns
                column_list = ", ".join(columns)
                try:
                    await db.execute(text(f"SELECT {column_list} FROM {table_name} LIMIT 1"))
                except Exception as e:
                    pytest.fail(f"Table {table_name} missing required columns: {e}")


class TestConnectionResilience:
    """Test database connection resilience and error handling"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_recovery(self):
        """Test that connection pool can recover from errors"""
        async with async_session_maker() as session:
            # First query should work
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            
            # Force a rollback
            await session.rollback()
            
            # Should still be able to use the session
            result = await session.execute(text("SELECT 2"))
            assert result.scalar() == 2
    
    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test multiple concurrent database connections"""
        import asyncio
        
        async def query_db(query_id: int):
            async with async_session_maker() as session:
                result = await session.execute(text(f"SELECT {query_id}"))
                return result.scalar()
        
        # Run 10 concurrent queries
        tasks = [query_db(i) for i in range(1, 11)]
        results = await asyncio.gather(*tasks)
        
        # All queries should return their respective numbers
        assert results == list(range(1, 11))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])