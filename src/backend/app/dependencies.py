"""
FastAPI dependencies for Supabase database connection
"""
import os
from fastapi import HTTPException, status, Depends, Header
from typing import Optional
import jwt

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Get current user from JWT token or bypass if disabled"""
    
    # Check if JWT authentication is disabled for testing
    disable_jwt_auth = os.getenv('DISABLE_JWT_AUTH', 'false').lower() == 'true'
    
    if disable_jwt_auth:
        # Return mock user for development/testing
        return {
            "user_id": os.getenv('DEFAULT_USER_ID', '00000000-0000-0000-0000-000000000001'),
            "email": "test@example.com",
            "sub": os.getenv('DEFAULT_USER_ID', '00000000-0000-0000-0000-000000000001'),
            "iss": "mock-auth",
            "aud": "authenticated",
            "role": "authenticated"
        }
    
    # Normal JWT verification
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        # Verify JWT token
        payload = verify_token(token)
        return payload
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

def verify_token(token: str) -> dict:
    """Verify JWT token and return user data"""
    try:
        # In production, use proper JWT verification with Supabase public key
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db():
    """Database dependency - placeholder for testing"""
    return None