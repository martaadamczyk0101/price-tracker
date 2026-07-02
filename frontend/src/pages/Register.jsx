import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import "../auth/Auth.css";
import "../index.css";
import "../styles/Header.css";

const isValidEmail = (email) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const isValidPassword = (password) => {
  if (password.length < 8)
    return "Password must be at least 8 characters long";
  if (!/[A-Z]/.test(password))
    return "Password must contain at least one uppercase letter";
  if (!/[^A-Za-z0-9]/.test(password))
    return "Password must contain at least one special character";
  return "";
};

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

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [confirmError, setConfirmError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [submitLoading, setSubmitLoading] = useState(false);

  const navigate = useNavigate();
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setEmailError("");
    setPasswordError("");
    setConfirmError("");
    setSubmitError("");

    let hasError = false;

    if (!isValidEmail(email)) {
      setEmailError("Please enter a valid email address");
      hasError = true;
    }

    const pwdError = isValidPassword(password);
    if (pwdError) {
      setPasswordError(pwdError);
      hasError = true;
    }

    if (password !== confirm) {
      setConfirmError("Passwords do not match");
      hasError = true;
    }

    if (hasError) return;

    setSubmitLoading(true);
    try {
      await register({ email, password });
      localStorage.setItem("pending_verification_email", email);
      navigate("/verify-telegram");
    } catch (err) {
      if (err?.message === "Failed to fetch") {
        setSubmitError("Unable to connect to server. Please try again later.");
        return;
      }
      if (err?.error === "EMAIL_EXISTS") {
        setEmailError("An account with this email already exists.");
        return;
      }
      setSubmitError(err?.message || "Registration failed");
    } finally {
      setSubmitLoading(false);
    }
  };

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
        <div className="auth-card">
          <h2 style={{ marginBottom: "24px" }}>Sign Up</h2>
          <form className="auth-form" onSubmit={handleSubmit}>
            <label>Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            {emailError && (
              <div className="product-error-label" style={{ marginTop: "-8px" }}>
                {emailError}
              </div>
            )}

            <label className="label-with-help">
              Password
              <span
                className="help-icon"
                data-tooltip={
                  "Password requirements:\n" +
                  "• At least 8 characters\n" +
                  "• At least one uppercase letter\n" +
                  "• At least one special character"
                }
              >
                ?
              </span>
            </label>

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

            <label>Confirm Password</label>
            <div className="pwd-field">
              <input
                type={showConfirm ? "text" : "password"}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
              <button
                type="button"
                className="pwd-toggle"
                onClick={() => setShowConfirm((v) => !v)}
                aria-label={showConfirm ? "Hide password" : "Show password"}
              >
                <EyeIcon open={showConfirm} />
              </button>
            </div>
            {confirmError && (
              <div className="product-error-label" style={{ marginTop: "-8px" }}>
                {confirmError}
              </div>
            )}

            {submitError && (
              <div className="product-error-label">{submitError}</div>
            )}

            <button className="login-btn" disabled={submitLoading}>
              {submitLoading ? "Creating account…" : "Sign Up"}
            </button>

            <p className="auth-footer">
              Already have an account? <Link to="/login">Sign in</Link>
            </p>
          </form>
        </div>
      </main>

      <footer className="footer">
        Price Tracker © insights & alerts
      </footer>
    </div>
  );
}
