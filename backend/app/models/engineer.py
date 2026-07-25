from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class Engineer(Base):
    __tablename__ = "engineers"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True, nullable=False) # e.g. C-101
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    level = Column(String, nullable=False) # L1, L2, L3
    is_available = Column(Boolean, default=True)
    max_capacity = Column(Integer, default=5)
    current_load = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
