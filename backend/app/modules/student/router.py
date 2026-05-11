from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
import httpx

router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not found"}},
)

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

async def get_user(token : str):
    user_data = await get_user_from_auth(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return user_data

@router.get("/profile")
async def get_student_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    user_data = await get_user(token)

    return {
        "message": "Dane profilu kursanta",
        "user_info": user_data,
        "status": "Pobrało xD"
    }

@router.get("/progress")
def get_student_progress(db: Session = Depends(get_db)):
    return {"message": "Postępy kursanta: 10/30h (mock)"}