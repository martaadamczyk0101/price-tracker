import { useState } from "react";
import { formatPrice } from "../utils/formatPrice";
import "../styles/PriceHistory.css";

export default function PriceHistory({ productId }) {
  const [prices, setPrices] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggle = async () => {
    if (!open && prices.length === 0) {
      setLoading(true);
      const res = await fetch(`/api/products/${productId}/price-history`);
      const data = await res.json();
      setPrices(data);
      setLoading(false);
    }
    setOpen(!open);
  };

    const arrow = (curr, prev) => {
    if (prev == null) return null;
    if (curr > prev) return { symbol: "↑", type: "up" };
    if (curr < prev) return { symbol: "↓", type: "down" };
    return null;
    };

  return (
    <div className="price-history">
      <button className="price-history__toggle" onClick={toggle}>
        {open ? <div>show less <span className={'chevron-down open'} /></div> : <div>show price history <span className={'chevron-down'} />
 </div>}
      </button>

      <div className={`price-history__content ${open ? "open" : ""}`}>
        {loading && <div className="price-history__loading">Loading…</div>}

        {!loading &&
          prices.map((p, idx) => {
            const prev = idx > 0 ? prices[idx - 1].price : null;

            return (
              <div key={idx} className="price-history__row">
                <span className="price-history__date">
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
                <span className="price-history__price">
                  {formatPrice(p.price)}
                </span>
                {(() => {
  const a = arrow(p.price, prev);
  if (!a) return <span className="price-history__arrow" />;

  return (
    <span className={`price-history__arrow ${a.type}`}>
      {a.symbol}
    </span>
  );
})()}

              </div>
            );
          })}
      </div>
    </div>
  );
}
