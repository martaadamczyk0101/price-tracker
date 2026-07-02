import requests

import backend.config as config


def send_telegram_message(text: str, chat_id: str):
    token = config.TELEGRAM_BOT_TOKEN

    if not token or not chat_id:
        return False

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }

        requests.post(url, json=payload, timeout=10)
        return True

    except Exception:
        return False
