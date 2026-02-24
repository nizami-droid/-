import asyncio

import pytest

import db


@pytest.mark.asyncio
async def test_mark_user_seen_first_call_inserts(tmp_path, monkeypatch):
    db_path = tmp_path / "users.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))

    await db.init_db()

    first = await db.mark_user_seen(123)
    second = await db.mark_user_seen(123)

    assert first is True
    assert second is False


@pytest.mark.asyncio
async def test_mark_user_seen_concurrent_only_one_inserts(tmp_path, monkeypatch):
    db_path = tmp_path / "users.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))

    await db.init_db()

    results = await asyncio.gather(
        *[db.mark_user_seen(456) for _ in range(10)]
    )

    assert sum(results) == 1
