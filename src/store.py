from __future__ import annotations

from collections.abc import Iterable

from .models import Check, Product, User


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}
        self.products: dict[str, Product] = {}
        self.checks: dict[str, Check] = {}

    def get_or_create_user(self, user_id: int, username: str | None) -> User:
        user = self.users.get(user_id)
        if user is None:
            user = User(user_id=user_id, username=username)
            self.users[user_id] = user
        else:
            user.username = username
        return user

    def add_products(self, products: Iterable[Product]) -> None:
        for product in products:
            self.products[product.sku] = product

    def get_product(self, sku: str) -> Product | None:
        return self.products.get(sku)

    def get_check(self, code: str) -> Check | None:
        return self.checks.get(code)

    def add_check(self, check: Check) -> None:
        self.checks[check.code] = check
