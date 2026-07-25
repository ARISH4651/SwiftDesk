from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "CUSTOMER"

class UserResponseSchema(BaseModel):
    id: int
    email: str
    role: str
    active: bool

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema
