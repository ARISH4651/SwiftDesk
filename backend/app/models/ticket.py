from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from datetime import datetime
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True, nullable=False) # e.g. TKT-100045
    external_ref = Column(String, index=True)
    
    # Customer Details
    customer_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    
    # Content
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    channel = Column(String, default="web_app")
    metadata_json = Column(JSON, nullable=True)

    # Classification & Verification
    original_category = Column(String)
    original_priority = Column(String)
    resolved_category = Column(String, nullable=False)
    resolved_priority = Column(String, nullable=False)
    confidence_score = Column(Float, default=1.0)
    
    # Edge case flags
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(String, nullable=True)
    is_vague = Column(Boolean, default=False)
    language = Column(String, default="en")

    # Routing & Lifecycle
    assigned_level = Column(String, nullable=False) # L1, L2, L3
    assigned_agent_id = Column(String, nullable=True) # e.g. C-301
    assigned_agent_name = Column(String, nullable=True)
    assignment_reason = Column(Text, nullable=True)
    status = Column(String, default="New") # New, Assigned, In Progress, Resolved, Closed
    
    # SLA & Escalation
    sla_hours = Column(Float, default=8.0)
    sla_deadline = Column(DateTime, nullable=True)
    is_escalated = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
