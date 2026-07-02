import json
import os
import secrets
import string
from datetime import datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask import session as flask_session

import backend.config as config
from backend.app.models import Alert, Log, Price, Product, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

DEMO_EMAIL = config.DEMO_EMAIL
SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "demo_snapshot.json")


def _reset_demo_account(db, user):
    snapshot_file = os.path.normpath(SNAPSHOT_PATH)
    if not os.path.exists(snapshot_file):
        return

    with open(snapshot_file) as f:
        snapshot_products = json.load(f)

    existing = {p.url: p for p in db.query(Product).filter_by(user_id=user.id).all()}
    snapshot_urls = {pd["url"] for pd in snapshot_products}

    # Remove products no longer in snapshot
    for url, product in list(existing.items()):
        if url not in snapshot_urls:
            pid = product.id
            db.query(Log).filter_by(product_id=pid).delete(synchronize_session=False)
            db.query(Price).filter_by(product_id=pid).delete(synchronize_session=False)
            db.query(Alert).filter_by(product_id=pid).delete(synchronize_session=False)
            db.delete(product)
    db.flush()

    for pd in snapshot_products:
        url = pd["url"]
        if url in existing:
            # Product already exists — keep its live prices, just refresh metadata
            product = existing[url]
            product.name = pd["name"]
            product.image_url = pd.get("image_url")
            product.active = True
            product.has_error = False
        else:
            # New product — create it with snapshot prices
            product = Product(
                url=url,
                name=pd["name"],
                image_url=pd.get("image_url"),
                user_id=user.id,
                initial_price=Decimal(pd["initial_price"]),
                active=True,
                has_error=False,
                created_at=datetime.fromisoformat(pd["created_at"]),
            )
            db.add(product)
            db.flush()

            for entry in pd["prices"]:
                db.add(Price(
                    product_id=product.id,
                    price_value=Decimal(entry["price_value"]),
                    currency=entry["currency"],
                    created_at=datetime.fromisoformat(entry["created_at"]),
                ))

            last_price = Decimal(pd["prices"][-1]["price_value"]) if pd["prices"] else Decimal(pd["initial_price"])
            alert = db.query(Alert).filter_by(user_id=user.id, product_id=product.id).first()
            if not alert:
                db.add(Alert(
                    user_id=user.id,
                    product_id=product.id,
                    last_notified_price=last_price,
                ))

    db.commit()


def generate_telegram_token(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@auth_bp.route("/register", methods=["POST"])
def register():
    db = auth_bp.session_factory()
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify(
                    {
                        "error": "VALIDATION_ERROR",
                        "message": "request body must be JSON",
                    }
                ),
                400,
            )

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return (
                jsonify(
                    {
                        "error": "VALIDATION_ERROR",
                        "message": "email and password are required",
                    }
                ),
                400,
            )

        if db.query(User).filter_by(email=email).first():
            return (
                jsonify(
                    {
                        "error": "EMAIL_EXISTS",
                        "message": "An account with this email already exists",
                    }
                ),
                409,
            )

        user = User(
            email=email,
            telegram_verification_token=generate_telegram_token(),
            telegram_verified=False,
            is_active=False,
        )
        user.set_password(password)

        db.add(user)
        db.commit()
        db.expire_all()

        return (
            jsonify(
                {
                    "message": "user registered",
                    "telegram_verification_required": True,
                }
            ),
            201,
        )

    except Exception as e:
        db.rollback()
        return jsonify({"error": "DB_ERROR", "message": str(e)}), 500

    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    db = auth_bp.session_factory()
    try:
        data = request.get_json()

        email = data.get("email") if data else None
        password = data.get("password") if data else None

        if not email or not password:
            return jsonify({"error": "email and password required"}), 400

        user = db.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid credentials"}), 401

        if not user.is_active:
            return (
                jsonify(
                    {
                        "error": "ACCOUNT_NOT_VERIFIED",
                        "message": "Verify Telegram first",
                    }
                ),
                403,
            )

        flask_session["user_id"] = user.id
        return jsonify({"message": "logged in"}), 200
    finally:
        db.close()


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = flask_session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 401

    db = auth_bp.session_factory()
    try:
        user = db.query(User).get(user_id)

        if not user:
            return jsonify({"authenticated": False}), 401

        return jsonify(
            {
                "authenticated": True,
                "email": user.email,
                "telegram_verified": user.telegram_verified,
                "is_demo": user.email == DEMO_EMAIL,
            }
        )
    finally:
        db.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    flask_session.clear()
    return jsonify({"message": "logged out"}), 200


@auth_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    data = request.get_json()
    email = data.get("email") if data else None
    if not email:
        return jsonify({"error": "email required"}), 400

    db = auth_bp.session_factory()
    user = db.query(User).filter_by(email=email).first()

    if not user:
        return jsonify({"error": "user not found"}), 404

    if user.telegram_verified:
        return jsonify({"error": "already verified"}), 400

    user.telegram_verification_token = generate_telegram_token()
    db.commit()
    token = user.telegram_verification_token
    db.close()

    return jsonify({"token": token}), 200


@auth_bp.route("/demo-login", methods=["POST"])
def demo_login():
    db = auth_bp.session_factory()

    user = db.query(User).filter_by(email=DEMO_EMAIL).first()
    if not user:
        user = User(
            email=DEMO_EMAIL,
            telegram_verification_token="DEMO00",
            telegram_verified=True,
            is_active=True,
        )
        user.set_password("demo123")
        db.add(user)
        db.commit()
        db.expire_all()

    _reset_demo_account(db, user)

    flask_session["user_id"] = user.id
    db.close()
    return jsonify({"message": "logged in"}), 200
