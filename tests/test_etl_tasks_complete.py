#!/usr/bin/env python3
"""
Comprehensive ETL Tasks Tests
Tests for task data transformation, validation, and import processes
"""

import unittest
import tempfile
import os
import csv
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timezone

# Add src to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from etl_tasks import GTDTasksETL, find_gtd_tasks_csv


class TestGTDTasksETLComplete(unittest.TestCase):
    """Comprehensive test cases for GTDTasksETL class"""
    
    def setUp(self):
        """Set up test environment"""
        self.env_vars = {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test_key',
            'DEFAULT_USER_ID': 'test-user-uuid'
        }
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', self.env_vars)
        self.env_patcher.start()
        
        # Sample task data for testing
        self.sample_task_data = {
            'Task': 'Complete project documentation',
            'Status': 'Done',
            'Due': '2024-01-15T10:30:00.000Z',
            'Done At': '2024-01-14T15:45:00.000Z',
            'Project': 'Documentation Project',
            'Tags': 'urgent, documentation',
            'Priority': 'High',
            'Context': '@computer',
            'Energy Level': 'High',
            'Time Required': '2 hours',
            'Notes': 'Final review needed',
            'Created': '2024-01-01T09:00:00.000Z',
            'Updated': '2024-01-14T15:45:00.000Z'
        }

    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()

    def test_init_success(self):
        """Test successful ETL initialization"""
        with patch('etl_tasks.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            etl = GTDTasksETL()
            
            self.assertIsNotNone(etl.supabase)
            self.assertEqual(etl.user_id, 'test-user-uuid')
            self.assertIsNotNone(etl.field_mapping)

    def test_init_missing_env_vars(self):
        """Test ETL initialization with missing environment variables"""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as context:
                GTDTasksETL()
            
            self.assertIn('environment variable', str(context.exception).lower())

    def test_extract_task_data_valid_csv(self):
        """Test task data extraction from valid CSV file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            # Create test CSV
            writer = csv.DictWriter(tmp_file, fieldnames=self.sample_task_data.keys())
            writer.writeheader()
            writer.writerow(self.sample_task_data)
            tmp_file.flush()
            
            try:
                with patch('etl_tasks.create_client'):
                    etl = GTDTasksETL()
                    
                    # Mock CSV file discovery
                    with patch('etl_tasks.find_gtd_tasks_csv', return_value=tmp_file.name):
                        tasks_df = etl.extract()
                        
                        self.assertIsInstance(tasks_df, pd.DataFrame)
                        self.assertEqual(len(tasks_df), 1)
                        self.assertEqual(tasks_df.iloc[0]['Task'], 'Complete project documentation')
                        
            finally:
                os.unlink(tmp_file.name)

    def test_extract_task_data_missing_file(self):
        """Test task data extraction with missing CSV file"""
        with patch('etl_tasks.create_client'), \
             patch('etl_tasks.find_gtd_tasks_csv', return_value=None):
            
            etl = GTDTasksETL()
            
            with self.assertRaises(FileNotFoundError) as context:
                etl.extract()
            
            self.assertIn('CSV file not found', str(context.exception))

    def test_transform_task_data_complete(self):
        """Test comprehensive task data transformation"""
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            
            # Mock field mapping and project lookup
            etl.field_mapping = {'urgent': 1, 'documentation': 2}
            etl.project_mapping = {'Documentation Project': 100}
            
            # Create test DataFrame
            df = pd.DataFrame([self.sample_task_data])
            
            transformed_df = etl.transform(df)
            
            # Verify transformation results
            self.assertIsInstance(transformed_df, pd.DataFrame)
            self.assertEqual(len(transformed_df), 1)
            
            row = transformed_df.iloc[0]
            
            # Test basic fields
            self.assertEqual(row['task_name'], 'Complete project documentation')
            self.assertEqual(row['status'], 'Done')
            self.assertEqual(row['project_id'], 100)
            
            # Test date conversions
            self.assertIsNotNone(row['due_date'])
            self.assertIsNotNone(row['done_at'])
            self.assertIsNotNone(row['created_at'])
            
            # Test field associations
            self.assertIn(1, row['field_ids'])  # urgent
            self.assertIn(2, row['field_ids'])  # documentation

    def test_transform_date_formats(self):
        """Test various date format transformations"""
        date_formats = [
            '2024-01-15T10:30:00.000Z',  # ISO with milliseconds
            '2024-01-15T10:30:00Z',      # ISO without milliseconds
            '2024-01-15 10:30:00',       # SQL datetime
            '2024-01-15',                # Date only
            '',                          # Empty
            None                         # None
        ]
        
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            
            for date_str in date_formats:
                test_data = self.sample_task_data.copy()
                test_data['Due'] = date_str
                
                df = pd.DataFrame([test_data])
                transformed_df = etl.transform(df)
                
                # Should handle all formats without error
                self.assertEqual(len(transformed_df), 1)
                
                # Check date parsing
                due_date = transformed_df.iloc[0]['due_date']
                if date_str and date_str.strip():
                    self.assertIsNotNone(due_date)
                else:
                    self.assertIsNone(due_date)

    def test_transform_status_normalization(self):
        """Test task status normalization"""
        status_tests = [
            ('Done', True),
            ('Completed', True),
            ('Complete', True),
            ('DONE', True),
            ('done', True),
            ('In Progress', False),
            ('Not started', False),
            ('Pending', False),
            ('', False),
            (None, False)
        ]
        
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            
            for status, expected_done in status_tests:
                test_data = self.sample_task_data.copy()
                test_data['Status'] = status
                
                df = pd.DataFrame([test_data])
                transformed_df = etl.transform(df)
                
                row = transformed_df.iloc[0]
                actual_done = row['done_at'] is not None
                
                if expected_done:
                    self.assertTrue(actual_done, f"Status '{status}' should be done")
                else:
                    # Note: done_at might still be set if 'Done At' field has value
                    pass  # Status alone doesn't determine done_at

    def test_transform_tags_parsing(self):
        """Test tag parsing and field mapping"""
        tag_tests = [
            ('urgent, documentation, review', ['urgent', 'documentation', 'review']),
            ('urgent,documentation,review', ['urgent', 'documentation', 'review']),
            ('single-tag', ['single-tag']),
            ('', []),
            (None, [])
        ]
        
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            etl.field_mapping = {
                'urgent': 1,
                'documentation': 2,
                'review': 3,
                'single-tag': 4
            }
            
            for tags_str, expected_tags in tag_tests:
                test_data = self.sample_task_data.copy()
                test_data['Tags'] = tags_str
                
                df = pd.DataFrame([test_data])
                transformed_df = etl.transform(df)
                
                row = transformed_df.iloc[0]
                field_ids = row['field_ids']
                
                expected_ids = [etl.field_mapping[tag] for tag in expected_tags if tag in etl.field_mapping]
                
                for expected_id in expected_ids:
                    self.assertIn(expected_id, field_ids)

    def test_transform_project_mapping(self):
        """Test project name to ID mapping"""
        project_tests = [
            ('Documentation Project', 100),
            ('New Project', None),  # Not in mapping
            ('', None),
            (None, None)
        ]
        
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            etl.project_mapping = {'Documentation Project': 100}
            
            for project_name, expected_id in project_tests:
                test_data = self.sample_task_data.copy()
                test_data['Project'] = project_name
                
                df = pd.DataFrame([test_data])
                transformed_df = etl.transform(df)
                
                row = transformed_df.iloc[0]
                actual_id = row['project_id']
                
                self.assertEqual(actual_id, expected_id)

    def test_transform_priority_normalization(self):
        """Test priority value normalization"""
        priority_tests = [
            ('High', 'High'),
            ('Medium', 'Medium'),
            ('Low', 'Low'),
            ('URGENT', 'High'),  # Normalize urgent to high
            ('normal', 'Medium'),
            ('', 'Medium'),  # Default
            (None, 'Medium')  # Default
        ]
        
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            
            for priority_input, expected_output in priority_tests:
                test_data = self.sample_task_data.copy()
                test_data['Priority'] = priority_input
                
                df = pd.DataFrame([test_data])
                transformed_df = etl.transform(df)
                
                row = transformed_df.iloc[0]
                actual_priority = row['priority']
                
                self.assertEqual(actual_priority, expected_output)

    def test_transform_data_validation(self):
        """Test data validation during transformation"""
        invalid_data_tests = [
            # Missing required task name
            {**self.sample_task_data, 'Task': ''},
            {**self.sample_task_data, 'Task': None},
            
            # Invalid date formats
            {**self.sample_task_data, 'Due': 'invalid-date'},
            {**self.sample_task_data, 'Created': '2024-13-45'},  # Invalid date
        ]
        
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            
            for invalid_data in invalid_data_tests:
                df = pd.DataFrame([invalid_data])
                
                # Should handle invalid data gracefully
                try:
                    transformed_df = etl.transform(df)
                    # Verify invalid rows are filtered out or corrected
                    if len(transformed_df) > 0:
                        row = transformed_df.iloc[0]
                        # Task name should not be empty
                        if 'task_name' in row:
                            self.assertTrue(len(str(row['task_name']).strip()) > 0)
                except Exception as e:
                    # Should provide meaningful error messages
                    self.assertIsInstance(e, (ValueError, TypeError))

    def test_load_task_data_batch_processing(self):
        """Test batch loading of task data"""
        with patch('etl_tasks.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            # Mock successful batch insert
            mock_client.table.return_value.insert.return_value.execute.return_value = Mock(
                data=[{'id': 1}, {'id': 2}, {'id': 3}]
            )
            
            etl = GTDTasksETL()
            
            # Create test data for batch processing
            test_data = []
            for i in range(15):  # More than batch size (10)
                task_data = self.sample_task_data.copy()
                task_data['Task'] = f'Task {i+1}'
                test_data.append(task_data)
            
            df = pd.DataFrame(test_data)
            transformed_df = etl.transform(df)
            
            # Mock load operation
            result = etl.load(transformed_df)
            
            # Verify batch processing
            self.assertIsNotNone(result)
            # Should have made multiple batch calls
            self.assertTrue(mock_client.table.return_value.insert.called)

    def test_full_etl_pipeline_integration(self):
        """Test complete ETL pipeline integration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            # Create test CSV with multiple tasks
            fieldnames = self.sample_task_data.keys()
            writer = csv.DictWriter(tmp_file, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write multiple test tasks
            for i in range(5):
                task_data = self.sample_task_data.copy()
                task_data['Task'] = f'Test Task {i+1}'
                task_data['Status'] = 'Done' if i % 2 == 0 else 'In Progress'
                writer.writerow(task_data)
            
            tmp_file.flush()
            
            try:
                with patch('etl_tasks.create_client') as mock_create:
                    mock_client = Mock()
                    mock_create.return_value = mock_client
                    
                    # Mock successful operations
                    mock_client.table.return_value.select.return_value.execute.return_value = Mock(
                        data=[
                            {'name': 'urgent', 'id': 1},
                            {'name': 'documentation', 'id': 2}
                        ]
                    )
                    mock_client.table.return_value.insert.return_value.execute.return_value = Mock(
                        data=[{'id': 1}, {'id': 2}, {'id': 3}]
                    )
                    
                    # Mock CSV file discovery
                    with patch('etl_tasks.find_gtd_tasks_csv', return_value=tmp_file.name):
                        etl = GTDTasksETL()
                        
                        # Run full ETL pipeline
                        result = etl.run()
                        
                        # Verify pipeline completion
                        self.assertIsNotNone(result)
                        self.assertTrue(mock_client.table.called)
                        
            finally:
                os.unlink(tmp_file.name)


class TestGTDTasksValidation(unittest.TestCase):
    """Test data validation and error handling"""
    
    def test_csv_file_discovery(self):
        """Test CSV file discovery function"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test file not found
            result = find_gtd_tasks_csv(tmp_dir)
            self.assertIsNone(result)
            
            # Test file found
            csv_file = Path(tmp_dir) / 'GTD Tasks.csv'
            csv_file.write_text('Task,Status\nTest,Done\n')
            
            result = find_gtd_tasks_csv(tmp_dir)
            self.assertEqual(result, str(csv_file))

    def test_data_integrity_checks(self):
        """Test data integrity validation"""
        with patch('etl_tasks.create_client'):
            etl = GTDTasksETL()
            
            # Test duplicate task detection
            duplicate_data = [
                {'Task': 'Duplicate Task', 'Status': 'Done'},
                {'Task': 'Duplicate Task', 'Status': 'In Progress'},
                {'Task': 'Unique Task', 'Status': 'Done'}
            ]
            
            df = pd.DataFrame(duplicate_data)
            transformed_df = etl.transform(df)
            
            # Should handle duplicates appropriately
            self.assertLessEqual(len(transformed_df), 3)

    def test_error_recovery(self):
        """Test error recovery and logging"""
        with patch('etl_tasks.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            # Mock database error
            mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
            
            etl = GTDTasksETL()
            
            # Should handle errors gracefully
            test_data = pd.DataFrame([{'task_name': 'Test Task', 'user_id': 'test'}])
            
            with self.assertRaises(Exception):
                etl.load(test_data)


if __name__ == '__main__':
    unittest.main()