import pytest
import httpx
import random
import string
import uuid

CORE_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:8001"

def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

test_password = "SecurePassword123!"
instructor_email = generate_random_email()
student_email = generate_random_email()

state = {
    "instructor_token": None,
    "instructor_user_id": None,
    "instructor_profile_id": None,
    "student_token": None,
    "student_user_id": None,
    "student_profile_id": None,
}

def test_01_proxy_register_instructor():
    register_payload = {
        "email": instructor_email,
        "password": test_password,
        "role": "instructor"
    }
    response = httpx.post(
        f"{CORE_URL}/instructor/register_initial",
        json=register_payload
    )
    assert response.status_code in [200, 201], f"Registration failed: {response.text}"
    data = response.json()
    assert "id" in data, f"Expected 'id' in response, got: {data}"
    state["instructor_user_id"] = data["id"]


def test_02_login_via_auth_service():
    login_payload = {
        "email": instructor_email,
        "password": test_password,
        "role": "instructor"
    }
    response = httpx.post(
        f"{AUTH_URL}/auth/login",
        json=login_payload
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    state["instructor_token"] = data["access_token"]


def test_03_check_instructor_profile_missing():
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}
    response = httpx.get(f"{CORE_URL}/instructor/check_only_user_created", headers=headers)
    assert response.status_code == 200
    assert response.json()["in_between_phases"] is True


def test_04_register_full_instructor_profile():
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}
    profile_payload = {
        "first_name": "Tomasz",
        "last_name": "Kowalski",
        "phone": "+48123456789",
        "license_number": "D99812/2026",
        "bio": "Experienced Category B and C driving instructor."
    }
    response = httpx.post(f"{CORE_URL}/instructor/register_full", json=profile_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "profile_id" in data, f"Expected 'profile_id' in response, got: {data}"
    state["instructor_profile_id"] = data["profile_id"]


def test_05_check_instructor_profile_complete():
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}
    response = httpx.get(f"{CORE_URL}/instructor/check_only_user_created", headers=headers)
    assert response.status_code == 200
    assert response.json()["in_between_phases"] is False


def test_06_get_instructor_profile_by_user_id():
    response = httpx.get(f"{CORE_URL}/instructor/profile/{state['instructor_user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state["instructor_profile_id"]
    assert data["user_id"] == state["instructor_user_id"]



def test_07_proxy_register_student():
    register_payload = {
        "email": student_email,
        "password": test_password,
        "role": "student"
    }
    response = httpx.post(
        f"{CORE_URL}/student/register_initial",
        json=register_payload
    )
    assert response.status_code in [200, 201], f"Registration failed: {response.text}"
    data = response.json()
    assert "id" in data
    state["student_user_id"] = data["id"]


def test_08_student_login():
    login_payload = {
        "email": student_email,
        "password": test_password,
        "role": "student"
    }
    response = httpx.post(
        f"{AUTH_URL}/auth/login",
        json=login_payload
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    state["student_token"] = response.json()["access_token"]


def test_09_register_full_student_profile():
    headers = {"Authorization": f"Bearer {state['student_token']}"}
    profile_payload = {
        "first_name": "Anna",
        "last_name": "Nowak",
        "phone": "+48987654321"
    }
    response = httpx.post(f"{CORE_URL}/student/register_full", json=profile_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "student_profile_id" in data or "id" in data
    state["student_profile_id"] = data.get("student_profile_id") or data.get("id")


def test_10_role_mismatch_protection():
    headers = {"Authorization": f"Bearer {state['student_token']}"}
    profile_payload = {
        "first_name": "Malicious",
        "last_name": "Actor",
        "phone": "+48000000000",
        "license_number": "BAD-PROMPT",
        "bio": "Trying to bypass role restrictions."
    }
    response = httpx.post(f"{CORE_URL}/instructor/register_full", json=profile_payload, headers=headers)
    assert response.status_code == 403

def test_11_instructor_creates_lesson():
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}

    inst_id = state.get("instructor_profile_id") or str(uuid.uuid4())
    stud_id = state.get("student_profile_id") or str(uuid.uuid4())

    lesson_payload = {
        "instructor_profile_id": inst_id,
        "student_profile_id": stud_id,
        "start_time": "2026-07-10T10:00:00Z",
        "end_time": "2026-07-10T12:00:00Z",
        "status": "SCHEDULED"
    }

    response = httpx.post(f"{CORE_URL}/calendar/lessons", json=lesson_payload, headers=headers)

    if response.status_code == 422:
        print("\n[FASTAPI VALIDATION ERROR DETAIL]:", response.json())

    assert response.status_code == 200


def test_12_student_view_own_lessons():
    headers = {"Authorization": f"Bearer {state['student_token']}"}
    response = httpx.get(
        f"{CORE_URL}/calendar/student/{state['student_profile_id']}/lessons",
        headers=headers
    )
    assert response.status_code == 200