from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.repositories.engineer_repository import EngineerRepository
from app.models.engineer import Engineer
from app.config import PRIORITY_TO_LEVEL, LEVEL_ELIGIBILITY

class RoutingService:
    def __init__(self, db: Session):
        self.db = db
        self.engineer_repo = EngineerRepository(db)

    def determine_target_level(self, priority: str) -> str:
        return PRIORITY_TO_LEVEL.get(priority, "L2")

    def auto_assign_ticket(self, priority: str) -> Tuple[str, Optional[Engineer], str]:
        """
        Determines target level and selects best available engineer respecting:
        1. Eligibility (L1=Low, L2=Low/Medium, L3=Low/Medium/High)
        2. Availability (is_available == True)
        3. Capacity (current_load < max_capacity)
        4. Load Balancing (Lowest active workload first)
        """
        target_level = self.determine_target_level(priority)

        # Candidate levels that can legally handle target_level priority
        eligible_levels = []
        for level, allowed_priorities in LEVEL_ELIGIBILITY.items():
            if priority in allowed_priorities:
                eligible_levels.append(level)

        available_engineers = self.engineer_repo.get_available_by_levels(eligible_levels)
        
        # Filter by capacity
        capable_engineers = [e for e in available_engineers if e.current_load < e.max_capacity]

        if not capable_engineers:
            reason = f"Queued: No eligible/available engineer with free capacity for {priority} priority."
            return target_level, None, reason

        # Sort by current_load ascending (lowest workload), then by agent_id for deterministic tie-breaking
        capable_engineers.sort(key=lambda e: (e.current_load, e.agent_id))
        selected_agent = capable_engineers[0]
        
        reason = f"Auto-assigned to {selected_agent.name} ({selected_agent.agent_id}, Level {selected_agent.level}) based on lowest workload ({selected_agent.current_load}/{selected_agent.max_capacity})."
        
        return target_level, selected_agent, reason
