from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True)
    assigned_level = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    assigned_by = Column(String, default="AutoAssignmentEngine") # AutoAssignmentEngine or Admin / SupportAgent
    assigned_at = Column(DateTime, default=datetime.utcnow)
