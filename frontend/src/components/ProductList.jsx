import React from "react";
import ProductCard from "./ProductCard";
import '../styles/ProductCard.css';

export default function ProductList({ products = [], onDelete }) {
  if (!products || products.length === 0) {
    return <div className="empty muted">No tracked products yet.</div>;
  }

  return (
    <div className="product-grid" role="list">
      {products.map((p) => (
        <ProductCard key={p.id} product={p} onDeleted={onDelete} />
      ))}
    </div>
  );
}
