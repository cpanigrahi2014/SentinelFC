"""Kafka consumer for processing incoming transactions."""

import json
import logging
from uuid import uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .config import settings
from .rule_engine import AMLRuleEngine

logger = logging.getLogger(__name__)

rule_engine = AMLRuleEngine(settings)


async def start_transaction_consumer():
    """Consume raw transactions, apply AML rules, and produce alerts."""
    consumer = AIOKafkaConsumer(
        settings.kafka_input_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
    )

    await consumer.start()
    await producer.start()
    logger.info("Transaction consumer started, listening on: %s", settings.kafka_input_topic)

    try:
        async for message in consumer:
            try:
                transaction = message.value
                logger.info("Processing transaction: %s", transaction.get("transaction_id"))

                # Apply AML rules
                results = rule_engine.evaluate(transaction)
                composite_score = rule_engine.calculate_composite_score(results)

                # Enrich transaction with scoring
                scored_txn = {
                    **transaction,
                    "risk_score": composite_score,
                    "risk_level": _score_to_level(composite_score),
                    "rules_triggered": [
                        {"rule_id": r.rule_id, "rule_name": r.rule_name, "score": r.risk_score}
                        for r in results
                    ],
                }

                # Publish scored transaction
                await producer.send_and_wait(
                    settings.kafka_scored_topic,
                    value=scored_txn,
                )

                # Generate alert if threshold exceeded
                if composite_score >= settings.alert_threshold:
                    alert = {
                        "alert_id": str(uuid4()),
                        "customer_id": transaction.get("customer_id"),
                        "transaction_id": transaction.get("transaction_id"),
                        "risk_score": composite_score,
                        "alert_type": "aml",
                        "rules_triggered": [r.rule_id for r in results],
                        "rule_details": [
                            {
                                "rule_id": r.rule_id,
                                "rule_name": r.rule_name,
                                "description": r.description,
                                "details": r.details,
                            }
                            for r in results
                        ],
                        "description": f"AML alert: {len(results)} rules triggered, score={composite_score:.2f}",
                    }
                    await producer.send_and_wait(settings.kafka_output_topic, value=alert)
                    logger.warning(
                        "AML ALERT generated for customer=%s, score=%.2f",
                        transaction.get("customer_id"),
                        composite_score,
                    )

            except Exception:
                logger.exception("Error processing transaction")
    finally:
        await consumer.stop()
        await producer.stop()


def _score_to_level(score: float) -> str:
    if score >= 0.9:
        return "critical"
    elif score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"
