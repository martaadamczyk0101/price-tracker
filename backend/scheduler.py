import schedule
import threading
import time

import requests

import backend.config as config
from backend.app import create_app
from backend.app.models import User
from backend.app.utils.price_checker import update_prices
from backend.app.utils.telegram_sender import send_telegram_message
from backend.snapshot_demo import run as snapshot_demo

app = create_app()


def run_update():
    try:
        with app.app_context():
            session = app.session_factory()
            update_prices(session)
            session.close()
        snapshot_demo()
        print("Price update completed", flush=True)
    except Exception as e:
        print(f"Price update error: {e}", flush=True)


def handle_telegram_update(update):
    message = update.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not text or not chat_id or not text.startswith("/start"):
        return

    parts = text.strip().split(" ")
    if len(parts) != 2:
        send_telegram_message("Nieprawidłowy format. Użyj: /start TOKEN", chat_id)
        return

    token = parts[1]

    db = app.session_factory()
    try:
        user = db.query(User).filter_by(telegram_verification_token=token).first()
        if not user:
            send_telegram_message("Nieprawidłowy lub wygasły token.", chat_id)
            return

        existing = db.query(User).filter_by(telegram_id=str(chat_id)).first()
        if existing and existing.id != user.id:
            send_telegram_message("To konto Telegram jest już powiązane z innym kontem.", chat_id)
            return

        user.telegram_id = str(chat_id)
        user.telegram_verified = True
        user.is_active = True
        user.telegram_verification_token = None
        db.commit()

        send_telegram_message("Konto zweryfikowane. Możesz się zalogować.", chat_id)
        print(f"Telegram verified for user {user.email}", flush=True)
    except Exception as e:
        print(f"Telegram verification error: {e}", flush=True)
        db.rollback()
    finally:
        db.close()


def run_telegram_polling():
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        print("No TELEGRAM_BOT_TOKEN set, skipping polling.", flush=True)
        return

    # Remove any existing webhook so polling works
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/deleteWebhook",
            json={"drop_pending_updates": False},
            timeout=10,
        )
        print("Webhook removed, starting polling.", flush=True)
    except Exception as e:
        print(f"Could not remove webhook: {e}", flush=True)

    offset = None
    while True:
        try:
            params = {"timeout": 30, "limit": 100}
            if offset is not None:
                params["offset"] = offset

            resp = requests.get(
                f"https://api.telegram.org/bot{token}/getUpdates",
                params=params,
                timeout=40,
            )
            data = resp.json()

            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                handle_telegram_update(update)

        except Exception as e:
            print(f"Telegram polling error: {e}", flush=True)
            time.sleep(5)


schedule.every().day.at("06:00").do(run_update)
schedule.every().day.at("18:00").do(run_update)

polling_thread = threading.Thread(target=run_telegram_polling, daemon=True)
polling_thread.start()

print("Scheduler started — running at 06:00, 18:00 PL.", flush=True)

while True:
    schedule.run_pending()
    time.sleep(60)
