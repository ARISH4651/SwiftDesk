from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.ticket import TicketCreateSchema, TicketResponseSchema, TicketStatusUpdateSchema
from app.services.ticket_service import TicketService
from app.repositories.ticket_repository import TicketRepository
from app.api.deps import require_roles, get_current_user
from app.models.user import User
from typing import List, Optional

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponseSchema, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["CUSTOMER", "ADMIN"]))
):
    """
    POST /api/tickets - Ingest Ticket
    Authorized for CUSTOMER and ADMIN.
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["CUSTOMER", "SUPPORT", "ADMIN"]))
):
    """
    GET /api/tickets - List Tickets
    Authorized for CUSTOMER, SUPPORT, ADMIN.
    """
    repo = TicketRepository(db)
    tickets = repo.get_all(status=status, priority=priority, category=category, agent_id=agent_id)
    return tickets

@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["CUSTOMER", "SUPPORT", "ADMIN"]))
):
    """
    GET /api/tickets/{ticket_id} - View Ticket Details
    Authorized for CUSTOMER, SUPPORT, ADMIN.
    """
    repo = TicketRepository(db)
    ticket = repo.get_by_ticket_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: str,
    payload: TicketStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["CUSTOMER", "SUPPORT", "ADMIN"]))
):
    """
    PATCH /api/tickets/{ticket_id}/status - Update Ticket Status
    Authorized for SUPPORT, ADMIN (and CUSTOMER for re-opening their own ticket).
    """
    service = TicketService(db)
    
    # If user is CUSTOMER, enforce that customer can only change status to 'In Progress' (re-open)
    if current_user.role.upper() == "CUSTOMER" and payload.status not in ["In Progress"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customers are only permitted to re-open tickets."
        )

    success, msg = service.update_status(
        ticket_id=ticket_id,
        new_status=payload.status,
        actor=payload.actor or f"{current_user.email}",
        notes=payload.notes
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}
