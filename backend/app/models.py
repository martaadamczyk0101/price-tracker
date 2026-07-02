from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)

    telegram_id = Column(String(50), nullable=True, unique=True)
    telegram_verified = Column(Boolean, default=False)
    telegram_verification_token = Column(String(64), nullable=True)

    is_active = Column(Boolean, default=False)

    password_hash = Column(String(255), nullable=False)

    products = relationship("Product", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    name = Column(String(255))
    image_url = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="products")
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    initial_price = Column(DECIMAL(10, 2))
    has_error = Column(Boolean, default=False)

    prices = relationship("Price", back_populates="product")
    alerts = relationship("Alert", back_populates="product")
    logs = relationship("Log", back_populates="product")

    @property
    def current_price(self):
        if not self.prices:
            return None
        return self.prices[-1].price_value


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price_value = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="PLN")
    created_at = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="prices")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    active = Column(Boolean, default=True)

    last_notified_price = Column(DECIMAL(10, 2), nullable=True)

    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    message = Column(Text)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="logs")
