from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models import Price, Product, User
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
        except Exception as e:
            add_log(
                product_id=product.id,
                message=f"Błąd scrapera: {e}",
                status="ERROR",
            )
            continue

        if price_value is None:
            log_message = f"Nie udało się pobrać ceny ({product.name})"
            product.has_error = True
            add_log(
                product_id=product.id,
                message=log_message,
                status="ERROR",
            )
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
                status="ERROR",
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
