# Architecture Documentation

## System Architecture

### Microservices Architecture

The platform follows a microservices architecture where each domain module runs as an independent service. Services communicate via:

- **Synchronous**: REST APIs for request-response patterns
- **Asynchronous**: Apache Kafka for event-driven communication

### Service Communication Matrix

```
┌──────────────────┬─────────────────────────────────────────────────┐
│ Producer         │ Kafka Topics                                    │
├──────────────────┼─────────────────────────────────────────────────┤
│ Data Integration │ raw-transactions, customer-events                │
│ TXN Monitoring   │ aml-alerts, transaction-scored                   │
│ Fraud Detection  │ fraud-alerts, fraud-scores                       │
│ Sanctions Screen │ sanctions-alerts, screening-results              │
│ Customer Risk    │ risk-score-updates, kyc-events                   │
│ Alert Management │ alert-created, alert-updated, alert-escalated    │
│ Case Management  │ case-created, case-updated, case-closed          │
│ Network Analytics│ network-alerts, cluster-detected                 │
│ AI/ML Scoring    │ ml-scores, model-predictions                     │
│ Audit Logging    │ audit-events                                     │
└──────────────────┴─────────────────────────────────────────────────┘
```

### Database Strategy

| Database       | Purpose                           | Services Using It        |
|---------------|-----------------------------------|--------------------------|
| PostgreSQL    | Transactional data, cases, alerts | All core services        |
| Elasticsearch | Alert search, full-text indexing   | Alert Mgmt, Case Mgmt   |
| Neo4j         | Graph relationships, fraud rings  | Network Analytics        |
| Redis         | Caching, session, rate limiting   | API Gateway, all services|

### Event Streaming Design

```
Data Sources → Kafka Connect → Raw Topics → Processing Services → Enriched Topics → Alert/Case Services
                                    │
                                    ├── raw-transactions
                                    ├── raw-customer-data
                                    ├── raw-sanctions-lists
                                    └── raw-payment-events

Processing Pipeline:
  raw-transactions → transaction-monitoring → aml-alerts
  raw-transactions → fraud-detection → fraud-alerts
  raw-transactions → ai-ml-scoring → risk-scores
  raw-customer-data → customer-risk-scoring → risk-profiles
  raw-customer-data → sanctions-screening → sanctions-alerts
  *-alerts → alert-management → case-management → regulatory-reporting
```

### Security Architecture

```
Client → API Gateway (JWT Validation) → Service Mesh → Microservice
              │                              │
              ├── Rate Limiting               ├── mTLS between services
              ├── CORS Policy                 ├── Network Policies (K8s)
              └── Request Logging             └── Secret Management (K8s Secrets)
```

### Deployment Architecture

```
                    ┌─────────────────────────┐
                    │    Load Balancer         │
                    │   (Ingress Controller)   │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   Kubernetes Cluster     │
                    │                          │
                    │  ┌─── Namespace: actimize│
                    │  │                       │
                    │  │  ┌─── Services ──┐    │
                    │  │  │ 12 Pods       │    │
                    │  │  │ HPA enabled   │    │
                    │  │  └───────────────┘    │
                    │  │                       │
                    │  │  ┌─── Data ──────┐    │
                    │  │  │ PostgreSQL    │    │
                    │  │  │ Kafka Cluster │    │
                    │  │  │ Elasticsearch │    │
                    │  │  │ Neo4j         │    │
                    │  │  │ Redis         │    │
                    │  │  └───────────────┘    │
                    │  │                       │
                    │  │  ┌─── Monitoring ─┐   │
                    │  │  │ Prometheus     │   │
                    │  │  │ Grafana        │   │
                    │  │  │ ELK Stack      │   │
                    │  │  └───────────────┘   │
                    │  │                       │
                    │  └───────────────────────│
                    └──────────────────────────┘
```
