from sqlalchemy.orm import Session
from app.repositories.email_repository import EmailRepository
from app.models.ticket import Ticket
from app.models.engineer import Engineer
from typing import Dict, Any

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.email_repo = EmailRepository(db)

    def send_customer_confirmation(self, ticket: Ticket, agent: Engineer = None):
        agent_info = f"Agent {agent.name} (Level {agent.level})" if agent else "Support Team Pool (Queued)"
        next_steps = (
            f"1. Your ticket is currently in '{ticket.status}' status.\n"
            f"2. Our {ticket.assigned_level} support level will review your issue.\n"
            f"3. Expected SLA Resolution time: {ticket.sla_hours} hours."
        )

        body = (
            f"Dear {ticket.customer_name},\n\n"
            f"Thank you for contacting SwiftDesk Support! We have received your ticket [{ticket.ticket_id}].\n\n"
            f"Ticket Details:\n"
            f"• Subject: {ticket.subject}\n"
            f"• Resolved Priority: {ticket.resolved_priority}\n"
            f"• Assigned Level: {ticket.assigned_level}\n"
            f"• Assigned Agent: {agent_info}\n\n"
            f"Next Steps:\n{next_steps}\n\n"
            f"Best regards,\nSwiftDesk Support Team"
        )

        self.email_repo.create_email_log({
            "ticket_id": ticket.ticket_id,
            "recipient_email": ticket.customer_email,
            "recipient_name": ticket.customer_name,
            "recipient_role": "Customer",
            "trigger_event": "TICKET_RECEIVED",
            "subject": f"[SwiftDesk] Ticket Received: {ticket.ticket_id} - {ticket.subject}",
            "body": body
        })

    def send_engineer_assignment(self, ticket: Ticket, agent: Engineer):
        if not agent:
            return

        body = (
            f"Hello {agent.name},\n\n"
            f"A new ticket [{ticket.ticket_id}] has been assigned to you.\n\n"
            f"Ticket Details:\n"
            f"• Customer: {ticket.customer_name} ({ticket.customer_email})\n"
            f"• Subject: {ticket.subject}\n"
            f"• Description: {ticket.description}\n"
            f"• Resolved Category: {ticket.resolved_category}\n"
            f"• Priority: {ticket.resolved_priority}\n"
            f"• SLA Deadline: {ticket.sla_deadline}\n\n"
            f"Please log in to the Support Portal to review and update status.\n\n"
            f"SwiftDesk Automation System"
        )

        self.email_repo.create_email_log({
            "ticket_id": ticket.ticket_id,
            "recipient_email": agent.email,
            "recipient_name": agent.name,
            "recipient_role": "SupportEngineer",
            "trigger_event": "ASSIGNMENT",
            "subject": f"[Assignment Notification] Ticket {ticket.ticket_id} - {ticket.resolved_priority} Priority",
            "body": body
        })

    def send_escalation_notification(self, ticket: Ticket, new_level: str, agent: Engineer = None):
        body = (
            f"ALERT: Ticket [{ticket.ticket_id}] has breached SLA response time and has been escalated!\n\n"
            f"• Subject: {ticket.subject}\n"
            f"• Escalated Level: {new_level}\n"
            f"• New Assigned Agent: {agent.name if agent else 'Unassigned Queue'}\n\n"
            f"Immediate attention is required."
        )

        # Notify admin and new agent
        self.email_repo.create_email_log({
            "ticket_id": ticket.ticket_id,
            "recipient_email": "admin@swiftdesk.com",
            "recipient_name": "Operations Manager",
            "recipient_role": "Admin",
            "trigger_event": "ESCALATION",
            "subject": f"[SLA ESCALATION] Ticket {ticket.ticket_id} Escalated to {new_level}",
            "body": body
        })

        if agent:
            self.send_engineer_assignment(ticket, agent)

    def send_completion_email(self, ticket: Ticket, action: str):
        body = (
            f"Dear {ticket.customer_name},\n\n"
            f"Your support ticket [{ticket.ticket_id}] has been marked as '{action}'.\n\n"
            f"Subject: {ticket.subject}\n"
            f"Resolution Notes: {ticket.resolution_notes or 'Issue resolved by support team.'}\n\n"
            f"If you still experience issues, you may re-open this ticket through the Customer Portal.\n\n"
            f"Thank you for choosing SwiftDesk!"
        )

        self.email_repo.create_email_log({
            "ticket_id": ticket.ticket_id,
            "recipient_email": ticket.customer_email,
            "recipient_name": ticket.customer_name,
            "recipient_role": "Customer",
            "trigger_event": action.upper(),
            "subject": f"[SwiftDesk] Ticket {ticket.ticket_id} Has Been {action}",
            "body": body
        })

    def send_daily_admin_summary(self, stats: Dict[str, Any]):
        body = (
            f"SwiftDesk Daily Operations Summary\n"
            f"=================================\n\n"
            f"• Total Tickets Ingested: {stats.get('total_tickets', 0)}\n"
            f"• Open Tickets: {stats.get('open_tickets', 0)}\n"
            f"• Resolved / Closed Tickets: {stats.get('resolved_tickets', 0)}\n"
            f"• SLA Breaches / Escalations: {stats.get('sla_breaches', 0)}\n"
            f"• Average Resolution Time: {stats.get('avg_resolution_hours', 0.0):.2f} hours\n\n"
            f"Engineer Workloads:\n"
        )

        for eng_stat in stats.get("engineer_workloads", []):
            body += f"  - {eng_stat['name']} ({eng_stat['agent_id']}, {eng_stat['level']}): {eng_stat['current_load']}/{eng_stat['max_capacity']} active\n"

        body += "\nSystem operating normally.\nSwiftDesk Operations Engine"

        self.email_repo.create_email_log({
            "ticket_id": None,
            "recipient_email": "admin@swiftdesk.com",
            "recipient_name": "Operations Manager",
            "recipient_role": "Admin",
            "trigger_event": "DAILY_ADMIN_SUMMARY",
            "subject": f"[Daily Admin Summary] SwiftDesk Operations Report",
            "body": body
        })
