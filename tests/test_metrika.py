import pytest

import metrika


class _FakeResponse:
    def __init__(self, status: int):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, status: int, attempts: list[int]):
        self._status = status
        self._attempts = attempts

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, *args, **kwargs):
        self._attempts.append(1)
        return _FakeResponse(self._status)


@pytest.mark.asyncio
async def test_send_goal_retries_on_5xx(monkeypatch):
    statuses = [500, 200]
    attempts: list[int] = []

    def fake_client_session(*args, **kwargs):
        return _FakeSession(statuses.pop(0), attempts)

    async def no_sleep(_):
        return None

    monkeypatch.setattr(metrika.aiohttp, "ClientSession", fake_client_session)
    monkeypatch.setattr(metrika.asyncio, "sleep", no_sleep)

    ok = await metrika.send_goal(
        counter_id="1",
        goal_name="bot_start",
        user_id=123,
        max_attempts=3,
        retry_backoff=0,
    )

    assert ok is True
    assert len(attempts) == 2
