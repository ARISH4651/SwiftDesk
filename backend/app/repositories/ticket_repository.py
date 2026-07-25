from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.models.ticket import Ticket
from app.models.assignment import Assignment
from typing import List, Optional
from datetime import datetime, timedelta

class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, status: str = None, priority: str = None, category: str = None, agent_id: str = None) -> List[Ticket]:
        query = self.db.query(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.resolved_priority == priority)
        if category:
            query = query.filter(Ticket.resolved_category == category)
        if agent_id:
            query = query.filter(Ticket.assigned_agent_id == agent_id)
        return query.order_by(desc(Ticket.created_at)).all()

    def get_by_ticket_id(self, ticket_id: str) -> Optional[Ticket]:
        return self.db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

    def find_recent_duplicate(self, customer_id: str, subject: str, external_ref: str = None) -> Optional[Ticket]:
        # Checks for the same external reference or a similar subject in the last 24 hours.
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = self.db.query(Ticket).filter(Ticket.created_at >= cutoff)

        duplicate_conditions = [Ticket.subject.ilike(f"%{subject.strip()}%")]
        if external_ref:
            duplicate_conditions.append(Ticket.external_ref == external_ref)

        return query.filter(
            Ticket.customer_id == customer_id,
            or_(*duplicate_conditions)
        ).order_by(desc(Ticket.created_at)).first()

    def create_ticket(self, ticket_data: dict) -> Ticket:
        ticket = Ticket(**ticket_data)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update_ticket(self, ticket: Ticket) -> Ticket:
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def create_assignment_record(self, assignment_data: dict) -> Assignment:
        assignment = Assignment(**assignment_data)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_count_next_id(self) -> int:
        count = self.db.query(Ticket).count()
        return 100001 + count
