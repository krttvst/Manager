import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMe } from "../api/auth.js";
import { AUTH_LOGOUT_EVENT } from "./authEvents.js";
import { clearStoredToken, getStoredToken, setStoredToken } from "./tokenStorage.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken());
  const [user, setUser] = useState(null);

  useEffect(() => {
    function handleStorage(event) {
      if (event.key === "token") {
        setToken(event.newValue);
      }
    }
    function handleLogout() {
      setToken(null);
      setUser(null);
    }
    window.addEventListener("storage", handleStorage);
    window.addEventListener(AUTH_LOGOUT_EVENT, handleLogout);
    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener(AUTH_LOGOUT_EVENT, handleLogout);
    };
  }, []);

  useEffect(() => {
    async function loadMe() {
      if (!token) {
        setUser(null);
        return;
      }
      try {
        const me = await getMe(token);
        setUser(me);
      } catch {
        setUser(null);
      }
    }
    loadMe();
  }, [token]);

  const value = useMemo(
    () => ({
      token,
      user,
      loginWithToken(nextToken) {
        setStoredToken(nextToken);
        setToken(nextToken);
      },
      logout() {
        clearStoredToken();
        setToken(null);
        setUser(null);
      }
    }),
    [token, user]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
