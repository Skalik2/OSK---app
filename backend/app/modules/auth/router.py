from fastapi import APIRouter, Depends
from tools import get_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth Proxy Gateway"]
)

@router.get("/verify")
def verify_token(current_user: dict = Depends(get_user)):
    return current_user