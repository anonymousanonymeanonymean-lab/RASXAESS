from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.db import get_session

router = APIRouter()


@router.get("/mission")
async def get_mission(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    m = ctx.mission.get(session, ctx.settings.mission_id)
    if m is None:
        raise HTTPException(status_code=404, detail="mission not found")
    return m


@router.post("/mission/start")
async def start_mission(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    m = ctx.mission.set_status(session, ctx.settings.mission_id, "active")
    return m


@router.post("/mission/stop")
async def stop_mission(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    m = ctx.mission.set_status(session, ctx.settings.mission_id, "stopped")
    return m