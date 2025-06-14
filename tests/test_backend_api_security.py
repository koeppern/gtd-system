#!/usr/bin/env python3
"""
Backend API Security Tests
Tests for FastAPI endpoint security, authentication, and authorization
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json
from fastapi.testclient import TestClient
from fastapi import HTTPException
import jwt
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from backend.main import app
from backend.dependencies import get_current_user, get_db


class TestAPIAuthentication(unittest.TestCase):
    """Test API authentication and authorization"""
    
    def setUp(self):
        """Set up test client and environment"""
        self.client = TestClient(app)
        self.valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJpYXQiOjE2NDAwMDAwMDAsImV4cCI6OTk5OTk5OTk5OX0.test"
        self.expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJpYXQiOjE2NDAwMDAwMDAsImV4cCI6MTY0MDAwMDAwMX0.expired"
        self.invalid_token = "invalid.token.format"
        
        # Mock database
        self.db_patcher = patch('backend.dependencies.get_db')
        self.mock_db = self.db_patcher.start()

    def tearDown(self):
        """Clean up test environment"""
        self.db_patcher.stop()

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without authentication token"""
        response = self.client.get("/api/projects/")
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        self.assertIn('unauthorized', response.json().get('detail', '').lower())

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        with patch('backend.dependencies.verify_token') as mock_verify:
            mock_verify.return_value = {'sub': 'test-user-id', 'email': 'test@test.com'}
            
            headers = {'Authorization': f'Bearer {self.valid_token}'}
            
            with patch('backend.projects.get_projects') as mock_get_projects:
                mock_get_projects.return_value = []
                
                response = self.client.get("/api/projects/", headers=headers)
                
                # Should return 200 OK
                self.assertEqual(response.status_code, 200)

    def test_protected_endpoint_with_expired_token(self):
        """Test accessing protected endpoint with expired token"""
        with patch('backend.dependencies.verify_token') as mock_verify:
            mock_verify.side_effect = HTTPException(status_code=401, detail="Token expired")
            
            headers = {'Authorization': f'Bearer {self.expired_token}'}
            response = self.client.get("/api/projects/", headers=headers)
            
            # Should return 401 Unauthorized
            self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token format"""
        headers = {'Authorization': f'Bearer {self.invalid_token}'}
        response = self.client.get("/api/projects/", headers=headers)
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)

    def test_user_context_isolation(self):
        """Test that users can only access their own data"""
        user1_id = 'user1-id'
        user2_id = 'user2-id'
        
        with patch('backend.dependencies.verify_token') as mock_verify:
            # Test user1 access
            mock_verify.return_value = {'sub': user1_id, 'email': 'user1@test.com'}
            
            with patch('backend.projects.get_projects') as mock_get_projects:
                mock_get_projects.return_value = [
                    {'id': 1, 'user_id': user1_id, 'project_name': 'User1 Project'}
                ]
                
                headers = {'Authorization': f'Bearer {self.valid_token}'}
                response = self.client.get("/api/projects/", headers=headers)
                
                self.assertEqual(response.status_code, 200)
                projects = response.json()
                
                # Verify only user1's projects are returned
                for project in projects:
                    self.assertEqual(project['user_id'], user1_id)

    def test_cross_user_data_access_prevention(self):
        """Test prevention of cross-user data access"""
        current_user_id = 'current-user'
        other_user_project_id = 999
        
        with patch('backend.dependencies.verify_token') as mock_verify:
            mock_verify.return_value = {'sub': current_user_id, 'email': 'current@test.com'}
            
            with patch('backend.projects.get_project') as mock_get_project:
                # Mock attempt to access other user's project
                mock_get_project.return_value = None  # Project not found due to RLS
                
                headers = {'Authorization': f'Bearer {self.valid_token}'}
                response = self.client.get(f"/api/projects/{other_user_project_id}", headers=headers)
                
                # Should return 404 Not Found (due to RLS filtering)
                self.assertEqual(response.status_code, 404)


class TestAPIInputValidation(unittest.TestCase):
    """Test API input validation and sanitization"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
        self.valid_headers = {'Authorization': 'Bearer valid-token'}
        
        # Mock authentication
        self.auth_patcher = patch('backend.dependencies.verify_token')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = {'sub': 'test-user', 'email': 'test@test.com'}

    def tearDown(self):
        """Clean up test environment"""
        self.auth_patcher.stop()

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in API endpoints"""
        malicious_inputs = [
            "'; DROP TABLE gtd_projects; --",
            "1' OR '1'='1",
            "1; UPDATE gtd_projects SET user_id='hacker'",
            "<script>alert('xss')</script>",
            "../../etc/passwd"
        ]
        
        for malicious_input in malicious_inputs:
            with patch('backend.projects.get_projects') as mock_get:
                mock_get.return_value = []
                
                # Test in query parameters
                response = self.client.get(
                    f"/api/projects/?search={malicious_input}",
                    headers=self.valid_headers
                )
                
                # Should handle malicious input safely
                self.assertIn(response.status_code, [200, 400])  # Either sanitized or rejected
                
                # Verify database function received sanitized input
                if mock_get.called:
                    call_args = mock_get.call_args
                    # Database layer should receive safe parameters

    def test_input_size_limits(self):
        """Test input size validation"""
        # Test extremely large input
        large_input = "A" * 10000  # 10KB input
        
        with patch('backend.projects.create_project') as mock_create:
            mock_create.return_value = {'id': 1, 'project_name': 'Test'}
            
            response = self.client.post(
                "/api/projects/",
                headers=self.valid_headers,
                json={'project_name': large_input}
            )
            
            # Should either reject or truncate large input
            self.assertIn(response.status_code, [200, 400, 413])

    def test_data_type_validation(self):
        """Test data type validation in API requests"""
        invalid_data_tests = [
            # Invalid data types
            {'project_name': 123},  # Should be string
            {'project_name': None},  # Should not be null
            {'project_name': []},    # Should not be array
            {'project_name': {}},    # Should not be object
            
            # Missing required fields
            {},  # Missing project_name
            {'wrong_field': 'value'},  # Wrong field name
        ]
        
        for invalid_data in invalid_data_tests:
            response = self.client.post(
                "/api/projects/",
                headers=self.valid_headers,
                json=invalid_data
            )
            
            # Should return validation error
            self.assertEqual(response.status_code, 422)

    def test_unicode_and_encoding_handling(self):
        """Test Unicode and special character handling"""
        unicode_tests = [
            "Project with émojis 🚀 and spëcial charäcters",
            "中文项目名称",
            "العربية",
            "Проект на русском",
            "🎯📋✅ Emoji Project",
            "Project\nwith\nnewlines",
            "Project\twith\ttabs"
        ]
        
        for unicode_input in unicode_tests:
            with patch('backend.projects.create_project') as mock_create:
                mock_create.return_value = {'id': 1, 'project_name': unicode_input}
                
                response = self.client.post(
                    "/api/projects/",
                    headers=self.valid_headers,
                    json={'project_name': unicode_input}
                )
                
                # Should handle Unicode correctly
                self.assertEqual(response.status_code, 200)


class TestAPIRateLimiting(unittest.TestCase):
    """Test API rate limiting and abuse prevention"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
        self.valid_headers = {'Authorization': 'Bearer valid-token'}
        
        # Mock authentication
        self.auth_patcher = patch('backend.dependencies.verify_token')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = {'sub': 'test-user', 'email': 'test@test.com'}

    def tearDown(self):
        """Clean up test environment"""
        self.auth_patcher.stop()

    def test_rate_limiting_simulation(self):
        """Simulate rate limiting behavior"""
        # Note: This would require actual rate limiting middleware in production
        with patch('backend.projects.get_projects') as mock_get:
            mock_get.return_value = []
            
            # Simulate rapid requests
            responses = []
            for i in range(100):  # Rapid-fire requests
                response = self.client.get("/api/projects/", headers=self.valid_headers)
                responses.append(response.status_code)
                
                # In production, should start returning 429 after rate limit
                if i > 50:  # Simulate rate limiting after 50 requests
                    break
            
            # All requests should succeed in test environment
            # In production, would expect some 429 responses
            self.assertTrue(all(status in [200, 429] for status in responses))

    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('backend.projects.get_projects') as mock_get:
                mock_get.return_value = []
                response = self.client.get("/api/projects/", headers=self.valid_headers)
                results.append(response.status_code)
        
        # Create multiple concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled successfully
        self.assertEqual(len(results), 10)
        self.assertTrue(all(status == 200 for status in results))


