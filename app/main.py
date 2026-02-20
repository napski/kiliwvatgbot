from collections import Counter
from datetime import datetime
from secrets import token_urlsafe

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.config import settings
from app.db import engine, get_session, init_db
from app.models import (
    Order,
    PaymentProvider,
    ProductType,
    ProviderState,
    StarsCheck,
    Ticket,
    User,
    UserStatus,
)

app = FastAPI(title=settings.app_name)


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None


class OrderCreate(BaseModel):
    user_id: int
    product_type: ProductType
    amount: int
    total_price: float


class TicketCreate(BaseModel):
    user_id: int
    title: str
    body: str


class StarsTopUp(BaseModel):
    amount: int


class StarsCheckCreate(BaseModel):
    amount: int


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_provider_states()


def seed_provider_states() -> None:
    with Session(engine) as session:
        for provider in PaymentProvider:
            existing = session.exec(
                select(ProviderState).where(ProviderState.provider == provider)
            ).first()
            if not existing:
                session.add(ProviderState(provider=provider, is_enabled=True))
        session.commit()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/users", response_model=User)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    user = User(telegram_id=payload.telegram_id, username=payload.username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users", response_model=list[User])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@app.patch("/users/{user_id}/block", response_model=User)
def block_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.BLOCKED
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/orders", response_model=Order)
def create_order(payload: OrderCreate, session: Session = Depends(get_session)):
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    order = Order(**payload.model_dump())
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@app.get("/orders", response_model=list[Order])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order).order_by(Order.created_at.desc())).all()


@app.post("/tickets", response_model=Ticket)
def create_ticket(payload: TicketCreate, session: Session = Depends(get_session)):
    ticket = Ticket(**payload.model_dump())
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@app.get("/tickets", response_model=list[Ticket])
def list_tickets(session: Session = Depends(get_session)):
    return session.exec(select(Ticket).order_by(Ticket.created_at.desc())).all()


@app.get("/payments/providers", response_model=list[ProviderState])
def list_provider_states(session: Session = Depends(get_session)):
    return session.exec(select(ProviderState)).all()


@app.patch("/payments/providers/{provider}/toggle", response_model=ProviderState)
def toggle_provider(provider: PaymentProvider, session: Session = Depends(get_session)):
    state = session.exec(
        select(ProviderState).where(ProviderState.provider == provider)
    ).first()
    if not state:
        raise HTTPException(status_code=404, detail="Provider not found")
    state.is_enabled = not state.is_enabled
    session.add(state)
    session.commit()
    session.refresh(state)
    return state


@app.post("/users/{user_id}/stars/topup", response_model=User)
def top_up_stars(user_id: int, payload: StarsTopUp, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    user.stars_balance += payload.amount
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/users/{user_id}/stars/checks", response_model=StarsCheck)
def create_stars_check(
    user_id: int, payload: StarsCheckCreate, session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.amount <= 0 or payload.amount > user.stars_balance:
        raise HTTPException(status_code=400, detail="Invalid amount")
    user.stars_balance -= payload.amount
    check = StarsCheck(
        user_id=user_id,
        amount=payload.amount,
        code=token_urlsafe(8),
    )
    session.add(user)
    session.add(check)
    session.commit()
    session.refresh(check)
    return check


@app.get("/analytics/top-users")
def top_users(session: Session = Depends(get_session)):
    orders = session.exec(select(Order)).all()
    totals = Counter()
    counts = Counter()
    for order in orders:
        if order.product_type == ProductType.STARS:
            totals[order.user_id] += order.total_price
            counts[order.user_id] += 1

    result = [
        {"user_id": uid, "stars_volume": round(total, 2), "transactions": counts[uid]}
        for uid, total in totals.items()
    ]
    result.sort(key=lambda row: row["stars_volume"], reverse=True)
    return result


@app.get("/analytics/profit-calculator")
def profit_calculator(revenue: float, cost: float, commission_percent: float = 0.0):
    commission = revenue * (commission_percent / 100)
    profit = revenue - cost - commission
    margin = (profit / revenue * 100) if revenue else 0
    return {
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "commission": round(commission, 2),
        "profit": round(profit, 2),
        "margin_percent": round(margin, 2),
    }
