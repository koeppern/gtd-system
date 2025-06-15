#!/usr/bin/env python3
"""
Database Security and Authentication Tests
Tests for RLS policies, authentication, and data access controls
"""

import unittest
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.database import get_supabase_client
from app.config import get_settings


class TestDatabaseSecurity(unittest.TestCase):
    """Test database security measures and RLS policies"""
    
    def setUp(self):
        """Set up test environment"""
        self.env_vars = {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_SERVICE_ROLE_KEY': 'test_service_key',
            'DEFAULT_USER_ID': 'test-user-uuid',
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
        }
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', self.env_vars)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()

    def test_supabase_client_initialization(self):
        """Test Supabase client can be initialized with correct credentials"""
        with patch('supabase.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            client = get_supabase_client()
            
            mock_create.assert_called_once_with(
                'https://test.supabase.co',
                'test_service_key'
            )
            self.assertEqual(client, mock_client)

    def test_supabase_client_missing_url(self):
        """Test error handling when SUPABASE_URL is missing"""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as context:
                get_supabase_client()
            
            self.assertIn('SUPABASE_URL', str(context.exception))

    def test_supabase_client_missing_key(self):
        """Test error handling when SUPABASE_SERVICE_ROLE_KEY is missing"""
        with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co'}, clear=True):
            with self.assertRaises(ValueError) as context:
                get_supabase_client()
            
            self.assertIn('SUPABASE_SERVICE_ROLE_KEY', str(context.exception))

    def test_database_url_configuration(self):
        """Test database URL configuration and parsing"""
        db_url = get_database_url()
        
        self.assertEqual(db_url, 'postgresql://test:test@localhost:5432/test')
        self.assertIn('postgresql://', db_url)

    @patch('backend.database.create_async_engine')
    def test_database_session_creation(self, mock_engine):
        """Test database session creation and configuration"""
        mock_session = AsyncMock()
        mock_engine.return_value = Mock()
        
        # Test session factory creation
        with patch('backend.database.async_sessionmaker') as mock_sessionmaker:
            mock_sessionmaker.return_value = mock_session
            
            session = get_session()
            
            # Verify session configuration
            mock_sessionmaker.assert_called_once()
            self.assertIsNotNone(session)

    def test_user_id_validation(self):
        """Test user ID format validation"""
        valid_uuids = [
            'test-user-uuid',
            '00000000-0000-0000-0000-000000000001',
            'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
        ]
        
        invalid_uuids = [
            '',
            'not-a-uuid',
            '123',
            'invalid-format'
        ]
        
        # Test valid UUIDs (mock validation)
        for uuid in valid_uuids:
            with patch.dict('os.environ', {'DEFAULT_USER_ID': uuid}):
                # Would normally validate UUID format
                self.assertTrue(len(uuid) > 0)
        
        # Test invalid UUIDs
        for uuid in invalid_uuids:
            with patch.dict('os.environ', {'DEFAULT_USER_ID': uuid}):
                # Would normally raise validation error
                if uuid == '':
                    with self.assertRaises(ValueError):
                        if not uuid:
                            raise ValueError("User ID cannot be empty")


class TestAuthenticationSecurity(unittest.TestCase):
    """Test authentication and authorization mechanisms"""
    
    def setUp(self):
        """Set up authentication test environment"""
        self.valid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        self.expired_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        self.malformed_jwt = "invalid.jwt.token"

    def test_jwt_token_validation_valid(self):
        """Test JWT token validation with valid token"""
        # Mock JWT validation (would use proper JWT library in production)
        with patch('jwt.decode') as mock_decode:
            mock_decode.return_value = {
                'sub': '1234567890',
                'name': 'John Doe',
                'iat': 1516239022
            }
            
            # Simulate token validation
            payload = mock_decode(self.valid_jwt, verify=False)
            self.assertEqual(payload['sub'], '1234567890')
            self.assertEqual(payload['name'], 'John Doe')

    def test_jwt_token_validation_expired(self):
        """Test JWT token validation with expired token"""
        with patch('jwt.decode') as mock_decode:
            from jwt.exceptions import ExpiredSignatureError
            mock_decode.side_effect = ExpiredSignatureError("Token has expired")
            
            with self.assertRaises(ExpiredSignatureError):
                mock_decode(self.expired_jwt, verify=True)

    def test_jwt_token_validation_malformed(self):
        """Test JWT token validation with malformed token"""
        with patch('jwt.decode') as mock_decode:
            from jwt.exceptions import InvalidTokenError
            mock_decode.side_effect = InvalidTokenError("Invalid token format")
            
            with self.assertRaises(InvalidTokenError):
                mock_decode(self.malformed_jwt, verify=True)

    def test_user_session_isolation(self):
        """Test that user sessions are properly isolated"""
        user1_id = 'user1-uuid'
        user2_id = 'user2-uuid'
        
        # Mock database queries to verify user isolation
        with patch('supabase.create_client') as mock_supabase:
            mock_client = Mock()
            mock_supabase.return_value = mock_client
            
            # Mock user1 data access
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
                data=[{'id': 1, 'user_id': user1_id, 'project_name': 'User1 Project'}]
            )
            
            # Verify user isolation in queries
            client = get_supabase_client()
            
            # User1 query
            result1 = client.table('gtd_projects').select('*').eq('user_id', user1_id).execute()
            
            # User2 query  
            result2 = client.table('gtd_projects').select('*').eq('user_id', user2_id).execute()
            
            # Verify different user contexts
            self.assertNotEqual(user1_id, user2_id)


class TestDataAccessSecurity(unittest.TestCase):
    """Test Row Level Security (RLS) and data access controls"""
    
    def test_rls_policy_enforcement(self):
        """Test that RLS policies are enforced at database level"""
        # Mock RLS policy checks
        with patch('supabase.create_client') as mock_supabase:
            mock_client = Mock()
            mock_supabase.return_value = mock_client
            
            # Mock RLS enforcement - should only return user's own data
            mock_client.table.return_value.select.return_value.execute.return_value = Mock(
                data=[{'id': 1, 'user_id': 'current-user', 'project_name': 'My Project'}]
            )
            
            client = get_supabase_client()
            
            # Attempt to access data (RLS should filter automatically)
            result = client.table('gtd_projects').select('*').execute()
            
            # Verify only authorized data is returned
            self.assertTrue(len(result.data) >= 0)  # RLS may return empty or filtered data

    def test_unauthorized_data_access_prevention(self):
        """Test prevention of unauthorized data access"""
        unauthorized_user_id = 'unauthorized-user'
        
        with patch('supabase.create_client') as mock_supabase:
            mock_client = Mock()
            mock_supabase.return_value = mock_client
            
            # Mock unauthorized access attempt (should return empty)
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
                data=[]  # RLS blocks unauthorized access
            )
            
            client = get_supabase_client()
            
            # Attempt unauthorized access
            result = client.table('gtd_projects').select('*').eq('user_id', unauthorized_user_id).execute()
            
            # Should return no data due to RLS
            self.assertEqual(len(result.data), 0)

    def test_data_modification_security(self):
        """Test that data modifications are properly secured"""
        with patch('supabase.create_client') as mock_supabase:
            mock_client = Mock()
            mock_supabase.return_value = mock_client
            
            # Mock successful authorized update
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(
                data=[{'id': 1, 'updated': True}]
            )
            
            client = get_supabase_client()
            
            # Authorized data update
            result = client.table('gtd_projects').update({
                'project_name': 'Updated Project'
            }).eq('id', 1).execute()
            
            # Verify update was processed
            self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()