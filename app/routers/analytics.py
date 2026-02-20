from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_session
from app.schemas import ProfitResponse, StarsTopRow

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stars-top", response_model=list[StarsTopRow])
async def stars_top(session: AsyncSession = Depends(get_session)):
    rows = await crud.stars_top(session)
    return [StarsTopRow(user_id=r[0], total_amount=float(r[1] or 0), transactions=int(r[2])) for r in rows]


@router.get("/profit", response_model=ProfitResponse)
async def profit(session: AsyncSession = Depends(get_session)):
    result = await crud.profit(session)
    return ProfitResponse(**result)
