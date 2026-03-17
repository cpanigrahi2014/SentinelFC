# AML End-to-End Endpoint Mapping

## Architecture Overview

All traffic enters through the **API Gateway** (port 8000), mounted at `/api/`.

| Service               | Port | Prefix (direct)             | Gateway proxy prefix                     |
|-----------------------|------|-----------------------------|------------------------------------------|
| api-gateway           | 8000 | `/api/`                     | N/A — this IS the gateway                |
| transaction-monitoring| 8001 | `/api/v1/monitoring`        | (admin) `/api/admin/data-sources/...`    |
| fraud-detection       | 8002 | `/api/v1/fraud`             | (admin) `.../efm/`, `.../dbf/`, `.../pmf/` |
| sanctions-screening   | 8003 | `/api/v1/sanctions`         | (admin) `.../wlf/`, `.../cdd-edd/screen/` |
| customer-risk-scoring | 8004 | `/api/v1/risk-scoring`      | (admin) `.../cdd-edd/`, `.../kyc/`       |
| alert-management      | 8005 | `/api/v1/alerts`            | — (not yet proxied)                       |
| case-management       | 8006 | `/api/v1/cases`, `/api/v1/actone` | (admin) `.../actone/`              |
| network-analytics     | 8007 | `/api/v1/network`           | — (not yet proxied)                       |
| regulatory-reporting  | 8008 | `/api/v1/reports`           | — (not yet proxied)                       |
| ai-ml-scoring         | 8009 | `/api/v1/ml`, `/api/v1/aiml`| (admin) `.../aiml/`                      |
| data-integration      | 8010 | `/api/v1/integration`       | — (not yet proxied)                       |
| audit-logging         | 8011 | `/api/v1/audit`             | — (not yet proxied)                       |

> **Note:** The frontend `api.js` calls paths like `/api/alerts`, `/api/cases`, `/api/reports/sar`, etc.
> These currently resolve only when the gateway adds proxy routes, or when the Ingress/nginx
> is configured to route them to individual microservices. Currently only the gateway's own
> 79 endpoints and the microservices' direct ports are functional.

---

## Scenario Flow: AML End-to-End

```
A: Customer makes unusual transfers
B: Transaction Monitoring generates alert
C: Alert routed to investigation queue (ActOne)
D: Investigator reviews in dashboard
E: Notes, evidence, network analysis attached
F: Case escalated to senior analyst
G: SAR filed with FinCEN
H: Case closed with full audit trail
```

---

## Step A — Customer Makes Unusual Transfers

**Purpose:** Ingest transaction data into the platform.

### A1. Data Integration — Ingest Transactions

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)**  | `http://localhost:8010/api/v1/integration/ingest/transactions` |
| **Auth**    | JWT Bearer |
| **Request Body** | `{ "transactions": [ { "transaction_id": "...", "customer_id": "...", "amount": 15000, "currency": "USD", "transaction_type": "wire_transfer", "channel": "online", "timestamp": "...", "counterparty_id": "...", "counterparty_country": "IR" } ] }` |
| **Response** | `{ "ingested": <count>, "errors": [], "status": "success" }` |
| **Frontend fn** | — (backend / Kafka pipeline) |

### A2. Data Integration — Ingest Customer Profile

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)**  | `http://localhost:8010/api/v1/integration/ingest/customers` |
| **Request Body** | `{ "customers": [ { "customer_id": "...", "name": "...", "account_type": "...", "risk_rating": "...", "country": "...", "kyc_status": "..." } ] }` |
| **Response** | `{ "ingested": <count>, "errors": [], "status": "success" }` |

### A3. Data Integration — Ingest Sanctions Lists

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)**  | `http://localhost:8010/api/v1/integration/ingest/sanctions` |
| **Request Body** | `{ "lists": [ { "list_name": "OFAC_SDN", "entries": [...] } ] }` |
| **Response** | `{ "ingested": <count>, "errors": [], "status": "success" }` |

### A4. Data Integration — List Sources

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)**  | `http://localhost:8010/api/v1/integration/sources` |
| **Response** | Array of configured data source metadata |

### A5. Data Integration — Stats

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)**  | `http://localhost:8010/api/v1/integration/stats` |
| **Response** | Ingestion counts and throughput metrics |

---

## Step B — Transaction Monitoring Generates Alert

