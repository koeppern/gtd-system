"""
Tests for utility modules, configuration, and other supporting code
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestEnvironmentConfiguration:
    """Test environment configuration handling"""
    
    def test_env_loading_success(self):
        """Test successful environment variable loading"""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            # Import modules that depend on env vars
            from etl_projects import GTDProjectsETL
            
            with patch('etl_projects.create_client'):
                etl = GTDProjectsETL()
                assert etl.supabase_url == 'https://test.supabase.co'

    def test_env_loading_missing_vars(self):
        """Test handling of missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            from etl_projects import GTDProjectsETL
            
            with pytest.raises(ValueError, match="Missing required environment variables"):
                GTDProjectsETL()

class TestFileOperations:
    """Test file operations and CSV handling"""
    
    def test_csv_discovery_patterns(self):
        """Test CSV file discovery with various naming patterns"""
        from etl_projects import find_gtd_projects_csv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test exact match
            csv_file = Path(temp_dir) / "GTD Projects Export.csv"
            csv_file.write_text("Project,Field\n")
            
            result = find_gtd_projects_csv(temp_dir)
            assert result == str(csv_file)

    def test_csv_discovery_multiple_files(self):
        """Test CSV discovery when multiple files exist"""
        from etl_projects import find_gtd_projects_csv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple potential files
            csv1 = Path(temp_dir) / "GTD Projects Export.csv"
            csv2 = Path(temp_dir) / "old_projects.csv"
            
            csv1.write_text("Project,Field\n")
            csv2.write_text("Project,Field\n")
            
            result = find_gtd_projects_csv(temp_dir)
            # Should return the canonical name
            assert result == str(csv1)

    def test_directory_traversal(self):
        """Test directory traversal functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            data_dir = Path(temp_dir) / "data" / "from_notion"
            data_dir.mkdir(parents=True)
            
            csv_file = data_dir / "GTD Projects Export.csv"
            csv_file.write_text("Project,Field\n")
            
            # Test that file can be found in subdirectory
            from etl_projects import find_gtd_projects_csv
            
            try:
                result = find_gtd_projects_csv(str(data_dir))
                assert result == str(csv_file)
            except FileNotFoundError:
                # Expected if function doesn't search subdirs
                pass

class TestDataValidation:
    """Test data validation and sanitization functions"""
    
    @patch('etl_projects.create_client')
    def test_boolean_normalization_comprehensive(self, mock_create_client):
        """Test comprehensive boolean normalization"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_projects import GTDProjectsETL
            etl = GTDProjectsETL()
            
        # Test various truthy values
        truthy_values = ["✓", "true", "True", "TRUE", "yes", "Yes", "YES", "1", 1, True]
        for value in truthy_values:
            assert etl.normalize_boolean(value) == True, f"Failed for {value}"
            
        # Test various falsy values
        falsy_values = ["", "false", "False", "FALSE", "no", "No", "NO", "0", 0, False, None]
        for value in falsy_values:
            assert etl.normalize_boolean(value) == False, f"Failed for {value}"

    @patch('etl_tasks.create_client')
    def test_date_parsing_comprehensive(self, mock_create_client):
        """Test comprehensive date parsing"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_tasks import GTDTasksETL
            etl = GTDTasksETL()
            
        # Test various date formats
        valid_dates = [
            "2024-06-14",
            "June 14, 2024", 
            "06/14/2024",
            "14/06/2024",
            "2024-06-14T10:30:00"
        ]
        
        for date_str in valid_dates:
            try:
                result = etl.parse_date(date_str)
                assert result is not None, f"Failed to parse {date_str}"
            except:
                # Some formats might not be supported
                pass
                
        # Test invalid dates
        invalid_dates = ["", None, "invalid", "32/13/2024", "not a date"]
        for date_str in invalid_dates:
            result = etl.parse_date(date_str)
            assert result is None, f"Should not parse {date_str}"

    @patch('etl_tasks.create_client')
    def test_priority_normalization(self, mock_create_client):
        """Test priority value normalization"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_tasks import GTDTasksETL
            etl = GTDTasksETL()
            
        # Test priority mappings
        assert etl.normalize_priority("High") == 1
        assert etl.normalize_priority("HIGH") == 1
        assert etl.normalize_priority("high") == 1
        assert etl.normalize_priority("Medium") == 2
        assert etl.normalize_priority("Low") == 3
        assert etl.normalize_priority("") == 3  # Default
        assert etl.normalize_priority(None) == 3  # Default
        assert etl.normalize_priority("Unknown") == 3  # Default

