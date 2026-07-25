from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, nullable=True, index=True)
    recipient_email = Column(String, nullable=False)
    recipient_name = Column(String, nullable=True)
    recipient_role = Column(String, nullable=False) # Customer, SupportEngineer, Admin
    trigger_event = Column(String, nullable=False) # TICKET_RECEIVED, ASSIGNMENT, ESCALATION, RESOLUTION, CLOSURE, EOD_ADMIN_SUMMARY
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
