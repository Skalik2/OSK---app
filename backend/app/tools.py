from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
import httpx

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_user_from_auth(token: str):
    async with httpx.AsyncClient() as client:
        # Call the Auth microservice internally
        response = await client.get(
            "http://localhost:8000/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None


async def get_user(token: str):
    user_data = await get_user_from_auth(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user_data