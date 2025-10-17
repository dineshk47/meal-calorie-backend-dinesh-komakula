from fastapi import APIRouter, Depends

from app.auth.router import router as auth_router
from app.calories.router import router as calories_router
from app.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(
    users_router, prefix="/users", tags=["Users"]
)
api_router.include_router(
    calories_router, prefix="/calories", tags=["Calories"]
)
