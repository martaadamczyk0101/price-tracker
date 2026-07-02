import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import "../auth/Auth.css";
import "../index.css";

const isValidEmail = (email) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

function EyeIcon({ open }) {
  return open ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>
  );
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [demoError, setDemoError] = useState("");
  const [demoLoading, setDemoLoading] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);

  const { login, demoLogin } = useAuth();
  const navigate = useNavigate();

  const handleDemoLogin = async () => {
    setDemoError("");
    setDemoLoading(true);
    try {
      await demoLogin();
      navigate("/");
    } catch {
      setDemoError("Demo is not available right now. Please try again later.");
    } finally {
      setDemoLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setEmailError("");
    setPasswordError("");
    setSubmitError("");

    let hasError = false;
    if (!isValidEmail(email)) {
      setEmailError("Please enter a valid email address");
      hasError = true;
    }
    if (!password) {
      setPasswordError("Please enter your password");
      hasError = true;
    }
    if (hasError) return;

    setLoginLoading(true);
    try {
      const success = await login(email, password);
      if (!success) {
        setSubmitError("Invalid email or password");
      }
    } catch (err) {
      if (err?.status === 403) {
        navigate("/verify-telegram");
        return;
      }
      setSubmitError("Something went wrong. Please try again.");
    } finally {
      setLoginLoading(false);
    }
  };

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
      <div className="login-two-col">

        <div className="auth-card">
          <h2 style={{ marginBottom: "24px" }}>Sign In</h2>
          <form className="auth-form" onSubmit={handleSubmit}>
            <label>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
            {emailError && (
              <div className="product-error-label" style={{ marginTop: "-8px" }}>
                {emailError}
              </div>
            )}

            <label>Password</label>
            <div className="pwd-field">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="pwd-toggle"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                <EyeIcon open={showPassword} />
              </button>
            </div>
            {passwordError && (
              <div className="product-error-label" style={{ marginTop: "-8px" }}>
                {passwordError}
              </div>
            )}

            {submitError && (
              <div className="product-error-label">{submitError}</div>
            )}

            <button className="login-btn" disabled={loginLoading}>
              {loginLoading ? "Signing in…" : "Sign In"}
            </button>

            <p className="auth-footer">
              Don't have an account? <Link to="/register">Sign Up</Link>
            </p>
          </form>
        </div>

        <div className="auth-or-divider"><span>or</span></div>

        <div className="auth-card demo-card">
          <h2 style={{ marginBottom: "12px" }}>Try Demo</h2>

          <p className="demo-description">
            Explore the app without creating an account. Add real product URLs,
            browse price history charts, and see how price tracking works in
            practice.
          </p>

          <p className="demo-description">
            The demo resets on each login, so you always start from a clean
            slate with pre-loaded products.
          </p>

          <p className="demo-description demo-description--note">
            Telegram price alerts are not available in the demo.
          </p>

          {demoError && (
            <div className="product-error-label" style={{ marginTop: "16px" }}>{demoError}</div>
          )}

          <button
            type="button"
            className="demo-primary-btn"
            onClick={handleDemoLogin}
            disabled={demoLoading}
          >
            {demoLoading ? "Loading…" : "Enter Demo"}
          </button>
        </div>

      </div>
      </main>

      <footer className="footer">
        Price Tracker © insights & alerts
      </footer>
    </div>
  );
}
