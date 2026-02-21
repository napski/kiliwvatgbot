from src.services import BusinessError, ShopService
from src.store import InMemoryStore


def build_service() -> ShopService:
    store = InMemoryStore()
    service = ShopService(store)
    service.seed_catalog()
    return service


def test_top_up_and_buy_flow() -> None:
    service = build_service()

    user = service.top_up_stars(1, "alice", 1000)
    assert user.stars_balance == 1000

    user, product, total = service.buy(1, "alice", "tg-premium-1m", 1)
    assert product.sku == "tg-premium-1m"
    assert total == 790
    assert user.stars_balance == 210


def test_check_redeem_once() -> None:
    service = build_service()
    service.top_up_stars(1, "alice", 500)

    check = service.create_check(1, "alice", 200)
    assert check.amount == 200

    bob = service.profile(2, "bob")
    assert bob.stars_balance == 0

    service.redeem_check(2, "bob", check.code)
    bob = service.profile(2, "bob")
    assert bob.stars_balance == 200

    try:
        service.redeem_check(1, "alice", check.code)
        assert False, "Expected BusinessError"
    except BusinessError:
        pass


def test_cannot_create_check_with_insufficient_balance() -> None:
    service = build_service()
    service.top_up_stars(1, "alice", 100)

    try:
        service.create_check(1, "alice", 200)
        assert False, "Expected BusinessError"
    except BusinessError:
        pass
