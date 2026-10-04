from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("CP_DB_PATH", "./data/test_cp.db")
os.environ.setdefault("CP_MQTT_ENABLED", "false")


@pytest.fixture
def tmp_db(tmp_path: Path) -> str:
    return str(tmp_path / "test.db")