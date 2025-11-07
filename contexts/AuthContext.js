// contexts/AuthContext.js - No Firebase version
'use client';
import { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false); // Set to false since no auth

  useEffect(() => {
    // No Firebase auth - just set a demo user immediately
    setCurrentUser({ uid: 'demo-user', email: 'demo@avicennamedicine.com' });
  }, []);

  const value = {
    currentUser,
    loading: false
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
