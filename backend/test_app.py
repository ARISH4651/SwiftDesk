import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models.engineer import Engineer
from app.models.ticket import Ticket
from app.models.assignment import Assignment
from app.models.audit import AuditLog
from app.models.email_log import EmailLog
import json

client = TestClient(app)


def reset_test_state():
    db = SessionLocal()
    db.query(Assignment).delete()
    db.query(AuditLog).delete()
    db.query(EmailLog).delete()
    db.query(Ticket).delete()
    db.query(Engineer).delete()

    engs = [
        Engineer(agent_id="C-101", name="Alex Johnson", email="alex@swiftdesk.com", level="L1", is_available=True, max_capacity=5, current_load=0),
        Engineer(agent_id="C-102", name="Beth Smith", email="beth@swiftdesk.com", level="L1", is_available=True, max_capacity=5, current_load=0),
        Engineer(agent_id="C-201", name="Carlos Rivera", email="carlos@swiftdesk.com", level="L2", is_available=True, max_capacity=5, current_load=0),
        Engineer(agent_id="C-202", name="Diana Prince", email="diana@swiftdesk.com", level="L2", is_available=True, max_capacity=5, current_load=0),
        Engineer(agent_id="C-301", name="Evan Wright", email="evan@swiftdesk.com", level="L3", is_available=True, max_capacity=5, current_load=0),
        Engineer(agent_id="C-302", name="Fiona Chen", email="fiona@swiftdesk.com", level="L3", is_available=True, max_capacity=5, current_load=0),
    ]
    db.add_all(engs)
    db.commit()
    db.close()

def setup_module(module):
    Base.metadata.create_all(bind=engine)
    reset_test_state()


@pytest.fixture(autouse=True)
def _isolate_tests():
    reset_test_state()

def test_single_ticket_ingestion():
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
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "accepted"
    assert data["resolved_priority"] == "High"
    assert data["assigned_level"] == "L3"
    assert data["assigned_agent_id"] == "C-301"

def test_untrusted_priority_correction():
    # Customer says Low priority, but description is critical server crash
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
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    # Hybrid AI classifier should overrule Low -> High priority, assigning to L3 agent
    assert data["resolved_priority"] == "High"
    assert data["assigned_level"] == "L3"

def test_low_priority_routing_to_l1():
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
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["resolved_priority"] == "Low"
    assert data["assigned_level"] == "L1"
    assert data["assigned_agent_id"] in ["C-101", "C-102"] # Eligible L1 agent

def test_non_english_ticket_is_analyzed_after_internal_normalization():
    payload = {
        "external_ref": "test-004",
        "customer": {
            "customer_id": "CUST-9996",
            "name": "Isabella Garcia",
            "email": "isabella.g@example.com"
        },
        "subject": "Error al procesar el pago de mi cuenta",
        "description": "Hola, intenté pagar mi factura mensual pero el sistema muestra un error de tarjeta rechazada sin explicaciones.",
        "category": "Billing",
        "priority": "Medium",
        "channel": "web_app"
    }
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["resolved_category"] == "Billing"
    assert data["resolved_priority"] == "Medium"
    assert data["language"] == "es"
    assert data["confidence_score"] >= 0.85
    assert "normalized" in data["reasoning"].lower()


def test_duplicate_ticket_is_flagged_and_not_assigned_twice():
    payload = {
        "external_ref": "dup-001",
        "customer": {
            "customer_id": "CUST-DUP-1",
            "name": "Duplicate Tester",
            "email": "dup@example.com"
        },
        "subject": "Charged twice for one order",
        "description": "My payment was deducted twice for order #4471. Please refund immediately.",
        "category": "Billing",
        "priority": "High",
        "channel": "web_app"
    }

    first_response = client.post("/api/tickets", json=payload)
    assert first_response.status_code == 201
    first_data = first_response.json()

    second_response = client.post("/api/tickets", json=payload)
    assert second_response.status_code == 201
    second_data = second_response.json()

    assert second_data["is_duplicate"] is True
    assert second_data["duplicate_of"] == first_data["ticket_id"]
    assert second_data["assigned_agent_id"] is None

    db = SessionLocal()
    try:
        assert db.query(Ticket).count() == 2
        assert db.query(Assignment).count() == 1
    finally:
        db.close()


def test_admin_reassignment_updates_ticket_and_audit_log():
    payload = {
        "external_ref": "reassign-001",
        "customer": {
            "customer_id": "CUST-REASSIGN-1",
            "name": "Admin Reassign",
            "email": "reassign@example.com"
        },
        "subject": "Production outage down",
        "description": "Database outage! Connection refused on production cluster!",
        "category": "Technical",
        "priority": "Low",
        "channel": "api"
    }

    create_response = client.post("/api/tickets", json=payload)
    assert create_response.status_code == 201
    ticket_id = create_response.json()["ticket_id"]

    reassign_response = client.post(
        f"/api/admin/reassign-ticket/{ticket_id}",
        json={"ticket_id": ticket_id, "agent_id": "C-302", "actor": "Admin", "reason": "Workload balancing"}
    )
    assert reassign_response.status_code == 200

    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        assert ticket is not None
        assert ticket.assigned_agent_id == "C-302"
        assert ticket.status == "Assigned"

        audit = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id, AuditLog.action == "REASSIGNED").first()
        assert audit is not None

        assignment_count = db.query(Assignment).filter(Assignment.ticket_id == ticket_id).count()
        assert assignment_count == 2
    finally:
        db.close()


def test_sla_escalation_promotes_overdue_ticket_and_logs_notification():
    payload = {
        "external_ref": "sla-001",
        "customer": {
            "customer_id": "CUST-SLA-1",
            "name": "SLA Tester",
            "email": "sla@example.com"
        },
        "subject": "Password reset link not received",
        "description": "I clicked forgot password but haven't received the link in my email yet.",
        "category": "Account",
        "priority": "Low",
        "channel": "web_app"
    }

    create_response = client.post("/api/tickets", json=payload)
    assert create_response.status_code == 201
    ticket_id = create_response.json()["ticket_id"]

    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        assert ticket is not None
        ticket.sla_deadline = ticket.created_at
        db.commit()
    finally:
        db.close()

    trigger_response = client.post("/api/admin/trigger-sla")
    assert trigger_response.status_code == 200

    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        assert ticket is not None
        assert ticket.is_escalated is True
        assert ticket.assigned_level in ["L2", "L3"]
        assert ticket.assigned_agent_id in ["C-201", "C-202", "C-301", "C-302"]

        audit = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id, AuditLog.action == "ESCALATED").first()
        assert audit is not None

        escalation_email = db.query(EmailLog).filter(EmailLog.ticket_id == ticket_id, EmailLog.trigger_event == "ESCALATION").first()
        assert escalation_email is not None
    finally:
        db.close()
