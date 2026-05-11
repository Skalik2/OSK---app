from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.modules.instructor import schemas
from app.modules.auth import schemas as auth_schema
from app import models, tools
import httpx

router = APIRouter(
    prefix="/instructor",
    tags=["Instructor"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register_user")
async def register_instructor_auth(user_in: auth_schema.UserCreate):
    """Phase 1: Create Auth User with 'instructor' role"""
    registration_data = {
        "email": user_in.email,
        "password": user_in.password,
        "role": "instructor" # Hardcoded for safety
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
async def register_instructor_profile(
        profile_data: schemas.InstructorProfileCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Phase 2: Create Instructor Profile in the instructor schema"""
    # 1. Get identity
    user_info = await tools.get_user(token)
    user_id = user_info['id']

    # 2. Check for existing instructor profile
    existing_profile = db.query(models.InProfiles).filter(models.InProfiles.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Instructor profile already exists")

    # 3. Create profile using the InProfiles model
    new_profile = models.InProfiles(
        user_id=user_id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        phone=profile_data.phone,
        license_number=profile_data.license_number,
        bio=profile_data.bio
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {"message": "Instructor profile created successfully", "profile_id": new_profile.id}


@router.get("/check_only_user_created")
async def check_instructor_status(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Check if auth exists but instructor profile is missing"""
    user_info = await tools.get_user(token)
    user_id = user_info['id']

    profile = db.query(models.InProfiles).filter(models.InProfiles.user_id == user_id).first()

    if profile:
        return {"in_between_phases": False, "message": "Instructor registration complete"}

    return {"in_between_phases": True, "message": "Auth created, instructor profile missing"}