from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.modules.instructor import schemas
from app.modules.auth import schemas as auth_schema
from app import models, tools
import httpx
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from typing import List



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

    existing_user = (db.query(models.AuUsers)
                        .filter(models.AuUsers.id == user_id)
                        .filter(models.AuUsers.role == "instructor")
                        .first())
    if not existing_user:
        raise HTTPException(status_code=400, detail="Role mismatch")

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


@router.get("/profile/{instructor_id}", response_model=schemas.InstructorProfileResponse)
async def get_instructor_profile_by_id(
        instructor_id: UUID,
        db: Session = Depends(get_db)
):
    """Get instructor profile details by their specific profile UUID"""

    # Query the instructor profile and join with the user table for the email
    profile = (
        db.query(models.InProfiles)
        .options(joinedload(models.InProfiles.user))
        .filter(models.InProfiles.user_id == instructor_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instructor with id {instructor_id} not found"
        )

    # Returning the flattened data to match the schema
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": profile.user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "phone": profile.phone,
        "license_number": profile.license_number,
        "bio": profile.bio
    }


# ------------------------------------------------------------------------------------ specki --------------------------
async def verify_management_permission(token: str, target_instructor_profile_id: UUID, db: Session):
    user_info = await tools.get_user(token)
    user_role = user_info.get("role")
    user_id = user_info.get("id")

    if user_role == "admin" or user_id == target_instructor_profile_id:
        return True
    return False


# --- GET ALL SPECIALTIES PER INSTRUCTOR ---
@router.get("/all/{instructor_profile_id}", response_model=List[schemas.SpecialtyResponse])
async def get_instructor_specialties(
        instructor_profile_id: UUID,
        db: Session = Depends(get_db)
):
    """Fetch all specialties for a specific instructor profile"""
    return db.query(models.InSpecialties).filter(
        models.InSpecialties.instructor_profile_id == instructor_profile_id
    ).all()


# --- ADD SPECIALTY ---
@router.post("/add/{instructor_profile_id}", response_model=schemas.SpecialtyResponse)
async def add_specialty(
        instructor_profile_id: UUID,
        specialty_in: schemas.SpecialtyCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    # 1. Permission Check
    await verify_management_permission(token, instructor_profile_id, db)



    # 2. Uniqueness Check (Per Instructor)
    existing = db.query(models.InSpecialties).filter(
        models.InSpecialties.instructor_profile_id == instructor_profile_id,
        models.InSpecialties.category == specialty_in.category
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This user already has this speciality assigned")



    # 3. Create
    new_specialty = models.InSpecialties(
        category=specialty_in.category,
        instructor_profile_id=instructor_profile_id
    )
    db.add(new_specialty)
    db.commit()
    db.refresh(new_specialty)
    return new_specialty


# --- MODIFY SPECIALTY ---
@router.put("/edit/{specialty_id}", response_model=schemas.SpecialtyResponse)
async def update_specialty(
        specialty_id: UUID,
        specialty_update: schemas.SpecialtyCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    db_specialty = db.query(models.InSpecialties).filter(models.InSpecialties.id == specialty_id).first()
    if not db_specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")

    # Permission Check (against the owner of the existing specialty)
    await verify_management_permission(token, db_specialty.instructor_profile_id, db)

    # Uniqueness Check (ensure the new name isn't already taken by another of their specialties)
    duplicate = db.query(models.InSpecialties).filter(
        models.InSpecialties.instructor_profile_id == db_specialty.instructor_profile_id,
        models.InSpecialties.category == specialty_update.category,
        models.InSpecialties.id != specialty_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="This user already has this speciality assigned")

    db_specialty.category = specialty_update.category
    db.commit()
    db.refresh(db_specialty)
    return db_specialty


# --- REMOVE SPECIALTY ---
@router.delete("/remove/{specialty_id}")
async def delete_specialty(
        specialty_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    db_specialty = db.query(models.InSpecialties).filter(models.InSpecialties.id == specialty_id).first()
    if not db_specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")

    # Permission Check
    await verify_management_permission(token, db_specialty.instructor_profile_id, db)

    db.delete(db_specialty)
    db.commit()
    return {"message": "Specialty removed"}