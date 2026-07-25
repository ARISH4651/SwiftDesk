import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models.engineer import Engineer
from app.models.user import User
from app.models.ticket import Ticket
from seed_data import seed

client = TestClient(app)

def setup_function(function):
    Base.metadata.create_all(bind=engine)
    seed()
    db = SessionLocal()
    for eng in db.query(Engineer).all():
        eng.current_load = 0
        eng.is_available = True
    db.commit()
    db.close()

def get_auth_headers(email="customer@swiftdesk.com", password="customer123", role="CUSTOMER"):
    res = client.post("/api/auth/login", json={"email": email, "password": password, "role": role})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_single_ticket_ingestion():
    headers = get_auth_headers("customer@swiftdesk.com", "customer123", "CUSTOMER")
    payload = {
        "external_ref": "test-001",
        "customer": {
            "customer_id": "CUST-9999",
            "name": "Test Customer",
            "email": "test@example.com"
        },
        "subject": "Charged twice for one order",
        "description": "My payment was deducted twice for order #4471. Please refund immediately.",
        "category": "Billing",
        "priority": "High",
        "channel": "web_app",
        "created_at": "2026-07-25T10:00:00+05:30",
        "metadata": {"test": "true"}
    }
    response = client.post("/api/tickets", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "accepted"
    assert data["resolved_priority"] == "High"
    assert data["assigned_level"] == "L3"
    assert data["assigned_agent_id"] in ["C-301", "C-302"]

def test_untrusted_priority_correction():
    headers = get_auth_headers("customer@swiftdesk.com", "customer123", "CUSTOMER")
    payload = {
        "external_ref": "test-002",
        "customer": {
            "customer_id": "CUST-9998",
            "name": "Ops Engineer",
            "email": "ops@example.com"
        },
        "subject": "Production outage down",
        "description": "Database outage! Connection refused on production cluster!",
        "category": "Technical",
        "priority": "Low",
        "channel": "api"
    }
    response = client.post("/api/tickets", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["resolved_priority"] == "High"
    assert data["assigned_level"] == "L3"

def test_low_priority_routing_to_l1():
    headers = get_auth_headers("customer@swiftdesk.com", "customer123", "CUSTOMER")
    payload = {
        "external_ref": "test-003",
        "customer": {
            "customer_id": "CUST-9997",
            "name": "Simple User",
            "email": "user@example.com"
        },
        "subject": "Password reset link not received",
        "description": "I clicked forgot password but haven't received the link in my email yet.",
        "category": "Account",
        "priority": "Low",
        "channel": "web_app"
    }
    response = client.post("/api/tickets", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["resolved_priority"] == "Low"
    assert data["assigned_level"] == "L1"
    assert data["assigned_agent_id"] in ["C-101", "C-102"]
