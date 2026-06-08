from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import httpx
from uuid import UUID

from app.database import get_db
from app import models, tools
from app.modules.admin import schemas

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Points directly to your Auth Microservice deployment address
AUTH_SERVICE_URL = "http://localhost:8000"


# --- Role Validation Guard ---
async def verify_only_admin(token: str) -> dict:
    """Verifies with token helper that the caller has an administrative role."""
    user_info = await tools.get_user(token)
    if user_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted strictly to system administrators."
        )
    return user_info


# --- Endpoints ---

@router.post("/register_user")
async def register_admin_auth(
        user_in: schemas.AdminAuthCreate,
        token: str = Depends(oauth2_scheme)
):
    """
    Step 1: Onboards an additional Admin auth record via the Auth Microservice.
    Enforces that only an active administrator can trigger this action.
    """
    # 1. Check permissions
    await verify_only_admin(token)

    # 2. Hardcode role to "admin" to prevent accidental escalation
    registration_data = {
        "email": user_in.email,
        "password": user_in.password,
        "role": "admin"
    }

    # 3. Communicate with the standalone Auth microservice
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


@router.post("/register_profile", response_model=schemas.AdminProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_admin_profile(
        profile_in: schemas.AdminProfileCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Step 2: Provisions the local admin profile record inside the database.
    Enforces that only an active administrator can populate profile records.
    """
    # 1. Check permissions
    await verify_only_admin(token)

    # 2. Prevent creating duplicate profiles for the same user ID
    existing_profile = db.query(models.AdProfiles).filter(models.AdProfiles.user_id == profile_in.user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="A profile already exists for this administrative user")

    # 3. Save the new profile record locally
    new_profile = models.AdProfiles(
        user_id=profile_in.user_id,
        first_name=profile_in.first_name,
        last_name=profile_in.last_name,
        position=profile_in.position
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.get("/profile/me", response_model=schemas.AdminProfileResponse)
async def get_my_admin_profile(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Fetches full details of the calling Admin profile."""
    user_info = await verify_only_admin(token)
    user_id = user_info.get("id")

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


@router.put("/profile/me/position", response_model=schemas.AdminProfileResponse)
async def update_admin_position(
        position_data: schemas.AdminPositionUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Allows an administrator to modify their administrative or internal position description."""
    user_info = await verify_only_admin(token)
    user_id = user_info.get("id")

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