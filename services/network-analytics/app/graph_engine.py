"""Graph analytics engine using Neo4j for fraud ring detection."""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j_secret")


class GraphAnalyticsEngine:
    """
    Graph-based analytics engine using Neo4j.
    Detects fraud rings, suspicious clusters, and relationship patterns.
    """

    def __init__(self):
        self._driver = None
        try:
            from neo4j import AsyncGraphDatabase
            self._driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            logger.info("Connected to Neo4j at %s", NEO4J_URI)
        except Exception:
            logger.warning("Neo4j not available, running in demo mode")

    async def close(self):
        if self._driver:
            await self._driver.close()

    # --- Schema Setup ---

    SETUP_QUERIES = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Device) REQUIRE d.device_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (ip:IPAddress) REQUIRE ip.address IS UNIQUE",
        "CREATE INDEX IF NOT EXISTS FOR (t:Transaction) ON (t.transaction_id)",
    ]

    async def setup_schema(self):
        """Create Neo4j constraints and indexes."""
        if not self._driver:
            return {"status": "demo_mode", "message": "Neo4j not connected"}
        async with self._driver.session() as session:
            for query in self.SETUP_QUERIES:
                await session.run(query)
        return {"status": "success", "constraints_created": len(self.SETUP_QUERIES)}

    # --- Data Ingestion ---

    async def ingest_transaction(self, txn: dict):
        """Create graph nodes and relationships for a transaction."""
        if not self._driver:
            return self._demo_ingest(txn)

        query = """
        MERGE (c:Customer {customer_id: $customer_id})
        MERGE (src:Account {account_id: $source_account})
        MERGE (dst:Account {account_id: $destination_account})
        MERGE (c)-[:OWNS]->(src)
        CREATE (t:Transaction {
            transaction_id: $transaction_id,
            amount: $amount,
            timestamp: $timestamp,
            type: $transaction_type
        })
        CREATE (src)-[:SENT]->(t)
        CREATE (t)-[:RECEIVED_BY]->(dst)
        WITH c, t
        FOREACH (ip IN CASE WHEN $ip_address IS NOT NULL THEN [$ip_address] ELSE [] END |
            MERGE (ipNode:IPAddress {address: ip})
            MERGE (c)-[:USED_IP]->(ipNode)
        )
        FOREACH (dev IN CASE WHEN $device_id IS NOT NULL THEN [$device_id] ELSE [] END |
            MERGE (dNode:Device {device_id: dev})
            MERGE (c)-[:USED_DEVICE]->(dNode)
        )
        """
        async with self._driver.session() as session:
            await session.run(query, **txn)

    # --- Fraud Ring Detection Queries ---

    async def detect_shared_devices(self, min_customers: int = 2) -> list[dict]:
        """Find devices shared by multiple customers (potential fraud ring indicator)."""
        if not self._driver:
            return self._demo_shared_devices()

        query = """
        MATCH (c:Customer)-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(c2:Customer)
        WHERE c.customer_id < c2.customer_id
        WITH d, COLLECT(DISTINCT c.customer_id) + COLLECT(DISTINCT c2.customer_id) AS customers
        WHERE SIZE(customers) >= $min_customers
        RETURN d.device_id AS device_id, customers, SIZE(customers) AS customer_count
        ORDER BY customer_count DESC
        """
        async with self._driver.session() as session:
            result = await session.run(query, min_customers=min_customers)
            return [dict(record) async for record in result]

    async def detect_shared_ips(self, min_customers: int = 2) -> list[dict]:
        """Find IP addresses shared by multiple customers."""
        if not self._driver:
            return self._demo_shared_ips()

        query = """
        MATCH (c:Customer)-[:USED_IP]->(ip:IPAddress)<-[:USED_IP]-(c2:Customer)
        WHERE c.customer_id < c2.customer_id
        WITH ip, COLLECT(DISTINCT c.customer_id) + COLLECT(DISTINCT c2.customer_id) AS customers
        WHERE SIZE(customers) >= $min_customers
        RETURN ip.address AS ip_address, customers, SIZE(customers) AS customer_count
        ORDER BY customer_count DESC
        """
        async with self._driver.session() as session:
            result = await session.run(query, min_customers=min_customers)
            return [dict(record) async for record in result]

    async def detect_circular_transfers(self, max_depth: int = 5) -> list[dict]:
        """Detect circular money transfer patterns (potential layering)."""
        if not self._driver:
            return self._demo_circular_transfers()

        query = """
        MATCH path = (a:Account)-[:SENT]->(:Transaction)-[:RECEIVED_BY]->(b:Account)
                      -[:SENT]->(:Transaction)-[:RECEIVED_BY*1..""" + str(max_depth) + """]->(a)
        WITH path, [n IN nodes(path) WHERE n:Account | n.account_id] AS accounts,
             [n IN nodes(path) WHERE n:Transaction | n.amount] AS amounts
        RETURN accounts, amounts, LENGTH(path) AS path_length
        ORDER BY path_length DESC
        LIMIT 20
        """
        async with self._driver.session() as session:
            result = await session.run(query)
            return [dict(record) async for record in result]

    async def detect_fraud_clusters(self, min_connections: int = 3) -> list[dict]:
        """Detect clusters of highly connected suspicious entities."""
        if not self._driver:
            return self._demo_fraud_clusters()

        query = """
        MATCH (c:Customer)-[r]-(connected)
        WITH c, COUNT(DISTINCT connected) AS connection_count, 
             COLLECT(DISTINCT type(r)) AS relationship_types
        WHERE connection_count >= $min_connections
        RETURN c.customer_id AS customer_id, 
               connection_count, 
               relationship_types
        ORDER BY connection_count DESC
        LIMIT 50
        """
        async with self._driver.session() as session:
            result = await session.run(query, min_connections=min_connections)
            return [dict(record) async for record in result]

    async def get_customer_network(self, customer_id: str, depth: int = 2) -> dict:
        """Get the full network graph for a specific customer."""
        if not self._driver:
            return self._demo_customer_network(customer_id)

        query = """
        MATCH path = (c:Customer {customer_id: $customer_id})-[*1..""" + str(depth) + """]-(connected)
        WITH COLLECT(DISTINCT {
            id: COALESCE(connected.customer_id, connected.account_id, 
                        connected.device_id, connected.address, connected.transaction_id),
            type: LABELS(connected)[0],
            properties: properties(connected)
        }) AS nodes,
        COLLECT(DISTINCT {
            source: COALESCE(startNode(last(relationships(path))).customer_id,
                            startNode(last(relationships(path))).account_id),
            target: COALESCE(endNode(last(relationships(path))).customer_id,
                            endNode(last(relationships(path))).account_id),
            type: type(last(relationships(path)))
        }) AS edges
        RETURN nodes, edges
        """
        async with self._driver.session() as session:
            result = await session.run(query, customer_id=customer_id)
            record = await result.single()
            if record:
                return {"nodes": record["nodes"], "edges": record["edges"]}
            return {"nodes": [], "edges": []}

    # --- Demo Mode Responses ---

    def _demo_ingest(self, txn: dict) -> dict:
        return {"status": "demo_mode", "transaction_id": txn.get("transaction_id")}

    def _demo_shared_devices(self) -> list[dict]:
        return [
            {"device_id": "DEV-001", "customers": ["CUST-001", "CUST-005", "CUST-012"], "customer_count": 3},
            {"device_id": "DEV-007", "customers": ["CUST-003", "CUST-009"], "customer_count": 2},
        ]

    def _demo_shared_ips(self) -> list[dict]:
        return [
            {"ip_address": "192.168.1.100", "customers": ["CUST-001", "CUST-005"], "customer_count": 2},
            {"ip_address": "10.0.0.50", "customers": ["CUST-003", "CUST-009", "CUST-015"], "customer_count": 3},
        ]

    def _demo_circular_transfers(self) -> list[dict]:
        return [
            {
                "accounts": ["ACC-001", "ACC-005", "ACC-012", "ACC-001"],
                "amounts": [50000, 49500, 49000],
                "path_length": 6,
            }
        ]

    def _demo_fraud_clusters(self) -> list[dict]:
        return [
            {"customer_id": "CUST-001", "connection_count": 8, "relationship_types": ["OWNS", "USED_DEVICE", "USED_IP"]},
            {"customer_id": "CUST-005", "connection_count": 6, "relationship_types": ["OWNS", "USED_DEVICE"]},
        ]

    def _demo_customer_network(self, customer_id: str) -> dict:
        return {
            "nodes": [
                {"id": customer_id, "type": "Customer", "properties": {}},
                {"id": "ACC-001", "type": "Account", "properties": {}},
                {"id": "DEV-001", "type": "Device", "properties": {}},
                {"id": "192.168.1.100", "type": "IPAddress", "properties": {}},
            ],
            "edges": [
                {"source": customer_id, "target": "ACC-001", "type": "OWNS"},
                {"source": customer_id, "target": "DEV-001", "type": "USED_DEVICE"},
                {"source": customer_id, "target": "192.168.1.100", "type": "USED_IP"},
            ],
        }
