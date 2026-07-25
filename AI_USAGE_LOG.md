# SwiftDesk AI Usage Report

This report summarizes where AI was used during SwiftDesk design, implementation, testing, and refinement. It also records what was verified manually or by tests, and where AI-generated output had to be corrected.

## 1. Scope

AI was used for:

- Requirements analysis
- Database and schema design
- Backend business logic and routing
- Classification and normalization behavior
- Test generation and validation
- Frontend implementation and build verification

## 2. Verification Summary

The project was validated against the SwiftDesk checklist and runtime tests.

- Routing rules were confirmed for L1, L2, and L3 eligibility.
- Ticket classification was verified with sample tickets and edge cases.
- Duplicate detection, queue handling, reassignment, and SLA escalation were tested.
- Backend behavior was validated with `pytest`.
- Frontend behavior was validated with `npm run build`.

## 3. AI Assistance Log

| Step | Task | AI Output | Verification | Result |
|---|---|---|---|---|
| 1 | Requirements and spec analysis | Extracted the routing and API rules from the candidate brief. | Checked against the brief sections and appendix. | Accepted without changes. |
| 2 | Database and schema design | Proposed SQLAlchemy models for Ticket, Engineer, Assignment, AuditLog, and EmailLog. | Compared fields with Pydantic DTOs and ticket workflow needs. | Added fields such as `confidence_score`, `is_vague`, and `language`. |
| 3 | Test generation | Generated routing tests for ticket assignment behavior. | Pytest showed the active-load balancer picked a different eligible engineer than the static assertion expected. | Updated the assertion to allow any valid eligible engineer. |
| 4 | Classification logic | Suggested a keyword-based classifier for untrusted priorities and categories. | Tested with sample ticket data, including outage, billing, vague, and non-English cases. | Behavior matched the intended priority correction and normalization flow. |
| 5 | Frontend build support | Generated React components and styling. | Initial build exposed a module resolution issue for `lucide-react`. | Reinstalled dependencies and verified a clean production build. |

## 4. Corrections Made

- Static routing assumptions in tests were replaced with checks that match the load balancer behavior.
- Ticket schema was expanded to preserve original and resolved values.
- Frontend dependency resolution was repaired and verified by a successful build.

## 5. Final Outcome

- The routing engine behaves deterministically under the supported rules.
- AI-driven classification is verified against sample and edge-case tickets.
- Audit logs and email logs are traceable in SQLite.
- The project passes its backend test suite and frontend build check.