**Purpose:** Run AML rules against transaction data. If composite score ≥ threshold, an alert is generated.

### B1. Analyze Single Transaction

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)**  | `http://localhost:8001/api/v1/monitoring/analyze` |
| **Auth**    | JWT (ANALYST, SENIOR_ANALYST, ADMIN) |
| **Request Body** | `TransactionEvent` schema: `{ "transaction_id": "uuid", "customer_id": "...", "amount": 15000.00, "currency": "USD", "transaction_type": "wire_transfer", "channel": "online", "timestamp": "...", "counterparty_id": "...", "counterparty_country": "IR" }` |
| **Response** | `{ "transaction_id": "...", "risk_score": 0.85, "risk_level": "high", "alert_generated": true, "rules_evaluated": 20, "rules_triggered": [ { "rule_id": "AML-003", "rule_name": "High-Risk Country Transfer", "risk_score": 0.9, "description": "...", "details": {...} } ] }` |
| **Key fields** | `risk_score` (0-1), `risk_level` (critical/high/medium/low), `alert_generated` (bool), `rules_triggered[]` |

### B2. Batch Analyze (Look-back Window)

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)**  | `http://localhost:8001/api/v1/monitoring/analyze/batch` |
| **Auth**    | JWT (ANALYST, SENIOR_ANALYST, ADMIN) |
| **Request Body** | `[ { "transaction_id": "...", "customer_id": "...", "amount": ..., ... }, ... ]` (max 10,000) |
| **Response** | `{ "batch_size": 500, "alerts_generated": 12, "total_rules_triggered": 47, "processing_mode": "batch_sequential", "results": [ { "transaction_id": "...", "customer_id": "...", "risk_score": 0.85, "alert_generated": true, "rules_triggered": ["AML-003","AML-009"] } ] }` |

### B3. List Active AML Rules

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)**  | `http://localhost:8001/api/v1/monitoring/rules` |
| **Auth**    | JWT (any) |
| **Response** | `{ "rules": [ { "rule_id": "AML-001", "name": "Large Cash Deposit", "description": "...", "category": "cash_threshold", "is_active": true }, ... ] }` |

**13 AML Rules (AML-001 → AML-013):**

| Rule ID  | Name                        | Category          |
|----------|-----------------------------|--------------------|
| AML-001  | Large Cash Deposit          | cash_threshold     |
| AML-002  | Structuring Detection       | structuring        |
| AML-003  | High-Risk Country Transfer  | geographic_risk    |
| AML-004  | Rapid Fund Movement         | velocity           |
| AML-005  | Round Amount Transaction    | pattern            |
| AML-006  | Unusual Channel for Amount  | channel_risk       |
| AML-007  | Dormant Account Activity    | behavioral         |
| AML-008  | ACH Transfer Threshold      | ach_threshold      |
| AML-009  | SWIFT/Wire Transfer Threshold| swift_threshold   |
| AML-010  | Card/ATM Threshold          | card_atm_threshold |
| AML-011  | Cross-Channel Anomaly       | cross_channel      |
| AML-012  | Velocity Spike              | velocity           |
| AML-013  | Smurfing / Fan-In Detection | smurfing           |

### B4. Monitoring Stats

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)**  | `http://localhost:8001/api/v1/monitoring/stats` |
| **Response** | `{ "service": "transaction-monitoring", "status": "operational", "alert_threshold": 0.7, "high_risk_countries": [...], "rules_active": 13 }` |

### B5. AI/ML Scoring — AML Prediction

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/aiml/predict/aml` |
| **Direct path** | `http://localhost:8009/api/v1/aiml/predict/aml` |
| **Auth**    | JWT |
| **Request Body** | `{ "customer_id": "...", "transaction_amount": 50000, "transaction_type": "wire_transfer", "country": "IR" }` |
| **Response** | `{ "prediction": {...}, "risk_score": 0.92, "risk_level": "critical", "contributing_factors": [...] }` |

### B6. AI/ML Scoring — Fraud Prediction

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/aiml/predict/fraud` |
| **Direct path** | `http://localhost:8009/api/v1/ml/predict/fraud` |
| **Auth**    | JWT |
| **Request Body** | `{ "transaction_data": {...} }` |
| **Response** | `{ "fraud_score": 0.78, "is_fraud": true, "model_version": "...", "features": {...} }` |

