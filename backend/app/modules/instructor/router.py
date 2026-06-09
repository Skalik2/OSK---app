# --- PATH: app/modules/instructor/router.py ---
import httpx
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models, tools
from modules.instructor import schemas

router = APIRouter(
    prefix="/instructor",
    tags=["Instructor"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/auth/login")

@router.post("/register_initial")
async def register_instructor_auth(email: str, password: str):
    """
    Proxies registration to the Auth Microservice (Port 8001).
    Bypasses local auth schemas entirely since they are redundant.
    """
    registration_data = {
        "email": email,
        "password": password,
        "role": "instructor"
    }

    async with httpx.AsyncClient() as client:
        try:
            # Pointed cleanly directly to our Auth Microservice instance on 8001
            response = await client.post("http://localhost:8001/auth/register", json=registration_data)

            if response.status_code == 400:
                raise HTTPException(status_code=400, detail="Email already registered")

            if response.status_code != 201:  # Auth service returns 201 on success
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
    user_info = await tools.get_user(token)
    user_id = UUID(user_info['id'])

    # Enforce token role matches the route requirement
    if user_info.get("role") != "instructor":
        raise HTTPException(status_code=403, detail="Role mismatch")

    existing_profile = db.query(models.InProfiles).filter(models.InProfiles.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Instructor profile already exists")

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
    user_info = await tools.get_user(token)
    user_id = UUID(user_info['id'])

    profile = db.query(models.InProfiles).filter(models.InProfiles.user_id == user_id).first()

    if profile:
        return {"in_between_phases": False, "message": "Instructor registration complete"}

    return {"in_between_phases": True, "message": "Auth created, instructor profile missing"}


@router.get("/profile/{instructor_id}", response_model=schemas.InstructorProfileResponse)
async def get_instructor_profile_by_id(
        instructor_id: UUID,
        db: Session = Depends(get_db)
):
    # instructor_id parameter passed down is the auth user_id
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


# ------------------------------------------------------------------------------------ specialties --------------------------
async def verify_management_permission(token: str, target_instructor_profile_id: UUID, db: Session):
    """Verifies if caller is an admin or is the instructor owning this specific profile id."""
    user_info = await tools.get_user(token)
    user_role = user_info.get("role")
    user_id = UUID(user_info.get("id"))

    if user_role == "admin":
        return True

    # Look up who owns this instructor profile
    profile = db.query(models.InProfiles).filter(models.InProfiles.id == target_instructor_profile_id).first()
    if profile and profile.user_id == user_id:
        return True

    raise HTTPException(status_code=403, detail="Permission denied")


@router.get("/specialities/all/{instructor_profile_id}", response_model=List[schemas.SpecialtyResponse])
async def get_instructor_specialties(
        instructor_profile_id: UUID,
        db: Session = Depends(get_db)
):
    return db.query(models.InSpecialties).filter(
        models.InSpecialties.instructor_profile_id == instructor_profile_id
    ).all()


@router.post("/specialities/add/{instructor_profile_id}", response_model=schemas.SpecialtyResponse)
async def add_specialty(
        instructor_profile_id: UUID,
        specialty_in: schemas.SpecialtyCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_management_permission(token, instructor_profile_id, db)

    existing = db.query(models.InSpecialties).filter(
        models.InSpecialties.instructor_profile_id == instructor_profile_id,
        models.InSpecialties.category == specialty_in.category
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This user already has this speciality assigned")

    new_specialty = models.InSpecialties(
        category=specialty_in.category,
        instructor_profile_id=instructor_profile_id
    )
    db.add(new_specialty)
    db.commit()
    db.refresh(new_specialty)
    return new_specialty


@router.put("/specialities/edit/{specialty_id}", response_model=schemas.SpecialtyResponse)
async def update_specialty(
        specialty_id: UUID,
        specialty_update: schemas.SpecialtyCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    db_specialty = db.query(models.InSpecialties).filter(models.InSpecialties.id == specialty_id).first()
    if not db_specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")

    await verify_management_permission(token, db_specialty.instructor_profile_id, db)

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


@router.delete("/specialities/remove/{specialty_id}")
async def delete_specialty(
        specialty_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    db_specialty = db.query(models.InSpecialties).filter(models.InSpecialties.id == specialty_id).first()
    if not db_specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")

    await verify_management_permission(token, db_specialty.instructor_profile_id, db)

    db.delete(db_specialty)
    db.commit()
    return {"message": "Specialty removed"}