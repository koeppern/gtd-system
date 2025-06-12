"""
Test database configuration and fallback behavior
This test would have caught the SQLite fallback issue
"""
import pytest
import os
from unittest.mock import patch, Mock
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.config import get_settings, Settings
from app.dependencies import get_db


class TestDatabaseFallbackBehavior:
    """Test that database configuration fails properly without SQLite fallback"""
    
    def test_missing_supabase_credentials_raises_error(self):
        """Test that missing Supabase credentials raise ValueError instead of falling back to SQLite"""
        # Clear the settings cache
        get_settings.cache_clear()
        
        # Mock environment to have no Supabase credentials AND clear pytest test detection
        with patch.dict(os.environ, {
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_ROLE_KEY": "",
            "DATABASE_URL": "",  # Also clear direct database URL
            "PYTEST_CURRENT_TEST": ""  # Clear test detection so it acts like production
        }, clear=True):
            
            # Create minimal config without Supabase credentials (NO test URL)
            config_data = {
                "app": {
                    "name": "Test App",
                    "version": "1.0.0", 
                    "environment": "production",  # Explicitly production
                    "debug": False
                },
                "server": {"host": "127.0.0.1", "port": 8000},
                "database": {
                    "supabase": {"url": "", "service_role_key": ""},
                    "postgres": {"url": None},
                    "test": {"url": None}  # No test URL either
                },
                "security": {
                    "secret_key": "test-key",
                    "algorithm": "HS256", 
                    "access_token_expire_minutes": 30
                },
                "cors": {
                    "origins": ["*"],
                    "allow_credentials": True,
                    "allow_methods": ["*"], 
                    "allow_headers": ["*"]
                },
                "logging": {"level": "INFO", "format": "%(message)s"},
                "api": {
                    "prefix": "/api",
                    "docs_url": "/docs",
                    "redoc_url": "/redoc",
                    "openapi_url": "/openapi.json"
                },
                "pagination": {"default_limit": 20, "max_limit": 100},
                "gtd": {
                    "default_user_id": "00000000-0000-0000-0000-000000000001",
                    "tasks": {},
                    "projects": {},
                    "weekly_review": {}
                },
                "features": {
                    "authentication_enabled": False,
                    "real_time_updates": False,
                    "email_notifications": False,
                    "export_import": False
                }
            }
            
            settings = Settings(**config_data)
            
            # Verify we're NOT in testing mode
            assert not settings.is_testing, "Should not be in testing mode for this test"
            
            # This should raise ValueError, NOT fall back to SQLite
            with pytest.raises(ValueError, match="Database configuration incomplete"):
                _ = settings.database_url_asyncpg
    
    def test_invalid_supabase_credentials_raises_error(self):
        """Test that invalid Supabase credentials raise ValueError"""
        get_settings.cache_clear()
        
        with patch.dict(os.environ, {
            "SUPABASE_URL": "invalid-url",
            "SUPABASE_SERVICE_ROLE_KEY": "invalid-key",
            "DATABASE_URL": ""
        }, clear=False):
            
            config_data = {
                "app": {
                    "name": "Test App",
                    "version": "1.0.0",
                    "environment": "production", 
                    "debug": False
                },
                "server": {"host": "127.0.0.1", "port": 8000},
                "database": {
                    "supabase": {"url": "invalid-url", "service_role_key": "invalid-key"},
                    "postgres": {"url": None},
                    "test": {"url": "sqlite+aiosqlite:///:memory:"}
                },
                "security": {
                    "secret_key": "test-key",
                    "algorithm": "HS256",
                    "access_token_expire_minutes": 30
                },
                "cors": {
                    "origins": ["*"],
                    "allow_credentials": True,
                    "allow_methods": ["*"],
                    "allow_headers": ["*"]
                },
                "logging": {"level": "INFO", "format": "%(message)s"},
                "api": {
                    "prefix": "/api",
                    "docs_url": "/docs", 
                    "redoc_url": "/redoc",
                    "openapi_url": "/openapi.json"
                },
                "pagination": {"default_limit": 20, "max_limit": 100},
                "gtd": {
                    "default_user_id": "00000000-0000-0000-0000-000000000001",
                    "tasks": {},
                    "projects": {},
                    "weekly_review": {}
                },
                "features": {
                    "authentication_enabled": False,
                    "real_time_updates": False,
                    "email_notifications": False,
                    "export_import": False
                }
            }
            
            settings = Settings(**config_data)
            
            # Should construct URL from invalid credentials (this part works)
            db_url = settings.database_url_asyncpg
            assert "postgresql+asyncpg://" in db_url
            assert "invalid-key" in db_url
    
    @pytest.mark.asyncio
    async def test_database_dependency_fails_gracefully_on_connection_error(self):
        """Test that get_db() dependency returns HTTP 503 on connection failure"""
        
        # Mock the async_session_maker to raise a connection error
        with patch('app.dependencies.async_session_maker') as mock_session_maker:
            mock_session = Mock()
            mock_session.execute.side_effect = OperationalError("Network is unreachable", None, None)
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            mock_session_maker.return_value.__aexit__.return_value = None
            
            # Test the dependency
            with pytest.raises(HTTPException) as exc_info:
                async for _ in get_db():
                    pass
            
            # Should raise HTTP 503 Service Unavailable
            assert exc_info.value.status_code == 503
            assert "Database service unavailable" in exc_info.value.detail
    
    def test_production_config_does_not_contain_sqlite_fallback(self):
        """Test that production configuration method doesn't contain SQLite fallback logic"""
        import inspect
        from app.config import Settings
        
        # Get the source code of the database_url_asyncpg property
        source = inspect.getsource(Settings.database_url_asyncpg.fget)
        
        # Should NOT contain SQLite fallback
        assert "sqlite" not in source.lower(), "Production config should not contain SQLite fallback"
        
        # Should contain error handling
        assert "ValueError" in source or "raise" in source, "Should raise error when config is incomplete"
    
    def test_test_config_still_uses_sqlite(self):
        """Verify that test configuration still properly uses SQLite for isolation"""
        # Clear cache and set test environment
        get_settings.cache_clear()
        
        with patch.dict(os.environ, {
            "CONFIG_FILE": "test_config.yaml",
            "PYTEST_CURRENT_TEST": "1"
        }, clear=False):
            
            settings = get_settings()
            
            # Test environment should use in-memory SQLite
            assert settings.app.environment == "testing"
            db_url = settings.database_url_asyncpg
            assert "sqlite+aiosqlite:///:memory:" in db_url
            
        # Clean up
        get_settings.cache_clear()
    
    def test_sqlite_fallback_completely_removed_from_production(self):
        """Comprehensive test that SQLite fallback is completely removed from production paths"""
        
        # Test 1: Check config.py source doesn't have fallback logic
        with open('/mnt/c/python/gtd/src/backend/app/config.py', 'r') as f:
            config_source = f.read()
        
        # Count occurrences of sqlite in different contexts
        lines = config_source.lower().split('\n')
        
        # Should not have production fallback to SQLite
        fallback_patterns = [
            'fallback to sqlite',
            'return "sqlite+aiosqlite',
            'sqlite.*fallback',
            'fallback.*sqlite'
        ]
        
        for line in lines:
            for pattern in fallback_patterns:
                if 'test' not in line and pattern in line:
                    pytest.fail(f"Found SQLite fallback in production code: {line.strip()}")
        
        # Test 2: Verify ValueError is raised instead
        assert 'ValueError' in config_source, "Should raise ValueError when config is incomplete"
        assert 'Database configuration incomplete' in config_source, "Should have descriptive error message"


