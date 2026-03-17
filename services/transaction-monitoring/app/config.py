"""Configuration for Transaction Monitoring Service."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    service_name: str = "transaction-monitoring"
    service_port: int = 8001
    kafka_bootstrap_servers: str = field(
        default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    kafka_group_id: str = "transaction-monitoring-group"
    kafka_input_topic: str = "raw-transactions"
    kafka_output_topic: str = "aml-alerts"
    kafka_scored_topic: str = "transaction-scored"
    postgres_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://actimize:actimize_secret@localhost:5432/actimize_txn",
        )
    )
    alert_threshold: float = float(os.getenv("ALERT_THRESHOLD", "0.7"))
    large_cash_threshold: float = float(os.getenv("LARGE_CASH_THRESHOLD", "10000"))
    structuring_window_hours: int = int(os.getenv("STRUCTURING_WINDOW_HOURS", "24"))
    structuring_threshold: float = float(os.getenv("STRUCTURING_THRESHOLD", "10000"))
    high_risk_countries: list[str] = field(default_factory=lambda: [
        "AF", "IR", "KP", "SY", "YE", "MM", "LY", "SO", "SS", "CU",
        "VE", "NI", "ZW", "BY", "RU",
    ])


settings = Settings()
