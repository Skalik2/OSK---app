from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from app.modules.student import schemas
from app.modules.auth import schemas as auth_schema
from app import models, tools
import httpx

router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register_user")
async def register_user_phase_one(user_in: auth_schema.UserCreate):
    registration_data = {
        "email": user_in.email,
        "password": user_in.password,
        "role": "student"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8000/auth/register", json=registration_data)

            if response.status_code == 400:
                raise HTTPException(status_code=400, detail="Email already registered")

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Auth service error")

            return response.json()

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service is down")

@router.post("/register_full")
async def register_student_profile(
        profile_data: schemas.StudentProfileCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    user_id = user_info['id']

    existing_user = (db.query(models.AuUsers)
                     .filter(models.AuUsers.id == user_id)
                     .filter(models.AuUsers.role == "student")
                     .first())
    if not existing_user:
        raise HTTPException(status_code=400, detail="Role mismatch")

    existing_profile = db.query(models.StProfiles).filter(models.StProfiles.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")

    new_profile = models.StProfiles(
        user_id=user_id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        phone=profile_data.phone
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {"message": "Profile created successfully", "profile_id": new_profile.id}


@router.get("/check_only_user_created")
async def check_registration_status(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    user_id = user_info['id']

    profile = db.query(models.StProfiles).filter(models.StProfiles.user_id == user_id).first()

    if profile:
        return {"in_between_phases": False, "message": "Full registration complete"}

    return {"in_between_phases": True, "message": "Auth created, profile missing"}