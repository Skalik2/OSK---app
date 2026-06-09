from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, schemas, utils
from database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Standalone Authentication Service"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def extract_active_user(token: str, db: Session) -> models.AuUsers:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing."
        )
    email = utils.decode_access_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided token is invalid or expired."
        )
    user = db.query(models.AuUsers).filter(models.AuUsers.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists."
        )
    return user


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.AuUsers).filter(models.AuUsers.email == user_credentials.email).first()

    if not user or not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials."
        )

    if user.role != user_credentials.role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials."
        )

    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify", response_model=schemas.TokenData)
async def verify_token_payload(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = await extract_active_user(token, db)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_credentials: schemas.UserCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    if user_credentials.role not in ['student', 'instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified. Must be 'student', 'instructor', or 'admin'."
        )

    if user_credentials.role == "admin":
        caller = await extract_active_user(token, db)
        if caller.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only existing administrators can register another admin account."
            )

    user_exists = db.query(models.AuUsers).filter(models.AuUsers.email == user_credentials.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_pwd = utils.hash_password(user_credentials.password)
    new_user = models.AuUsers(
        email=user_credentials.email,
        password_hash=hashed_pwd,
        role=user_credentials.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user