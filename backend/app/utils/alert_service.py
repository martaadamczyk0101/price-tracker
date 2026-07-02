from backend.app.models import Alert, Product, User
from backend.app.utils.format_price import format_price
from backend.app.utils.telegram_sender import send_telegram_message


def process_price_alerts(db, product: Product, new_price: float):
    alert = (
        db.query(Alert)
        .filter_by(product_id=product.id, user_id=product.user_id, active=True)
        .first()
    )

    if not alert:
        return

    old_notified_price = alert.last_notified_price
    old_price = product.current_price

    if alert.last_notified_price is None:
        alert.last_notified_price = old_price
        db.commit()
        old_notified_price = old_price

    if new_price >= old_notified_price:
        return

    message = (
        f"📉 <b>Spadek ceny!</b>\n\n"
        f"<b>{product.name}</b>\n"
        f"URL: {product.url}\n\n"
        f"Poprzednia cena: {format_price(old_notified_price)}\n"
        f"Nowa cena: {format_price(new_price)}"
    )

    if not product.user.telegram_verified or product.user.email == "demo@demo.com":
        return

    send_telegram_message(message, product.user.telegram_id)

    alert.last_notified_price = new_price
    db.commit()
