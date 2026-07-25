from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class CustomerSchema(BaseModel):
    customer_id: str
    name: str
    email: EmailStr

class TicketCreateSchema(BaseModel):
    external_ref: Optional[str] = None
    customer: CustomerSchema
    subject: str
    description: str
    category: Optional[str] = ""
    priority: Optional[str] = ""
    channel: Optional[str] = "web_app"
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TicketResponseSchema(BaseModel):
    status: str
    ticket_id: str
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    original_category: str
    original_priority: str
    resolved_category: str
    resolved_priority: str
    confidence_score: float
    language: str
    reasoning: str
    assigned_level: str
    assigned_agent_id: Optional[str] = None
    message: str

class TicketStatusUpdateSchema(BaseModel):
    status: str # New, Assigned, In Progress, Resolved, Closed
    actor: str = "SupportAgent"
    notes: Optional[str] = None

class TicketReassignSchema(BaseModel):
    ticket_id: str
    agent_id: str
    reason: Optional[str] = "Manual reassignment by Admin"
    actor: str = "Admin"