### B7. AI/ML — Anomaly Detection

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/aiml/anomaly/detect` |
| **Request Body** | `{ "customer_id": "...", "features": {...} }` |
| **Response** | `{ "is_anomaly": true, "anomaly_score": 0.88, "detection_method": "...", "anomalous_features": [...] }` |

### B8. Sanctions Screening — Screen Payment

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/wlf/screen-payment` |
| **Direct path** | `http://localhost:8003/api/v1/sanctions/screen/payment` |
| **Auth**    | JWT |
| **Request Body** | `{ "originator_name": "...", "beneficiary_name": "...", "amount": 50000, "currency": "USD" }` |
| **Response** | `{ "screening_id": "...", "matches": [...], "risk_level": "...", "recommendation": "..." }` |

---

## Step C — Alert Routed to Investigation Queue (ActOne)

**Purpose:** Alert is created in alert-management, triaged and assigned via ActOne.

### C1. List Alerts

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8005/api/v1/alerts/` |
| **Auth**    | JWT (any) |
| **Query params** | `status` (new/open/investigating/escalated/closed), `type`, `customer_id`, `priority` (low/medium/high/critical), `assigned_to`, `page`, `page_size` |
| **Response** | `{ "alerts": [ { "alert_id": "uuid", "type": "aml_high_risk", "customer_id": "...", "risk_score": 0.85, "priority": "high", "status": "new", "description": "...", "created_at": "...", "assigned_to": null } ], "total": 42 }` |
| **Frontend fn** | `getAlerts(params)` |

### C2. Get Single Alert

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8005/api/v1/alerts/{alert_id}` |
| **Auth**    | JWT (any) |
| **Response** | Full alert object with history |
| **Frontend fn** | `getAlert(alertId)` |

### C3. Assign Alert to Investigator

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8005/api/v1/alerts/{alert_id}/assign` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "assigned_to": "investigator_user_id" }` |
| **Response** | Updated alert with `status: "investigating"`, `assigned_to` set |
| **Frontend fn** | `assignAlert(alertId, data)` |

### C4. Alert Statistics

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8005/api/v1/alerts/stats/summary` |
| **Auth**    | JWT (any) |
| **Response** | `{ "total_alerts": 150, "by_status": {"new": 30, "investigating": 45, ...}, "by_type": {...}, "by_priority": {...} }` |
| **Frontend fn** | `getAlertStats()` |

### C5. ActOne — Triage Alert into Case

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/actone/triage` |
| **Direct path** | `http://localhost:8006/api/v1/actone/triage` |
| **Auth**    | JWT |
| **Request Body** | `{ "alert_id": "...", "customer_id": "...", "alert_type": "aml", "risk_score": 0.85 }` |
| **Response** | `{ "triage_id": "...", "case_id": "...", "priority": "high", "assigned_team": "AML_INVESTIGATIONS", "recommended_action": "...", "state": "triage_complete" }` |
| **Frontend fn** | `triageAlert(data)` |

### C6. ActOne — AML Investigation Scenario

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/actone/scenarios/aml-investigation` |
| **Auth**    | JWT |
| **Request Body** | `{ "customer_id": "...", "alert_ids": ["..."], "investigation_type": "structuring" }` |
| **Response** | Full investigation scenario with steps, SLA timelines, customer360, risk_factors |

### C7. ActOne — Dashboard

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/actone/dashboard` |
| **Auth**    | JWT |
| **Response** | `{ "total_cases": ..., "by_status": {...}, "by_priority": {...}, "sla_compliance": {...}, "team_workload": [...] }` |
| **Frontend fn** | `getActOneDashboard()` |

---

## Step D — Investigator Reviews in Dashboard

**Purpose:** Open case, examine customer history, risk scores, transaction patterns, network links.

### D1. Create Investigation Case (from alerts)

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "alert_ids": ["alert-uuid-1", "alert-uuid-2"], "customer_id": "CUST-001", "case_type": "aml_investigation", "assigned_to": "investigator_id", "priority": "high", "description": "Suspected structuring activity" }` |
| **Response** | `{ "case_id": "uuid", "alert_ids": [...], "customer_id": "...", "case_type": "aml_investigation", "status": "open", "assigned_to": "...", "priority": "high", "description": "...", "created_at": "...", "notes": [], "evidence": [] }` |
| **Frontend fn** | `createCase(data)` |

### D2. List Cases

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/` |
| **Auth**    | JWT (any) |
| **Query params** | `status` (open/investigating/escalated/pending_sar/closed), `assigned_to`, `customer_id`, `priority`, `page`, `page_size` |
| **Response** | `{ "cases": [...], "total": 25 }` |
| **Frontend fn** | `getCases(params)` |

