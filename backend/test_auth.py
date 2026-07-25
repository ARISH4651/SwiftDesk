import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import hash_password, decode_access_token

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    users = [
        {"email": "customer@swiftdesk.com", "password": "customer123", "role": "CUSTOMER"},
        {"email": "support@swiftdesk.com", "password": "support123", "role": "SUPPORT"},
        {"email": "admin@swiftdesk.com", "password": "admin123", "role": "ADMIN"},
    ]
    for u in users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            existing.password_hash = hash_password(u["password"])
            existing.role = u["role"]
        else:
            db.add(User(
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                active=True
            ))
    db.commit()
    db.close()

def test_login_invalid_password():
    res = client.post("/api/auth/login", json={
        "email": "customer@swiftdesk.com",
        "password": "wrongpassword",
        "role": "CUSTOMER"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]

def test_frontend_role_claim_ignored_jwt_uses_db_role():
    # Customer tries claiming ADMIN role in frontend login payload
    res = client.post("/api/auth/login", json={
        "email": "customer@swiftdesk.com",
        "password": "customer123",
        "role": "ADMIN" # Untrusted frontend claim
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    payload = decode_access_token(token)
    # The JWT MUST contain the authentic DB role (CUSTOMER), ignoring untrusted frontend claim
    assert payload["role"] == "CUSTOMER"

    # Attempting to access admin route with this token fails with 403 Forbidden
    admin_res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert admin_res.status_code == 403

def test_login_success_and_jwt_format():
    res = client.post("/api/auth/login", json={
        "email": "customer@swiftdesk.com",
        "password": "customer123",
        "role": "CUSTOMER"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "customer@swiftdesk.com"
    assert data["user"]["role"] == "CUSTOMER"

    # Decode and verify JWT claims
    payload = decode_access_token(data["access_token"])
    assert payload is not None
    assert payload["email"] == "customer@swiftdesk.com"
    assert payload["role"] == "CUSTOMER"
    assert "sub" in payload
    assert "exp" in payload

def test_unauthenticated_request_returns_401():
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 401

def test_customer_rbac_denied_admin_endpoint():
    # Login as customer
    login_res = client.post("/api/auth/login", json={
        "email": "customer@swiftdesk.com",
        "password": "customer123",
        "role": "CUSTOMER"
    })
    token = login_res.json()["access_token"]

    # Try accessing admin dashboard with customer token
    res = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403
    assert "Insufficient role permissions" in res.json()["detail"]

def test_support_rbac_denied_admin_endpoint():
    # Login as support
    login_res = client.post("/api/auth/login", json={
        "email": "support@swiftdesk.com",
        "password": "support123",
        "role": "SUPPORT"
    })
    token = login_res.json()["access_token"]

    # Try accessing admin audit-logs with support token
    res = client.get(
        "/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403

def test_admin_access_all_endpoints():
    # Login as admin
    login_res = client.post("/api/auth/login", json={
        "email": "admin@swiftdesk.com",
        "password": "admin123",
        "role": "ADMIN"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Access admin dashboard
    res_dash = client.get("/api/admin/dashboard", headers=headers)
    assert res_dash.status_code == 200

    # Access engineers roster
    res_eng = client.get("/api/engineers", headers=headers)
    assert res_eng.status_code == 200
