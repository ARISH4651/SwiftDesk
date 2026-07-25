# SwiftDesk — Automated Support Routing & Ticket System

SwiftDesk is a production-grade automated support ticket classification, routing, and management web application. It features a Python **FastAPI** backend with **SQLAlchemy + SQLite**, an **APScheduler** background monitoring system, persistent mock email logging, and a sleek **React (Vite)** single-page web app supporting 3 distinct roles: **Customer Portal**, **Support Team Portal**, and **Admin Operations Dashboard**.

---

## Key Features

- **Hybrid AI & Heuristic Classifier**: Evaluates incoming tickets, overrules untrusted customer priorities/categories based on text analysis, infers missing fields, and detects duplicate submissions, vague text, and non-English descriptions.
- **Strict L1 / L2 / L3 Routing Engine**:
  - `Low` Priority $\rightarrow$ Target Level **L1** (Handled by L1, L2, L3 agents).
  - `Medium` Priority $\rightarrow$ Target Level **L2** (Handled by L2, L3 agents).
  - `High` Priority $\rightarrow$ Target Level **L3** (Handled by L3 agents only).
- **Active Workload Load Balancer**: Respects agent capacity limits (`max_capacity`) and assigns new tickets to the eligible, available engineer with the lowest active workload. Queues tickets when no eligible engineer has free capacity.
- **SLA Monitoring & Auto-Escalation**: Background scheduler checks for unassigned queued tickets and SLA breaches every 60 seconds. Breached tickets are automatically escalated (`L1` $\rightarrow$ `L2` / `L2` $\rightarrow$ `L3`) and reassigned.
- **Persistent Email Logs & Audit Trail**: Records structured emails for Ticket Receipt, Assignment, Escalation, Resolution, Closure, and EOD Admin Summary in SQLite. Every state change produces an immutable audit record.
- **3 Role UIs**:
  - **Customer Portal**: Ticket submission form with real-time JSON response preview, ticket status search, lifecycle timeline, and ticket re-opening.
  - **Support Team Portal**: Selectable engineer profiles (L1/L2/L3), assigned ticket lifecycle management (`New` $\rightarrow$ `Assigned` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved` $\rightarrow$ `Closed`), and an Eligible Queue tab to pick up unassigned tickets.
  - **Admin Dashboard**: Real-time KPI metrics, Recharts charts, engineer availability toggle & workload controls, searchable/filterable master ticket table with manual reassignment modal, live email logs viewer, audit trail viewer, and batch ingestion triggers.

---

## Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 1. Backend Setup & Run
```bash
# Navigate to repository root
cd SwiftDesk

# Install Python dependencies
pip install -r backend/requirements.txt

# Seed support engineers into SQLite database
python backend/seed_data.py

# Run FastAPI backend server (http://localhost:8000)
python backend/app/main.py
```
*(FastAPI interactive OpenAPI docs will be available at http://localhost:8000/docs)*

### 2. Frontend Setup & Run
```bash
# Open a new terminal and navigate to frontend folder
cd SwiftDesk/frontend

# Install node packages
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` (or the URL printed by Vite) in your browser.

---

## Architectural Layers

```
SwiftDesk Layered Architecture:
Controllers (API Endpoints)  -->  app/api/
Services (Business Logic)    -->  app/services/ (AI, Routing, Ticket, Notification, Analytics)
Repositories (Data Access)   -->  app/repositories/
Models (SQLAlchemy ORM)      -->  app/models/
Schemas (Pydantic DTOs)      -->  app/schemas/
Scheduler (APScheduler)      -->  app/scheduler/ (SLA Monitor)
Data Store                   -->  swiftdesk.db (SQLite)
```

---

## Key Decisions & Trade-Offs

1. **Hybrid Classification Rule Engine**:
   - *Decision*: Implemented keyword & rule-based text analysis with confidence scoring before fallback to external LLM calls.
   - *Trade-off*: Instant processing (< 5ms) without external API latencies or cost while reliably detecting untrusted priorities (e.g. "Low" marked for production outages).

2. **Capacity Overload & Queueing**:
   - *Decision*: When all eligible agents are at maximum capacity or unavailable, tickets remain in `New` status with reason `"Queued: Capacity Exceeded"`. The SLA monitor periodically attempts auto-assignment as agents free up.
   - *Trade-off*: Prevents engineer burnout while maintaining queue visibility for admin reassignment.

3. **Persistent Mock Email Store**:
   - *Decision*: Saved all rendered emails to an `EmailLog` SQLite table rather than relying on dummy SMTP servers.
   - *Trade-off*: Allows instant real-time inspection in the Admin UI without setting up local mailboxes.

---

## Production Improvements

- **WebSockets / Server-Sent Events (SSE)**: Replace polling with real-time push updates for the Admin and Support dashboards.
- **OAuth2 / OIDC Integration**: Implement JWT authentication and role-based access control (RBAC) across the 3 portals.
- **PostgreSQL Database**: Migrate from SQLite to PostgreSQL with connection pooling for high-concurrency enterprise deployments.
