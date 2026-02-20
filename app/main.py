from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import admin, analytics, stars, store

app = FastAPI(title=settings.app_name)

app.include_router(admin.router)
app.include_router(store.router)
app.include_router(stars.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "features": [
            "telegram-shop-api",
            "admin-panel-backend",
            "stars-checks",
            "analytics",
        ],
    }
