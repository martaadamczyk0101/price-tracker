import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/auth/me", { credentials: "include" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.authenticated) setUser(data);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });

    if (res.status === 401) return false;

    if (res.status === 403) {
      const error = new Error("ACCOUNT_NOT_VERIFIED");
      error.code = "ACCOUNT_NOT_VERIFIED";
      error.status = 403;
      throw error;
    }

    if (!res.ok) throw new Error("LOGIN_FAILED");

    const data = await res.json();
    setUser(data);
    return true;
  };

  const demoLogin = async () => {
    const res = await fetch("/auth/demo-login", {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) throw new Error("DEMO_NOT_AVAILABLE");
    const meRes = await fetch("/auth/me", { credentials: "include" });
    const data = await meRes.json();
    if (data?.authenticated) setUser(data);
    return true;
  };

  const logout = async () => {
    await fetch("/auth/logout", { method: "POST", credentials: "include" });
    setUser(null);
  };

  const register = async ({ email, password, telegramId }) => {
    const res = await fetch("/auth/register", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, telegram_id: telegramId }),
    });

    const data = await res.json();

    if (!res.ok) {
      const err = new Error(data.message || "Registration failed");
      err.error = data.error;
      throw err;
    }

    return true;
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, demoLogin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