### D3. Get Full Case Details

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}` |
| **Auth**    | JWT (any) |
| **Response** | Full case object including `notes[]`, `evidence[]`, all metadata |
| **Frontend fn** | `getCase(caseId)` |

### D4. Update Case

| Field       | Value |
|-------------|-------|
| **Method**  | `PUT` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "status": "investigating", "assigned_to": "...", "priority": "critical", "description": "Updated findings..." }` |
| **Response** | Updated case object |
| **Frontend fn** | `updateCase(caseId, data)` |

### D5. Customer 360 View (ActOne)

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/actone/customer360/{customer_id}` |
| **Auth**    | JWT |
| **Response** | `{ "customer_id": "...", "profile": {...}, "risk_scores": {...}, "transaction_summary": {...}, "alerts_history": [...], "cases_history": [...], "sanctions_matches": [...], "network_connections": [...] }` |
| **Frontend fn** | `getCustomer360(customerId)` |

### D6. Customer Risk Profile (CDD/EDD)

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/cdd-edd/profiles` |
| **Direct path** | `http://localhost:8004/api/v1/risk-scoring/profiles` |
| **Auth**    | JWT |
| **Response** | Array of customer risk profiles with CDD scores, risk factors |

### D7. Customer Risk — Calculate Score

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Direct path** | `http://localhost:8004/api/v1/risk-scoring/calculate` |
| **Auth**    | JWT |
| **Request Body** | `{ "customer_id": "...", "customer_type": "individual", "country": "...", "products": [...], "annual_income": ..., "source_of_funds": "..." }` |
| **Response** | `{ "customer_id": "...", "risk_score": 78, "risk_level": "high", "risk_factors": [...], "recommendations": [...] }` |

### D8. EDD Workflows (Enhanced Due Diligence)

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/cdd-edd/edd/workflows` |
| **Direct path** | `http://localhost:8004/api/v1/risk-scoring/edd/workflows` |
| **Auth**    | JWT |
| **Response** | `{ "workflows": [ { "workflow_id": "...", "customer_id": "...", "status": "...", "checklist": [...], "approvals": [...] } ] }` |

### D9. KYC Dashboard

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/kyc/dashboard` |
| **Direct path** | `http://localhost:8004/api/v1/risk-scoring/kyc/dashboard` |
| **Response** | KYC pipeline status, counts by state, due reviews |

---

## Step E — Notes, Evidence, and Network Analysis

**Purpose:** Attach investigation notes, evidence files, and run network analytics to identify related entities.

### E1. Add Investigation Note

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}/notes` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "content": "Customer shows structuring pattern across 3 accounts...", "note_type": "investigation_finding" }` |
| **Response** | `{ "note_id": "uuid", "case_id": "...", "content": "...", "note_type": "investigation_finding", "created_by": "current_user", "created_at": "..." }` |
| **Frontend fn** | `addCaseNote(caseId, data)` |

### E2. Get Case Notes

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}/notes` |
| **Auth**    | JWT (any) |
| **Response** | `{ "notes": [...], "total": 5 }` |
| **Frontend fn** | `getCaseNotes(caseId)` |

### E3. Attach Evidence

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}/evidence` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "filename": "bank_statement_jan2024.pdf", "file_type": "pdf", "description": "Bank statement showing structuring pattern" }` |
| **Response** | `{ "evidence_id": "uuid", "case_id": "...", "filename": "...", "file_type": "pdf", "description": "...", "uploaded_by": "current_user", "uploaded_at": "...", "file_size": ..., "checksum": "sha256:..." }` |
| **Frontend fn** | `attachEvidence(caseId, data)` |

### E4. Network Analytics — Detect Circular Transfers

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8007/api/v1/network/detect/circular-transfers` |
| **Auth**    | JWT (ANALYST, SENIOR_ANALYST, INVESTIGATOR, ADMIN) |
| **Query params** | `max_depth` (2-10, default 5) |
| **Response** | `{ "circular_transfers": [...], "total": 3 }` |
| **Frontend fn** | `getCircularTransfers()` |

