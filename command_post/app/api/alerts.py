from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.db import get_session

router = APIRouter()


@router.get("/alerts")
async def list_alerts(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    return ctx.alerts.list(session, ctx.settings.mission_id)


@router.post("/alerts/{alert_id}/ack")
async def ack_alert(alert_id: str, request: Request,
                    session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    a = ctx.alerts.ack(session, alert_id)
    if a is None:
        raise HTTPException(status_code=404, detail="alert not found")
    return a


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, request: Request,
                        session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    a = ctx.alerts.resolve(session, alert_id)
    if a is None:
        raise HTTPException(status_code=404, detail="alert not found")
    return a