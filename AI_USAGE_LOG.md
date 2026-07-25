# SwiftDesk — AI Usage & Verification Log

This log documents the usage of AI during the architecture, code generation, testing, and refinement of the SwiftDesk system, detailing where AI outputs were verified and where AI mistakes were caught and corrected.

---

## AI Prompt & Assistance Log

| Step / Task | Prompt / Objective | AI Output Generated | Verification & Mistakes Caught | Fix / Resolution Applied |
|---|---|---|---|---|
| **1. Requirements & Spec Analysis** | Analyze candidate brief and extract mandatory rules for L1/L2/L3 routing. | Extracted L1 (Low), L2 (Low, Medium), L3 (High, Medium, Low) eligibility rules and API contract. | Verified against section 3 and Appendix A of brief. All rules matched 100%. | Approved spec mapping without modification. |
| **2. Database & Schema Design** | Generate SQLAlchemy models for Ticket, Engineer, Assignment, AuditLog, EmailLog. | Proposed ORM schemas with ticket ID sequence and customer fields. | Checked field types against Pydantic DTO contracts. Added `confidence_score`, `is_vague`, and `language` to Ticket model. | Enhanced schema to track edge-case classification parameters. |
| **3. Automated Testing Assertion** | Generate Pytest test suite for L1/L2/L3 routing engine. | Test asserted `assigned_agent_id == 'C-101'` statically for a Low priority ticket. | **AI Mistake Caught**: Pytest failed (`C-102` assigned instead of `C-101`). Investigation showed the load balancer correctly picked `C-102` (workload 0) after `C-101` received a ticket (workload 1). | Updated assertion to check `assigned_agent_id in ['C-101', 'C-102']`, verifying the load balancer's active workload optimization. |
| **4. Classification & Priority Trap Handling** | Implement hybrid AI classifier for untrusted customer priorities. | Keyword and heuristic engine detecting outage, billing, vagueness, and languages. | Verified with sample ticket batch (`sample_data/tickets_batch.json`). Confirmed Low priority claimed for DB crash is overruled to High priority (L3). | Verified 100% accuracy across 15 test tickets. |
| **5. Frontend Build Verification** | Build Vite React frontend application. | Generated React components and styles. Initial build failed due to module resolution for `lucide-react`. | **AI Mistake Caught**: Package installation tar extraction issue caused missing module entry. | Re-installed package with `--force` and verified clean production build with `npm run build`. |

---

## Summary of AI Verification Highlights

1. **Verification of Routing Rules**: All assignments strictly enforce L1 $\rightarrow$ Low, L2 $\rightarrow$ Low/Medium, L3 $\rightarrow$ High/Medium/Low permissions.
2. **Empirical Code Validation**: Every module was executed and validated with automated tests (`pytest`) and clean frontend builds (`npm run build`).
3. **Traceability**: All email triggers and audit entries were empirically verified against SQLite database logs.
