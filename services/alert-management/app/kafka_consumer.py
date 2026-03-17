"""Kafka consumer for ingesting alerts from detection services."""

import json
import logging
import math
import os
from uuid import UUID, uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
INPUT_TOPICS = ["aml-alerts", "fraud-alerts", "sanctions-alerts", "network-alerts"]
OUTPUT_TOPIC = "alert-created"
GROUP_ID = "alert-management-group"

# In-memory alert store (in production, this writes to PostgreSQL + Elasticsearch)
alert_store: dict[str, dict] = {}

# ----- ML-based alert prioritization weights (learned from analyst feedback) -----
# These weights simulate a logistic regression model trained on historical analyst
# disposition data (SAR filed vs. closed-no-action).  In production these would be
# loaded from MLflow / a model registry.
_PRIORITY_WEIGHTS = {
    "risk_score": 3.5,            # base composite risk score from detection engines
    "is_sanctions_alert": 2.0,    # sanctions matches are always high priority
    "is_network_alert": 1.2,      # network / ring patterns
    "rule_count": 0.3,            # number of distinct rules triggered
    "is_high_risk_country": 0.8,  # geographic risk indicator
    "is_pep": 1.5,                # politically exposed person
    "amount_log": 0.4,            # log-scaled transaction amount
    "intercept": -2.0,            # model intercept / bias
}


def _ml_priority_score(alert_data: dict) -> float:
    """Compute an ML-based priority score (0-1) using weighted logistic model."""
    risk_score = float(alert_data.get("risk_score", 0))
    source_topic = alert_data.get("_source_topic", "")
    amount = float(alert_data.get("amount", 0))
    rule_count = len(alert_data.get("rules_triggered", [])) or (1 if alert_data.get("rule_triggered") else 0)

    logit = _PRIORITY_WEIGHTS["intercept"]
    logit += _PRIORITY_WEIGHTS["risk_score"] * risk_score
    logit += _PRIORITY_WEIGHTS["is_sanctions_alert"] * (1.0 if source_topic == "sanctions-alerts" else 0.0)
    logit += _PRIORITY_WEIGHTS["is_network_alert"] * (1.0 if source_topic == "network-alerts" else 0.0)
    logit += _PRIORITY_WEIGHTS["rule_count"] * min(rule_count, 5)
    logit += _PRIORITY_WEIGHTS["is_high_risk_country"] * (1.0 if alert_data.get("is_high_risk_country") else 0.0)
    logit += _PRIORITY_WEIGHTS["is_pep"] * (1.0 if alert_data.get("is_pep") else 0.0)
    logit += _PRIORITY_WEIGHTS["amount_log"] * (math.log10(amount + 1) / 7.0)  # normalise log-amount

    # Sigmoid
    score = 1.0 / (1.0 + math.exp(-logit))
    return round(score, 4)


def _score_to_priority(ml_score: float) -> str:
    """Convert ML priority score to categorical label."""
    if ml_score >= 0.85:
        return "critical"
    elif ml_score >= 0.65:
        return "high"
    elif ml_score >= 0.35:
        return "medium"
    return "low"


async def start_alert_consumer():
    """Consume alerts from all detection engines."""
    consumer = AIOKafkaConsumer(
        *INPUT_TOPICS,
        bootstrap_servers=KAFKA_SERVERS,
        group_id=GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
    )

    await consumer.start()
    await producer.start()
    logger.info("Alert management consumer started, listening on: %s", INPUT_TOPICS)

    try:
        async for message in consumer:
            try:
                alert_data = message.value
                alert_id = alert_data.get("alert_id", str(uuid4()))

                # Enrich with source topic for ML scoring
                alert_data["_source_topic"] = message.topic

                ml_score = _ml_priority_score(alert_data)

                alert = {
                    "alert_id": alert_id,
                    "customer_id": alert_data.get("customer_id"),
                    "transaction_id": alert_data.get("transaction_id"),
                    "risk_score": alert_data.get("risk_score", 0),
                    "alert_type": alert_data.get("alert_type", "unknown"),
                    "rule_triggered": alert_data.get("rule_triggered", ""),
                    "description": alert_data.get("description", ""),
                    "status": "open",
                    "priority": _score_to_priority(ml_score),
                    "ml_priority_score": ml_score,
                    "source_topic": message.topic,
                }

                # Store alert
                alert_store[alert_id] = alert

                # Publish alert-created event
                await producer.send_and_wait(OUTPUT_TOPIC, value=alert)
                logger.info("Alert created: %s type=%s score=%.2f ml_priority=%.4f",
                           alert_id, alert["alert_type"], alert["risk_score"], ml_score)

            except Exception:
                logger.exception("Error processing alert")
    finally:
        await consumer.stop()
        await producer.stop()
