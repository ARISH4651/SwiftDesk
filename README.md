# SwiftDesk

SwiftDesk is an automated support ticket classification, routing, and management app. It combines a FastAPI backend, SQLite persistence, scheduled SLA monitoring, and a React/Vite frontend with three role-based portals:

- Customer Portal
- Support Team Portal
- Admin Operations Dashboard

## Project Overview

The system is designed to:

- classify tickets with hybrid AI and heuristic rules
- correct untrusted customer priority or category input
- route tickets to the appropriate support level
- respect workload and capacity limits
- queue tickets when no engineer is available
- monitor SLA deadlines and escalate overdue tickets
- log audit events and persistent email notifications

## Key Features

### Ticket Intelligence

- Detects duplicate submissions
- Flags vague ticket descriptions
- Detects non-English input and normalizes it internally
- Preserves original customer values and stores resolved values separately

### Routing Rules

- Low priority -> L1 eligible agents
- Medium priority -> L2 or L3 eligible agents
- High priority -> L3 eligible agents only

### Assignment Logic

- Selects the eligible available engineer with the lowest active workload
- Respects `max_capacity`
- Keeps tickets queued when no suitable engineer is free

### SLA and Escalation

- Background scheduler runs every 60 seconds
- Rechecks queued tickets for assignment
- Escalates overdue tickets and reassigns them when possible

### Logging and Traceability

- Stores audit events in SQLite
- Stores rendered email notifications in SQLite
- Supports ticket history and dashboard analytics

## Portals

### Customer Portal

- Submit support tickets
- Search ticket status
- View lifecycle timeline
- Re-open resolved or closed tickets

### Support Portal

- Switch between engineer profiles
- View assigned tickets
- Pick up eligible queued tickets
- Move tickets through the lifecycle

### Admin Dashboard

- View ticket and engineer metrics
- Reassign tickets manually
- Toggle engineer availability
- View audit logs and email logs
- Trigger batch ingestion and SLA checks

## Architecture

```text
Controllers (API Endpoints)  -> app/api/
Services (Business Logic)    -> app/services/
Repositories (Data Access)   -> app/repositories/
Models (SQLAlchemy ORM)      -> app/models/
Schemas (Pydantic DTOs)      -> app/schemas/
Scheduler (APScheduler)      -> app/scheduler/
Data Store                   -> swiftdesk.db
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm

### Backend

```bash
cd SwiftDesk
pip install -r backend/requirements.txt
python backend/seed_data.py
python backend/app/main.py
```

Backend docs:

- http://localhost:8000/docs

### Frontend

```bash
cd SwiftDesk/frontend
npm install
npm run dev
```

Frontend URL:

- http://localhost:5173

## Design Decisions

### Hybrid classifier

The classifier uses rules and keyword matching before any external model call. This keeps the system fast and makes priority correction deterministic for known cases such as outages, billing issues, and vague text.

### Queue-first capacity control

Tickets stay queued when no eligible engineer has capacity. This avoids overload while keeping the ticket visible for later auto-assignment or manual reassignment.

### Persistent email logs

Email notifications are stored in SQLite instead of being sent through live SMTP during local development. That makes notification behavior easy to inspect from the Admin Dashboard.

## Validation

The current implementation has been validated with:

- backend pytest coverage
- frontend production build
- manual checks for ticket creation, routing, reassignment, and SLA escalation

## Future Improvements

- WebSockets or SSE for live dashboard updates
- OAuth2 or OIDC authentication and RBAC
- PostgreSQL for production-scale concurrency
