# --- PATH: app/tests/test_core_integration.py ---
import pytest
import httpx
import random
import string
import uuid

CORE_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:8001"

def generate_random_email():
    """Generates a random email to prevent unique constraint DB collisions on rerun."""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

# Shared test state across steps
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

# --- 1. INSTRUCTOR WORKFLOW TESTS ---

def test_01_proxy_register_instructor():
    """Test that Core App properly proxies registration requests using register_initial."""
    response = httpx.post(
        f"{CORE_URL}/instructor/register_initial",
        params={"email": instructor_email, "password": test_password}
    )
    assert response.status_code in [200, 201], f"Registration failed: {response.text}"
    data = response.json()
    assert "id" in data, f"Expected 'id' in response, got: {data}"
    state["instructor_user_id"] = data["id"]


def test_02_login_via_auth_service():
    """Verify that we can obtain a bearer token using a JSON body matching UserCreate."""
    # Modified to match your Auth microservice schema requirements
    login_payload = {
        "email": instructor_email,
        "password": test_password,
        "role": "instructor"
    }
    response = httpx.post(
        f"{AUTH_URL}/auth/login",
        json=login_payload  # Switched to json payload to satisfy schemas.UserCreate parsing
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    state["instructor_token"] = data["access_token"]


def test_03_check_instructor_profile_missing():
    """Verify check_only_user_created catches that the secondary profile isn't built yet."""
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}
    response = httpx.get(f"{CORE_URL}/instructor/check_only_user_created", headers=headers)
    assert response.status_code == 200
    assert response.json()["in_between_phases"] is True


def test_04_register_full_instructor_profile():
    """Test creating the secondary local profile row using our validated token."""
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

    # Based on your app logs, your endpoint returns 'profile_id' as the key!
    assert "profile_id" in data, f"Expected 'profile_id' in response, got: {data}"
    state["instructor_profile_id"] = data["profile_id"]


def test_05_check_instructor_profile_complete():
    """Verify check_only_user_created acknowledges a completed phase-two state."""
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}
    response = httpx.get(f"{CORE_URL}/instructor/check_only_user_created", headers=headers)
    assert response.status_code == 200
    assert response.json()["in_between_phases"] is False


def test_06_get_instructor_profile_by_user_id():
    """Verify fetching profile data via strict nomenclature path parameter {user_id}."""
    response = httpx.get(f"{CORE_URL}/instructor/profile/{state['instructor_user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state["instructor_profile_id"]
    assert data["user_id"] == state["instructor_user_id"]


# --- 2. STUDENT WORKFLOW TESTS ---

def test_07_proxy_register_student():
    """Verify proxy student registration routing via register_initial."""
    response = httpx.post(
        f"{CORE_URL}/student/register_initial",
        params={"email": student_email, "password": test_password}
    )
    assert response.status_code in [200, 201], f"Registration failed: {response.text}"
    data = response.json()
    assert "id" in data
    state["student_user_id"] = data["id"]


def test_08_student_login():
    """Verify token generation for a student user account."""
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
    """Test populating a student data profile row."""
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


# --- 3. ROLES & PERMISSIONS CROSS-TESTS ---

def test_10_role_mismatch_protection():
    """Enforce that a student token cannot build an instructor profile row."""
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


# --- 4. CALENDAR WORKFLOW TESTS ---

def test_11_instructor_creates_lesson():
    """Verify authorized instructor can append practical hours onto the calendar."""
    headers = {"Authorization": f"Bearer {state['instructor_token']}"}

    inst_id = state.get("instructor_profile_id") or str(uuid.uuid4())
    stud_id = state.get("student_profile_id") or str(uuid.uuid4())

    lesson_payload = {
        "instructor_profile_id": inst_id,  # Changed from instructor_id
        "student_profile_id": stud_id,  # Changed from student_id
        "start_time": "2026-07-10T10:00:00Z",
        "end_time": "2026-07-10T12:00:00Z",
        "status": "SCHEDULED"
    }

    response = httpx.post(f"{CORE_URL}/calendar/lessons", json=lesson_payload, headers=headers)

    if response.status_code == 422:
        print("\n[FASTAPI VALIDATION ERROR DETAIL]:", response.json())

    assert response.status_code == 200


def test_12_student_view_own_lessons():
    """Verify security bounds permit students to track their own calendar rows."""
    headers = {"Authorization": f"Bearer {state['student_token']}"}
    response = httpx.get(
        f"{CORE_URL}/calendar/student/{state['student_profile_id']}/lessons",
        headers=headers
    )
    assert response.status_code == 200