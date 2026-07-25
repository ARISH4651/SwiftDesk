from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.repositories.ticket_repository import TicketRepository
from app.repositories.engineer_repository import EngineerRepository
from app.repositories.audit_repository import AuditRepository
from app.services.routing_service import RoutingService
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService

def check_sla_and_escalate():
    db: Session = SessionLocal()
    try:
        ticket_repo = TicketRepository(db)
        engineer_repo = EngineerRepository(db)
        audit_repo = AuditRepository(db)
        routing_service = RoutingService(db)
        notification_service = NotificationService(db)

        tickets = ticket_repo.get_all()
        now = datetime.utcnow()

        for t in tickets:
            if t.status in ["Resolved", "Closed"]:
                continue

            # 1. Handle Queued 'New' tickets (retry auto-assignment if agent became available)
            if t.status == "New" and not t.assigned_agent_id:
                level, agent, reason = routing_service.auto_assign_ticket(t.resolved_priority)
                if agent:
                    t.assigned_agent_id = agent.agent_id
                    t.assigned_agent_name = agent.name
                    t.assigned_level = level
                    t.assignment_reason = reason
                    t.status = "Assigned"
                    engineer_repo.update_load(agent.agent_id, +1)
                    ticket_repo.update_ticket(t)

                    audit_repo.log_event(
                        ticket_id=t.ticket_id,
                        actor="SLAMonitorScheduler",
                        action="AUTO_ASSIGNED_FROM_QUEUE",
                        previous_state="New",
                        new_state="Assigned",
                        details=reason
                    )
                    notification_service.send_engineer_assignment(t, agent)

            # 2. SLA Breach Escalation
            if t.sla_deadline and now > t.sla_deadline and not t.is_escalated:
                t.is_escalated = True
                prev_level = t.assigned_level
                new_level = "L2" if prev_level == "L1" else "L3"
                
                # Attempt escalation assignment to higher level agent
                eligible_levels = ["L2", "L3"] if new_level == "L2" else ["L3"]
                available_engs = engineer_repo.get_available_by_levels(eligible_levels)
                capable_engs = [e for e in available_engs if e.current_load < e.max_capacity]
                
                old_agent_id = t.assigned_agent_id
                if old_agent_id:
                    engineer_repo.update_load(old_agent_id, -1)

                new_agent = None
                if capable_engs:
                    capable_engs.sort(key=lambda e: (e.current_load, e.agent_id))
                    new_agent = capable_engs[0]
                    t.assigned_agent_id = new_agent.agent_id
                    t.assigned_agent_name = new_agent.name
                    engineer_repo.update_load(new_agent.agent_id, +1)
                else:
                    t.assigned_agent_id = None
                    t.assigned_agent_name = None

                t.assigned_level = new_level
                ticket_repo.update_ticket(t)

                audit_repo.log_event(
                    ticket_id=t.ticket_id,
                    actor="SLAMonitorScheduler",
                    action="ESCALATED",
                    previous_state=f"Level: {prev_level}, Agent: {old_agent_id}",
                    new_state=f"Level: {new_level}, Agent: {new_agent.agent_id if new_agent else 'Unassigned'}",
                    details=f"SLA Breached (Deadline: {t.sla_deadline}). Escalated to {new_level}."
                )

                notification_service.send_escalation_notification(t, new_level, new_agent)

    except Exception as e:
        print(f"Error in check_sla_and_escalate: {e}")
    finally:
        db.close()

def trigger_eod_admin_summary():
    db: Session = SessionLocal()
    try:
        analytics = AnalyticsService(db)
        notification_service = NotificationService(db)
        stats = analytics.get_admin_dashboard_stats()
        notification_service.send_daily_admin_summary(stats)
    except Exception as e:
        print(f"Error in trigger_eod_admin_summary: {e}")
    finally:
        db.close()
