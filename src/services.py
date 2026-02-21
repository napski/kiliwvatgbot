from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from .models import Check, Operation, OperationType, Product, User
from .store import InMemoryStore


class BusinessError(ValueError):
    pass


class ShopService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def seed_catalog(self) -> None:
        self.store.add_products(
            [
                Product("stars-100", "100 Telegram Stars", "Stars", 120),
                Product("nft-rent-24h", "NFT аренда 24ч", "NFT", 350),
                Product("vm-number", "Виртуальный номер", "Numbers", 180),
                Product("tg-premium-1m", "Telegram Premium 1 мес", "Premium", 790),
            ]
        )

    def profile(self, user_id: int, username: str | None) -> User:
        return self.store.get_or_create_user(user_id, username)

    def top_up_stars(self, user_id: int, username: str | None, amount: int) -> User:
        if amount <= 0:
            raise BusinessError("Сумма пополнения должна быть больше 0.")
        user = self.profile(user_id, username)
        self._ensure_not_blocked(user)
        user.stars_balance += amount
        user.operations.append(Operation(OperationType.TOP_UP, amount, "Пополнение Stars"))
        return user

    def buy(self, user_id: int, username: str | None, sku: str, qty: int = 1) -> tuple[User, Product, int]:
        if qty <= 0:
            raise BusinessError("Количество должно быть больше 0.")
        user = self.profile(user_id, username)
        self._ensure_not_blocked(user)

        product = self.store.get_product(sku)
        if not product:
            raise BusinessError("Товар не найден.")

        if product.stock is not None and product.stock < qty:
            raise BusinessError("Недостаточно товара на складе.")

        total = product.price_stars * qty
        if user.stars_balance < total:
            raise BusinessError("Недостаточно Stars на балансе.")

        user.stars_balance -= total
        user.orders_count += qty
        user.purchases_total += total
        user.operations.append(
            Operation(OperationType.PURCHASE, total, f"Покупка {product.sku} x{qty}")
        )

        if product.stock is not None:
            product.stock -= qty

        return user, product, total

    def create_check(self, user_id: int, username: str | None, amount: int) -> Check:
        if amount <= 0:
            raise BusinessError("Сумма чека должна быть больше 0.")

        user = self.profile(user_id, username)
        self._ensure_not_blocked(user)

        if user.stars_balance < amount:
            raise BusinessError("Нельзя создать чек больше текущего баланса.")

        user.stars_balance -= amount
        user.operations.append(Operation(OperationType.CHECK_CREATE, amount, "Создание чека"))

        code = uuid4().hex[:10].upper()
        check = Check(code=code, owner_user_id=user.user_id, amount=amount)
        self.store.add_check(check)
        return check

    def redeem_check(self, user_id: int, username: str | None, code: str) -> Check:
        user = self.profile(user_id, username)
        self._ensure_not_blocked(user)

        check = self.store.get_check(code.strip().upper())
        if not check:
            raise BusinessError("Чек не найден.")

        if check.is_activated:
            raise BusinessError("Чек уже активирован.")

        check.activated_by = user.user_id
        check.activated_at = datetime.utcnow()

        user.stars_balance += check.amount
        user.operations.append(Operation(OperationType.CHECK_REDEEM, check.amount, f"Активация чека {check.code}"))
        return check

    def leaderboard(self, limit: int = 10) -> list[User]:
        users = sorted(self.store.users.values(), key=lambda u: (u.purchases_total, u.orders_count), reverse=True)
        return users[:limit]

    @staticmethod
    def _ensure_not_blocked(user: User) -> None:
        if user.is_blocked:
            raise BusinessError("Пользователь заблокирован.")
