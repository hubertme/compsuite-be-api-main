import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from app.config.app_config import settings

def test_password_hash():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token():
    subject = "test@example.com"
    token = create_access_token(subject)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == subject
    assert "exp" in payload

def test_create_refresh_token():
    subject = "test@example.com"
    token = create_refresh_token(subject)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == subject
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_decode_token():
    subject = "test@example.com"
    token = create_access_token(subject)
    payload = decode_token(token)
    assert payload["sub"] == subject
    assert "exp" in payload

def test_decode_invalid_token():
    assert decode_token("invalid_token") is None

def test_token_expiration():
    subject = "test@example.com"
    expires_delta = timedelta(minutes=-1)  # Token that has already expired
    token = create_access_token(subject, expires_delta=expires_delta)
    assert decode_token(token) is None
