from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.db import get_session

router = APIRouter()


@router.get("/beacons")
async def list_beacons(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    return ctx.beacons.list(session)