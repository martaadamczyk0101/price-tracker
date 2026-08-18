from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models import Log, Price, Product, User
from backend.app.utils.alert_service import process_price_alerts
from backend.app.utils.logger import add_log
from backend.app.utils.scraper import get_product_info


def update_prices(db: Session):

    products = (
        db.query(Product)
        .join(User)
        .filter(Product.active == True)
        .all()
    )

    for product in products:

        try:
            price_value, title_value, image = get_product_info(product.url)
            fetch_error_message = f"Nie udało się pobrać ceny ({product.name})"
        except Exception as e:
            price_value, title_value, image = None, None, None
            fetch_error_message = f"Błąd scrapera: {e}"

        if price_value is None:
            # Only look at fetch-outcome logs (OK/ERROR/PRICE_CHANGE) — alert
            # failures also log status="ERROR" for this product even when the
            # price fetch itself succeeded, which would otherwise make a
            # single real failure look like the second one in a row.
            last_fetch_log = (
                db.query(Log)
                .filter(Log.product_id == product.id, Log.status != "ALERT_ERROR")
                .order_by(Log.created_at.desc())
                .first()
            )
            if last_fetch_log and last_fetch_log.status == "ERROR":
                product.has_error = True
            add_log(
                product_id=product.id,
                message=fetch_error_message,
                status="ERROR",
            )
            db.commit()
            continue

        else:
            log_message = f"Cena pobrana ({product.name})"
            product.has_error = False
            add_log(
                product_id=product.id,
                message=log_message,
                status="OK",
            )

        price_value = Decimal(str(price_value))

        if product.initial_price is None:
            product.initial_price = price_value

        if not product.name and title_value:
            product.name = title_value

        new_price = Price(
            product_id=product.id,
            price_value=price_value,
            currency="PLN",
        )
        db.add(new_price)
        db.flush()

        try:
            process_price_alerts(db, product, price_value)
        except Exception as e:
            add_log(
                product_id=product.id,
                message=f"Błąd alertu cenowego: {e}",
                status="ALERT_ERROR",
            )

        if price_value < product.initial_price:
            log_message = f"Obnizka ceny z {product.initial_price} na {price_value} ({product.name})"
            add_log(
                product_id=product.id,
                message=log_message,
                status="PRICE_CHANGE",
            )
        elif price_value > product.initial_price:
            log_message = f"Wzrost ceny z {product.initial_price} na {price_value} ({product.name})"
            add_log(
                product_id=product.id,
                message=log_message,
                status="PRICE_CHANGE",
            )

        db.commit()
