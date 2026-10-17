import { createContext, useContext, useState } from "react";
import apiClient from "../api/client";
import { clearApiCache } from "../utils/apiCache";

const AuthContext = createContext(null);


export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(
    () => localStorage.getItem("token") || null
    );

  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem("user");
      return savedUser ? JSON.parse(savedUser) : null;
      } catch {
    localStorage.removeItem("user");
    return null;
    }
  });

  const login = async (email, password) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const loginResponse = await apiClient.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const accessToken = loginResponse.data.access_token;
    // Cached responses are keyed by path, not by user, so a fresh sign-in must not
    // be able to reuse anything fetched during the previous session.
    clearApiCache();
    localStorage.setItem("token", accessToken);
    setToken(accessToken);

    const meResponse = await apiClient.get("/auth/me");
    const userData = meResponse.data;
    
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
    return userData;
  };

  const logout = () => {
    clearApiCache();
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);