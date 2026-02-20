import secrets

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderStatus, PaymentProvider, PaymentToggle, ProductType, StarsCheck, Ticket, User
from app.schemas import OrderCreate, TicketCreate, UserCreate


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    user = User(telegram_id=payload.telegram_id, username=payload.username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def list_users(session: AsyncSession) -> list[User]:
    res = await session.execute(select(User).order_by(User.id.desc()))
    return list(res.scalars().all())


async def set_user_block(session: AsyncSession, user_id: int, is_blocked: bool) -> User | None:
    user = await session.get(User, user_id)
    if not user:
        return None
    user.is_blocked = is_blocked
    await session.commit()
    await session.refresh(user)
    return user


async def create_order(session: AsyncSession, payload: OrderCreate) -> Order:
    order = Order(**payload.model_dump())
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def list_orders(session: AsyncSession) -> list[Order]:
    res = await session.execute(select(Order).order_by(Order.id.desc()))
    return list(res.scalars().all())


async def create_ticket(session: AsyncSession, payload: TicketCreate) -> Ticket:
    ticket = Ticket(**payload.model_dump())
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket


async def list_tickets(session: AsyncSession) -> list[Ticket]:
    res = await session.execute(select(Ticket).order_by(Ticket.id.desc()))
    return list(res.scalars().all())


async def set_provider_toggle(session: AsyncSession, provider: PaymentProvider, enabled: bool) -> PaymentToggle:
    res = await session.execute(select(PaymentToggle).where(PaymentToggle.provider == provider))
    row = res.scalar_one_or_none()
    if row is None:
        row = PaymentToggle(provider=provider, is_enabled=enabled)
        session.add(row)
    else:
        row.is_enabled = enabled
    await session.commit()
    await session.refresh(row)
    return row


async def get_provider_toggle(session: AsyncSession, provider: PaymentProvider) -> bool:
    res = await session.execute(select(PaymentToggle).where(PaymentToggle.provider == provider))
    row = res.scalar_one_or_none()
    return True if row is None else row.is_enabled


async def create_stars_check(session: AsyncSession, user_id: int, amount: float) -> StarsCheck:
    user = await session.get(User, user_id)
    if user is None:
        raise ValueError("User not found")
    if user.stars_balance < amount:
        raise ValueError("Insufficient stars balance")
    user.stars_balance -= amount
    check = StarsCheck(user_id=user_id, amount=amount, code=secrets.token_hex(8))
    session.add(check)
    await session.commit()
    await session.refresh(check)
    return check


async def stars_top(session: AsyncSession):
    q = (
        select(
            Order.user_id,
            func.sum(Order.amount).label("total_amount"),
            func.count(Order.id).label("transactions"),
        )
        .where(Order.product_type == ProductType.telegram_stars)
        .where(Order.status.in_([OrderStatus.paid, OrderStatus.fulfilled]))
        .group_by(Order.user_id)
        .order_by(func.sum(Order.amount).desc())
        .limit(10)
    )
    res = await session.execute(q)
    return res.all()


async def profit(session: AsyncSession):
    q = select(func.sum(Order.amount), func.sum(Order.cost_price)).where(
        Order.status.in_([OrderStatus.paid, OrderStatus.fulfilled])
    )
    gross, cost = (await session.execute(q)).one()
    gross = float(gross or 0)
    cost = float(cost or 0)
    return {"gross": gross, "cost_price": cost, "net_profit": gross - cost}
