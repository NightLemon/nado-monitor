import pyotp
from fastapi import APIRouter, Depends, HTTPException, Response

from ..config import get_settings
from ..dependencies import create_session_token, verify_session_token
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest, response: Response):
    settings = get_settings()
    if not settings.totp_secret:
        raise HTTPException(status_code=400, detail="Authentication not configured")

    totp = pyotp.TOTP(settings.totp_secret)
    if not totp.verify(body.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid code")

    token, expires_in = create_session_token()

    # Set HttpOnly cookie for security (XSS-safe)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=expires_in,
        path="/",
    )

    return LoginResponse(token=token, expires_in=expires_in)


@router.post("/auth/logout")
def logout_endpoint(response: Response):
    response.delete_cookie(key="session", path="/")
    return {"status": "ok"}


@router.get("/auth/check", dependencies=[Depends(verify_session_token)])
def check_auth():
    """Endpoint to verify cookie auth is valid (protected by session token dep)."""
    return {"authenticated": True}
