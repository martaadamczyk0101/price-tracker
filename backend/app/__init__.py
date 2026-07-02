from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import config
from backend.app.models import Base
from backend.app.routes.auth import auth_bp
from backend.app.routes.telegram import telegram_bp
from backend.app.routes.ui import ui_bp


def create_app():
    app = Flask(__name__)

    CORS(
        app,
        supports_credentials=True,
        origins=config.ALLOWED_ORIGINS,
    )

    app.config.update(
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )

    app.secret_key = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False, pool_pre_ping=True, pool_recycle=3600)
    Base.metadata.create_all(engine)
    app.session_factory = sessionmaker(bind=engine)

    app.register_blueprint(ui_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(telegram_bp)

    ui_bp.session_factory = app.session_factory
    auth_bp.session_factory = app.session_factory
    telegram_bp.session_factory = app.session_factory

    return app
