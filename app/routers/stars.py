from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session

router = APIRouter(prefix="/stars", tags=["stars"])


class StarsCheckCreate(BaseModel):
    user_id: int
    amount: float


@router.post("/checks")
async def create_check(payload: StarsCheckCreate, session: AsyncSession = Depends(get_session)):
    try:
        row = await crud.create_stars_check(session, payload.user_id, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"check_code": row.code, "amount": row.amount}
