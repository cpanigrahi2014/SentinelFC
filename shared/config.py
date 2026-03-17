"""Shared configuration management for all services."""

import os
from dataclasses import dataclass, field


@dataclass
class ServiceConfig:
    """Base configuration for all microservices."""

    # Service identity
    service_name: str = "actimize-service"
    service_port: int = 8000
    debug: bool = False

    # PostgreSQL
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    postgres_db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "actimize"))
    postgres_user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "actimize"))
    postgres_password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "actimize_secret"))

    # Kafka
    kafka_bootstrap_servers: str = field(
        default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    kafka_group_id: str = ""

    # Elasticsearch
    elasticsearch_url: str = field(
        default_factory=lambda: os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    )

    # Neo4j
    neo4j_uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    neo4j_user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "neo4j_secret"))

    # Redis
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))

    # JWT
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "change-me-in-production"))
    jwt_expiry_minutes: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRY_MINUTES", "60")))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
