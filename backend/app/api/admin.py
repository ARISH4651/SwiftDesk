from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.ticket_service import TicketService
from app.repositories.audit_repository import AuditRepository
from app.repositories.email_repository import EmailRepository
from app.schemas.ticket import TicketReassignSchema
from app.scheduler.sla_monitor import check_sla_and_escalate, trigger_eod_admin_summary
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_admin_dashboard_stats()

@router.post("/reassign")
def reassign_ticket(payload: TicketReassignSchema, db: Session = Depends(get_db)):
    service = TicketService(db)
    success, msg = service.reassign_ticket(
        ticket_id=payload.ticket_id,
        new_agent_id=payload.agent_id,
        actor=payload.actor,
        reason=payload.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@router.post("/reassign-ticket/{ticket_id}")
def reassign_specific_ticket(ticket_id: str, payload: TicketReassignSchema, db: Session = Depends(get_db)):
    service = TicketService(db)
    success, msg = service.reassign_ticket(
        ticket_id=ticket_id,
        new_agent_id=payload.agent_id,
        actor=payload.actor,
        reason=payload.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@router.get("/audit-logs")
def list_audit_logs(ticket_id: Optional[str] = None, db: Session = Depends(get_db)):
    repo = AuditRepository(db)
    return repo.get_all(ticket_id=ticket_id)

@router.get("/email-logs")
def list_email_logs(ticket_id: Optional[str] = None, db: Session = Depends(get_db)):
    repo = EmailRepository(db)
    return repo.get_all(ticket_id=ticket_id)

@router.post("/trigger-sla")
def trigger_sla_check():
    check_sla_and_escalate()
    return {"status": "success", "message": "SLA check completed"}

@router.post("/trigger-eod-summary")
def trigger_eod_summary():
    trigger_eod_admin_summary()
    return {"status": "success", "message": "Daily Admin Summary email sent"}
