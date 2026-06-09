# --- PATH: auth_service/tests/test_auth.py ---
import pytest
import httpx
from main import app
from database import get_db

# Use ASGITransport for processing internal async cycles
transport = httpx.ASGITransport(app=app)


@pytest.mark.anyio
async def test_public_student_registration_and_login_flow(override_get_db):
    """Verifies that a student can register publicly and log in with strict role checks."""
    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register a student publicly
        reg_payload = {
            "email": "test.student@szkolajazdy.pl",
            "password": "securepassword123",
            "role": "student"
        }
        reg_response = await client.post("/auth/register", json=reg_payload)
        assert reg_response.status_code == 201
        assert reg_response.json()["email"] == "test.student@szkolajazdy.pl"
        assert reg_response.json()["role"] == "student"

        # 2. Attempt login with correct password but WRONG role choice
        bad_login_payload = {
            "email": "test.student@szkolajazdy.pl",
            "password": "securepassword123",
            "role": "admin"
        }
        bad_login_res = await client.post("/auth/login", json=bad_login_payload)
        assert bad_login_res.status_code == 401
        assert bad_login_res.json()["detail"] == "Incorrect email or password designation."

        # 3. Attempt login with correct password and CORRECT matching role
        good_login_payload = {
            "email": "test.student@szkolajazdy.pl",
            "password": "securepassword123",
            "role": "student"
        }
        good_login_res = await client.post("/auth/login", json=good_login_payload)
        assert good_login_res.status_code == 200
        assert "access_token" in good_login_res.json()

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_register_admin_without_token_fails(override_get_db):
    """Verifies that trying to register an admin without providing a token is blocked."""
    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin_payload = {
            "email": "rogue.admin@szkolajazdy.pl",
            "password": "dangerouspwd123",
            "role": "admin"
        }
        response = await client.post("/auth/register", json=admin_payload)
        assert response.status_code == 401

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_admin_can_successfully_register_another_admin(override_get_db, db_session):
    """Verifies that an authorized admin can provision another administrator account."""
    app.dependency_overrides[get_db] = override_get_db

    # 1. Seed a uniquely named master admin into our nested database sandbox context
    import models, utils

    master_admin = models.AuUsers(
        email="temporary.test.admin@szkolajazdy.pl",  # Changed to ensure no overlap with existing records
        password_hash=utils.hash_password("rootpassword"),
        role="admin"
    )
    db_session.add(master_admin)
    db_session.commit()

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 2. Log in as that master admin to get a valid token
        login_res = await client.post("/auth/login", json={
            "email": "temporary.test.admin@szkolajazdy.pl",
            "password": "rootpassword",
            "role": "admin"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Use that admin token to register a secondary admin
        new_admin_payload = {
            "email": "secondary.admin@szkolajazdy.pl",
            "password": "password456",
            "role": "admin"
        }
        response = await client.post("/auth/register", json=new_admin_payload, headers=headers)

        assert response.status_code == 201
        assert response.json()["email"] == "secondary.admin@szkolajazdy.pl"
        assert response.json()["role"] == "admin"

    app.dependency_overrides.clear()