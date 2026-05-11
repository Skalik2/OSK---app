import logging
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

# Suppress passlib's internal warnings regarding legacy backends
logging.getLogger("passlib").setLevel(logging.ERROR)

# --- Configuration ---
# In production, load these from environment variables (.env)
SECRET_KEY = "asdagfshgadgaa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Using Argon2 as the primary scheme (avoids bcrypt-related ValueErrors)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using Argon2.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against the hashed version in the DB.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Generates a JWT Access Token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)