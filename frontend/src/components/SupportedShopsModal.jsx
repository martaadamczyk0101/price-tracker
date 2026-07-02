import React, { useMemo, useState } from "react";

export default function SupportedShopsModal({ open, onClose, shops }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    if (!query) return shops;
    return shops.filter((shop) =>
      shop.toLowerCase().includes(query.toLowerCase())
    );
  }, [query, shops]);

  if (!open) return null;

  return (
    <div className="confirm-overlay-fixed">
      <div
        className="confirm-box"
        style={{
          width: 420,
          height: 500,
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {/* HEADER */}
        <div
          style={{
            marginBottom: 12,
            fontWeight: 600,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>Supported shops</span>

          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              background: "none",
              border: "none",
              fontSize: "1.2rem",
              lineHeight: 1,
              cursor: "pointer",
              color: "#777",
            }}
          >
            ×
          </button>
        </div>

        {/* SEARCH */}
        <input
          className="input clean-input"
          placeholder="Search shop…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ marginBottom: 12 }}
        />

        {/* LIST */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            paddingRight: 4,
          }}
        >
          {filtered.length === 0 && (
            <div style={{ fontSize: "0.85rem", color: "#777" }}>
              No matching shops
            </div>
          )}

          {filtered.map((shop) => (
            <div
              key={shop}
              style={{
                padding: "6px 4px",
                fontSize: "0.9rem",
                borderBottom: "1px solid rgba(0,0,0,0.05)",
              }}
            >
              {shop}
            </div>
          ))}
        </div>
          <div style={{fontSize:'11px', color: 'gray', letterSpacing: '0.5px', marginTop:'15px'}}>MORE COMING SOON</div>
      </div>
    </div>
  );
}