class TestHistoricalBugScenario:
    """Test the exact scenario that caused the original SQLite fallback issue"""
    
    @pytest.mark.asyncio 
    async def test_network_unreachable_scenario(self):
        """Test the exact 'Network is unreachable' scenario that exposed the fallback issue"""
        
        # This simulates the production scenario where:
        # 1. Supabase credentials are configured  
        # 2. Network connection to Supabase fails
        # 3. System should fail gracefully, NOT fall back to SQLite
        
        # Mock valid Supabase config but failing connection
        get_settings.cache_clear()
        
        with patch.dict(os.environ, {
            "SUPABASE_URL": "https://test-project.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "valid-looking-key-12345",
            "CONFIG_FILE": "config.yaml"  # Use production config
        }, clear=False):
            
            # Mock async_session_maker to simulate network failure
            with patch('app.dependencies.async_session_maker') as mock_session_maker:
                # Simulate the exact error we encountered
                mock_session = Mock()
                mock_session.execute.side_effect = OSError("[Errno 101] Network is unreachable")
                mock_session_maker.return_value.__aenter__.return_value = mock_session
                mock_session_maker.return_value.__aexit__.return_value = None
                
                # The dependency should handle this gracefully
                with pytest.raises(HTTPException) as exc_info:
                    async for _ in get_db():
                        pass
                
                # Should return HTTP 503, not crash or fall back to SQLite
                assert exc_info.value.status_code == 503
                assert "Network is unreachable" in exc_info.value.detail
                assert "sqlite" not in exc_info.value.detail.lower()
        
        get_settings.cache_clear()
    
    def test_before_and_after_behavior(self):
        """Document the before/after behavior to show what the test would have caught"""
        
        # BEFORE (with SQLite fallback): 
        # - Missing Supabase credentials -> silently fall back to SQLite
        # - Network issues -> silently fall back to SQLite  
        # - No visibility into database connection problems
        
        # AFTER (without SQLite fallback):
        # - Missing Supabase credentials -> ValueError with clear message
        # - Network issues -> HTTP 503 Service Unavailable
        # - Clear error reporting and proper failure modes
        
        # This test documents that the change was intentional and correct
        get_settings.cache_clear()
        
        # Test the current (correct) behavior
        config_data = {
            "app": {"name": "Test", "version": "1.0.0", "environment": "production", "debug": False},
            "server": {"host": "127.0.0.1", "port": 8000},
            "database": {
                "supabase": {"url": "", "service_role_key": ""},  # Empty credentials
                "postgres": {"url": None},
                "test": {"url": "sqlite+aiosqlite:///:memory:"}
            },
            "security": {"secret_key": "test", "algorithm": "HS256", "access_token_expire_minutes": 30},
            "cors": {"origins": ["*"], "allow_credentials": True, "allow_methods": ["*"], "allow_headers": ["*"]},
            "logging": {"level": "INFO", "format": "%(message)s"},
            "api": {"prefix": "/api", "docs_url": "/docs", "redoc_url": "/redoc", "openapi_url": "/openapi.json"},
            "pagination": {"default_limit": 20, "max_limit": 100},
            "gtd": {"default_user_id": "00000000-0000-0000-0000-000000000001", "tasks": {}, "projects": {}, "weekly_review": {}},
            "features": {"authentication_enabled": False, "real_time_updates": False, "email_notifications": False, "export_import": False}
        }
        
        settings = Settings(**config_data)
        
        # Should raise ValueError (correct behavior)
        with pytest.raises(ValueError):
            _ = settings.database_url_asyncpg
        
        # This test would have FAILED before our fix because it would have
        # returned "sqlite+aiosqlite:///./gtd_dev.db" instead of raising an error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])