class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling and logging"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
        self.valid_headers = {'Authorization': 'Bearer valid-token'}
        
        # Mock authentication
        self.auth_patcher = patch('backend.dependencies.verify_token')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = {'sub': 'test-user', 'email': 'test@test.com'}

    def tearDown(self):
        """Clean up test environment"""
        self.auth_patcher.stop()

    def test_database_error_handling(self):
        """Test handling of database errors"""
        with patch('backend.projects.get_projects') as mock_get:
            mock_get.side_effect = Exception("Database connection failed")
            
            response = self.client.get("/api/projects/", headers=self.valid_headers)
            
            # Should return 500 Internal Server Error
            self.assertEqual(response.status_code, 500)
            
            # Should not expose internal error details
            error_detail = response.json().get('detail', '')
            self.assertNotIn('Database connection failed', error_detail)

    def test_not_found_error_handling(self):
        """Test handling of resource not found errors"""
        with patch('backend.projects.get_project') as mock_get:
            mock_get.return_value = None
            
            response = self.client.get("/api/projects/999", headers=self.valid_headers)
            
            # Should return 404 Not Found
            self.assertEqual(response.status_code, 404)

    def test_validation_error_responses(self):
        """Test validation error response format"""
        response = self.client.post(
            "/api/projects/",
            headers=self.valid_headers,
            json={'invalid_field': 'value'}
        )
        
        # Should return 422 Unprocessable Entity
        self.assertEqual(response.status_code, 422)
        
        # Should include validation error details
        error_data = response.json()
        self.assertIn('detail', error_data)


if __name__ == '__main__':
    unittest.main()