"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.config.settings import Settings, load_settings


@pytest.fixture
def settings() -> Settings:
    return load_settings()


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> str:
    return str(tmp_path / "test_ona.db")