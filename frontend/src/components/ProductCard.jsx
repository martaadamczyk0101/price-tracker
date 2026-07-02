import React, { useState } from "react";
import PriceHistory from "./PriceHistory";
import '../styles/ProductCard.css';

function formatDateTime(value) {
  return new Date(value).toLocaleString("sv-SE").replace(",", "");
}

function truncateText(text, maxLength = 80) {
  if (!text) return "";
  return text.length > maxLength
    ? text.slice(0, maxLength) + "..."
    : text;
};


export default function ProductCard({ product, onDeleted }) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  let domain = "";
  try {
    if (product && product.url) {
      domain = new URL(product.url).hostname.replace(/^www\./, "");
    }
  } catch {}

  const initialPrice = product?.initial_price ?? null;
  const currentPrice = product?.current_price ?? null;
  const initialPriceNum = initialPrice != null ? parseFloat(initialPrice) : null;
  const currentPriceNum = currentPrice != null ? parseFloat(currentPrice) : null;
  const lastChecked = product?.last_checked ?? null;

  const thumbSrc = product?.image_url
    ? product.image_url
    : product?.url
    ? `https://www.google.com/s2/favicons?domain=${encodeURIComponent(
        new URL(product.url).hostname
      )}&sz=64`
    : null;

  async function doDelete() {
    try {
      setDeleting(true);
      const res = await fetch(`/delete/${product.id}`, { method: "POST" });
      if (res.ok) {
        setConfirmOpen(false);
        if (onDeleted) await onDeleted();
      } else {
        alert("Error deleting item");
      }
    } finally {
      setDeleting(false);
    }
  }

  return (
    <>
        <div className={`nice-card ${product.has_error ? "nice-error" : ""}`} data-id={product.id}>


        <div className="pc-row">
          <div className="pc-left">
            
            <div className="product-img">
            {thumbSrc ? (
              <img className="pc-thumb" src={thumbSrc} alt={product.name} />
            ) : (
              <div className="pc-thumb placeholder">IMG</div>
            )}
            </div>
            <div className="pc-info">
              <div
                className="pc-title clickable-title"
                onClick={() => window.open(product.url, "_blank")}
              >
                {product?.name ? truncateText(product.name, 60) : "Unnamed"}
              </div>

              {product.has_error && (
                <div className="product-error-label">
                    Niedostępne – błąd pobierania
                </div>
            )}

              {domain && <div className="pc-domain">{domain}</div>}
              {lastChecked && <div className="pc-check">last checked @ {formatDateTime(lastChecked)}</div>}
            </div>
          </div>

          <div className="pc-right">
            <div className="pc-initial">
              added @ {initialPrice != null ? initialPrice + 'zł' : "—"}
            </div>

            <div className="pc-current-row">
              {currentPriceNum != null && initialPriceNum != null && currentPriceNum < initialPriceNum && (
                <span className="pc-drop-badge">↓ {Math.round((1 - currentPriceNum / initialPriceNum) * 100)}%</span>
              )}
              {currentPriceNum != null && initialPriceNum != null && currentPriceNum > initialPriceNum && (
                <span className="pc-rise-badge">↑ +{Math.round((currentPriceNum / initialPriceNum - 1) * 100)}%</span>
              )}
              <div className={`pc-current${currentPriceNum != null && initialPriceNum != null && currentPriceNum < initialPriceNum ? " pc-current--drop" : currentPriceNum != null && initialPriceNum != null && currentPriceNum > initialPriceNum ? " pc-current--rise" : ""}`}>
                {currentPrice != null ? currentPrice + "zł" : "—"}
              </div>
            </div>
                        <div className="pc-actions">
          <button className="btn stop" onClick={() => setConfirmOpen(true)}>
            Stop Tracking
          </button>
        </div>
          </div>
        </div>

                      <PriceHistory productId={product.id} />

      </div>

      {confirmOpen && (
        <div className="confirm-overlay-fixed">
          <div className="confirm-box">
            <div style={{ marginBottom: 20 }}>Do you want to stop tracking this item?</div>

            <div className="confirm-actions" style={{ gap: 10 }}>
              <button className="btn stop confirm" onClick={doDelete} disabled={deleting}>
                {deleting ? "Removing…" : "Confirm"}
              </button>

              <button className="btn secondary" onClick={() => setConfirmOpen(false)} disabled={deleting}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