### E5. Network Analytics — Detect Fraud Clusters

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8007/api/v1/network/detect/clusters` |
| **Auth**    | JWT (ANALYST, SENIOR_ANALYST, INVESTIGATOR, ADMIN) |
| **Query params** | `min_connections` (≥2, default 3) |
| **Response** | `{ "clusters": [...], "total": 2 }` |
| **Frontend fn** | `getFraudRings()` |

### E6. Network Analytics — Customer Network Graph

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8007/api/v1/network/customer/{customer_id}/network` |
| **Auth**    | JWT (any) |
| **Query params** | `depth` (1-4, default 2) |
| **Response** | `{ "customer_id": "...", "nodes": [...], "edges": [...], "stats": {...} }` |
| **Frontend fn** | `getCustomerNetwork(customerId)` |

### E7. Network Analytics — Detect Shared Devices

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8007/api/v1/network/detect/shared-devices` |
| **Auth**    | JWT (ANALYST, SENIOR_ANALYST, INVESTIGATOR, ADMIN) |
| **Query params** | `min_customers` (≥2, default 2) |
| **Response** | `{ "shared_devices": [...], "total": 5 }` |

### E8. Network Analytics — Detect Shared IPs

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8007/api/v1/network/detect/shared-ips` |
| **Auth**    | JWT (ANALYST, SENIOR_ANALYST, INVESTIGATOR, ADMIN) |
| **Query params** | `min_customers` (≥2, default 2) |
| **Response** | `{ "shared_ips": [...], "total": 8 }` |

### E9. PEP Screening

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/cdd-edd/screen/pep` |
| **Direct path** | `http://localhost:8003/api/v1/sanctions/screen/pep` |
| **Request Body** | `{ "name": "...", "country": "...", "date_of_birth": "..." }` |
| **Response** | PEP match results with risk score |

### E10. Adverse Media Screening

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/cdd-edd/screen/adverse-media` |
| **Direct path** | `http://localhost:8003/api/v1/sanctions/screen/adverse-media` |
| **Request Body** | `{ "name": "...", "keywords": [...] }` |
| **Response** | Adverse media matches and risk assessment |

### E11. AI/ML — XAI Explain Decision

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/aiml/xai/explain` |
| **Request Body** | `{ "prediction_id": "...", "model_id": "..." }` |
| **Response** | SHAP/LIME explanation of model decision, feature contributions |

---

## Step F — Escalate to Senior Analyst

**Purpose:** Escalate alert and/or case for senior review.

### F1. Escalate Alert

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8005/api/v1/alerts/{alert_id}/escalate` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "reason": "Multiple rule triggers and high-risk country involvement" }` |
| **Response** | Alert with `status: "escalated"`, `escalation_reason` set, `escalated_at` timestamp |
| **Frontend fn** | `escalateAlert(alertId, data)` |

### F2. Escalate Case

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}/escalate` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "reason": "Structuring pattern confirmed, SAR recommended" }` |
| **Response** | Case with `status: "escalated"`, `escalation_reason` set, `escalated_at` timestamp |
| **Frontend fn** | `escalateCase(caseId, data)` |

---

## Step G — SAR Filing with FinCEN

**Purpose:** Generate, review, approve, and file a Suspicious Activity Report.

### G1. Generate SAR Draft (Case Management)

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}/generate-sar` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "suspicious_activity_type": "structuring", "amount_involved": 125000.00, "activity_start_date": "2024-01-01", "activity_end_date": "2024-03-15", "narrative": "Customer conducted 47 cash deposits between $8,000-$9,500 across 3 branches over 10 weeks..." }` |
| **Response** | `{ "sar_id": "uuid", "case_id": "...", "status": "draft", "suspicious_activity_type": "structuring", "amount_involved": 125000, "narrative": "...", "generated_at": "..." }` |
| **Frontend fn** | `generateSAR(caseId, data)` |

### G2. Create SAR (Regulatory Reporting)

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/sar` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, SENIOR_ANALYST, ADMIN) |
| **Request Body** | `{ "case_id": "...", "customer_id": "...", "filing_type": "initial", "suspicious_activity_type": "structuring", "amount_involved": 125000.00, "activity_start_date": "2024-01-01", "activity_end_date": "2024-03-15", "narrative": "..." }` |
| **Response** | `{ "sar_id": "uuid", "case_id": "...", "customer_id": "...", "status": "draft", "created_at": "..." }` |
| **Frontend fn** | — (or `submitSAR` flow) |

