from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit import AuditLog
from typing import List

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, ticket_id: str, actor: str, action: str, previous_state: str = None, new_state: str = None, details: str = None) -> AuditLog:
        audit = AuditLog(
            ticket_id=ticket_id,
            actor=actor,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            details=details
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def get_all(self, ticket_id: str = None) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if ticket_id:
            query = query.filter(AuditLog.ticket_id == ticket_id)
        return query.order_by(desc(AuditLog.timestamp)).all()
