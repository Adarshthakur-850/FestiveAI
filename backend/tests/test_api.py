import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FestiveAI"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    if "application/json" in response.headers.get("content-type", ""):
        assert "documentation" in response.json()
    else:
        assert "<!doctype html>" in response.text.lower() or "festiveai" in response.text.lower()

def test_calendar_festivals_endpoint():
    response = client.get("/api/v1/calendar/festivals")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 5

def test_auth_registration_and_login():
    unique_suffix = uuid.uuid4().hex[:6]
    email = f"test_{unique_suffix}@example.com"
    password = "TestPassword2026!"

    # 1. Register
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": f"Acme Corp {unique_suffix}",
            "email": email,
            "password": password,
            "full_name": "Acme Admin"
        }
    )
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data["data"]

    # 2. Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    token = login_data["data"]["access_token"]
    assert token is not None

    # 3. Get /me
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["email"] == email
