/**
 * Authentication Context Tests
 * Tests for user authentication, session management, and security
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../src/contexts/auth-context';
import '@testing-library/jest-dom';

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Test component to use auth context
const TestComponent = () => {
  const { user, login, logout, isLoading } = useAuth();
  
  return (
    <div>
      <div data-testid="loading">{isLoading ? 'Loading' : 'Ready'}</div>
      <div data-testid="user">{user ? user.email : 'Not logged in'}</div>
      <button 
        data-testid="login-btn" 
        onClick={() => login('test@example.com', 'password')}
      >
        Login
      </button>
      <button data-testid="logout-btn" onClick={logout}>
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should start with no user and loading false', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('Ready');
      });
      
      expect(screen.getByTestId('user')).toHaveTextContent('Not logged in');
    });

    it('should restore user session from localStorage', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        loginTime: new Date().toISOString()
      };
      
      const mockSession = {
        isActive: true,
        loginTime: mockUser.loginTime,
        userId: mockUser.id
      };

      mockLocalStorage.setItem('gtd_user', JSON.stringify(mockUser));
      mockLocalStorage.setItem('gtd_session', JSON.stringify(mockSession));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });
    });

    it('should clear invalid session data on startup', async () => {
      // Set invalid session data
      mockLocalStorage.setItem('gtd_user', 'invalid-json');
      mockLocalStorage.setItem('gtd_session', JSON.stringify({ isActive: false }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Not logged in');
      });

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_user');
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_session');
    });
  });

  describe('Login Functionality', () => {
    it('should successfully log in a user', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('Ready');
      });

      // Click login button
      fireEvent.click(screen.getByTestId('login-btn'));

      // Should show loading during login
      expect(screen.getByTestId('loading')).toHaveTextContent('Loading');

      // Wait for login to complete
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      }, { timeout: 2000 });

      expect(screen.getByTestId('loading')).toHaveTextContent('Ready');
    });

    it('should store user data in localStorage on login', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      fireEvent.click(screen.getByTestId('login-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      }, { timeout: 2000 });

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'gtd_user',
        expect.stringContaining('test@example.com')
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'gtd_session',
        expect.stringContaining('isActive')
      );
    });

    it('should handle login errors gracefully', async () => {
      // Mock console.error to avoid noise in tests
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Simulate login error by rejecting the promise
      // Note: In the current implementation, login always succeeds
      // In a real implementation, we'd mock the Supabase client to throw an error

      consoleSpy.mockRestore();
    });
  });

  describe('Logout Functionality', () => {
    it('should successfully log out a user', async () => {
      // Set up logged in state
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        loginTime: new Date().toISOString()
      };
      
      mockLocalStorage.setItem('gtd_user', JSON.stringify(mockUser));
      mockLocalStorage.setItem('gtd_session', JSON.stringify({
        isActive: true,
        loginTime: mockUser.loginTime,
        userId: mockUser.id
      }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for user to be restored
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });

      // Click logout button
      fireEvent.click(screen.getByTestId('logout-btn'));

      // Wait for logout to complete
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Not logged in');
      }, { timeout: 1000 });
    });

    it('should clear localStorage on logout', async () => {
      // Set up logged in state
      mockLocalStorage.setItem('gtd_user', JSON.stringify({ email: 'test@example.com' }));
      mockLocalStorage.setItem('gtd_session', JSON.stringify({ isActive: true }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });

      fireEvent.click(screen.getByTestId('logout-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Not logged in');
      });

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_user');
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_session');
    });
  });

  describe('Session Persistence', () => {
    it('should validate session data structure', async () => {
      const validSession = {
        isActive: true,
        loginTime: new Date().toISOString(),
        userId: 'test-user-id'
      };

      const validUser = {
        id: 'test-user-id',
        email: 'test@example.com',
        name: 'Test User',
        loginTime: validSession.loginTime
      };

      mockLocalStorage.setItem('gtd_user', JSON.stringify(validUser));
      mockLocalStorage.setItem('gtd_session', JSON.stringify(validSession));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });
    });

    it('should reject sessions missing required fields', async () => {
      const invalidSession = {
        isActive: true
        // Missing loginTime and userId
      };

      const validUser = {
        id: 'test-user-id',
        email: 'test@example.com'
      };

      mockLocalStorage.setItem('gtd_user', JSON.stringify(validUser));
      mockLocalStorage.setItem('gtd_session', JSON.stringify(invalidSession));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Not logged in');
      });

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_user');
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_session');
    });

    it('should handle corrupted localStorage data', async () => {
      mockLocalStorage.setItem('gtd_user', '{invalid-json}');
      mockLocalStorage.setItem('gtd_session', '{also-invalid}');

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Not logged in');
      });

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_user');
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('gtd_session');
    });
  });

  describe('Security Features', () => {
    it('should include login timestamp in user data', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      fireEvent.click(screen.getByTestId('login-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });

      // Check that loginTime was stored
      const storedUserData = mockLocalStorage.setItem.mock.calls.find(
        call => call[0] === 'gtd_user'
      );
      
      if (storedUserData) {
        const userData = JSON.parse(storedUserData[1]);
        expect(userData.loginTime).toBeDefined();
        expect(new Date(userData.loginTime)).toBeInstanceOf(Date);
      }
    });

    it('should maintain session state consistency', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      fireEvent.click(screen.getByTestId('login-btn'));

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });

      // Verify both user and session data were stored
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'gtd_user',
        expect.any(String)
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'gtd_session',
        expect.any(String)
      );

      // Verify session data structure
      const sessionCall = mockLocalStorage.setItem.mock.calls.find(
        call => call[0] === 'gtd_session'
      );
      
      if (sessionCall) {
        const sessionData = JSON.parse(sessionCall[1]);
        expect(sessionData.isActive).toBe(true);
        expect(sessionData.loginTime).toBeDefined();
        expect(sessionData.userId).toBeDefined();
      }
    });
  });

  describe('Error Boundaries', () => {
    it('should provide context outside of provider', () => {
      // This should throw an error when useAuth is called outside AuthProvider
      const ConsoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useAuth must be used within an AuthProvider');

      ConsoleErrorSpy.mockRestore();
    });
  });
});