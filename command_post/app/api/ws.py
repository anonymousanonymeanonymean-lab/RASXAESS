from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    mgr = websocket.app.state.ctx.ws
    await mgr.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()  # ignore incoming
    except WebSocketDisconnect:
        await mgr.disconnect(websocket)
    except Exception:
        await mgr.disconnect(websocket)