import { Link } from "react-router-dom";
import "../index.css";

export default function AuthLayout({ title, children, authClass='' }) {
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
          <div className={`auth-card ${authClass}`}>
          <h1>{title}</h1>
          {children}
        </div>
      </main>

      <footer className="footer">
        Price Tracker © insights & alerts
      </footer>
    </div>
  );
}
