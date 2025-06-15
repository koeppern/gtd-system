"""
Tests für JWT-Bypass-Funktionalität in Development Environment
"""
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_current_user

client = TestClient(app)


class TestJWTBypass:
    """Test JWT-Bypass für Development/Testing"""
    
    def test_jwt_bypass_enabled(self):
        """Test JWT-Bypass wenn DISABLE_JWT_AUTH=true"""
        with patch.dict(os.environ, {'DISABLE_JWT_AUTH': 'true'}):
            # Dependency direkt testen
            user = get_current_user()
            
            assert user is not None
            assert user["email"] == "test@example.com"
            assert user["user_id"] == os.getenv('DEFAULT_USER_ID', '00000000-0000-0000-0000-000000000001')
            assert user["role"] == "authenticated"
            assert user["iss"] == "mock-auth"
    
    def test_jwt_bypass_disabled(self):
        """Test normale JWT-Verification wenn DISABLE_JWT_AUTH=false"""
        with patch.dict(os.environ, {'DISABLE_JWT_AUTH': 'false'}):
            # Ohne Authorization Header sollte 401 kommen
            with pytest.raises(Exception):  # HTTPException erwartet
                get_current_user(authorization=None)
    
    def test_jwt_bypass_not_set(self):
        """Test normale JWT-Verification wenn DISABLE_JWT_AUTH nicht gesetzt"""
        # Environment Variable entfernen falls gesetzt
        env_copy = os.environ.copy()
        if 'DISABLE_JWT_AUTH' in env_copy:
            del env_copy['DISABLE_JWT_AUTH']
            
        with patch.dict(os.environ, env_copy, clear=True):
            # Ohne Authorization Header sollte 401 kommen
            with pytest.raises(Exception):  # HTTPException erwartet
                get_current_user(authorization=None)
    
    def test_api_endpoint_with_bypass(self):
        """Test API-Endpoint mit JWT-Bypass"""
        with patch.dict(os.environ, {'DISABLE_JWT_AUTH': 'true'}):
            response = client.get("/api/users/me")
            
            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data
            assert "email" in data
            assert data["email"] == "test@example.com"
    
    def test_api_endpoint_without_bypass_no_auth(self):
        """Test API-Endpoint ohne JWT-Bypass und ohne Authorization"""
        with patch.dict(os.environ, {'DISABLE_JWT_AUTH': 'false'}):
            response = client.get("/api/users/me")
            
            # Sollte 401 Unauthorized zurückgeben
            assert response.status_code == 401
    
    def test_api_endpoint_without_bypass_with_auth(self):
        """Test API-Endpoint ohne JWT-Bypass aber mit Authorization Header"""
        with patch.dict(os.environ, {'DISABLE_JWT_AUTH': 'false'}):
            # Mock JWT Token (wird ohne Signature-Verification akzeptiert)
            headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"}
            
            response = client.get("/api/users/me", headers=headers)
            
            # Mit gültigem Token sollte es funktionieren
            assert response.status_code == 200
    
    def test_environment_variable_case_insensitive(self):
        """Test dass DISABLE_JWT_AUTH case-insensitive ist"""
        test_cases = ['True', 'TRUE', 'true', 'tRuE']
        
        for value in test_cases:
            with patch.dict(os.environ, {'DISABLE_JWT_AUTH': value}):
                user = get_current_user()
                assert user is not None
                assert user["email"] == "test@example.com"
    
    def test_custom_default_user_id(self):
        """Test dass custom DEFAULT_USER_ID verwendet wird"""
        custom_user_id = "12345678-1234-1234-1234-123456789012"
        
        with patch.dict(os.environ, {
            'DISABLE_JWT_AUTH': 'true',
            'DEFAULT_USER_ID': custom_user_id
        }):
            user = get_current_user()
            
            assert user["user_id"] == custom_user_id
            assert user["sub"] == custom_user_id


class TestProductionSafety:
    """Test Production-Sicherheit"""
    
    def test_production_environment_safe(self):
        """Test dass Production-Environment sicher ist"""
        # Simuliere Production Environment (keine DISABLE_JWT_AUTH Variable)
        env_copy = os.environ.copy()
        if 'DISABLE_JWT_AUTH' in env_copy:
            del env_copy['DISABLE_JWT_AUTH']
            
        with patch.dict(os.environ, env_copy, clear=True):
            # API-Call ohne Authorization sollte 401 geben
            response = client.get("/api/users/me")
            assert response.status_code == 401
            
            # Direkte Dependency sollte Exception werfen
            with pytest.raises(Exception):
                get_current_user(authorization=None)
    
    def test_false_values_disable_bypass(self):
        """Test dass verschiedene 'false'-Werte den Bypass deaktivieren"""
        false_values = ['false', 'False', 'FALSE', 'f', 'F', '0', '', 'no', 'off']
        
        for value in false_values:
            with patch.dict(os.environ, {'DISABLE_JWT_AUTH': value}):
                response = client.get("/api/users/me")
                assert response.status_code == 401, f"Value '{value}' should disable bypass"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])