### G3. List SARs

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/sar` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, SENIOR_ANALYST, ADMIN) |
| **Query params** | `status` (draft/pending_review/approved/filed), `customer_id`, `page`, `page_size` |
| **Response** | `{ "reports": [...], "total": 10 }` |
| **Frontend fn** | `getSARReports(params)` |

### G4. Get SAR Detail

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/sar/{sar_id}` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, SENIOR_ANALYST, ADMIN) |
| **Response** | Full SAR object |

### G5. Submit SAR for Review

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/sar/{sar_id}/submit` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Request Body** | (none) |
| **Response** | SAR with `status: "pending_review"` |
| **Frontend fn** | `submitSAR(sarId)` |

### G6. Approve SAR

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/sar/{sar_id}/approve` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Prerequisite** | SAR must be in `pending_review` status |
| **Response** | SAR with `status: "approved"` |
| **Frontend fn** | `approveSAR(sarId)` |

### G7. File SAR with FinCEN

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/sar/{sar_id}/file` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Prerequisite** | SAR must be in `approved` status |
| **Response** | `{ "sar_id": "...", "status": "filed", "filed_at": "...", "filing_reference": "BSA-XXXXXXXXXXXX" }` |
| **Frontend fn** | `fileSAR(sarId)` |

**SAR Status Flow:** `draft` → `pending_review` → `approved` → `filed`

### G8. Create CTR (Currency Transaction Report)

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/ctr` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ANALYST, ADMIN) |
| **Request Body** | `{ "transaction_id": "...", "customer_id": "...", "amount": 15000.00, "transaction_date": "2024-03-15" }` |
| **Response** | `{ "ctr_id": "uuid", "status": "draft", ... }` |
| **Frontend fn** | — |

### G9. List CTRs

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/ctr` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Query params** | `status`, `page`, `page_size` |
| **Response** | `{ "reports": [...], "total": ... }` |
| **Frontend fn** | `getCTRReports(params)` |

### G10. Reporting Stats

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8008/api/v1/reports/stats` |
| **Auth**    | JWT (any) |
| **Response** | `{ "total_sars": ..., "total_ctrs": ..., "sars_by_status": {...}, "ctrs_by_status": {...} }` |

---

## Step H — Case Closed with Full Audit Trail

**Purpose:** Close the alert and case with resolution, and maintain audit trail.

### H1. Close Alert

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8005/api/v1/alerts/{alert_id}/close` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "reason": "confirmed_suspicious" }` |
| **Valid reasons** | `false_positive`, `confirmed_suspicious`, `duplicate`, `insufficient_evidence` |
| **Response** | Alert with `status: "closed"`, `close_reason`, `closed_at` |
| **Frontend fn** | `closeAlert(alertId, data)` |

### H2. Close Case

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8006/api/v1/cases/{case_id}/close` |
| **Auth**    | JWT (any) |
| **Request Body** | `{ "resolution": "sar_filed" }` |
| **Valid resolutions** | `no_action`, `sar_filed`, `ctr_filed`, `false_positive`, `referred_to_law_enforcement` |
| **Response** | Case with `status: "closed"`, `resolution`, `closed_at` |
| **Frontend fn** | `closeCase(caseId, data)` |

### H3. Log Audit Event

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path (direct)** | `http://localhost:8011/api/v1/audit/log` |
| **Auth**    | None (internal service call) |
| **Request Body** | `{ "user_id": "...", "username": "...", "action": "case_closed", "resource_type": "case", "resource_id": "case-uuid", "details": {"resolution": "sar_filed"}, "ip_address": "...", "service_name": "case-management", "status": "success" }` |
| **Response** | `{ "event_id": "uuid", "user_id": "...", "action": "case_closed", "timestamp": "..." }` |

### H4. Search Audit Logs

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8011/api/v1/audit/logs` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Query params** | `user_id`, `action`, `resource_type`, `resource_id`, `service_name`, `start_date`, `end_date`, `page`, `page_size` |
| **Response** | `{ "logs": [ { "event_id": "...", "user_id": "...", "action": "...", "resource_type": "...", "resource_id": "...", "details": {...}, "timestamp": "..." } ], "pagination": { "page": 1, "page_size": 50, "total": 230 } }` |
| **Frontend fn** | `getAuditLogs(params)` |

### H5. User Audit Trail

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8011/api/v1/audit/logs/user/{user_id}` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Response** | `{ "user_id": "...", "logs": [...], "total": 45 }` |

