"""ML-based fraud detection model serving."""

import logging
import pickle
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class FraudDetectionModel:
    """
    Fraud detection ML model wrapper.
    Uses a pre-trained model or falls back to a rule-based heuristic scorer.
    In production, this loads a scikit-learn or TensorFlow model from disk/MLflow.
    """

    # Feature names expected by the model
    FEATURE_NAMES = [
        "amount",
        "hour_of_day",
        "day_of_week",
        "is_international",
        "is_cash",
        "is_online",
        "amount_zscore",
        "txn_frequency_1h",
        "txn_frequency_24h",
        "avg_amount_30d",
        "std_amount_30d",
        "unique_destinations_7d",
        "is_new_destination",
        "is_round_amount",
        "distance_from_home",
    ]

    def __init__(self, model_path: Optional[str] = None):
        self._model = None
        self._model_version = "heuristic-v1"
        # Per-customer transaction history for feature computation
        self._customer_history: dict[str, list[dict]] = defaultdict(list)
        if model_path and Path(model_path).exists():
            self._load_model(model_path)

    def _load_model(self, path: str):
        """Load a pre-trained sklearn model from disk."""
        try:
            with open(path, "rb") as f:
                self._model = pickle.load(f)  # noqa: S301
            self._model_version = "ml-v1"
            logger.info("ML model loaded from %s", path)
        except Exception:
            logger.warning("Failed to load ML model, using heuristic scorer")

    def extract_features(self, transaction: dict) -> np.ndarray:
        """Extract feature vector from a transaction dict."""
        from datetime import datetime

        timestamp = transaction.get("timestamp", datetime.utcnow().isoformat())
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp)
            except ValueError:
                dt = datetime.utcnow()
        else:
            dt = timestamp

        amount = float(transaction.get("amount", 0))
        txn_type = transaction.get("transaction_type", "")
        channel = transaction.get("channel", "")
        dest_country = transaction.get("destination_country", "")
        src_country = transaction.get("source_country", "US")
        customer_id = transaction.get("customer_id", "")

        # --- Compute historical features from customer cache ---
        history = self._customer_history.get(customer_id, [])
        now = dt

        # Frequency: txns in last 1h and 24h
        one_h_ago = now - timedelta(hours=1)
        twenty_four_h_ago = now - timedelta(hours=24)
        txns_1h = [t for t in history if t.get("_dt", now) > one_h_ago]
        txns_24h = [t for t in history if t.get("_dt", now) > twenty_four_h_ago]
        txn_frequency_1h = float(len(txns_1h))
        txn_frequency_24h = float(len(txns_24h))

        # 30d stats
        thirty_d_ago = now - timedelta(days=30)
        txns_30d = [t for t in history if t.get("_dt", now) > thirty_d_ago]
        amounts_30d = [t.get("amount", 0) for t in txns_30d]
        avg_amount_30d = float(np.mean(amounts_30d)) if amounts_30d else 0.0
        std_amount_30d = float(np.std(amounts_30d)) if len(amounts_30d) > 1 else 1.0
        amount_zscore = (amount - avg_amount_30d) / std_amount_30d if std_amount_30d > 0 else 0.0

        # Unique destinations in 7d
        seven_d_ago = now - timedelta(days=7)
        txns_7d = [t for t in history if t.get("_dt", now) > seven_d_ago]
        dest_set = {t.get("destination_country", "") for t in txns_7d if t.get("destination_country")}
        unique_destinations_7d = float(len(dest_set))
        is_new_destination = 1.0 if dest_country and dest_country not in dest_set else 0.0

        # Store this transaction in history for future feature computation
        history.append({**transaction, "_dt": dt, "amount": amount})
        # Trim history to 30 days
        self._customer_history[customer_id] = [
            t for t in history if t.get("_dt", now) > thirty_d_ago
        ]

        features = np.array([
            amount,                                                  # amount
            dt.hour,                                                 # hour_of_day
            dt.weekday(),                                            # day_of_week
            1.0 if dest_country and dest_country != src_country else 0.0,  # is_international
            1.0 if "cash" in txn_type else 0.0,                     # is_cash
            1.0 if channel in ("online", "mobile") else 0.0,        # is_online
            amount_zscore,                                           # amount_zscore
            txn_frequency_1h,                                        # txn_frequency_1h
            txn_frequency_24h,                                       # txn_frequency_24h
            avg_amount_30d,                                          # avg_amount_30d
            std_amount_30d,                                          # std_amount_30d
            unique_destinations_7d,                                  # unique_destinations_7d
            is_new_destination,                                      # is_new_destination
            1.0 if amount > 100 and amount % 100 == 0 else 0.0,     # is_round_amount
            0.0,  # distance_from_home (requires geolocation service)
        ]).reshape(1, -1)

        return features

    def predict(self, transaction: dict) -> dict:
        """Predict fraud probability for a transaction."""
        features = self.extract_features(transaction)

        if self._model is not None:
            # Use trained ML model
            proba = self._model.predict_proba(features)[0]
            fraud_score = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            # Heuristic scoring fallback
            fraud_score = self._heuristic_score(transaction, features[0])

        return {
            "fraud_score": round(fraud_score, 4),
            "is_fraud": fraud_score >= 0.7,
            "model_version": self._model_version,
            "confidence": round(abs(fraud_score - 0.5) * 2, 4),
            "risk_factors": self._identify_risk_factors(transaction, fraud_score),
        }

    def _heuristic_score(self, txn: dict, features: np.ndarray) -> float:
        """Rule-based heuristic scoring when no ML model is available."""
        score = 0.0
        amount = float(txn.get("amount", 0))

        # High amount factor
        if amount > 50000:
            score += 0.3
        elif amount > 10000:
            score += 0.15

        # Late night transaction
        hour = features[1]
        if 0 <= hour <= 5:
            score += 0.15

        # International transfer
        if features[3] == 1.0:
            score += 0.2

        # Online/mobile channel for high amounts
        if features[5] == 1.0 and amount > 10000:
            score += 0.15

        # Round amount
        if features[13] == 1.0:
            score += 0.1

        # Weekend transaction for business accounts
        if features[2] >= 5:  # Saturday or Sunday
            score += 0.05

        return min(score, 1.0)

    def _identify_risk_factors(self, txn: dict, score: float) -> list[str]:
        """Identify which factors contributed to the fraud score."""
        factors = []
        amount = float(txn.get("amount", 0))

        if amount > 50000:
            factors.append("very_high_amount")
        elif amount > 10000:
            factors.append("high_amount")

        dest = txn.get("destination_country", "")
        src = txn.get("source_country", "US")
        if dest and dest != src:
            factors.append("international_transfer")

        channel = txn.get("channel", "")
        if channel in ("online", "mobile") and amount > 10000:
            factors.append("high_value_digital_channel")

        if amount > 100 and amount % 100 == 0:
            factors.append("round_amount")

        return factors


# Singleton model instance
fraud_model = FraudDetectionModel()
