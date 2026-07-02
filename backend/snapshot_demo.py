import json
import os

import backend.config as config
from backend.app import create_app
from backend.app.models import Price, Product, User

DEMO_EMAIL = config.DEMO_EMAIL
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "demo_snapshot.json")


def run():
    app = create_app()

    with app.app_context():
        db = app.session_factory()

        user = db.query(User).filter_by(email=DEMO_EMAIL).first()
        if not user:
            print(f"Demo user ({DEMO_EMAIL}) not found. Run seed_demo.py first.")
            db.close()
            return

        products = db.query(Product).filter_by(user_id=user.id, active=True).all()
        if not products:
            print("No products found on demo account. Add some via the UI first.")
            db.close()
            return

        snapshot = []
        for p in products:
            prices = (
                db.query(Price)
                .filter_by(product_id=p.id)
                .order_by(Price.created_at)
                .all()
            )
            snapshot.append({
                "name": p.name,
                "url": p.url,
                "image_url": p.image_url,
                "initial_price": str(p.initial_price),
                "created_at": p.created_at.isoformat(),
                "prices": [
                    {
                        "price_value": str(pr.price_value),
                        "currency": pr.currency,
                        "created_at": pr.created_at.isoformat(),
                    }
                    for pr in prices
                ],
            })

        db.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"Snapshot saved: {OUTPUT_PATH}")
    print(f"  {len(snapshot)} products")
    for p in snapshot:
        print(f"  - {p['name']} ({len(p['prices'])} price entries)")


if __name__ == "__main__":
    run()
