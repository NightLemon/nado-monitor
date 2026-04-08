import hashlib
import hmac
import time

from fastapi import Header, HTTPException

from .config import get_settings


async def verify_api_key(x_api_key: str = Header(...)):
    if not hmac.compare_digest(x_api_key, get_settings().api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


def create_session_token() -> tuple[str, int]:
    """Create an HMAC-based session token. Returns (token, expires_in_seconds)."""
    settings = get_settings()
    expires_in = settings.session_token_expiry_hours * 3600
    expiry = int(time.time()) + expires_in
    sig = hmac.new(
        settings.session_token_secret.encode(),
        str(expiry).encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{expiry}.{sig}", expires_in


def _validate_session_token(token: str) -> bool:
    settings = get_settings()
    parts = token.split(".", 1)
    if len(parts) != 2:
        return False
    expiry_str, sig = parts
    try:
        expiry = int(expiry_str)
    except ValueError:
        return False
    if time.time() > expiry:
        return False
    expected_sig = hmac.new(
        settings.session_token_secret.encode(),
        expiry_str.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(sig, expected_sig)


async def verify_session_token(authorization: str = Header(default="")):
    settings = get_settings()
    if not settings.totp_secret:
        return  # Auth disabled in dev

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization[7:]
    if not _validate_session_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
