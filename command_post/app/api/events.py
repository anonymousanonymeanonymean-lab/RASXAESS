from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.db import get_session

router = APIRouter()


@router.get("/events")
async def list_events(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    return [ctx.events.to_dict(e) for e in ctx.events.list(session, ctx.settings.mission_id)]


@router.get("/events/{event_id}")
async def get_event(event_id: str, request: Request,
                    session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    for e in ctx.events.list(session, ctx.settings.mission_id):
        if e.event_id == event_id:
            return ctx.events.to_dict(e)
    raise HTTPException(status_code=404, detail="event not found")