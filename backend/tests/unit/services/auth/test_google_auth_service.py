import pytest

from app.services.auth.google_auth_service import exchange_code_for_tokens


class DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, status_code: int, payload: dict):
        self._resp = DummyResponse(status_code, payload)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, data=None):
        return self._resp


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_code_for_tokens_success(monkeypatch):
    def fake_client(*args, **kwargs):
        return DummyClient(200, {"id_token": "xyz", "access_token": "abc"})

    monkeypatch.setattr("httpx.AsyncClient", fake_client)
    tokens = await exchange_code_for_tokens("code", "verifier")
    assert tokens["id_token"] == "xyz"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_code_for_tokens_failure(monkeypatch):
    def fake_client(*args, **kwargs):
        return DummyClient(400, {})

    monkeypatch.setattr("httpx.AsyncClient", fake_client)
    with pytest.raises(Exception):
        await exchange_code_for_tokens("code", "verifier")