### H6. Resource Audit Trail

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8011/api/v1/audit/logs/resource/{resource_type}/{resource_id}` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Response** | `{ "resource_type": "case", "resource_id": "case-uuid", "logs": [...], "total": 12 }` |

### H7. Audit Stats

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path (direct)** | `http://localhost:8011/api/v1/audit/stats` |
| **Auth**    | JWT (COMPLIANCE_OFFICER, ADMIN) |
| **Response** | `{ "total_events": ..., "by_action": {...}, "by_resource_type": {...}, "by_service": {...}, "by_status": {...} }` |

### H8. ActOne — Audit Trail

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/actone/audit` |
| **Auth**    | JWT |
| **Response** | ActOne-specific audit trail with case state transitions |

### H9. ActOne — State Machine

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Gateway path** | `http://localhost:8000/api/admin/data-sources/actone/state-machine` |
| **Auth**    | JWT |
| **Response** | Complete case lifecycle state machine definition with transitions |

---

## Cross-Cutting: Authentication

### Auth — Login

| Field       | Value |
|-------------|-------|
| **Method**  | `POST` |
| **Path**    | `http://localhost:8000/api/auth/login` |
| **Request Body** | `{ "username": "admin", "password": "admin123" }` |
| **Response** | `{ "access_token": "eyJ...", "token_type": "bearer", "user": { "user_id": "...", "username": "admin", "role": "ADMIN", "full_name": "..." } }` |
| **Frontend fn** | `login(credentials)` |

**Demo users:** `admin/admin123` (ADMIN), `analyst/analyst123` (ANALYST), `senior/senior123` (SENIOR_ANALYST), `investigator/invest123` (INVESTIGATOR), `compliance/comply123` (COMPLIANCE_OFFICER), `manager/manage123` (MANAGER)

### Auth — Get Current User

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path**    | `http://localhost:8000/api/auth/me` |
| **Auth**    | JWT Bearer |
| **Response** | Current user profile |
| **Frontend fn** | `getCurrentUser()` |

### Services Status

| Field       | Value |
|-------------|-------|
| **Method**  | `GET` |
| **Path**    | `http://localhost:8000/api/services/status` |
| **Auth**    | JWT Bearer |
| **Response** | Health status of all 11 microservices |
| **Frontend fn** | `getServiceStatus()` |

---

## Cross-Cutting: Gateway Admin / CAPABILITY_TESTS

The gateway offers **18 capability tests** (invoked via `POST /api/admin/data-sources/verify-capabilities`):

| Capability ID  | Name                              | Category          |
|----------------|-----------------------------------|--------------------|
| CAP-RT-001     | Real-Time Transaction Monitoring  | Transaction Monitoring |
| CAP-BATCH-001  | Batch/Retrospective Analysis      | Transaction Monitoring |
| CAP-SCN-001    | Scenario-Based Detection          | Transaction Monitoring |
| CAP-BEH-001    | Behavioral Analytics              | Risk Scoring       |
| CAP-THR-001    | Threshold Management              | Configuration      |
| CAP-AIML-001   | AI/ML Model Integration           | AI/ML              |
| CAP-XCHAN-001  | Cross-Channel Monitoring          | Transaction Monitoring |
| CAP-RISK-001   | Customer Risk Scoring             | Risk Scoring       |
| CAP-ALERT-001  | Alert Prioritization              | Alert Management   |
| CAP-WLF-001    | Watch List Filtering              | Sanctions          |
| CAP-CDD-001    | CDD/EDD Process                   | KYC                |
| CAP-EFM-001    | Enterprise Fraud Management       | Fraud Detection    |
| CAP-DBF-001    | Digital Banking Fraud             | Fraud Detection    |
| CAP-PMF-001    | Payment & Messaging Fraud         | Fraud Detection    |
| CAP-KYC-001    | KYC Lifecycle Management          | KYC                |
| CAP-ACTONE-001 | ActOne Case Management            | Case Management    |
| CAP-AIML-002   | AI/ML Analytics & Risk Scoring    | AI/ML              |

