from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session
from app.schemas import OrderCreate, OrderRead, TicketCreate, TicketRead

router = APIRouter(prefix="/store", tags=["store"])


@router.post("/orders", response_model=OrderRead)
async def create_order(payload: OrderCreate, session: AsyncSession = Depends(get_session)):
    enabled = await crud.get_provider_toggle(session, payload.provider)
    if not enabled:
        raise HTTPException(status_code=400, detail="Payment provider disabled")
    order = await crud.create_order(session, payload)
    return OrderRead.model_validate(order, from_attributes=True)


@router.get("/orders", response_model=list[OrderRead])
async def list_orders(session: AsyncSession = Depends(get_session)):
    rows = await crud.list_orders(session)
    return [OrderRead.model_validate(x, from_attributes=True) for x in rows]


@router.post("/tickets", response_model=TicketRead)
async def create_ticket(payload: TicketCreate, session: AsyncSession = Depends(get_session)):
    row = await crud.create_ticket(session, payload)
    return TicketRead.model_validate(row, from_attributes=True)


@router.get("/tickets", response_model=list[TicketRead])
async def list_tickets(session: AsyncSession = Depends(get_session)):
    rows = await crud.list_tickets(session)
    return [TicketRead.model_validate(x, from_attributes=True) for x in rows]
