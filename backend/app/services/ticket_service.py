from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.repositories.ticket_repository import TicketRepository
from app.repositories.engineer_repository import EngineerRepository
from app.repositories.audit_repository import AuditRepository
from app.services.ai_service import AIService
from app.services.routing_service import RoutingService
from app.services.notification_service import NotificationService
from app.schemas.ticket import TicketCreateSchema
from app.config import SLA_HOURS

class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.engineer_repo = EngineerRepository(db)
        self.audit_repo = AuditRepository(db)
        self.ai_service = AIService()
        self.routing_service = RoutingService(db)
        self.notification_service = NotificationService(db)

    def process_incoming_ticket(self, payload: TicketCreateSchema) -> Dict[str, Any]:
        # 1. Duplicate Detection Check
        recent_dup = self.ticket_repo.find_recent_duplicate(
            customer_id=payload.customer.customer_id,
            subject=payload.subject,
            external_ref=payload.external_ref
        )
        is_duplicate = False
        duplicate_of_id = None
        if recent_dup:
            is_duplicate = True
            duplicate_of_id = recent_dup.ticket_id

        # 2. AI Hybrid Classification & Verification
        analysis = self.ai_service.analyze_and_verify(
            subject=payload.subject,
            description=payload.description,
            customer_cat=payload.category,
            customer_prio=payload.priority
        )

        resolved_cat = analysis["resolved_category"]
        resolved_prio = analysis["resolved_priority"]
        confidence = analysis["confidence_score"]
        is_vague = analysis["is_vague"]
        lang = analysis["language"]
        reasoning = analysis["reasoning"]

        # 3. Determine Support Level & Auto-Assign
        target_level = self.routing_service.determine_target_level(resolved_prio)
        assigned_agent = None
        assign_reason = "Duplicate ticket detected; no new assignment was created." if is_duplicate else "Queued for manual review."
        if not is_duplicate:
            target_level, assigned_agent, assign_reason = self.routing_service.auto_assign_ticket(resolved_prio)

        # 4. Generate Ticket ID
        next_num = self.ticket_repo.get_count_next_id()
        ticket_id = f"TKT-{next_num}"

        # 5. SLA Deadline Calculation
        sla_h = SLA_HOURS.get(resolved_prio, 8.0)
        sla_deadline = datetime.utcnow() + timedelta(hours=sla_h)

        status = "Assigned" if assigned_agent else "New"

        ticket_data = {
            "ticket_id": ticket_id,
            "external_ref": payload.external_ref or f"ext-{next_num}",
            "customer_id": payload.customer.customer_id,
            "customer_name": payload.customer.name,
            "customer_email": payload.customer.email,
            "subject": payload.subject,
            "description": payload.description,
            "channel": payload.channel or "web_app",
            "metadata_json": payload.metadata,
            "original_category": payload.category or "Unspecified",
            "original_priority": payload.priority or "Unspecified",
            "resolved_category": resolved_cat,
            "resolved_priority": resolved_prio,
            "confidence_score": confidence,
            "is_duplicate": is_duplicate,
            "duplicate_of": duplicate_of_id,
            "is_vague": is_vague,
            "language": lang,
            "assigned_level": target_level,
            "assigned_agent_id": assigned_agent.agent_id if assigned_agent else None,
            "assigned_agent_name": assigned_agent.name if assigned_agent else None,
            "assignment_reason": assign_reason,
            "status": status,
            "sla_hours": sla_h,
            "sla_deadline": sla_deadline,
            "is_escalated": False
        }

        ticket = self.ticket_repo.create_ticket(ticket_data)

        # 6. Record Assignment History & Update Engineer Load
        if assigned_agent:
            self.engineer_repo.update_load(assigned_agent.agent_id, +1)
            self.ticket_repo.create_assignment_record({
                "ticket_id": ticket_id,
                "agent_id": assigned_agent.agent_id,
                "assigned_level": target_level,
                "reason": assign_reason,
                "assigned_by": "AutoAssignmentEngine"
            })

        # 7. Audit Log Entry
        audit_details = (
            f"Ingested ticket. Priority: {resolved_prio} (orig: {payload.priority}). "
            f"Category: {resolved_cat} (orig: {payload.category}). Assigned: {assigned_agent.agent_id if assigned_agent else 'None'}."
        )
        audit_details += f" Reasoning: {reasoning}"
        if is_duplicate:
            audit_details += f" [DUPLICATE DETECTED of {duplicate_of_id}]"
        if is_vague:
            audit_details += " [VAGUE DESCRIPTION DETECTED]"

        self.audit_repo.log_event(
            ticket_id=ticket_id,
            actor="System",
            action="TICKET_RECEIVED",
            previous_state=None,
            new_state=status,
            details=audit_details
        )

        # 8. Notifications
        self.notification_service.send_customer_confirmation(ticket, assigned_agent)
        if assigned_agent:
            self.notification_service.send_engineer_assignment(ticket, assigned_agent)

        return {
            "status": "accepted",
            "ticket_id": ticket_id,
            "is_duplicate": is_duplicate,
            "duplicate_of": duplicate_of_id,
            "original_category": payload.category or "Unspecified",
            "original_priority": payload.priority or "Unspecified",
            "resolved_category": resolved_cat,
            "resolved_priority": resolved_prio,
            "confidence_score": confidence,
            "language": lang,
            "reasoning": reasoning,
            "assigned_level": target_level,
            "assigned_agent_id": assigned_agent.agent_id if assigned_agent else None,
            "message": "Duplicate ticket received and flagged. A confirmation email has been sent." if is_duplicate else "Ticket received and assigned. A confirmation email has been sent."
        }

    def update_status(self, ticket_id: str, new_status: str, actor: str = "SupportAgent", notes: str = None) -> Tuple[bool, str]:
        ticket = self.ticket_repo.get_by_ticket_id(ticket_id)
        if not ticket:
            return False, "Ticket not found"

        prev_status = ticket.status
        ticket.status = new_status
        if notes:
            ticket.resolution_notes = notes

        if new_status in ["Resolved", "Closed"] and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
            # Decrement engineer load if ticket was active
            if ticket.assigned_agent_id:
                self.engineer_repo.update_load(ticket.assigned_agent_id, -1)

        self.ticket_repo.update_ticket(ticket)

        # Audit Log
        self.audit_repo.log_event(
            ticket_id=ticket_id,
            actor=actor,
            action=f"STATUS_CHANGED_TO_{new_status.upper()}",
            previous_state=prev_status,
            new_state=new_status,
            details=notes or f"Ticket status changed from {prev_status} to {new_status} by {actor}."
        )

        # Completion Email Trigger
        if new_status in ["Resolved", "Closed"]:
            self.notification_service.send_completion_email(ticket, new_status)

        return True, f"Status updated to {new_status}"

    def reassign_ticket(self, ticket_id: str, new_agent_id: str, actor: str = "Admin", reason: str = "Manual Reassignment") -> Tuple[bool, str]:
        ticket = self.ticket_repo.get_by_ticket_id(ticket_id)
        if not ticket:
            return False, "Ticket not found"

        new_agent = self.engineer_repo.get_by_agent_id(new_agent_id)
        if not new_agent:
            return False, "Agent not found"

        prev_agent_id = ticket.assigned_agent_id
        if prev_agent_id:
            self.engineer_repo.update_load(prev_agent_id, -1)

        ticket.assigned_agent_id = new_agent.agent_id
        ticket.assigned_agent_name = new_agent.name
        ticket.assigned_level = new_agent.level
        ticket.assignment_reason = f"Reassigned by {actor}: {reason}"
        ticket.status = "Assigned"

        self.engineer_repo.update_load(new_agent.agent_id, +1)
        self.ticket_repo.update_ticket(ticket)

        self.ticket_repo.create_assignment_record({
            "ticket_id": ticket_id,
            "agent_id": new_agent.agent_id,
            "assigned_level": new_agent.level,
            "reason": reason,
            "assigned_by": actor
        })

        self.audit_repo.log_event(
            ticket_id=ticket_id,
            actor=actor,
            action="REASSIGNED",
            previous_state=f"Agent: {prev_agent_id}",
            new_state=f"Agent: {new_agent.agent_id}",
            details=reason
        )

        self.notification_service.send_engineer_assignment(ticket, new_agent)

        return True, f"Ticket reassigned to {new_agent.name} ({new_agent.agent_id})"
