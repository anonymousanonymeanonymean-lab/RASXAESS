from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.aging import AgingPolicy, AgingState


def test_aging_classification():
    p = AgingPolicy(new_s=10, active_s=60, recent_s=300, stale_s=900)
    now = datetime.now(timezone.utc)

    assert p.classify(now - timedelta(seconds=1), now)[0] == AgingState.NEW
    assert p.classify(now - timedelta(seconds=30), now)[0] == AgingState.ACTIVE
    assert p.classify(now - timedelta(seconds=120), now)[0] == AgingState.RECENT
    assert p.classify(now - timedelta(seconds=600), now)[0] == AgingState.STALE
    assert p.classify(now - timedelta(seconds=3600), now)[0] == AgingState.EXPIRED