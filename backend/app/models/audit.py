from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, nullable=False, index=True)
    actor = Column(String, nullable=False) # e.g. System, Customer, SupportAgent, Admin
    action = Column(String, nullable=False) # e.g. TICKET_RECEIVED, AUTO_ASSIGNED, STATUS_CHANGED, ESCALATED, REASSIGNED
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
