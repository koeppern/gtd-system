'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  loginTime?: string; // Zeitstempel der Anmeldung
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Debug: Test if console.log works
  console.log('AuthProvider initialized, isLoading:', isLoading);

  // Check for existing session on mount
  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      // Check for stored session in localStorage
      const storedUser = localStorage.getItem('gtd_user');
      const storedSession = localStorage.getItem('gtd_session');
      
      if (storedUser && storedSession) {
        const user = JSON.parse(storedUser);
        const sessionData = JSON.parse(storedSession);
        
        // Check if session is still valid (optional: add expiration check)
        const isValidSession = sessionData.isActive && sessionData.loginTime;
        
        if (isValidSession) {
          console.log('Restoring user session from localStorage');
          setUser(user);
        } else {
          // Clean up invalid session
          localStorage.removeItem('gtd_user');
          localStorage.removeItem('gtd_session');
        }
      }
    } catch (error) {
      console.error('Session check failed:', error);
      // Clean up potentially corrupted data
      localStorage.removeItem('gtd_user');
      localStorage.removeItem('gtd_session');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, _password: string) => {
    console.log('Login attempt started for:', email);
    setIsLoading(true);
    try {
      // TODO: Implement actual Supabase authentication
      // For now, simulate successful login
      const loginTime = new Date().toISOString();
      const mockUser: User = {
        id: '1',
        email,
        name: email.split('@')[0], // Use email prefix as name
        loginTime,
      };
      
      // Store user data and session info for persistence
      const sessionData = {
        isActive: true,
        loginTime,
        userId: mockUser.id,
      };
      
      setUser(mockUser);
      localStorage.setItem('gtd_user', JSON.stringify(mockUser));
      localStorage.setItem('gtd_session', JSON.stringify(sessionData));
      
      console.log('User logged in and session saved to localStorage');
      console.log('Login process completed successfully for:', email);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      console.log('Login loading state set to false');
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      // TODO: Implement actual Supabase sign out
      setUser(null);
      
      // Clear all session data from localStorage
      localStorage.removeItem('gtd_user');
      localStorage.removeItem('gtd_session');
      
      console.log('User logged out and session cleared from localStorage');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, _password: string, name?: string) => {
    setIsLoading(true);
    try {
      // TODO: Implement actual Supabase sign up
      const loginTime = new Date().toISOString();
      const mockUser: User = {
        id: Date.now().toString(),
        email,
        name: name || email.split('@')[0],
        loginTime,
      };
      
      // Store user data and session info for persistence
      const sessionData = {
        isActive: true,
        loginTime,
        userId: mockUser.id,
      };
      
      setUser(mockUser);
      localStorage.setItem('gtd_user', JSON.stringify(mockUser));
      localStorage.setItem('gtd_session', JSON.stringify(sessionData));
      
      console.log('User signed up and session saved to localStorage');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    signup,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}