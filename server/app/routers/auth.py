import pyotp
from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..dependencies import create_session_token
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    settings = get_settings()
    if not settings.totp_secret:
        raise HTTPException(status_code=400, detail="Authentication not configured")

    totp = pyotp.TOTP(settings.totp_secret)
    if not totp.verify(body.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid code")

    token, expires_in = create_session_token()
    return LoginResponse(token=token, expires_in=expires_in)
