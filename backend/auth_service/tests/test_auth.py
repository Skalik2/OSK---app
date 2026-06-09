import pytest
import httpx
from main import app
from database import get_db

transport = httpx.ASGITransport(app=app)


@pytest.mark.anyio
async def test_public_student_registration_and_login_flow(override_get_db):
    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. rejestracja
        reg_payload = {
            "email": "test.student@szkolajazdy.pl",
            "password": "securepassword123",
            "role": "student"
        }
        reg_response = await client.post("/auth/register", json=reg_payload)
        assert reg_response.status_code == 201
        assert reg_response.json()["email"] == "test.student@szkolajazdy.pl"
        assert reg_response.json()["role"] == "student"

        # 2. logowanie ze złą rolą
        bad_login_payload = {
            "email": "test.student@szkolajazdy.pl",
            "password": "securepassword123",
            "role": "admin"
        }
        bad_login_res = await client.post("/auth/login", json=bad_login_payload)
        assert bad_login_res.status_code == 401
        assert bad_login_res.json()["detail"] == "Incorrect credentials."

        # 3. poprawne logowanie
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
    # rejestracja admina bez uprawnień
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
    # rejestracja admina z uprawnieniami
    app.dependency_overrides[get_db] = override_get_db

    import models, utils

    master_admin = models.AuUsers(
        email="temporary.test.admin@szkolajazdy.pl",
        password_hash=utils.hash_password("rootpassword"),
        role="admin"
    )
    db_session.add(master_admin)
    db_session.commit()

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        login_res = await client.post("/auth/login", json={
            "email": "temporary.test.admin@szkolajazdy.pl",
            "password": "rootpassword",
            "role": "admin"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
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