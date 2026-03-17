# SentinelFC — User Manual

**Financial Crime Investigation Platform**
Version 1.0 | March 2026

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Login & Authentication](#2-login--authentication)
3. [Dashboard](#3-dashboard)
4. [Alert Management](#4-alert-management)
5. [Case Management](#5-case-management)
6. [Network Analytics](#6-network-analytics)
7. [Sanctions Screening](#7-sanctions-screening)
8. [Regulatory Reports](#8-regulatory-reports)
9. [Audit Logs](#9-audit-logs)
10. [AML Module](#10-aml-module)
11. [Fraud Management](#11-fraud-management)
12. [KYC / CDD Module](#12-kyc--cdd-module)
13. [ActOne Investigation Hub](#13-actone-investigation-hub)
14. [AI/ML Analytics](#14-aiml-analytics)
15. [Data Sources (Admin)](#15-data-sources-admin)
16. [Key Workflows](#16-key-workflows)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Getting Started

### 1.1 Accessing the Platform

Open your web browser and navigate to the SentinelFC URL:

| Environment | URL |
|---|---|
| Local (Development) | `http://localhost:3000` |
| EC2 (Production) | `http://<ec2-ip>:3001` |

### 1.2 System Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- JavaScript enabled
- Minimum screen resolution: 1280 × 720

### 1.3 Navigation Overview

The platform uses a **left sidebar** navigation with three sections:

**Main:**
| Menu Item | Description |
|---|---|
| Dashboard | Executive overview with KPIs and charts |
| Alerts | Alert queue — view, filter, assign, escalate |
| Cases | Investigation cases — create, manage, close |
| Network Analytics | Fraud ring detection, shared devices, circular transfers |
| Sanctions Screening | Entity screening against watchlists (OFAC, UN, EU) |
| Regulatory Reports | SAR and CTR report management & filing |
| Audit Logs | System-wide audit trail |

**Financial Crime:**
| Menu Item | Description |
|---|---|
| AML | Anti-Money Laundering capabilities and CDD/EDD |
| Fraud Management | Enterprise, Digital Banking, and Payments fraud engines |
| KYC / CDD | Customer onboarding, reviews, trigger events |
| ActOne | Unified investigation hub with scenarios |
| AI/ML Analytics | ML models, predictions, risk scoring, explainability |

**Administration:**
| Menu Item | Description |
|---|---|
| Data Sources | Manage 16+ data source connections and field mappings |

The **top bar** displays the page title, your current role badge, and a user avatar menu for logging out.

---

## 2. Login & Authentication

### 2.1 Logging In

1. Navigate to the platform URL. You will see the **SentinelFC** login page.
2. Enter your **Username** and **Password**.
3. Click **Sign In**.

### 2.2 Demo Users

The following demo accounts are available:

| Username | Role | Department |
|---|---|---|
| `admin` | Administrator | IT |
| `analyst1` | Analyst | AML Operations |
| `senior_analyst` | Senior Analyst | AML Operations |
| `investigator` | Investigator | Financial Crime |
| `compliance_officer` | Compliance Officer | Compliance |
| `manager` | Manager | AML Operations |

> **Demo Mode:** Any non-empty password is accepted (e.g., `admin123`, `analyst123`).

### 2.3 Session Management

- Sessions last **60 minutes** after login.
- If your session expires, you will be automatically redirected to the login page.
- To log out manually, click your **avatar** in the top-right corner and select **Logout**.

---

## 3. Dashboard

The Dashboard provides an executive overview of your financial crime operations.

### 3.1 Key Performance Indicators (KPIs)

Four stat cards are displayed at the top:

| KPI | Color | Description |
|---|---|---|
| **Open Alerts** | Orange | Count of alerts with status `new` or `open` |
| **Critical Alerts** | Red | Alerts with severity `critical` or risk score ≥ 90 |
| **Open Cases** | Blue | Cases with status `open` or `in_progress` |
| **Resolved** | Green | Count of closed alerts |

### 3.2 Charts

- **Alert & Case Trend (7 Days)** — Line chart showing daily alert and case volumes
- **Alerts by Severity** — Pie chart showing critical / high / medium / low distribution
- **Alerts by Type** — Bar chart showing AML / Fraud / Sanctions / Network breakdown
- **Service Health** — Status indicators for all 11 microservices (green = healthy, red = down)

---

## 4. Alert Management

### 4.1 Alert Queue (`Alerts` in sidebar)

The Alert Queue displays all financial crime alerts in a filterable data grid.

**Filters** (top of page):

| Filter | Options |
|---|---|
| Status | All, New, Open, Assigned, Escalated, Closed |
| Severity | All, Critical, High, Medium, Low |
| Type | All, AML, Fraud, Sanctions, Network |

**Grid Columns:**

| Column | Description |
|---|---|
| Alert ID | Unique alert identifier |
| Type | Alert category (AML, Fraud, etc.) |
| Severity | Color-coded chip (Critical=red, High=orange, Medium=blue, Low=green) |
| Status | Current status chip |
| Risk Score | Numeric risk score |
| Customer | Associated customer ID |
| Created | Timestamp of alert creation |
| Actions | Click the 👁 eye icon to view details |

**Pagination:** Choose 10, 25, or 50 rows per page.

### 4.2 Alert Detail

Click any alert's eye icon to open its detail view.

**Left Panel — Alert Information:**
- Alert ID, Type, Status, Risk Score, Customer ID, Created Date, Assigned To, Description
- **Triggered Rules** section showing which detection rules flagged this alert

**Right Panel — Actions:**

| Action | Button | What It Does |
|---|---|---|
| **Assign** | Outlined | Assign the alert to an analyst (enter Analyst ID) |
| **Escalate** | Warning (yellow) | Escalate for senior review (enter reason) |
| **Close** | Success (green) | Close the alert with resolution notes |
| **Create Case** | Primary (blue) | Creates a new investigation case linked to this alert |

> **Note:** All action buttons are disabled once an alert is `Closed`.

---

## 5. Case Management

### 5.1 Case List (`Cases` in sidebar)

**Creating a New Case:**
1. Click the **"New Case"** button in the top-right corner.
2. Fill in:
   - **Title** (required)
   - **Description** (multiline)
   - **Priority** (Critical / High / Medium / Low)
3. Click **Create**.

**Filters:**

| Filter | Options |
|---|---|
| Status | All, Open, In Progress, Escalated, Closed |
| Priority | All, Critical, High, Medium, Low |

**Grid Columns:** Case ID, Title, Status, Priority, Assigned To, Created, Actions (eye icon).

### 5.2 Case Detail

Click any case's eye icon to open the investigation workspace.

**Left Panel:**
- **Case Info**: Case ID, Title, Status, Priority, Assigned To, Created, Description
- **Linked Alerts**: Clickable chips that navigate to the corresponding alert details
- **Investigation Notes**: Chronological list of notes with author and timestamp

**Right Panel — Actions:**

| Action | Description |
|---|---|
| **Add Note** | Add an investigation note to the case timeline |
| **Escalate** | Escalate the case for senior review (enter reason) |
| **Close Case** | Close the case with resolution notes |
| **Generate SAR** | Create a Suspicious Activity Report from this case |

> **Tip:** Use **Add Note** frequently to document your investigation steps for audit purposes.

---

## 6. Network Analytics

### 6.1 Overview

Network Analytics detects complex financial crime patterns across entity networks. Access via **Network Analytics** in the sidebar.

### 6.2 Fraud Rings Tab

Displays detected fraud ring clusters:
- **Cluster Number** and **Risk Score** (color-coded chip)
- **Member Count** and individual **Member ID** chips
- **Total Transaction Amount** involved in the ring

### 6.3 Shared Devices Tab

Identifies accounts sharing devices or IP addresses:

| Column | Description |
|---|---|
| Device / IP | The shared device identifier or IP address |
| Accounts | Chips showing all accounts using this device |
| Risk Level | High (red) or Medium (orange) |

### 6.4 Circular Transfers Tab

Detects circular money flows:
- **Transfer Path**: Visual chip chain showing the flow (Account A → B → C → A)
- **Total Amount**: Sum of transfers in the circular pattern

---

## 7. Sanctions Screening

### 7.1 Screening an Entity

1. Navigate to **Sanctions Screening** in the sidebar.
2. Enter the **Name** to screen (required).
3. Select **Entity Type**: Individual, Organization, or Vessel.
4. Optionally enter a **Country**.
5. Click **Screen** (or press Enter).

### 7.2 Understanding Results

- **Green "No Matches" banner**: The entity is clear against all watchlists.
- **Red "X Match(es) Found" banner**: Potential hits were detected.

**Match Table Columns:**

| Column | Description |
|---|---|
| Name | Watchlist entity name |
| Source | Which list (OFAC SDN, UN, EU, etc.) |
| Score | Match confidence percentage (red ≥ 90%, orange ≥ 70%, green < 70%) |
| Country | Country associated with the sanctioned entity |
| Programs | Applicable sanctions programs (as chips) |

---

## 8. Regulatory Reports

### 8.1 SAR Reports Tab

View and manage Suspicious Activity Reports.

**Table Columns:** Report ID, Case ID, Subject Name, Status, Filing Date.

**SAR Status Workflow:**

| Current Status | Available Action | Next Status |
|---|---|---|
| `draft` | **Submit for Review** (send icon) | `pending_review` |
| `pending_review` | **Approve** (check icon) | `approved` |
| `approved` | **File with FinCEN** (file button) | `filed` |
| `filed` | — (no further action) | — |

**How to Generate a SAR:**
1. Go to **Cases** → Open a case.
2. Click **Generate SAR** in the case detail view.
3. The SAR appears in the **SAR Reports** tab with status `draft`.

### 8.2 CTR Reports Tab

View Currency Transaction Reports (transactions over $10,000).

**Table Columns:** Report ID, Customer Name, Amount, Transaction Date, Status.

> **Note:** CTR reports are automatically filed and are display-only.

---

## 9. Audit Logs

### 9.1 Viewing Audit Logs

Navigate to **Audit Logs** in the sidebar to view the system-wide audit trail.

**Filters:**

| Filter | Options |
|---|---|
| Action | All, Login, View, Create, Update, Delete, Assign, Escalate, Close |
| Service | All, API Gateway, Alert Management, Case Management, Transaction Monitoring, Fraud Detection, Sanctions Screening |
| User ID | Free text search for specific user |

**Grid Columns:** Timestamp, User, Action, Resource, Resource ID, Service, IP Address, Details.

> **Compliance Tip:** Audit logs capture every significant action across the platform — use the User ID filter to review an individual's activity.

---

## 10. AML Module

### 10.1 Key Capabilities Tab

Displays a verification dashboard of all AML platform capabilities with pass/fail indicators per category.

### 10.2 CDD / EDD Tab

- **Customer Due Diligence (CDD)**: View customer profiles, check overdue KYC reviews, manage EDD workflows.
- **PEP Screening**: Screen customers against Politically Exposed Persons lists.
- **Adverse Media Screening**: Check customers against negative media sources.

### 10.3 Watchlist Filtering (WLF) Tab

- **Payment Screening**: Screen individual payments against watchlists.
- **Batch Screening**: Process bulk screening requests.
- **Name Screening**: Screen customer names against all active lists.
- **Alert Management**: Manage WLF alerts, groups, and statistics.

---

## 11. Fraud Management

### 11.1 Enterprise Fraud Management (EFM)

Run fraud detection simulations:
- Account Takeover, Mule Account Detection, Card Fraud, Device Fraud, Biometrics Fraud, Payment Fraud, Cross-Channel Fraud

### 11.2 Digital Banking Fraud (DBF)

Simulations for digital channel threats:
- Login Anomaly, Session Hijack, Bot Detection, Social Engineering

### 11.3 Payments Fraud (PMF)

Simulations for payment-specific fraud:
- ACH Fraud, Wire Fraud, RTP/Zelle Fraud, Card Not Present (CNP), Check Fraud

> Each simulation displays engine details, detection results, risk scores, and recommended actions.

---

## 12. KYC / CDD Module

### 12.1 KYC Dashboard

KPI overview: Total KYC Cases, Active, Refresh Due, In Progress, Trigger Events. Includes status and risk distribution charts.

### 12.2 Onboarding

**Creating a New Onboarding:**
1. Click **"New Onboarding"**.
2. Fill in: Customer ID, Type (Individual/Corporate/Business/Trust), First Name, Last Name, Country, PEP Status, Annual Income, Age.
3. Click **Submit**.
4. The system determines: CDD Level (SDD/CDD/EDD), required documents, risk indicators, and onboarding checklist.

**CDD Levels:**
| Level | Description |
|---|---|
| SDD | Simplified Due Diligence — low-risk customers |
| CDD | Customer Due Diligence — standard risk |
| EDD | Enhanced Due Diligence — high-risk customers (PEP, high-risk country, high income) |

### 12.3 Periodic Reviews

Automated review scheduling based on risk level:

| Risk Level | Review Frequency |
|---|---|
| Critical | Every 30 days |
| High | Every 90 days |
| Medium | Every 365 days (annual) |
| Low | Every 1,095 days (3 years) |

Reviews are color-coded: **Red** = overdue, **Orange** = due within 30 days, **Blue** = due within 90 days.

### 12.4 Trigger Events

Events that may require an immediate or accelerated review:

| Event Type | Severity |
|---|---|
| Sanctions Hit | Critical |
| Adverse Media | Critical |
| PEP Status Change | High |
| Unusual Activity | High |
| Large Transaction | Medium |
| Account Dormancy Reactivation | Medium |
| Country Risk Change | High |
| Customer Info Change | Low |
| Regulatory Request | High |
| Law Enforcement Request | Critical |

**To Simulate a Trigger Event:**
1. Click **"Simulate Trigger"**.
2. Enter Customer ID and select Event Type.
3. The system auto-classifies severity and determines the required action.

### 12.5 Integrations

Sync KYC data with external systems:
- **CRM System** — Customer relationship data
- **Core Banking** — Account and balance data
- **Digital Onboarding Platform** — Digital identity verification

### 12.6 Status Machine

Visual reference of the 11-state KYC lifecycle:
```
initiated → pending_documents → documents_received → under_review →
approved / rejected / escalated → active → refresh_due →
refresh_in_progress → renewed / suspended / closed
```

---

## 13. ActOne Investigation Hub

### 13.1 KPI Dashboard

Executive metrics: Total Cases, SLA Breach Rate, SARs Filed, Average Resolution Time (hours). Includes distribution breakdowns by status, priority, and case type, plus an investigator workload table.

### 13.2 Alert Triage

Priority scoring formula:
- **Amount Risk** (30%) + **Customer Risk** (30%) + **PEP Flag** (20%) + **Sanctions Flag** (20%)

| Priority | Score Threshold | Response SLA | Resolution SLA |
|---|---|---|---|
| Critical | ≥ 0.80 | 4 hours | 24 hours |
| High | ≥ 0.60 | 24 hours | 72 hours |
| Medium | ≥ 0.40 | 72 hours | 168 hours (7 days) |
| Low | < 0.40 | 168 hours (7 days) | 720 hours (30 days) |

**To Triage an Alert:**
1. Click **"Triage Alert"**.
2. Enter: Alert ID, Alert Type, Amount, Customer Risk Score, PEP Status, Sanctions Flag.
3. The system calculates priority and creates an investigation case with SLA targets.

### 13.3 Cases Tab

View all investigation cases with: Case ID, Type (AML/Fraud/Surveillance), Status, Priority, Assignee, Title, Created date.

### 13.4 Customer 360 View

Comprehensive customer view:
1. Enter a **Customer ID** and click **Search**.
2. View: Customer Profile, Risk Profile, Accounts, Recent Alerts, Related Parties.

### 13.5 Scenarios

Three pre-built investigation scenarios you can run step-by-step:

**Scenario 1 — AML Alert Investigation:**
Suspicious transaction → Triage → Assign → Investigate → Gather Evidence → Customer 360 Review → Draft SAR → File SAR → Close Case

**Scenario 2 — Fraud Case (Account Takeover):**
Fraud alert → Triage → Assign → Freeze Account → Contact Customer → Collect Evidence → Close or Refer to Law Enforcement

**Scenario 3 — Trading Surveillance:**
Suspicious trade → Triage → Assign → Communication Review → Escalate → Approval → Regulatory Referral

### 13.6 Audit Trail

Case-level audit trail showing: Timestamp, Case ID, Action, Actor, Details (JSON).

---

## 14. AI/ML Analytics

### 14.1 Dashboard

Overview KPIs: Active Models, Total Features, Behavioral Profiles, Peer Groups, Anomaly Detection Methods, XAI Methods, Ingestion Jobs, Simulations.

### 14.2 Model Registry

View all machine learning models: Model ID, Name, Type, Framework, Status, Feature Count, Accuracy, AUC-ROC, False Positive Rate.

### 14.3 ML Predictions

1. Select prediction type: **AML** or **Fraud**.
2. Enter a transaction amount.
3. Click **Run Prediction**.
4. View: Risk Score, Risk Level, Confidence, and **SHAP Risk Drivers** (feature importance).

### 14.4 Behavioral Analytics

Update and analyze customer behavioral profiles:
1. Enter Customer ID.
2. Click **Update Profile**.
3. View: Observations count, Average Transaction, Risk Adjustment, Deviation Alerts (z-scores).

### 14.5 Peer Group Analysis

Compare a customer against their peer group:
1. Enter Customer ID.
2. Select Peer Group: Retail Banking, Small Business, Corporate, High Net Worth, MSB.
3. View: Z-Score, Peer Average, Anomaly Flags.

### 14.6 Anomaly Detection

Multi-method anomaly detection:
- **Isolation Forest**, **Autoencoder**, **Z-Score**, and **Ensemble** methods
- Batch results show per-method anomaly scores

### 14.7 Risk Scoring

Composite risk calculation with 6 configurable factors:

| Factor | Weight |
|---|---|
| Demographics Risk | Configurable |
| Transaction Risk | Configurable |
| Behavioral Risk | Configurable |
| Network Risk | Configurable |
| External Risk | Configurable |
| KYC Risk | Configurable |

### 14.8 Explainable AI (XAI)

- **SHAP Analysis**: Feature importance with direction indicators
- **Counterfactual Analysis**: "What would need to change to alter the outcome?"
- **Human-Readable Summary**: Plain-language risk explanation

### 14.9 Model Governance

Monitor model health: Accuracy trends, Population Stability Index (PSI), drift detection, retraining recommendations, compliance status, model risk tier, governance policies.

### 14.10 Data Ingestion

Run ingestion pipelines from: Transaction Feed, Customer Data, Watchlist, Market Data, External API. View: pipeline stages, data quality metrics, anomalies flagged.

### 14.11 Threshold Simulation

Tune alert thresholds:
- Adjust score threshold and view the confusion matrix
- Metrics: Precision, Recall, F1 Score, Alert Reduction %

---

## 15. Data Sources (Admin)

### 15.1 Connection Status

Monitor 16+ data source connections:

| Data Source | Type |
|---|---|
| Core Banking (T24) | Core Banking |
| Loan Origination System | Lending |
| Card Processing System | Payments |
| ATM Transaction Feed | ATM |
| SWIFT/Wire Transfer | Payments |
| ACH/NACHA Feed | Payments |
| Mobile Banking | Digital |
| Online Banking | Digital |
| Trade Finance System | Trade |
| Securities Trading | Trading |
| Treasury System | Treasury |
| Customer Master (CRM) | CRM |
| External Credit Bureau | External |
| OFAC/Sanctions Lists | Compliance |
| PEP Database | Compliance |
| Adverse Media Feed | Compliance |

Each shows: Connection status, latency, records/day, auth method, sync status.

### 15.2 Field Mappings

Map data source fields to the AML schema. View coverage progress bars and warnings for unmapped required fields.

### 15.3 Data Quality

Run ingestion tests across all sources. View: completeness percentage, timeliness SLA checks, error/warning counts per source.

---

## 16. Key Workflows

### 16.1 Alert-to-SAR Complete Lifecycle

```
1. Alert Generated (automatic)
2. Alert appears in queue (status: new)
3. Assign to analyst (status: assigned)
4. Investigate alert details
5. Escalate if needed (status: escalated)
6. Create Case from alert
7. Add investigation notes to case
8. Generate SAR from case (status: draft)
9. Submit SAR for review (status: pending_review)
10. Approve SAR (status: approved)
11. File SAR with FinCEN (status: filed)
12. Close case
```

### 16.2 KYC Onboarding Workflow

```
1. New Onboarding submitted
2. Risk assessment performed automatically
3. CDD Level determined (SDD / CDD / EDD)
4. Required documents identified
5. Onboarding checklist generated
6. Customer activated
7. Periodic review schedule set based on risk level
```

### 16.3 Trigger-Based Review

```
1. Trigger event detected (e.g., sanctions hit, adverse media)
2. Severity auto-classified (Critical / High / Medium / Low)
3. Action taken:
   - Critical → Immediate review initiated
   - High → Priority scheduling
   - Medium → Flagged for next scheduled review
   - Low → Noted for reference
```

### 16.4 Fraud Investigation

```
1. Fraud alert triggered by detection engine
2. Alert triaged and prioritized
3. Case created, analyst assigned
4. Account frozen (if needed)
5. Customer contacted for verification
6. Evidence collected and documented
7. Case closed or referred to law enforcement
```

---

## 17. Troubleshooting

### Common Issues

| Issue | Solution |
|---|---|
| **Login page won't load** | Verify the URL is correct. Check that the server is running. |
| **"Session Expired" message** | Your 60-minute session timed out. Log in again. |
| **No data on Dashboard** | The API gateway may be restarting. Wait 30 seconds and refresh. |
| **Actions disabled on alert/case** | The alert or case may be in `Closed` status. Closed items cannot be modified. |
| **Sanctions screening returns no results** | Verify the name spelling. Try variations or partial names. |
| **SAR "File with FinCEN" not available** | The SAR must be in `approved` status. Follow the workflow: Submit → Approve → File. |

### Browser Console Errors

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | JWT token expired | Log in again |
| `404 Not Found` | API endpoint missing | Contact administrator |
| `CORS policy blocked` | Frontend/API URL mismatch | Ensure frontend is served via nginx proxy |
| `Network Error` | Server unreachable | Check server status on Dashboard |

---

*SentinelFC — Financial Crime Investigation Platform*
*© 2026 SentinelFC. All rights reserved.*
