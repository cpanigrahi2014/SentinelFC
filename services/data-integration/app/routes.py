"""API routes for Data Integration service."""

import json
import logging
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter()


class DataSourceStatus(BaseModel):
    source_name: str
    source_type: str
    status: str = "active"
    last_sync: Optional[str] = None
    records_synced: int = 0


class TransactionIngestionRequest(BaseModel):
    source: str  # core_banking, card_system, payment_gateway, online_banking, mobile_banking
    transactions: list[dict]


class CustomerIngestionRequest(BaseModel):
    source: str  # kyc_database
    customers: list[dict]


class SanctionsListIngestionRequest(BaseModel):
    list_name: str  # OFAC, EU, UN
    entries: list[dict]


# Data source registry
DATA_SOURCES = [
    DataSourceStatus(source_name="Core Banking System", source_type="transaction", status="active", last_sync="2025-01-15T10:00:00Z", records_synced=1500000),
    DataSourceStatus(source_name="Card Transaction System", source_type="transaction", status="active", last_sync="2025-01-15T10:05:00Z", records_synced=850000),
    DataSourceStatus(source_name="Payment Gateway", source_type="transaction", status="active", last_sync="2025-01-15T10:02:00Z", records_synced=320000),
    DataSourceStatus(source_name="Online Banking", source_type="transaction", status="active", last_sync="2025-01-15T10:01:00Z", records_synced=420000),
    DataSourceStatus(source_name="Mobile Banking", source_type="transaction", status="active", last_sync="2025-01-15T10:03:00Z", records_synced=280000),
    DataSourceStatus(source_name="Customer KYC Database", source_type="customer", status="active", last_sync="2025-01-15T08:00:00Z", records_synced=250000),
    DataSourceStatus(source_name="OFAC Sanctions List", source_type="sanctions", status="active", last_sync="2025-01-14T00:00:00Z", records_synced=12500),
    DataSourceStatus(source_name="EU Sanctions List", source_type="sanctions", status="active", last_sync="2025-01-14T00:00:00Z", records_synced=8200),
    DataSourceStatus(source_name="PEP Database", source_type="pep", status="active", last_sync="2025-01-13T00:00:00Z", records_synced=35000),
    DataSourceStatus(source_name="Country Risk Data", source_type="reference", status="active", last_sync="2025-01-01T00:00:00Z", records_synced=250),
    DataSourceStatus(source_name="Adverse Media Feed", source_type="media", status="active", last_sync="2025-01-15T09:00:00Z", records_synced=5600),
]


@router.get("/sources")
async def list_data_sources(_user=Depends(get_current_user)):
    """List all configured data sources and their status."""
    return {
        "sources": [s.model_dump() for s in DATA_SOURCES],
        "total": len(DATA_SOURCES),
    }


@router.post("/ingest/transactions")
async def ingest_transactions(
    request: TransactionIngestionRequest,
    _user=Depends(require_roles(UserRole.ADMIN)),
):
    """Ingest transactions from external source into Kafka pipeline."""
    # In production, this would publish to Kafka topic "raw-transactions"
    return {
        "status": "accepted",
        "source": request.source,
        "transactions_received": len(request.transactions),
        "batch_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/ingest/customers")
async def ingest_customers(
    request: CustomerIngestionRequest,
    _user=Depends(require_roles(UserRole.ADMIN)),
):
    """Ingest customer data from KYC database."""
    return {
        "status": "accepted",
        "source": request.source,
        "customers_received": len(request.customers),
        "batch_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/ingest/sanctions")
async def ingest_sanctions_list(
    request: SanctionsListIngestionRequest,
    _user=Depends(require_roles(UserRole.ADMIN)),
):
    """Ingest sanctions list updates."""
    return {
        "status": "accepted",
        "list_name": request.list_name,
        "entries_received": len(request.entries),
        "batch_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stats")
async def integration_stats(_user=Depends(get_current_user)):
    """Get data integration statistics."""
    total_records = sum(s.records_synced for s in DATA_SOURCES)
    return {
        "total_sources": len(DATA_SOURCES),
        "active_sources": sum(1 for s in DATA_SOURCES if s.status == "active"),
        "total_records_synced": total_records,
        "by_type": {
            "transaction": sum(s.records_synced for s in DATA_SOURCES if s.source_type == "transaction"),
            "customer": sum(s.records_synced for s in DATA_SOURCES if s.source_type == "customer"),
            "sanctions": sum(s.records_synced for s in DATA_SOURCES if s.source_type == "sanctions"),
        },
    }
