import pytest
from datetime import datetime, timedelta, timezone

from app.services.token_service import TokenService


def test_create_and_decode_refresh_token_roundtrip():
    exp = datetime.now(timezone.utc) + timedelta(minutes=5)
    token = TokenService.create_refresh_token({"sub": "123", "jti": "abc"}, exp)
    payload = TokenService.decode_refresh_token(token)
    assert payload["purpose"] == "refresh_token"
    assert payload["sub"] == "123"
    assert payload["jti"] == "abc"


def test_decode_refresh_token_invalid_raises():
    # A clearly invalid token should raise
    with pytest.raises(Exception):
        TokenService.decode_refresh_token("not.a.jwt")


def test_signup_token_roundtrip():
    token = TokenService.generate_signup_token(email="foo@example.com", hashed_pw="hpw", remember_me=True)
    data = TokenService.decode_signup_token(token)
    assert data["sub"] == "foo@example.com"
    assert data["hashed_pw"] == "hpw"
    assert data["remember_me"] is True
    assert data["purpose"] == "sign_up"


def test_password_token_roundtrip():
    token = TokenService.generate_password_token(email="bar@example.com")
    data = TokenService.decode_password_token(token)
    assert data["sub"] == "bar@example.com"
    assert data["purpose"] == "reset_password"

