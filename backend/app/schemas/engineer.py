from pydantic import BaseModel, EmailStr
from typing import Optional

class EngineerSchema(BaseModel):
    agent_id: str
    name: str
    email: EmailStr
    level: str # L1, L2, L3
    is_available: bool = True
    max_capacity: int = 5
    current_load: int = 0

class EngineerStatusUpdateSchema(BaseModel):
    is_available: bool
