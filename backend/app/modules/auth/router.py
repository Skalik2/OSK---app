from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.auth import models, schemas, utils

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=schemas.UserOut)
def register(user_credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists using the correct model name 'Users'
    user_exists = db.query(models.Users).filter(models.Users.email == user_credentials.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. Hash the password using your updated utils (Argon2)
    hashed_pwd = utils.hash_password(user_credentials.password)

    # 3. Create new user instance mapping to your specific columns
    # id is handled by server_default=text('uuid_generate_v4()')
    new_user = models.Users(
        email=user_credentials.email,
        password_hash=hashed_pwd,
        role='Student'  # domyślnie studenciak I guess
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Fetch user from the 'Users' model
    user = db.query(models.Users).filter(models.Users.email == user_credentials.email).first()

    # 2. Validate user and password_hash
    if not user or not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 3. Create JWT (using email as the subject)
    access_token = utils.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}