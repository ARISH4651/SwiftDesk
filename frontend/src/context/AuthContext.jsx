import React, { createContext, useState, useEffect, useContext } from 'react';
import api, { loginUser } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('swiftdesk_token') || null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('swiftdesk_user');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem('swiftdesk_token', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('swiftdesk_token');
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem('swiftdesk_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('swiftdesk_user');
    }
  }, [user]);

  // Request interceptor to inject Bearer token
  useEffect(() => {
    const reqInterceptor = api.interceptors.request.use((config) => {
      const savedToken = localStorage.getItem('swiftdesk_token');
      if (savedToken) {
        config.headers['Authorization'] = `Bearer ${savedToken}`;
      }
      return config;
    });
    return () => api.interceptors.request.eject(reqInterceptor);
  }, []);

  // Response interceptor for 401 handling
  useEffect(() => {
    const resInterceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          logout();
        }
        return Promise.reject(error);
      }
    );
    return () => api.interceptors.response.eject(resInterceptor);
  }, []);

  const login = async (email, password, role) => {
    const res = await loginUser(email, password, role);
    const { access_token, user: userData } = res.data;
    setToken(access_token);
    setUser(userData);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    return userData;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('swiftdesk_token');
    localStorage.removeItem('swiftdesk_user');
    delete api.defaults.headers.common['Authorization'];
  };

  const value = {
    token,
    user,
    role: user ? user.role.toUpperCase() : null,
    isAuthenticated: !!token && !!user,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
