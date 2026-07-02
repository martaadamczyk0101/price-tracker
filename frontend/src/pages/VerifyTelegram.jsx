import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../auth/Auth.css";
import "../index.css";
import "../styles/Header.css";

export default function VerifyTelegram() {
  const [loading, setLoading] = useState(true);
  const [verified, setVerified] = useState(false);
  const [token, setToken] = useState(null);
  const [checked, setChecked] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();

  const refreshToken = async () => {
    const email = localStorage.getItem("pending_verification_email");
    if (!email) return;
    setRefreshing(true);
    setChecked(false);
    try {
      const res = await fetch("/auth/refresh-token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) setToken(data.token);
    } catch {
      // ignore
    }
    setRefreshing(false);
  };

  const loadStatus = async (manual = false) => {
    setLoading(true);
    if (manual) setChecked(false);

    const email = localStorage.getItem("pending_verification_email");
    if (!email) {
      navigate("/login");
      return;
    }

    try {
      const res = await fetch(
        `/telegram-verification/by-email?email=${encodeURIComponent(email)}`
      );

      if (!res.ok) throw new Error("status check failed");

      const data = await res.json();

      if (data.telegram_verified) {
        localStorage.removeItem("pending_verification_email");
        setVerified(true);
      } else {
        setToken(data.token);
        if (manual) setChecked(true);
      }
    } catch {
      if (manual) setChecked(true);
    }

    setLoading(false);
  };

  useEffect(() => {
    loadStatus();
  }, []);

  if (loading) {
    return (
      <div className="app-container">
        <header className="top-header">
          <Link to="/login" className="brand" style={{ textDecoration: "none" }}>
            <div className="brand-icon">%</div>
            <div className="brand-meta">
              <div className="brand-title">E-commerce Price Tracker</div>
              <div className="brand-subtitle">insights & alerts</div>
            </div>
          </Link>
        </header>
        <main className="auth-page"><div className="auth-card"><p>Loading…</p></div></main>
      </div>
    );
  }

  if (verified) {
    return (
      <div className="app-container">
        <header className="top-header">
          <Link to="/login" className="brand" style={{ textDecoration: "none" }}>
            <div className="brand-icon">%</div>
            <div className="brand-meta">
              <div className="brand-title">E-commerce Price Tracker</div>
              <div className="brand-subtitle">insights & alerts</div>
            </div>
          </Link>
        </header>

        <main className="auth-page">
          <div className="auth-card" style={{ textAlign: "center" }}>
            <h2 style={{ marginBottom: "16px" }}>You're all set!</h2>
            <p style={{ color: "#4b5563", marginBottom: "28px", lineHeight: 1.6 }}>
              Your Telegram account has been verified. You can now log in and start tracking prices.
            </p>
            <button className="login-btn" style={{ width: "100%" }} onClick={() => navigate("/login")}>
              Go to login
            </button>
          </div>
        </main>

        <footer className="footer">Price Tracker © insights & alerts</footer>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="top-header">
        <div className="brand">
          <div className="brand-icon">%</div>
          <div className="brand-meta">
            <div className="brand-title">E-commerce Price Tracker</div>
            <div className="brand-subtitle">insights & alerts</div>
          </div>
        </div>
      </header>

      <main className="auth-page">
        <div className="auth-card auth-verify">
          <h2 style={{ marginBottom: "8px" }}>One last step</h2>
          <p style={{ color: "#9ca3af", fontSize: "0.9rem", marginBottom: "36px" }}>
            Connect your Telegram to enable price drop alerts.
          </p>

          <div className="verify-telegram-layout">
            <div className="verify-steps">
              <div className="verify-step">
                <span className="verify-step-num">1</span>
                <span>Open Telegram and find <strong>@EPRICETRACKERBOT</strong>, or scan the QR code on the right.</span>
              </div>
              <div className="verify-step">
                <span className="verify-step-num">2</span>
                <span>Start a chat and send:</span>
              </div>

              <pre className="verify-token">/start {token}</pre>

              <div className="verify-step">
                <span className="verify-step-num">3</span>
                <span>Come back here and click <strong>Check status</strong>.</span>
              </div>

            </div>

            <div className="verify-qr">
              <img src="/telegram-qr.png" alt="Scan to open @EPRICETRACKERBOT" />
              <span>@EPRICETRACKERBOT</span>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px", marginTop: "36px" }}>
            {checked && (
              <p style={{ margin: 0, color: "#b00020", fontSize: "0.85rem", fontWeight: 500, textAlign: "center" }}>
                Not verified yet - make sure you sent the command above to <strong>@EPRICETRACKERBOT</strong>.
              </p>
            )}

            <button className="demo-primary-btn" style={{ width: "220px" }} onClick={() => loadStatus(true)}>
              Check status
            </button>

            <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
              Code not working?{" "}
              <button
                onClick={refreshToken}
                disabled={refreshing}
                style={{ background: "none", border: "none", color: "#2563eb", cursor: "pointer", fontSize: "0.85rem", fontWeight: 500, padding: 0 }}
              >
                {refreshing ? "Generating…" : "Get a new code"}
              </button>
            </p>
          </div>
        </div>
      </main>

      <footer className="footer">Price Tracker © insights & alerts</footer>
    </div>
  );
}
