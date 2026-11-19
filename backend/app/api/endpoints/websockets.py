from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.ws_manager import ws_manager

router = APIRouter()

@router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await ws_manager.connect(task_id, websocket)
    try:
        while True:
            # Keeps websocket connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(task_id, websocket)