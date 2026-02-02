import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { apiFetch } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function loadMe() {
      if (!token) {
        setUser(null);
        return;
      }
      try {
        const me = await apiFetch("/users/me", { token });
        setUser(me);
      } catch {
        setUser(null);
      }
    }
    loadMe();
  }, [token]);

  const value = useMemo(() => ({ token, setToken, user }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
