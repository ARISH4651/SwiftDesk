from sqlalchemy.orm import Session
from app.models.engineer import Engineer
from typing import List, Optional

class EngineerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Engineer]:
        return self.db.query(Engineer).all()

    def get_by_agent_id(self, agent_id: str) -> Optional[Engineer]:
        return self.db.query(Engineer).filter(Engineer.agent_id == agent_id).first()

    def get_available_by_levels(self, levels: List[str]) -> List[Engineer]:
        return self.db.query(Engineer).filter(
            Engineer.level.in_(levels),
            Engineer.is_available == True
        ).all()

    def update_load(self, agent_id: str, delta: int):
        eng = self.get_by_agent_id(agent_id)
        if eng:
            eng.current_load = max(0, eng.current_load + delta)
            self.db.commit()
            self.db.refresh(eng)

    def set_availability(self, agent_id: str, is_available: bool) -> Optional[Engineer]:
        eng = self.get_by_agent_id(agent_id)
        if eng:
            eng.is_available = is_available
            self.db.commit()
            self.db.refresh(eng)
        return eng

    def create(self, eng_data: dict) -> Engineer:
        eng = Engineer(**eng_data)
        self.db.add(eng)
        self.db.commit()
        self.db.refresh(eng)
        return eng
