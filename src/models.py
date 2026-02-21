from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OperationType(str, Enum):
    TOP_UP = "top_up"
    PURCHASE = "purchase"
    CHECK_CREATE = "check_create"
    CHECK_REDEEM = "check_redeem"


@dataclass(slots=True)
class Product:
    sku: str
    name: str
    category: str
    price_stars: int
    stock: int | None = None


@dataclass(slots=True)
class Operation:
    op_type: OperationType
    amount: int
    reason: str
    at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class User:
    user_id: int
    username: str | None
    stars_balance: int = 0
    orders_count: int = 0
    purchases_total: int = 0
    is_blocked: bool = False
    operations: list[Operation] = field(default_factory=list)


@dataclass(slots=True)
class Check:
    code: str
    owner_user_id: int
    amount: int
    activated_by: int | None = None
    activated_at: datetime | None = None

    @property
    def is_activated(self) -> bool:
        return self.activated_by is not None
