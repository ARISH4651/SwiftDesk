from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.ticket import TicketCreateSchema, TicketResponseSchema, TicketStatusUpdateSchema
from app.services.ticket_service import TicketService
from app.repositories.ticket_repository import TicketRepository
from typing import List, Optional

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponseSchema, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreateSchema, db: Session = Depends(get_db)):
    """
    POST /api/tickets - Main Ingestion Endpoint
    Validates payload, verifies priority/category, infers missing fields, detects duplicates/vagueness/language,
    auto-assigns eligible engineer, creates audit log, triggers email notifications, and returns HTTP 201 response.
    """
    try:
        service = TicketService(db)
        response = service.process_incoming_ticket(payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    repo = TicketRepository(db)
    tickets = repo.get_all(status=status, priority=priority, category=category, agent_id=agent_id)
    return tickets

@router.get("/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    repo = TicketRepository(db)
    ticket = repo.get_by_ticket_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}/status")
def update_ticket_status(ticket_id: str, payload: TicketStatusUpdateSchema, db: Session = Depends(get_db)):
    service = TicketService(db)
    success, msg = service.update_status(
        ticket_id=ticket_id,
        new_status=payload.status,
        actor=payload.actor,
        notes=payload.notes
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}
