from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session
from app.models import PaymentProvider
from app.schemas import ToggleUpdate, UserCreate, UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=UserRead)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    row = await crud.create_user(session, payload)
    return UserRead.model_validate(row, from_attributes=True)


@router.get("/users", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)):
    rows = await crud.list_users(session)
    return [UserRead.model_validate(x, from_attributes=True) for x in rows]


@router.post("/users/{user_id}/block", response_model=UserRead)
async def block_user(user_id: int, session: AsyncSession = Depends(get_session)):
    row = await crud.set_user_block(session, user_id, True)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(row, from_attributes=True)


@router.post("/users/{user_id}/unblock", response_model=UserRead)
async def unblock_user(user_id: int, session: AsyncSession = Depends(get_session)):
    row = await crud.set_user_block(session, user_id, False)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(row, from_attributes=True)


@router.put("/payments/{provider}")
async def toggle_provider(provider: PaymentProvider, payload: ToggleUpdate, session: AsyncSession = Depends(get_session)):
    row = await crud.set_provider_toggle(session, provider, payload.is_enabled)
    return {"provider": row.provider, "is_enabled": row.is_enabled}
