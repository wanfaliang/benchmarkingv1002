// frontend/src/context/AuthContext.tsx
import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import type { User, LoginResult, RegisterData } from '../types';

// ============================================================================
// Types
// ============================================================================

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<LoginResult>;
  register: (userData: RegisterData) => Promise<LoginResult>;
  loginWithGoogle: (idToken: string) => Promise<LoginResult>;
  logout: () => void;
}

interface AuthProviderProps {
  children: ReactNode;
}

// ============================================================================
// Context
// ============================================================================

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// ============================================================================
// Provider
// ============================================================================

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is logged in on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Auth initialization failed:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<LoginResult> => {
    try {
      // FastAPI OAuth2PasswordRequestForm expects form data, not JSON
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await authAPI.login(formData);
      const { access_token } = response.data;

      localStorage.setItem('token', access_token);

      const userResponse = await authAPI.getCurrentUser();
      const userData = userResponse.data;

      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      console.error('Login error:', err.response?.data);
      return {
        success: false,
        error: err.response?.data?.detail || 'Login failed',
      };
    }
  };

  const register = async (userData: RegisterData): Promise<LoginResult> => {
    try {
      await authAPI.register(userData);
      // After registration, user needs to verify email
      return { success: true };
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      console.error('Registration error:', err.response?.data);
      return {
        success: false,
        error: err.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const loginWithGoogle = async (idToken: string): Promise<LoginResult> => {
    try {
      const response = await authAPI.verifyGoogleToken(idToken);
      const { access_token } = response.data;

      localStorage.setItem('token', access_token);

      // Fetch user data after setting token
      const userResponse = await authAPI.getCurrentUser();
      const userData = userResponse.data;

      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      console.error('Google login error:', err.response?.data);
      return {
        success: false,
        error: err.response?.data?.detail || 'Google login failed',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    loginWithGoogle,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
