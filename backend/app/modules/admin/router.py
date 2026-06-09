from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import httpx
from uuid import UUID

from database import get_db
import models, tools
from modules.admin import schemas

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

AUTH_SERVICE_URL = "http://localhost:8001"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_SERVICE_URL+"/auth/login")


async def verify_only_admin(token: str) -> dict:
    user_info = await tools.get_user(token)
    if user_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted strictly to system administrators."
        )
    return user_info



@router.post("/register_initial")
async def register_admin_auth(
        user_in: schemas.AdminAuthCreate,
        token: str = Depends(oauth2_scheme)
):
    await verify_only_admin(token)

    registration_data = {
        "email": user_in.email,
        "password": user_in.password,
        "role": "admin"
    }

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/register_staff",
                json=registration_data,
                headers=headers
            )

            if response.status_code == 400:
                raise HTTPException(status_code=400, detail="Email already registered")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="Auth service rejected request (Caller lacks permission)")
            elif response.status_code != 201:
                raise HTTPException(status_code=500, detail="Auth service error")

            return response.json()

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service is down")


@router.post("/register_full", status_code=status.HTTP_201_CREATED)
async def register_admin_profile(
        profile_in: schemas.AdminProfileCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_only_admin(token)

    target_user_id = UUID(str(profile_in.user_id))

    existing_profile = db.query(models.AdProfiles).filter(models.AdProfiles.user_id == target_user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="A profile already exists for this administrative user")

    new_profile = models.AdProfiles(
        user_id=target_user_id,
        first_name=profile_in.first_name,
        last_name=profile_in.last_name,
        position=profile_in.position
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "message": "Admin profile created successfully",
        "admin_profile_id": new_profile.id,
        "user_id": new_profile.user_id
    }


@router.get("/profile/me")
async def get_my_admin_profile(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await verify_only_admin(token)
    user_id = UUID(user_info.get("id"))

    profile = db.query(models.AdProfiles).filter(models.AdProfiles.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Admin data profile record not found.")

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": user_info.get("email"),
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "position": profile.position,
        "created_at": profile.created_at
    }


@router.put("/profile/me/position")
async def update_admin_position(
        position_data: schemas.AdminPositionUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await verify_only_admin(token)
    user_id = UUID(user_info.get("id"))

    profile = db.query(models.AdProfiles).filter(models.AdProfiles.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Admin profile data matching target id not found.")

    # Mutate the corporate designation
    profile.position = position_data.position
    db.commit()
    db.refresh(profile)

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": user_info.get("email"),
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "position": profile.position,
        "created_at": profile.created_at
    }