import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaymentProvider(str, enum.Enum):
    pally = "pally"
    platega = "platega"
    cryptobot = "cryptobot"
    freekassa = "freekassa"


class OrderStatus(str, enum.Enum):
    created = "created"
    paid = "paid"
    cancelled = "cancelled"
    fulfilled = "fulfilled"


class ProductType(str, enum.Enum):
    telegram_stars = "telegram_stars"
    nft_rent = "nft_rent"
    virtual_number = "virtual_number"
    telegram_premium = "telegram_premium"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    stars_balance: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType), index=True)
    amount: Mapped[float] = mapped_column(Float)
    cost_price: Mapped[float] = mapped_column(Float, default=0)
    provider: Mapped[PaymentProvider] = mapped_column(Enum(PaymentProvider))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.created, index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="orders")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(Text)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="tickets")


class PaymentToggle(Base):
    __tablename__ = "payment_toggles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[PaymentProvider] = mapped_column(Enum(PaymentProvider), unique=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class StarsCheck(Base):
    __tablename__ = "stars_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    is_redeemed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
