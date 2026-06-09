import pytest
import httpx
import random
import string

CORE_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:8001"

def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

def test_get_my_student_profile_not_implemented():
    # 1. Register
    email = generate_random_email()
    password = "Password123!"
    reg_resp = httpx.post(f"{CORE_URL}/student/register_initial", json={"email": email, "password": password})
    assert reg_resp.status_code in [200, 201]
    
    # 2. Login
    login_resp = httpx.post(f"{AUTH_URL}/auth/login", json={"email": email, "password": password, "role": "student"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create profile
    profile_payload = {"first_name": "Test", "last_name": "User", "phone": "123456789"}
    prof_resp = httpx.post(f"{CORE_URL}/student/register_full", json=profile_payload, headers=headers)
    assert prof_resp.status_code == 200
    
    # 4. Try to get profile - SHOULD SUCCEED AFTER IMPLEMENTATION
    resp = httpx.get(f"{CORE_URL}/student/profile/me", headers=headers)
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["phone"] == "123456789"
    assert "id" in data
    assert "user_id" in data
