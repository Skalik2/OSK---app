# --- PATH: app/tools.py ---
import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Ensure the core app points directly to your port 8001 microservice login for docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/auth/login")

async def get_user_from_auth(token: str):
    """Hits the isolated Auth Microservice on Port 8001 to verify a JWT."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8001/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is currently unavailable."
            )

async def get_user(token: str = Depends(oauth2_scheme)):
    """FastAPI Dependency to inject verified user token details into routes."""
    user_data = await get_user_from_auth(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user_data