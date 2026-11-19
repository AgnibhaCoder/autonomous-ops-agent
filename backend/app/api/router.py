from fastapi import APIRouter
from app.api.endpoints import tasks, approval, websockets

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(approval.router, prefix="/tasks", tags=["Approvals"])
api_router.include_router(websockets.router, tags=["WebSockets"])