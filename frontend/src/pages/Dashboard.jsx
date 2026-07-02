import React, { useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import AddProduct from "../components/AddProduct";
import ProductList from "../components/ProductList";
import "../index.css";
import '../styles/Header.css';

export default function Dashboard() {
  const [products, setProducts] = useState([]);
  const { logout, user } = useAuth();

  async function loadProducts() {
    try {
      const res = await fetch("/api/products");
      const data = await res.json();

      setProducts(Array.isArray(data) ? data.reverse() : []);
    } catch {
      setProducts([]);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  return (
    <div className="app-container">
      {user?.is_demo && (
        <div className="demo-banner">
          You're viewing a demo. Telegram price alerts are not available here.
        </div>
      )}
      <header className="top-header">
        <div className="brand">
          <div className="brand-icon">%</div>
          <div className="brand-meta">
            <div className="brand-title">E-commerce Price Tracker</div>
            <div className="brand-sub">insights & alerts</div>
          </div>
        </div>

        <div className="header-actions">
          <button className="logout-link" onClick={logout}>
            {user?.is_demo ? "Leave Demo" : "Logout"}
          </button>
        </div>
      </header>

      <main className="main-layout">
        <section className="section card products-column">
          <h1 className="section-title">
            tracked items
            <span className="product-count">{products.length}/20</span>
          </h1>
          <ProductList products={products} onDelete={loadProducts} />
        </section>

        <section className="section card add-panel">
          <h2 className="section-title">add URL</h2>
          <AddProduct onProductAdded={loadProducts} />
        </section>
      </main>

      <footer className="footer">
        E-commerce Price Tracker © insights & alerts 
      </footer>
    </div>
  );
}