---

## Frontend API Function → Endpoint Map (Investigation Dashboard)

| Frontend Function          | HTTP Method | Endpoint Path                                     | Step |
|----------------------------|-------------|---------------------------------------------------|------|
| `login()`                  | POST        | /api/auth/login                                   | Auth |
| `getCurrentUser()`         | GET         | /api/auth/me                                      | Auth |
| `getAlerts()`              | GET         | /api/alerts                                       | C    |
| `getAlert(id)`             | GET         | /api/alerts/{id}                                  | C    |
| `updateAlert(id, data)`    | PUT         | /api/alerts/{id}                                  | C    |
| `assignAlert(id, data)`    | POST        | /api/alerts/{id}/assign                           | C    |
| `escalateAlert(id, data)`  | POST        | /api/alerts/{id}/escalate                         | F    |
| `closeAlert(id, data)`     | POST        | /api/alerts/{id}/close                            | H    |
| `getAlertStats()`          | GET         | /api/alerts/stats                                 | C    |
| `createCase(data)`         | POST        | /api/cases                                        | D    |
| `getCases()`               | GET         | /api/cases                                        | D    |
| `getCase(id)`              | GET         | /api/cases/{id}                                   | D    |
| `updateCase(id, data)`     | PUT         | /api/cases/{id}                                   | D    |
| `addCaseNote(id, data)`    | POST        | /api/cases/{id}/notes                             | E    |
| `getCaseNotes(id)`         | GET         | /api/cases/{id}/notes                             | E    |
| `attachEvidence(id, data)` | POST        | /api/cases/{id}/evidence                          | E    |
| `escalateCase(id, data)`   | POST        | /api/cases/{id}/escalate                          | F    |
| `closeCase(id, data)`      | POST        | /api/cases/{id}/close                             | H    |
| `generateSAR(id, data)`    | POST        | /api/cases/{id}/generate-sar                      | G    |
| `getCaseStats()`           | GET         | /api/cases/stats                                  | D    |
| `screenSanctions(data)`    | POST        | /api/sanctions/screen                             | B    |
| `getSanctionsLists()`      | GET         | /api/sanctions/lists                              | B    |
| `getCustomerRisk(id)`      | GET         | /api/risk/customer/{id}                           | D    |
| `calculateRisk(data)`      | POST        | /api/risk/calculate                               | D    |
| `getFraudRings()`          | GET         | /api/network/fraud-rings                          | E    |
| `getCustomerNetwork(id)`   | GET         | /api/network/customer/{id}                        | E    |
| `getCircularTransfers()`   | GET         | /api/network/circular-transfers                   | E    |
| `getSharedDevices()`       | GET         | /api/network/shared-devices                       | E    |
| `getSARReports()`          | GET         | /api/reports/sar                                  | G    |
| `getCTRReports()`          | GET         | /api/reports/ctr                                  | G    |
| `submitSAR(id)`            | POST        | /api/reports/sar/{id}/submit                      | G    |
| `approveSAR(id)`           | POST        | /api/reports/sar/{id}/approve                     | G    |
| `fileSAR(id)`              | POST        | /api/reports/sar/{id}/file                        | G    |
| `getAuditLogs()`           | GET         | /api/audit/logs                                   | H    |
| `getAuditStats()`          | GET         | /api/audit/stats                                  | H    |
| `getServiceStatus()`       | GET         | /api/services/status                              | —    |
| `getCompositeScore(id)`    | POST        | /api/ml/composite-score                           | B    |
| `getMLModels()`            | GET         | /api/ml/models                                    | B    |

---

## Complete Endpoint Count by Service

| Service                 | Endpoints | Port  |
|-------------------------|-----------|-------|
| API Gateway (own)       | 79        | 8000  |
| Transaction Monitoring  | 4         | 8001  |
| Fraud Detection         | 22        | 8002  |
| Sanctions Screening     | 13        | 8003  |
| Customer Risk Scoring   | 27        | 8004  |
| Alert Management        | 7         | 8005  |
| Case Management         | 13        | 8006  |
| Network Analytics       | 7         | 8007  |
| Regulatory Reporting    | 9         | 8008  |
| AI/ML Scoring           | 3         | 8009  |
| Data Integration        | 5         | 8010  |
| Audit Logging           | 5         | 8011  |
| **Total**               | **194**   |       |
