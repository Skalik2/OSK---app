from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.auth import schemas, utils
from app import models

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=schemas.UserOut)
def register(user_credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists using the correct model name 'Users'
    user_exists = db.query(models.AuUsers).filter(models.AuUsers.email == user_credentials.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user_credentials.role != 'student' and user_credentials.role != 'instructor':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only register students and instructors"
        )

    # 2. Hash the password using your updated utils (Argon2)
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


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Fetch user from the 'Users' model
    user = db.query(models.AuUsers).filter(models.AuUsers.email == user_credentials.email).filter(models.AuUsers.role == user_credentials.role).first()

    # 2. Validate user and password_hash
    if not user or not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 3. Create JWT (using email as the subject)
    access_token = utils.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decode Token
    email = utils.decode_access_token(token)
    if email is None:
        raise credentials_exception

    # 2. Look up user in Postgres
    user = db.query(models.AuUsers).filter(models.AuUsers.email == email).first()
    if user is None:
        raise credentials_exception

    return user  # This returns the actual SQLAlchemy model object


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.AuUsers = Depends(get_current_user)):
    # FastAPI handles the token verification automatically before this code runs.
    # If the token is invalid, the user gets a 401 before they even reach this line.
    return current_user

@router.get("/verify")
def verify_token(current_user: models.AuUsers = Depends(get_current_user)):
    # This endpoint is only accessible with a valid token
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }