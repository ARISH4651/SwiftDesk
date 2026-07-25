from sqlalchemy.orm import Session
from app.repositories.ticket_repository import TicketRepository
from app.repositories.engineer_repository import EngineerRepository
from app.models.ticket import Ticket
from typing import Dict, Any, List
from datetime import datetime

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.engineer_repo = EngineerRepository(db)

    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        all_tickets = self.ticket_repo.get_all()
        all_engineers = self.engineer_repo.get_all()

        total_tickets = len(all_tickets)
        
        status_counts = {"New": 0, "Assigned": 0, "In Progress": 0, "Resolved": 0, "Closed": 0}
        priority_counts = {"Low": 0, "Medium": 0, "High": 0}
        category_counts = {}
        level_counts = {"L1": 0, "L2": 0, "L3": 0}

        resolution_times = []
        sla_breaches = 0
        escalations = 0

        now = datetime.utcnow()

        for t in all_tickets:
            status_counts[t.status] = status_counts.get(t.status, 0) + 1
            priority_counts[t.resolved_priority] = priority_counts.get(t.resolved_priority, 0) + 1
            category_counts[t.resolved_category] = category_counts.get(t.resolved_category, 0) + 1
            level_counts[t.assigned_level] = level_counts.get(t.assigned_level, 0) + 1

            if t.is_escalated:
                escalations += 1

            if t.status not in ["Resolved", "Closed"] and t.sla_deadline and now > t.sla_deadline:
                sla_breaches += 1

            if t.resolved_at and t.created_at:
                delta_h = (t.resolved_at - t.created_at).total_seconds() / 3600.0
                resolution_times.append(delta_h)

        avg_resolution_hours = sum(resolution_times) / len(resolution_times) if resolution_times else 0.0

        engineer_workloads = [
            {
                "agent_id": e.agent_id,
                "name": e.name,
                "level": e.level,
                "is_available": e.is_available,
                "max_capacity": e.max_capacity,
                "current_load": e.current_load
            }
            for e in all_engineers
        ]

        return {
            "total_tickets": total_tickets,
            "open_tickets": status_counts["New"] + status_counts["Assigned"] + status_counts["In Progress"],
            "resolved_tickets": status_counts["Resolved"] + status_counts["Closed"],
            "sla_breaches": sla_breaches,
            "escalations": escalations,
            "avg_resolution_hours": round(avg_resolution_hours, 2),
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "category_counts": category_counts,
            "level_counts": level_counts,
            "engineer_workloads": engineer_workloads
        }
