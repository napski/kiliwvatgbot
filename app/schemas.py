from datetime import datetime

from pydantic import BaseModel

from app.models import OrderStatus, PaymentProvider, ProductType


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None


class UserRead(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    is_blocked: bool
    stars_balance: float


class OrderCreate(BaseModel):
    user_id: int
    product_type: ProductType
    amount: float
    cost_price: float = 0
    provider: PaymentProvider
    details: str | None = None


class OrderRead(BaseModel):
    id: int
    user_id: int
    product_type: ProductType
    amount: float
    provider: PaymentProvider
    status: OrderStatus
    created_at: datetime


class TicketCreate(BaseModel):
    user_id: int
    subject: str
    message: str


class TicketRead(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    is_closed: bool
    created_at: datetime


class ToggleUpdate(BaseModel):
    is_enabled: bool


class StarsTopRow(BaseModel):
    user_id: int
    total_amount: float
    transactions: int


class ProfitResponse(BaseModel):
    gross: float
    cost_price: float
    net_profit: float
