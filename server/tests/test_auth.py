import os
import time
import hmac
import hashlib

from app.dependencies import create_session_token, _validate_session_token


def test_create_and_validate_token():
    os.environ["SESSION_TOKEN_SECRET"] = "test-secret-123"
    from app.config import _settings
    # Reset singleton to pick up new env
    import app.config
    app.config._settings = None

    token, expires_in = create_session_token()
    assert "." in token
    assert expires_in > 0
    assert _validate_session_token(token) is True

    # Clean up
    app.config._settings = None


def test_expired_token():
    secret = "test-secret"
    expiry = int(time.time()) - 100  # already expired
    sig = hmac.new(
        secret.encode(), str(expiry).encode(), hashlib.sha256
    ).hexdigest()
    token = f"{expiry}.{sig}"

    os.environ["SESSION_TOKEN_SECRET"] = secret
    import app.config
    app.config._settings = None

    assert _validate_session_token(token) is False

    app.config._settings = None


def test_invalid_token():
    assert _validate_session_token("garbage") is False
    assert _validate_session_token("123.wrongsig") is False
    assert _validate_session_token("") is False
