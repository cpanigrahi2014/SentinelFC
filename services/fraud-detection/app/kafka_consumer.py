"""Kafka consumer for fraud detection processing."""

import json
import logging
import os
from uuid import uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .ml_model import fraud_model

logger = logging.getLogger(__name__)

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
INPUT_TOPIC = "raw-transactions"
OUTPUT_TOPIC = "fraud-alerts"
SCORES_TOPIC = "fraud-scores"
GROUP_ID = "fraud-detection-group"
ALERT_THRESHOLD = float(os.getenv("FRAUD_ALERT_THRESHOLD", "0.7"))


async def start_fraud_consumer():
    """Consume transactions and run fraud detection ML model."""
    consumer = AIOKafkaConsumer(
        INPUT_TOPIC,
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
    logger.info("Fraud detection consumer started")

    try:
        async for message in consumer:
            try:
                transaction = message.value
                prediction = fraud_model.predict(transaction)

                # Publish fraud score
                score_event = {
                    "transaction_id": transaction.get("transaction_id"),
                    "customer_id": transaction.get("customer_id"),
                    **prediction,
                }
                await producer.send_and_wait(SCORES_TOPIC, value=score_event)

                # Generate alert if fraud detected
                if prediction["fraud_score"] >= ALERT_THRESHOLD:
                    alert = {
                        "alert_id": str(uuid4()),
                        "customer_id": transaction.get("customer_id"),
                        "transaction_id": transaction.get("transaction_id"),
                        "risk_score": prediction["fraud_score"],
                        "alert_type": "fraud",
                        "rule_triggered": "ML_FRAUD_DETECTION",
                        "description": f"ML fraud score: {prediction['fraud_score']:.4f}",
                        "risk_factors": prediction["risk_factors"],
                        "model_version": prediction["model_version"],
                    }
                    await producer.send_and_wait(OUTPUT_TOPIC, value=alert)
                    logger.warning(
                        "FRAUD ALERT: customer=%s score=%.4f",
                        transaction.get("customer_id"),
                        prediction["fraud_score"],
                    )

            except Exception:
                logger.exception("Error in fraud detection processing")
    finally:
        await consumer.stop()
        await producer.stop()
