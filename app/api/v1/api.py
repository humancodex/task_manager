from fastapi import APIRouter
from app.api.v1.endpoints import tasks, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tasks.router, tags=["tasks"])