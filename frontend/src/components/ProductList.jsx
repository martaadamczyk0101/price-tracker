import React from "react";
import ProductCard from "./ProductCard";
import '../styles/ProductCard.css';

function SkeletonCard() {
  return (
    <div className="nice-card skeleton-card">
      <div className="pc-row">
        <div className="pc-left">
          <div className="product-img">
            <div className="skeleton-thumb" />
          </div>
          <div className="pc-info">
            <div className="skeleton-line skeleton-title" />
            <div className="skeleton-line skeleton-domain" />
            <div className="skeleton-line skeleton-check" />
          </div>
        </div>
        <div className="pc-right">
          <div className="skeleton-line skeleton-price-small" />
          <div className="skeleton-line skeleton-price-big" />
          <div className="pc-actions">
            <div className="skeleton-line skeleton-stop-btn" />
          </div>
        </div>
      </div>
      <div className="price-history">
        <div className="price-history__toggle">
          <div className="skeleton-line skeleton-history-btn" />
        </div>
      </div>
      <div className="skeleton-overlay">
        <div className="skeleton-message">
          <span className="skeleton-spinner" />
          Adding product… this may take up to a few minutes
        </div>
      </div>
    </div>
  );
}

export default function ProductList({ products = [], onDelete, adding }) {
  if (!adding && (!products || products.length === 0)) {
    return <div className="empty muted">No tracked products yet.</div>;
  }

  return (
    <div className="product-grid" role="list">
      {adding && <SkeletonCard />}
      {products.map((p) => (
        <ProductCard key={p.id} product={p} onDeleted={onDelete} />
      ))}
    </div>
  );
}
