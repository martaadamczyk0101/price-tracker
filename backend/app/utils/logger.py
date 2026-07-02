import traceback
from typing import Optional


def add_log(product_id: Optional[int], message: str, status: str = "INFO"):
    try:
        from flask import current_app
        from backend.app.models import Log

        db = current_app.session_factory()
        try:
            log = Log(product_id=product_id, message=message[:390], status=status)
            db.add(log)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print("Failed to write log to DB:", e)
        traceback.print_exc()
