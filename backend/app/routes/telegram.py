from flask import Blueprint, request

from backend.app.models import User
from backend.app.utils.telegram_sender import send_telegram_message

telegram_bp = Blueprint("telegram", __name__, url_prefix="/telegram")


@telegram_bp.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json() or {}
    message = data.get("message", {})
    text = message.get("text")
    chat_id = message.get("chat", {}).get("id")

    if not text or not chat_id:
        return "ok"

    if not text.startswith("/start"):
        return "ok"

    parts = text.split(" ")
    if len(parts) != 2:
        send_telegram_message("Nieprawidłowy format. Użyj: /start TOKEN", chat_id)
        return "ok"

    token = parts[1]

    db = telegram_bp.session_factory()
    user = db.query(User).filter_by(telegram_verification_token=token).first()

    if not user:
        send_telegram_message("Nieprawidłowy lub wygasły token.", chat_id)
        db.close()
        return "ok"

    user.telegram_id = str(chat_id)
    user.telegram_verified = True
    user.is_active = True
    user.telegram_verification_token = None

    db.commit()
    db.close()

    send_telegram_message("Konto zweryfikowane. Możesz się zalogować.", chat_id)
    return "ok"
