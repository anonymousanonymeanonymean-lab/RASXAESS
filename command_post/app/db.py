"""SQLite engine + session factory."""
from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

_engine = None


def init_db(db_path: str):
    global _engine
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    _engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    # Import models to register them
    from app import models  # noqa: F401
    SQLModel.metadata.create_all(_engine)
    return _engine


def get_engine():
    if _engine is None:
        raise RuntimeError("DB not initialized")
    return _engine


def get_session():
    with Session(get_engine()) as session:
        yield session