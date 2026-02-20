from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class UserStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class ProductType(StrEnum):
    STARS = "stars"
    NFT_RENT = "nft_rent"
    VIRTUAL_NUMBER = "virtual_number"
    TELEGRAM_PREMIUM = "telegram_premium"


class PaymentProvider(StrEnum):
    PALLY = "pally"
    PLATEGA = "platega"
    CRYPTOBOT = "cryptobot"
    FREEKASSA = "freekassa"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(index=True, unique=True)
    username: str | None = None
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    stars_balance: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    product_type: ProductType
    amount: int = Field(default=1)
    total_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProviderState(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    provider: PaymentProvider = Field(unique=True)
    is_enabled: bool = Field(default=True)


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    title: str
    body: str
    is_closed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StarsCheck(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    amount: int
    code: str = Field(unique=True)
    is_redeemed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
