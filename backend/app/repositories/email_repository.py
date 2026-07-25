from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.email_log import EmailLog
from typing import List

class EmailRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_email_log(self, email_data: dict) -> EmailLog:
        email = EmailLog(**email_data)
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email

    def get_all(self, ticket_id: str = None) -> List[EmailLog]:
        query = self.db.query(EmailLog)
        if ticket_id:
            query = query.filter(EmailLog.ticket_id == ticket_id)
        return query.order_by(desc(EmailLog.sent_at)).all()
