import React, { createContext, useContext, useState, useEffect } from 'react';
import api, { authApi } from '../api/axios';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, role: string) => Promise<void>;
  logout: () => void;
  refreshProfileStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshProfileStatus = async () => {
    const role = localStorage.getItem('userRole');
    const token = localStorage.getItem('token');
    if (!token || !role) {
      setIsLoading(false);
      return;
    }

    try {
      const verifyRes = await authApi.get('/auth/verify');
      setUser(verifyRes.data);
    } catch (error) {
      console.error("Auth initialization failed", error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (token: string, role: string) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userRole', role);
    await refreshProfileStatus();
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    setUser(null);
    setIsLoading(false);
  };

  useEffect(() => {
    const init = async () => {
      if (localStorage.getItem('token')) {
        await refreshProfileStatus();
      } else {
        setIsLoading(false);
      }
    };
    init();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout, refreshProfileStatus }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
