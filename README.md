# Actimize - Financial Crime Detection Platform

A production-grade Financial Crime Detection platform supporting AML monitoring, fraud detection, sanctions screening, and regulatory reporting for banks and financial institutions.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                            │
│                     JWT Auth / Rate Limiting / RBAC                     │
└──────────┬──────────────────────────────────────────────────────────────┘
           │
    ┌──────┴──────────────────────────────────────────────────────┐
    │                    Apache Kafka Event Bus                    │
    │  Topics: transactions, alerts, cases, audit, risk-scores    │
    └──────┬──────────────────────────────────────────────────────┘
           │
    ┌──────┼──────────┬──────────┬──────────┬──────────┬─────────┐
    │      │          │          │          │          │         │
┌───▼──┐┌──▼───┐┌────▼──┐┌─────▼──┐┌─────▼──┐┌─────▼──┐┌─────▼──┐
│ TXN  ││FRAUD ││SANCT- ││CUST   ││ALERT  ││CASE   ││NETWORK│
│ MON  ││DET   ││IONS   ││RISK   ││MGMT   ││MGMT   ││ANALYT │
│ENGINE││ENGINE││SCREEN ││SCORE  ││SYSTEM ││PLATFRM││ICS    │
└──┬───┘└──┬───┘└──┬────┘└──┬────┘└──┬────┘└──┬────┘└──┬────┘
   │       │       │        │        │        │        │
   │  ┌────▼───┐   │   ┌────▼───┐   │   ┌────▼───┐   │
   │  │AI/ML   │   │   │REG     │   │   │AUDIT   │   │
   │  │SCORING │   │   │REPORT  │   │   │LOGGING │   │
   │  └────────┘   │   └────────┘   │   └────────┘   │
   │               │                │                 │
┌──▼───────────────▼────────────────▼─────────────────▼──┐
│              Data Integration Layer                      │
│    (Core Banking, Cards, Payments, KYC, Sanctions)      │
└──┬───────────────┬────────────────┬─────────────────┬──┘
   │               │                │                 │
┌──▼──┐      ┌─────▼──┐      ┌─────▼──┐        ┌─────▼──┐
│Postgres│   │Elastic │      │Neo4j   │        │Redis   │
│(OLTP) │   │Search  │      │(Graph) │        │(Cache) │
└───────┘   └────────┘      └────────┘        └────────┘
```

## Modules

| Module | Service | Port | Description |
|--------|---------|------|-------------|
| Transaction Monitoring | `transaction-monitoring` | 8001 | Real-time transaction analysis via AML rules |
| Fraud Detection | `fraud-detection` | 8002 | ML-based fraud pattern detection |
| Sanctions Screening | `sanctions-screening` | 8003 | Watchlist & sanctions list matching |
| Customer Risk Scoring | `customer-risk-scoring` | 8004 | KYC/CDD risk profiling |
| Alert Management | `alert-management` | 8005 | Alert lifecycle management |
| Case Management | `case-management` | 8006 | Investigation workflow management |
| Network Analytics | `network-analytics` | 8007 | Graph-based fraud ring detection |
| Regulatory Reporting | `regulatory-reporting` | 8008 | SAR/CTR report generation |
| AI/ML Risk Scoring | `ai-ml-scoring` | 8009 | ML model serving for risk scores |
| Data Integration | `data-integration` | 8010 | External data source connectors |
| Audit Logging | `audit-logging` | 8011 | Compliance audit trail |
| API Gateway | `api-gateway` | 8000 | Auth, routing, rate limiting |
| Investigation Dashboard | `frontend` | 3000 | React-based investigator UI |

## Tech Stack

- **Backend**: Python FastAPI
- **Event Streaming**: Apache Kafka
- **Databases**: PostgreSQL, Elasticsearch, Neo4j, Redis
- **AI/ML**: Scikit-learn, TensorFlow
- **Rule Engine**: Custom Python rule engine (Drools-compatible DSL)
- **Frontend**: React + Material UI
- **Infrastructure**: Docker, Kubernetes

## Quick Start

```bash
# Clone and start all services
docker-compose up -d

# Or run individual services
cd services/transaction-monitoring
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Start frontend
cd frontend/investigation-dashboard
npm install
npm start
```

## Data Flow

1. **Ingest** → Transactions arrive via Kafka from core banking, cards, payments
2. **Monitor** → Transaction Monitoring applies AML rules (structuring, large cash, high-risk countries)
3. **Detect** → Fraud Detection runs ML models for anomaly detection
4. **Score** → AI/ML engine generates composite risk score
5. **Alert** → Scores exceeding thresholds generate alerts
6. **Investigate** → Alerts enter investigation queue in Case Management
7. **Report** → Confirmed suspicious activity generates regulatory reports (SAR/CTR)

## Security

- JWT-based API authentication
- Role-Based Access Control (RBAC)
- AES-256 encryption for sensitive data
- Complete audit trail logging
- API rate limiting
