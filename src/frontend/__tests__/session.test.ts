/**
 * Session Management Tests
 * Tests for JWT token handling, session validation, and authentication logic
 */

import { getSessionFromRequest, isAuthenticationRequired } from '../src/lib/session';
import { NextRequest } from 'next/server';

// Mock the backend-client module
jest.mock('../src/lib/backend-client', () => ({
  getBackendConfig: jest.fn(() => ({
    url: 'http://localhost:8000',
    hasServiceKey: true,
    defaultUserId: 'test-default-user-id'
  }))
}));

describe('Session Management', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getSessionFromRequest', () => {
    it('should return default user for localhost', async () => {
      const mockRequest = {
        headers: new Map(),
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toEqual({
        userId: 'test-default-user-id',
        isAuthenticated: true,
        email: 'dev@localhost.local'
      });
    });

    it('should extract JWT from Authorization header', async () => {
      // Mock 127.0.0.1 backend (requires auth)
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const validJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJleHAiOjk5OTk5OTk5OTl9.test';
      
      const mockHeaders = new Map();
      mockHeaders.set('authorization', `Bearer ${validJWT}`);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toEqual({
        userId: 'test-user-id',
        authToken: validJWT,
        email: 'test@test.com',
        isAuthenticated: true
      });
    });

    it('should extract JWT from cookies', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const validJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJleHAiOjk5OTk5OTk5OTl9.test';
      
      const mockCookies = new Map();
      mockCookies.set('supabase-auth-token', { value: validJWT });

      const mockRequest = {
        headers: new Map(),
        cookies: mockCookies,
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toEqual({
        userId: 'test-user-id',
        authToken: validJWT,
        email: 'test@test.com',
        isAuthenticated: true
      });
    });

    it('should extract JWT from custom header', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://production.example.com:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const validJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJleHAiOjk5OTk5OTk5OTl9.test';
      
      const mockHeaders = new Map();
      mockHeaders.set('x-supabase-auth', validJWT);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toEqual({
        userId: 'test-user-id',
        authToken: validJWT,
        email: 'test@test.com',
        isAuthenticated: true
      });
    });

    it('should return null for missing JWT on non-localhost', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://production.example.com:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const mockRequest = {
        headers: new Map(),
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toBeNull();
    });

    it('should return null for invalid JWT format', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const invalidJWT = 'invalid.jwt.format';
      
      const mockHeaders = new Map();
      mockHeaders.set('authorization', `Bearer ${invalidJWT}`);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toBeNull();
    });

    it('should return null for expired JWT', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      // JWT with past expiration
      const expiredJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJleHAiOjE2NDAwMDAwMDB9.expired';
      
      const mockHeaders = new Map();
      mockHeaders.set('authorization', `Bearer ${expiredJWT}`);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toBeNull();
    });

    it('should handle malformed JWT gracefully', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const malformedJWTs = [
        'not.jwt.at.all',
        'onlyonepart',
        'two.parts',
        '...',
        'header.payload.signature.extra'
      ];

      for (const malformedJWT of malformedJWTs) {
        const mockHeaders = new Map();
        mockHeaders.set('authorization', `Bearer ${malformedJWT}`);

        const mockRequest = {
          headers: mockHeaders,
          cookies: new Map(),
          url: 'http://localhost:3000/api/test'
        } as unknown as NextRequest;

        const session = await getSessionFromRequest(mockRequest);

        expect(session).toBeNull();
      }
    });
  });

  describe('isAuthenticationRequired', () => {
    it('should return false for localhost', () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://localhost:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const result = isAuthenticationRequired();
      expect(result).toBe(false);
    });

    it('should return true for 127.0.0.1', () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const result = isAuthenticationRequired();
      expect(result).toBe(true);
    });

    it('should return true for production URLs', () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'https://api.production.com:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const result = isAuthenticationRequired();
      expect(result).toBe(true);
    });

    it('should return true for invalid URL (fail safe)', () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'invalid-url',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const result = isAuthenticationRequired();
      expect(result).toBe(true); // Fail safe to require auth
    });
  });

  describe('JWT Token Validation', () => {
    it('should validate JWT structure', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      // Valid JWT with proper structure
      const validJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJleHAiOjk5OTk5OTk5OTl9.signature';
      
      const mockHeaders = new Map();
      mockHeaders.set('authorization', `Bearer ${validJWT}`);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).not.toBeNull();
      expect(session?.userId).toBe('test-user-id');
      expect(session?.email).toBe('test@test.com');
    });

    it('should require sub claim in JWT', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      // JWT without sub claim
      const jwtWithoutSub = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJleHAiOjk5OTk5OTk5OTl9.signature';
      
      const mockHeaders = new Map();
      mockHeaders.set('authorization', `Bearer ${jwtWithoutSub}`);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toBeNull();
    });
  });

  describe('Security Edge Cases', () => {
    it('should handle extremely long tokens', async () => {
      const { getBackendConfig } = require('../src/lib/backend-client');
      getBackendConfig.mockReturnValue({
        url: 'http://127.0.0.1:8000',
        hasServiceKey: true,
        defaultUserId: 'test-default-user-id'
      });

      const veryLongToken = 'x'.repeat(10000); // Extremely long token
      
      const mockHeaders = new Map();
      mockHeaders.set('authorization', `Bearer ${veryLongToken}`);

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      expect(session).toBeNull(); // Should reject malformed token
    });

    it('should handle null and undefined values', async () => {
      const mockRequest = {
        headers: new Map([['authorization', 'Bearer null']]),
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      // Should handle gracefully (localhost should still work)
      expect(session).not.toBeNull();
    });

    it('should handle special characters in headers', async () => {
      const mockHeaders = new Map();
      mockHeaders.set('authorization', 'Bearer token-with-special-chars-!@#$%^&*()');

      const mockRequest = {
        headers: mockHeaders,
        cookies: new Map(),
        url: 'http://localhost:3000/api/test'
      } as unknown as NextRequest;

      const session = await getSessionFromRequest(mockRequest);

      // Should handle gracefully for localhost
      expect(session).not.toBeNull();
    });
  });
});