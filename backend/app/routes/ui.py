from datetime import datetime

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from backend.app.models import Alert, Log, Price, Product, User
from backend.app.utils.auth import login_required
from backend.app.utils.scraper import get_product_info
from backend.app.utils.logger import add_log
from backend.app.utils.selectors import SELECTORS

ui_bp = Blueprint("ui", __name__, template_folder="templates")

MAX_PRODUCTS_PER_USER = 20


@ui_bp.route("/")
def index():
    return render_template("index.html")


@ui_bp.route("/api/products")
@login_required
def api_products():
    db = ui_bp.session_factory()
    try:
        user_id = session["user_id"]

        products = (
            db.query(Product)
            .filter(Product.active == True, Product.user_id == user_id)
            .all()
        )

        return jsonify(
            [
                {
                    "id": p.id,
                    "name": p.name,
                    "url": p.url,
                    "initial_price": str(p.initial_price) if p.initial_price is not None else None,
                    "current_price": (
                        str(p.current_price) if hasattr(p, "current_price") and p.current_price is not None else None
                    ),
                    "image_url": p.image_url,
                    "last_checked": (
                        max(p.prices, key=lambda p: p.created_at).created_at.isoformat()
                        if p.prices
                        else None
                    ),
                    "has_error": p.has_error,
                }
                for p in products
            ]
        )
    finally:
        db.close()


@ui_bp.route("/add", methods=["POST"])
@login_required
def add_product():
    db = ui_bp.session_factory()
    url = request.form.get("url")
    user_id = session["user_id"]

    if not url or not url.strip():
        return (
            jsonify({"error": "EMPTY_URL", "message": "Product URL is required."}),
            400,
        )

    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    if url.startswith("http://"):
        url = "https://" + url[7:]
    if not url.startswith("https://www."):
        url = url.replace("https://", "https://www.", 1)

    product_count = db.query(Product).filter_by(user_id=user_id, active=True).count()
    if product_count >= MAX_PRODUCTS_PER_USER:
        db.close()
        return (
            jsonify({
                "error": "PRODUCT_LIMIT",
                "message": f"You can track up to {MAX_PRODUCTS_PER_USER} products.",
            }),
            403,
        )

    existing = (
        db.query(Product)
        .filter_by(url=url.strip(), user_id=user_id, active=True)
        .first()
    )
    if existing:
        db.close()
        return (
            jsonify(
                {
                    "error": "DUPLICATE_PRODUCT",
                    "message": "You are already tracking this product.",
                }
            ),
            409,
        )

    db.close()

    currency = "PLN"

    try:
        price, name, image = get_product_info(url.strip())

    except ValueError as e:
        add_log(
            product_id=None,
            message=str(e),
            status="ERROR",
        )
        return (
            jsonify(
                {
                    "error": "UNSUPPORTED_SHOP",
                    "message": "The link may be invalid or the shop is not supported yet.",
                }
            ),
            422,
        )

    except Exception as e:
        add_log(
            product_id=None,
            message=f"Błąd scrapera: {str(e)}",
            status="ERROR",
        )
        return (
            jsonify(
                {
                    "error": "SCRAPER_ERROR",
                    "message": "Failed to fetch product data from this page.",
                }
            ),
            500,
        )

    db = ui_bp.session_factory()

    if not name:
        return (
            jsonify(
                {
                    "error": "PRODUCT_NOT_FOUND",
                    "message": "Product could not be found on this page.",
                }
            ),
            404,
        )

    if not price:
        return (
            jsonify(
                {
                    "error": "PRICE_NOT_FOUND",
                    "message": "Product price could not be detected.",
                }
            ),
            422,
        )

    try:
        product = Product(
            url=url.strip(),
            name=name,
            image_url=image,
            user_id=user_id,
            initial_price=price,
            active=True,
            created_at=datetime.now(),
        )

        db.add(product)
        db.commit()

        db.add(
            Price(
                product_id=product.id,
                price_value=price,
                currency=currency,
                created_at=datetime.now(),
            )
        )

        alert = Alert(
            user_id=user_id,
            product_id=product.id,
            last_notified_price=product.initial_price,
        )

        db.add(alert)
        db.commit()
        db.expire_all()

        add_log(
            product_id=product.id,
            message=f"Produkt dodany ({product.name})",
            status="OK",
        )

        return jsonify({"success": True, "product_id": product.id}), 201

    except Exception as e:
        db.rollback()
        add_log(
            product_id=None,
            message=f"Błąd zapisu produktu: {str(e)}",
            status="ERROR",
        )
        return jsonify({"error": "DB_ERROR", "message": "Failed to save product."}), 500

    finally:
        db.close()


@ui_bp.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    db = ui_bp.session_factory()

    try:
        product = (
            db.query(Product)
            .filter_by(id=product_id, user_id=session["user_id"])
            .first()
        )

        if not product:
            return redirect(url_for("ui.index"))

        db.query(Price).filter_by(product_id=product_id).delete()
        product.active = False

        db.commit()
        db.expire_all()

        add_log(
            product_id=product.id,
            message="Produkt usunięty",
            status="OK",
        )

    except Exception as e:
        db.rollback()
        db.expire_all()
        add_log(
            product_id=product_id,
            message=f"Błąd podczas usuwania produktu: {product_id}: {str(e)}",
            status="ERROR",
        )
        return f"Wystąpił błąd podczas usuwania produktu: {e}", 500

    finally:
        db.close()

    return redirect(url_for("ui.index"))


@ui_bp.route("/logs")
@login_required
def show_logs():
    db = ui_bp.session_factory()
    try:
        logs = (
            db.query(Log)
            .join(Product)
            .filter(Product.user_id == session["user_id"])
            .order_by(Log.created_at.desc())
            .limit(200)
            .all()
        )

        return render_template("logs.html", logs=logs)
    finally:
        db.close()


@ui_bp.route("/api/products/<int:product_id>/price-history")
@login_required
def price_history(product_id):
    db = ui_bp.session_factory()
    try:
        prices = (
            db.query(Price)
            .join(Product)
            .filter(Price.product_id == product_id, Product.user_id == session["user_id"])
            .all()
        )

        history = []
        last_price = None

        for p in prices:
            current_price = float(p.price_value)

            if last_price is None or current_price != last_price:
                history.append(
                    {"price": current_price, "created_at": p.created_at.isoformat()}
                )
                last_price = current_price

        return jsonify(history)
    finally:
        db.close()


@ui_bp.route("/api/supported-shops")
def api_supported_shops():
    shops = sorted(
        base.replace("https://", "").replace("http://", "") for base in SELECTORS.keys()
    )

    return jsonify(shops)


@ui_bp.route("/telegram-verification", methods=["GET"])
@login_required
def telegram_verification():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthenticated"}), 401

    db = ui_bp.session_factory()
    user = db.query(User).get(user_id)

    if not user:
        db.close()
        return jsonify({"error": "unauthenticated"}), 401

    token = user.telegram_verification_token
    db.close()

    return jsonify({"token": token})


@ui_bp.route("/telegram-verification/by-email", methods=["GET"])
def telegram_verification_by_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400

    db = ui_bp.session_factory()
    user = db.query(User).filter_by(email=email).first()

    if not user:
        db.close()
        return jsonify({"error": "user not found"}), 404

    result = {
        "telegram_verified": user.telegram_verified,
        "token": user.telegram_verification_token,
    }

    db.close()
    return jsonify(result), 200
