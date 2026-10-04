from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.db import get_session

router = APIRouter()


@router.get("/robots")
async def list_robots(request: Request, session: Session = Depends(get_session)):
    ctx = request.app.state.ctx
    return ctx.robots.list(session)