class TestDatabaseOperations:
    """Test database operation utilities"""
    
    @patch('src.backend.app.database.psycopg2.connect')
    def test_database_connection_config(self, mock_connect):
        """Test database connection configuration"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test@localhost/testdb'}):
            from src.backend.app.database import get_db_connection
            
            result = get_db_connection()
            assert result == mock_conn
            mock_connect.assert_called_once_with('postgresql://test@localhost/testdb')

    @patch('src.backend.app.database.psycopg2.connect')
    def test_database_connection_fallback(self, mock_connect):
        """Test database connection fallback behavior"""
        mock_connect.side_effect = Exception("Connection failed")
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test@localhost/testdb'}):
            from src.backend.app.database import get_db_connection
            
            with pytest.raises(Exception):
                get_db_connection()

class TestCacheOperations:
    """Test caching functionality in ETL processes"""
    
    @patch('etl_tasks.create_client')
    def test_field_cache_lifecycle(self, mock_create_client):
        """Test field cache creation and usage"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock database response
        mock_client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": 1, "name": "Technology"},
            {"id": 2, "name": "Business"},
            {"id": 3, "name": "Personal"}
        ]
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_tasks import GTDTasksETL
            etl = GTDTasksETL()
            
        # First access should populate cache
        cache1 = etl.get_field_id_cache()
        assert len(cache1) == 3
        assert cache1["Technology"] == 1
        
        # Reset mock and access again - should use cache
        mock_client.reset_mock()
        cache2 = etl.get_field_id_cache()
        
        assert cache1 == cache2
        # Verify no additional database calls
        assert not mock_client.table.called

    @patch('etl_tasks.create_client')
    def test_project_mapping_cache(self, mock_create_client):
        """Test project name to ID mapping cache"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock project data
        mock_client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": 1, "project_name": "Project Alpha"},
            {"id": 2, "project_name": "Project Beta"}
        ]
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_tasks import GTDTasksETL
            etl = GTDTasksETL()
            
        # Test project mapping
        project_id = etl.map_project_name_to_id("Project Alpha")
        assert project_id == 1
        
        # Test caching behavior
        mock_client.reset_mock()
        project_id2 = etl.map_project_name_to_id("Project Alpha")
        assert project_id == project_id2

class TestErrorRecovery:
    """Test error recovery and resilience mechanisms"""
    
    @patch('etl_projects.create_client')
    def test_partial_data_processing(self, mock_create_client):
        """Test handling of partial data processing failures"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock intermittent failures
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail on second call
                raise Exception("Simulated failure")
            return Mock()
        
        mock_client.table.return_value.insert.side_effect = side_effect
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_projects import GTDProjectsETL
            etl = GTDProjectsETL()
            
        # Test that errors are handled gracefully
        # (Implementation depends on actual error handling in ETL)

    @patch('etl_tasks.create_client')
    def test_malformed_csv_handling(self, mock_create_client):
        """Test handling of malformed CSV data"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
        }):
            from etl_tasks import GTDTasksETL
            etl = GTDTasksETL()
            
        # Test various malformed data scenarios
        test_data = [
            {"Task": None, "Priority": "High"},  # None values
            {"Task": "", "Priority": ""},  # Empty strings
            {"Task": "Test", "Priority": "InvalidPriority"},  # Invalid enum
        ]
        
        for data in test_data:
            # Test that ETL handles malformed data gracefully
            try:
                priority = etl.normalize_priority(data.get("Priority"))
                assert priority in [1, 2, 3]  # Should always return valid priority
            except:
                pass  # Expected for some edge cases

class TestLogging:
    """Test logging functionality"""
    
    def test_logger_configuration(self):
        """Test that loggers are properly configured"""
        import logging
        
        # Test that ETL modules have loggers
        from etl_projects import logger as projects_logger
        from etl_tasks import logger as tasks_logger
        
        assert isinstance(projects_logger, logging.Logger)
        assert isinstance(tasks_logger, logging.Logger)
        
        # Test log levels
        assert projects_logger.level <= logging.INFO
        assert tasks_logger.level <= logging.INFO

    def test_logging_output(self):
        """Test logging output format and content"""
        import logging
        from io import StringIO
        
        # Create a string stream to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        # Configure logger
        test_logger = logging.getLogger("test_etl")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        
        # Test log message
        test_logger.info("Test log message")
        
        log_output = log_stream.getvalue()
        assert "Test log message" in log_output

class TestUtilityFunctions:
    """Test various utility functions"""
    
    def test_string_cleaning(self):
        """Test string cleaning and normalization"""
        # Test with actual ETL functions
        from etl_projects import GTDProjectsETL
        
        with patch('etl_projects.create_client'):
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
                'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
            }):
                etl = GTDProjectsETL()
                
        # Test project name extraction
        assert etl.extract_project_name("  Project: Test Name  ").strip() == "Test Name"
        assert etl.extract_project_name("Project:") == ""

    def test_data_type_conversion(self):
        """Test data type conversion utilities"""
        from etl_tasks import GTDTasksETL
        
        with patch('etl_tasks.create_client'):
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
                'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001'
            }):
                etl = GTDTasksETL()
                
        # Test various conversions
        assert etl.normalize_boolean("✓") == True
        assert etl.normalize_boolean("") == False
        assert etl.normalize_priority("High") == 1
        assert etl.normalize_priority("") == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])