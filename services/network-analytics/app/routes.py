"""API routes for Network Analytics service."""

from fastapi import APIRouter, Depends, Request, Query

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles

router = APIRouter()


@router.post("/setup")
async def setup_graph_schema(
    request: Request,
    _user=Depends(require_roles(UserRole.ADMIN)),
):
    """Initialize Neo4j schema with constraints and indexes."""
    engine = request.app.state.graph_engine
    result = await engine.setup_schema()
    return result


@router.post("/ingest")
async def ingest_transaction(
    txn: dict,
    request: Request,
    _user=Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
):
    """Ingest a transaction into the graph database."""
    engine = request.app.state.graph_engine
    result = await engine.ingest_transaction(txn)
    return result


@router.get("/detect/shared-devices")
async def detect_shared_devices(
    request: Request,
    min_customers: int = Query(2, ge=2),
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Detect devices shared by multiple customers."""
    engine = request.app.state.graph_engine
    results = await engine.detect_shared_devices(min_customers)
    return {"shared_devices": results, "total": len(results)}


@router.get("/detect/shared-ips")
async def detect_shared_ips(
    request: Request,
    min_customers: int = Query(2, ge=2),
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Detect IP addresses shared by multiple customers."""
    engine = request.app.state.graph_engine
    results = await engine.detect_shared_ips(min_customers)
    return {"shared_ips": results, "total": len(results)}


@router.get("/detect/circular-transfers")
async def detect_circular_transfers(
    request: Request,
    max_depth: int = Query(5, ge=2, le=10),
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Detect circular money transfer patterns indicating layering."""
    engine = request.app.state.graph_engine
    results = await engine.detect_circular_transfers(max_depth)
    return {"circular_transfers": results, "total": len(results)}


@router.get("/detect/clusters")
async def detect_fraud_clusters(
    request: Request,
    min_connections: int = Query(3, ge=2),
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Detect suspicious entity clusters (potential fraud rings)."""
    engine = request.app.state.graph_engine
    results = await engine.detect_fraud_clusters(min_connections)
    return {"clusters": results, "total": len(results)}


@router.get("/customer/{customer_id}/network")
async def get_customer_network(
    customer_id: str,
    request: Request,
    depth: int = Query(2, ge=1, le=4),
    _user=Depends(get_current_user),
):
    """Get the full network graph for a customer."""
    engine = request.app.state.graph_engine
    result = await engine.get_customer_network(customer_id, depth)
    return result
