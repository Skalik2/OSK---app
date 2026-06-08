# --- PATH: app/modules/auth/router.py ---
from fastapi import APIRouter, Depends
from app.tools import get_user  # <-- Changed here

router = APIRouter(
    prefix="/auth",
    tags=["Auth Proxy Gateway"]
)

@router.get("/verify")
def verify_token(current_user: dict = Depends(get_user)):  # <-- Changed here
    """
    Proxies requests from internal network callers to verify tokens.
    Returns the parsed user authorization dictionary (id, email, role).
    """
    return current_user