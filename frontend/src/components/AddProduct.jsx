import React, { useState, useEffect } from "react";
import SupportedShopsModal from "./SupportedShopsModal";
import '../styles/AddProduct.css';

export default function AddProduct({ onProductAdded }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const [infoOpen, setInfoOpen] = useState(false);
  const [infoMessage, setInfoMessage] = useState("");
  const [shopsOpen, setShopsOpen] = useState(false);
  const [supportedShops, setSupportedShops] = useState([]);

  async function submit(e) {
    e.preventDefault();
    if (!url || !url.trim()) return;

    try {
      setLoading(true);

      const body = new URLSearchParams();
      body.append("url", url.trim());

      const res = await fetch("/add", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });

      const data = await res.json();

      if (!res.ok) {
        setInfoMessage(data.message || "Could not add product.");
        setInfoOpen(true);
        return;
      }

      setUrl("");
      if (typeof onProductAdded === "function") {
        onProductAdded();
      }

    } catch {
      setInfoMessage("Unexpected error occurred. Please try again.");
      setInfoOpen(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
  fetch("/api/supported-shops")
    .then((res) => res.json())
    .then((data) => {
      if (Array.isArray(data)) {
        setSupportedShops(data);
      }
    })
    .catch(() => {
      setSupportedShops([]);
    });
}, []);


  return (
    <>
      <form className="add-form" onSubmit={submit}>
        <label className="form-label">
          product URL
          <input
            className="input clean-input"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/product"
            required
          />
        </label>

        <div className="add-actions">
          <button className="btn primary" type="submit" disabled={loading}>
            {loading ? <span>adding<span className="adding-dot">.</span><span className="adding-dot">.</span><span className="adding-dot">.</span></span> : "add"}
          </button>

          <button
            type="button"
            className="btn secondary"
            onClick={() => setUrl("")}
            disabled={loading}
          >
            clear
          </button>
        </div>
      </form>
      <div
          style={{
            marginTop: 24,
            fontSize: "0.85rem",
            color: "#777",
            textAlign: "center",
            cursor: "pointer",
            textDecoration:'underline',
          }}
          onClick={() => setShopsOpen(true)}
      >
      supported shops
      </div>


      {infoOpen && (
        <div className="confirm-overlay-fixed">
          <div className="confirm-box" style={{width: 'min(500px, 90vw)'}}>
              <div className="failed-info">FAILED TO ADD PRODUCT</div>
            <div style={{ marginBottom: 20 }}>
              {infoMessage}
            </div>
              <button
                className="btn primary"
                onClick={() => setInfoOpen(false)}
              >
                OK
              </button>
           </div>
        </div>
      )}

      <SupportedShopsModal
        open={shopsOpen}
        onClose={() => setShopsOpen(false)}
        shops={supportedShops}
      />

    </>
  );
}
