"""AI/ML, Analytics, and Risk Scoring Engine.

Covers 9 functionalities:
 1. Machine learning models for AML & fraud
 2. Adaptive behavioral analytics
 3. Peer group analysis
 4. Anomaly detection
 5. Predictive risk scoring
 6. Explainable AI (XAI)
 7. Model governance & monitoring
 8. Data ingestion & big data analytics
 9. Scenario simulation & tuning

3 Scenarios:
 - ML-based Alert Reduction (40-60% false-positive reduction)
 - Predictive Fraud Detection (pre-transaction suspicious behaviour)
 - Customer Risk Score Update (ML model recalculates risk on new data)
"""

import hashlib
import math
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


# ═══════════════════ Enums & Constants ═══════════════════

class ModelStatus(str, Enum):
    active = "active"
    training = "training"
    validating = "validating"
    staging = "staging"
    deprecated = "deprecated"
    retired = "retired"


class ModelType(str, Enum):
    binary_classification = "binary_classification"
    multi_classification = "multi_classification"
    regression = "regression"
    unsupervised = "unsupervised"
    ensemble = "ensemble"
    deep_learning = "deep_learning"


class RiskLevel(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


PEER_GROUP_DEFINITIONS = {
    "retail_banking_individual": {
        "description": "Individual retail banking customers",
        "avg_monthly_transactions": 45, "avg_monthly_amount": 8500,
        "std_dev_amount": 3200, "avg_balance": 15000,
    },
    "small_business": {
        "description": "Small business accounts with <$1M annual revenue",
        "avg_monthly_transactions": 120, "avg_monthly_amount": 75000,
        "std_dev_amount": 25000, "avg_balance": 85000,
    },
    "corporate": {
        "description": "Corporate entities with >$1M annual revenue",
        "avg_monthly_transactions": 350, "avg_monthly_amount": 500000,
        "std_dev_amount": 150000, "avg_balance": 1200000,
    },
    "high_net_worth": {
        "description": "HNW individuals with >$1M in assets",
        "avg_monthly_transactions": 25, "avg_monthly_amount": 120000,
        "std_dev_amount": 60000, "avg_balance": 2500000,
    },
    "money_service_business": {
        "description": "MSBs, remittance providers, currency exchanges",
        "avg_monthly_transactions": 800, "avg_monthly_amount": 350000,
        "std_dev_amount": 120000, "avg_balance": 250000,
    },
}

ANOMALY_METHODS = {
    "isolation_forest": {"description": "Tree-based anomaly isolation", "contamination": 0.05},
    "autoencoder": {"description": "Neural reconstruction error", "threshold": 0.85},
    "statistical_zscore": {"description": "Z-score deviation from peer group", "threshold": 3.0},
    "dbscan_clustering": {"description": "Density-based spatial clustering", "eps": 0.5},
    "local_outlier_factor": {"description": "Local density deviation", "n_neighbors": 20},
}

XAI_METHODS = ["shap_values", "lime_explanation", "feature_importance", "partial_dependence", "counterfactual"]


# ═══════════════════ In-Memory Stores ═══════════════════

model_registry: list[dict] = []
model_governance_log: list[dict] = []
behavioral_profiles: dict[str, dict] = {}
ingestion_jobs: list[dict] = []
simulation_results: list[dict] = []
risk_score_history: dict[str, list[dict]] = {}
alert_reduction_log: list[dict] = []


# ═══════════════════ Seed Model Registry ═══════════════════

def _seed_models():
    if model_registry:
        return
    models = [
        {"model_id": "MDL-AML-001", "name": "AML Transaction Classifier",
         "type": ModelType.binary_classification, "framework": "XGBoost",
         "version": "3.2.1", "status": ModelStatus.active,
         "features": 42, "training_samples": 2_500_000,
         "accuracy": 0.962, "precision": 0.945, "recall": 0.938, "f1": 0.941, "auc_roc": 0.978,
         "false_positive_rate": 0.042, "false_negative_rate": 0.062,
         "last_trained": "2026-02-15", "last_validated": "2026-02-20",
         "feature_groups": ["transaction_amount", "velocity", "geographic", "temporal", "counterparty", "behavioral"]},
        {"model_id": "MDL-FRD-001", "name": "Real-Time Fraud Detector",
         "type": ModelType.ensemble, "framework": "LightGBM + Neural Net",
         "version": "4.1.0", "status": ModelStatus.active,
         "features": 56, "training_samples": 5_000_000,
         "accuracy": 0.971, "precision": 0.958, "recall": 0.949, "f1": 0.953, "auc_roc": 0.985,
         "false_positive_rate": 0.031, "false_negative_rate": 0.051,
         "last_trained": "2026-03-01", "last_validated": "2026-03-05",
         "feature_groups": ["device", "velocity", "amount", "merchant", "behavioral", "geo_ip", "session"]},
        {"model_id": "MDL-BEH-001", "name": "Behavioral Analytics Engine",
         "type": ModelType.unsupervised, "framework": "PyTorch Autoencoder",
         "version": "2.0.3", "status": ModelStatus.active,
         "features": 38, "training_samples": 1_800_000,
         "accuracy": None, "precision": None, "recall": None, "f1": None, "auc_roc": None,
         "reconstruction_error_threshold": 0.85, "anomaly_detection_rate": 0.94,
         "last_trained": "2026-02-28", "last_validated": "2026-03-02",
         "feature_groups": ["temporal_patterns", "amount_distribution", "counterparty_network", "channel_usage"]},
        {"model_id": "MDL-RSK-001", "name": "Predictive Customer Risk Scorer",
         "type": ModelType.regression, "framework": "TensorFlow",
         "version": "2.5.0", "status": ModelStatus.active,
         "features": 65, "training_samples": 3_200_000,
         "accuracy": 0.934, "precision": None, "recall": None, "f1": None, "auc_roc": None,
         "mae": 0.048, "rmse": 0.072, "r_squared": 0.912,
         "last_trained": "2026-03-10", "last_validated": "2026-03-12",
         "feature_groups": ["demographics", "transaction_history", "account_behavior", "network", "external_data", "kyc"]},
        {"model_id": "MDL-ANM-001", "name": "Multi-Method Anomaly Detector",
         "type": ModelType.ensemble, "framework": "Scikit-learn + PyTorch",
         "version": "1.8.2", "status": ModelStatus.active,
         "features": 30, "training_samples": 2_000_000,
         "accuracy": None, "precision": 0.912, "recall": 0.887, "f1": 0.899, "auc_roc": 0.956,
         "false_positive_rate": 0.055, "anomaly_detection_rate": 0.887,
         "last_trained": "2026-02-25", "last_validated": "2026-03-01",
         "feature_groups": ["transaction_patterns", "velocity", "peer_deviation", "temporal_anomaly"]},
        {"model_id": "MDL-PGA-001", "name": "Peer Group Analyzer",
         "type": ModelType.unsupervised, "framework": "Scikit-learn KMeans + DBSCAN",
         "version": "1.3.0", "status": ModelStatus.active,
         "features": 22, "training_samples": 1_500_000,
         "accuracy": None, "precision": None, "recall": None, "f1": None, "auc_roc": None,
         "silhouette_score": 0.72, "calinski_harabasz": 1850,
         "last_trained": "2026-03-05", "last_validated": "2026-03-08",
         "feature_groups": ["account_type", "industry", "geography", "transaction_volume", "balance_pattern"]},
    ]
    model_registry.extend(models)


_seed_models()


# ═══════════════════ AI/ML Engine ═══════════════════

class AIMLEngine:
    """Core AI/ML, Analytics, and Risk Scoring engine."""

    # ── 1. ML Models for AML & Fraud ──

    def get_model_registry(self):
        """Return all registered ML models."""
        return {
            "models": model_registry,
            "total": len(model_registry),
            "active": sum(1 for m in model_registry if m["status"] == ModelStatus.active),
            "total_features": sum(m["features"] for m in model_registry),
            "frameworks": list({m["framework"] for m in model_registry}),
        }

    def predict_aml(self, transaction: dict) -> dict:
        """Run AML transaction classification."""
        amount = transaction.get("amount", 0)
        is_international = transaction.get("is_international", False)
        is_pep = transaction.get("is_pep", False)
        sanctions_proximity = transaction.get("sanctions_proximity", 0)
        velocity_ratio = transaction.get("velocity_ratio", 1.0)
        country_risk = transaction.get("country_risk", 0.1)

        # Simulated model scoring
        base = min(1.0, (amount / 500000) * 0.25)
        geo = 0.2 if is_international else 0.0
        pep = 0.15 if is_pep else 0.0
        sanc = sanctions_proximity * 0.2
        vel = min(0.15, (velocity_ratio - 1.0) * 0.05) if velocity_ratio > 1.0 else 0.0
        cr = country_risk * 0.15
        score = min(1.0, base + geo + pep + sanc + vel + cr)

        explanation = self._generate_xai(transaction, score, "aml")

        return {
            "model_id": "MDL-AML-001",
            "model_version": "3.2.1",
            "aml_score": round(score, 4),
            "risk_level": self._score_to_risk(score),
            "is_suspicious": score >= 0.6,
            "confidence": round(min(0.99, 0.7 + score * 0.25), 4),
            "explanation": explanation,
            "features_used": 42,
            "inference_time_ms": random.randint(8, 35),
        }

    def predict_fraud(self, transaction: dict) -> dict:
        """Run real-time fraud detection (ensemble)."""
        amount = transaction.get("amount", 0)
        channel = transaction.get("channel", "online")
        hour = transaction.get("hour_of_day", 12)
        device_trust = transaction.get("device_trust_score", 0.8)
        velocity = transaction.get("velocity_ratio", 1.0)
        merchant_risk = transaction.get("merchant_risk", 0.1)

        base = min(0.35, (amount / 100000) * 0.2)
        ch = 0.1 if channel in ("online", "mobile") and amount > 5000 else 0.0
        hr = 0.12 if hour < 5 or hour > 23 else 0.0
        dev = max(0, (1.0 - device_trust) * 0.2)
        vel = min(0.15, max(0, (velocity - 1.5) * 0.1))
        mr = merchant_risk * 0.15
        score = min(1.0, base + ch + hr + dev + vel + mr)

        explanation = self._generate_xai(transaction, score, "fraud")

        return {
            "model_id": "MDL-FRD-001",
            "model_version": "4.1.0",
            "fraud_score": round(score, 4),
            "risk_level": self._score_to_risk(score),
            "is_fraudulent": score >= 0.7,
            "confidence": round(min(0.99, 0.65 + score * 0.3), 4),
            "explanation": explanation,
            "features_used": 56,
            "inference_time_ms": random.randint(5, 20),
        }

    # ── 2. Adaptive Behavioral Analytics ──

    def update_behavioral_profile(self, customer_id: str, activity: dict) -> dict:
        """Update customer behavioral profile with new activity and detect deviations."""
        now = datetime.utcnow()
        if customer_id not in behavioral_profiles:
            behavioral_profiles[customer_id] = {
                "customer_id": customer_id,
                "created_at": now.isoformat(),
                "total_observations": 0,
                "avg_transaction_amount": 0,
                "avg_monthly_transactions": 0,
                "typical_hours": list(range(8, 20)),
                "typical_channels": ["online", "branch"],
                "typical_counterparties": [],
                "amount_std_dev": 5000,
                "baseline_established": False,
            }

        profile = behavioral_profiles[customer_id]
        n = profile["total_observations"]
        amount = activity.get("amount", 0)

        # Running average update
        if n > 0:
            old_avg = profile["avg_transaction_amount"]
            profile["avg_transaction_amount"] = round((old_avg * n + amount) / (n + 1), 2)
        else:
            profile["avg_transaction_amount"] = amount
        profile["total_observations"] = n + 1
        if profile["total_observations"] >= 30:
            profile["baseline_established"] = True

        # Deviation detection
        deviations = []
        if profile["baseline_established"]:
            z_amount = abs(amount - profile["avg_transaction_amount"]) / max(profile["amount_std_dev"], 1)
            if z_amount > 3.0:
                deviations.append({"type": "amount_deviation", "z_score": round(z_amount, 2),
                                   "detail": f"Amount ${amount:,.0f} is {z_amount:.1f}σ from mean ${profile['avg_transaction_amount']:,.0f}"})
            hour = activity.get("hour_of_day", 12)
            if hour not in profile["typical_hours"]:
                deviations.append({"type": "temporal_deviation", "detail": f"Activity at hour {hour} outside typical range"})
            channel = activity.get("channel", "online")
            if channel not in profile["typical_channels"]:
                deviations.append({"type": "channel_deviation", "detail": f"Unusual channel: {channel}"})

        profile["updated_at"] = now.isoformat()
        deviation_score = min(1.0, len(deviations) * 0.3 + (0.1 if not profile["baseline_established"] else 0))

        return {
            "customer_id": customer_id,
            "profile_status": "established" if profile["baseline_established"] else "learning",
            "observations": profile["total_observations"],
            "avg_transaction_amount": profile["avg_transaction_amount"],
            "deviations_detected": len(deviations),
            "deviations": deviations,
            "deviation_score": round(deviation_score, 4),
            "risk_adjustment": "elevated" if deviation_score > 0.5 else "normal",
            "updated_at": now.isoformat(),
        }

    def get_behavioral_profile(self, customer_id: str) -> dict:
        """Get stored behavioral profile for a customer."""
        if customer_id in behavioral_profiles:
            return behavioral_profiles[customer_id]
        return {"customer_id": customer_id, "status": "no_profile", "message": "No behavioral profile recorded yet"}

    # ── 3. Peer Group Analysis ──

    def analyze_peer_group(self, customer_id: str, peer_group: str, metrics: dict) -> dict:
        """Compare customer activity against peer group benchmarks."""
        pg = PEER_GROUP_DEFINITIONS.get(peer_group)
        if not pg:
            return {"error": f"Unknown peer group: {peer_group}", "available": list(PEER_GROUP_DEFINITIONS.keys())}

        monthly_txns = metrics.get("monthly_transactions", 0)
        monthly_amount = metrics.get("monthly_amount", 0)
        balance = metrics.get("balance", 0)

        txn_deviation = (monthly_txns - pg["avg_monthly_transactions"]) / max(pg["avg_monthly_transactions"], 1)
        amount_deviation = (monthly_amount - pg["avg_monthly_amount"]) / max(pg["std_dev_amount"], 1)
        balance_deviation = (balance - pg["avg_balance"]) / max(pg["avg_balance"], 1)

        anomaly_flags = []
        if abs(amount_deviation) > 3.0:
            anomaly_flags.append({"flag": "amount_outlier", "z_score": round(amount_deviation, 2),
                                  "detail": f"Monthly amount ${monthly_amount:,.0f} is {abs(amount_deviation):.1f}σ from peer avg ${pg['avg_monthly_amount']:,.0f}"})
        if abs(txn_deviation) > 2.0:
            anomaly_flags.append({"flag": "transaction_volume_outlier", "deviation_pct": round(txn_deviation * 100, 1),
                                  "detail": f"Monthly txns {monthly_txns} vs peer avg {pg['avg_monthly_transactions']}"})
        if balance_deviation > 5.0:
            anomaly_flags.append({"flag": "balance_outlier", "deviation_pct": round(balance_deviation * 100, 1),
                                  "detail": f"Balance ${balance:,.0f} vs peer avg ${pg['avg_balance']:,.0f}"})

        peer_risk = min(1.0, sum(abs(d) for d in [txn_deviation, amount_deviation, balance_deviation]) / 10)

        return {
            "customer_id": customer_id,
            "peer_group": peer_group,
            "peer_group_description": pg["description"],
            "metrics": {
                "transaction_volume": {"customer": monthly_txns, "peer_avg": pg["avg_monthly_transactions"],
                                       "deviation_pct": round(txn_deviation * 100, 1)},
                "monthly_amount": {"customer": monthly_amount, "peer_avg": pg["avg_monthly_amount"],
                                   "z_score": round(amount_deviation, 2)},
                "balance": {"customer": balance, "peer_avg": pg["avg_balance"],
                            "deviation_pct": round(balance_deviation * 100, 1)},
            },
            "anomaly_flags": anomaly_flags,
            "peer_risk_score": round(peer_risk, 4),
            "risk_level": self._score_to_risk(peer_risk),
            "peer_groups_available": list(PEER_GROUP_DEFINITIONS.keys()),
        }

    # ── 4. Anomaly Detection ──

    def detect_anomalies(self, transactions: list[dict]) -> dict:
        """Run multi-method anomaly detection on a batch of transactions."""
        results = []
        anomaly_count = 0
        for txn in transactions:
            txn_id = txn.get("transaction_id", f"TXN-{random.randint(1000,9999)}")
            amount = txn.get("amount", 0)
            scores = {}

            # Isolation Forest
            seed = int(hashlib.md5(str(amount).encode()).hexdigest()[:8], 16)
            rng = random.Random(seed)
            iso_score = min(1.0, (amount / 100000) * 0.4 + rng.uniform(0, 0.3))
            scores["isolation_forest"] = round(iso_score, 4)

            # Autoencoder reconstruction error
            ae_score = min(1.0, iso_score * 0.9 + rng.uniform(0, 0.15))
            scores["autoencoder"] = round(ae_score, 4)

            # Z-score
            z = abs(amount - 8500) / 3200  # vs retail peer avg
            z_norm = min(1.0, z / 5.0)
            scores["statistical_zscore"] = round(z_norm, 4)

            # Ensemble
            ensemble = round((iso_score * 0.35 + ae_score * 0.35 + z_norm * 0.30), 4)
            is_anomaly = ensemble >= 0.6

            if is_anomaly:
                anomaly_count += 1

            results.append({
                "transaction_id": txn_id,
                "amount": amount,
                "method_scores": scores,
                "ensemble_score": ensemble,
                "is_anomaly": is_anomaly,
                "anomaly_type": self._classify_anomaly(txn, ensemble) if is_anomaly else None,
            })

        return {
            "total_transactions": len(transactions),
            "anomalies_detected": anomaly_count,
            "anomaly_rate": round(anomaly_count / max(len(transactions), 1), 4),
            "methods_used": list(ANOMALY_METHODS.keys()),
            "results": results,
        }

    def _classify_anomaly(self, txn: dict, score: float) -> str:
        amount = txn.get("amount", 0)
        if amount > 50000:
            return "large_value_anomaly"
        if txn.get("hour_of_day", 12) < 5:
            return "temporal_anomaly"
        if score > 0.85:
            return "statistical_extreme"
        return "behavioral_anomaly"

    # ── 5. Predictive Risk Scoring ──

    def calculate_predictive_risk(self, customer_id: str, data: dict) -> dict:
        """Calculate predictive customer risk score using ML model."""
        now = datetime.utcnow()
        demographics_risk = data.get("demographics_risk", 0.1)
        transaction_risk = data.get("transaction_risk", 0.2)
        behavioral_risk = data.get("behavioral_risk", 0.15)
        network_risk = data.get("network_risk", 0.1)
        external_risk = data.get("external_risk", 0.1)
        kyc_risk = data.get("kyc_risk", 0.1)

        weights = {"demographics": 0.10, "transaction": 0.25, "behavioral": 0.25,
                    "network": 0.15, "external": 0.15, "kyc": 0.10}

        composite = (demographics_risk * weights["demographics"]
                     + transaction_risk * weights["transaction"]
                     + behavioral_risk * weights["behavioral"]
                     + network_risk * weights["network"]
                     + external_risk * weights["external"]
                     + kyc_risk * weights["kyc"])
        composite = round(min(1.0, composite), 4)

        previous = risk_score_history.get(customer_id, [])
        prev_score = previous[-1]["score"] if previous else None
        delta = round(composite - prev_score, 4) if prev_score is not None else None

        entry = {"score": composite, "risk_level": self._score_to_risk(composite),
                 "timestamp": now.isoformat(), "components": {
                     "demographics": round(demographics_risk, 4), "transaction": round(transaction_risk, 4),
                     "behavioral": round(behavioral_risk, 4), "network": round(network_risk, 4),
                     "external": round(external_risk, 4), "kyc": round(kyc_risk, 4),
                 }}
        risk_score_history.setdefault(customer_id, []).append(entry)

        return {
            "model_id": "MDL-RSK-001",
            "model_version": "2.5.0",
            "customer_id": customer_id,
            "risk_score": composite,
            "risk_level": self._score_to_risk(composite),
            "previous_score": prev_score,
            "score_delta": delta,
            "trend": "increasing" if delta and delta > 0.05 else "decreasing" if delta and delta < -0.05 else "stable",
            "component_scores": entry["components"],
            "weights": weights,
            "explanation": self._generate_xai(data, composite, "risk"),
            "timestamp": now.isoformat(),
        }

    # ── 6. Explainable AI ──

    def explain_prediction(self, model_id: str, prediction: dict) -> dict:
        """Generate XAI explanation for a model prediction."""
        score = prediction.get("score", 0.5)
        features = prediction.get("features", {})

        # SHAP values (simulated)
        shap_values = {}
        for feat, val in features.items():
            impact = round((val - 0.5) * random.uniform(0.05, 0.25), 4)
            shap_values[feat] = {"value": val, "shap_value": impact,
                                 "direction": "increases_risk" if impact > 0 else "decreases_risk"}

        sorted_shap = sorted(shap_values.items(), key=lambda x: abs(x[1]["shap_value"]), reverse=True)
        top_drivers = [{"feature": k, **v} for k, v in sorted_shap[:5]]

        # LIME (simulated)
        lime_weights = {feat: round(random.uniform(-0.3, 0.3), 4) for feat in list(features.keys())[:8]}

        # Counterfactual
        counterfactual = {}
        for feat, val in list(features.items())[:3]:
            cf_val = round(max(0, val - 0.2), 2) if val > 0.5 else round(min(1, val + 0.2), 2)
            counterfactual[feat] = {"current": val, "counterfactual": cf_val,
                                    "would_change_prediction": abs(val - cf_val) > 0.15}

        return {
            "model_id": model_id,
            "prediction_score": score,
            "xai_methods": XAI_METHODS,
            "shap_analysis": {"top_risk_drivers": top_drivers, "total_features_analyzed": len(shap_values)},
            "lime_analysis": {"feature_weights": lime_weights, "interpretable_model": "linear_regression"},
            "feature_importance": {k: round(abs(v["shap_value"]), 4) for k, v in sorted_shap[:10]},
            "counterfactual_analysis": {
                "description": "Minimal feature changes to alter prediction",
                "changes": counterfactual,
            },
            "partial_dependence": {feat: {"effect": round(random.uniform(-0.2, 0.2), 4)}
                                   for feat in list(features.keys())[:5]},
            "human_readable_summary": self._generate_human_summary(score, top_drivers),
        }

    def _generate_human_summary(self, score: float, drivers: list) -> str:
        level = self._score_to_risk(score)
        top3 = ", ".join(d["feature"].replace("_", " ") for d in drivers[:3])
        return f"Risk level is {level} (score {score:.2f}). Top contributing factors: {top3}."

    # ── 7. Model Governance & Monitoring ──

    def get_model_governance(self) -> dict:
        """Get model governance dashboard with performance tracking."""
        now = datetime.utcnow()
        governance_entries = []
        for m in model_registry:
            drift_seed = int(hashlib.md5(m["model_id"].encode()).hexdigest()[:6], 16)
            rng = random.Random(drift_seed)
            psi = round(rng.uniform(0.01, 0.18), 4)  # Population Stability Index
            drift_detected = psi > 0.10
            governance_entries.append({
                "model_id": m["model_id"],
                "model_name": m["name"],
                "status": m["status"],
                "version": m["version"],
                "accuracy": m.get("accuracy"),
                "auc_roc": m.get("auc_roc"),
                "false_positive_rate": m.get("false_positive_rate"),
                "population_stability_index": psi,
                "data_drift_detected": drift_detected,
                "last_trained": m["last_trained"],
                "last_validated": m["last_validated"],
                "retraining_recommended": drift_detected or (m.get("accuracy") and m["accuracy"] < 0.93),
                "compliance_status": "compliant",
                "model_risk_tier": "tier_1" if m["features"] > 40 else "tier_2",
            })

        log_entry = {"action": "governance_review", "timestamp": now.isoformat(),
                     "models_reviewed": len(governance_entries),
                     "drift_alerts": sum(1 for g in governance_entries if g["data_drift_detected"])}
        model_governance_log.append(log_entry)

        return {
            "review_timestamp": now.isoformat(),
            "total_models": len(governance_entries),
            "active_models": sum(1 for g in governance_entries if g["status"] == ModelStatus.active),
            "drift_alerts": sum(1 for g in governance_entries if g["data_drift_detected"]),
            "retraining_needed": sum(1 for g in governance_entries if g["retraining_recommended"]),
            "models": governance_entries,
            "governance_policies": {
                "max_psi_threshold": 0.10,
                "min_accuracy_threshold": 0.93,
                "retraining_frequency": "quarterly",
                "validation_frequency": "monthly",
                "model_risk_tiers": ["tier_1 (>40 features, critical models)", "tier_2 (≤40 features, standard models)"],
            },
        }

    # ── 8. Data Ingestion & Big Data Analytics ──

    def run_ingestion_job(self, source: dict) -> dict:
        """Simulate a big-data ingestion and analytics pipeline."""
        now = datetime.utcnow()
        source_type = source.get("source_type", "transaction_feed")
        record_count = source.get("record_count", 100000)

        rng = random.Random(hash(source_type))
        processing_time_sec = round(record_count / 50000 * rng.uniform(2.5, 8.0), 2)
        anomalies_found = int(record_count * rng.uniform(0.002, 0.015))
        quality_score = round(rng.uniform(0.92, 0.99), 4)

        job = {
            "job_id": f"ING-{now.strftime('%Y%m%d%H%M%S')}",
            "source_type": source_type,
            "records_ingested": record_count,
            "records_processed": record_count - int(record_count * 0.002),
            "records_rejected": int(record_count * 0.002),
            "anomalies_flagged": anomalies_found,
            "processing_time_seconds": processing_time_sec,
            "throughput_records_per_sec": int(record_count / max(processing_time_sec, 0.1)),
            "data_quality_score": quality_score,
            "pipeline_stages": [
                {"stage": "extraction", "status": "completed", "duration_sec": round(processing_time_sec * 0.2, 2)},
                {"stage": "validation", "status": "completed", "duration_sec": round(processing_time_sec * 0.15, 2)},
                {"stage": "transformation", "status": "completed", "duration_sec": round(processing_time_sec * 0.25, 2)},
                {"stage": "feature_engineering", "status": "completed", "duration_sec": round(processing_time_sec * 0.2, 2)},
                {"stage": "model_scoring", "status": "completed", "duration_sec": round(processing_time_sec * 0.15, 2)},
                {"stage": "storage", "status": "completed", "duration_sec": round(processing_time_sec * 0.05, 2)},
            ],
            "analytics_summary": {
                "total_value_processed": round(record_count * rng.uniform(500, 5000), 2),
                "high_risk_transactions": int(anomalies_found * 0.4),
                "medium_risk_transactions": int(anomalies_found * 0.35),
                "low_risk_transactions": record_count - anomalies_found,
            },
            "timestamp": now.isoformat(),
        }
        ingestion_jobs.append(job)
        return job

    def get_ingestion_history(self) -> dict:
        return {"jobs": ingestion_jobs[-20:], "total_jobs": len(ingestion_jobs)}

    # ── 9. Scenario Simulation & Tuning ──

    def run_simulation(self, config: dict) -> dict:
        """Run scenario simulation to tune model thresholds."""
        now = datetime.utcnow()
        model_id = config.get("model_id", "MDL-AML-001")
        threshold = config.get("threshold", 0.6)
        dataset_size = config.get("dataset_size", 50000)

        rng = random.Random(hash(f"{model_id}-{threshold}"))

        tp = int(dataset_size * 0.02 * (1 - (threshold - 0.5) * 0.8))
        fp = int(dataset_size * 0.05 * max(0.1, 1 - threshold))
        fn = int(dataset_size * 0.02 * threshold * 0.5)
        tn = dataset_size - tp - fp - fn

        precision = round(tp / max(tp + fp, 1), 4)
        recall = round(tp / max(tp + fn, 1), 4)
        f1 = round(2 * precision * recall / max(precision + recall, 0.001), 4)
        fpr = round(fp / max(fp + tn, 1), 4)
        alert_volume = tp + fp
        alert_reduction_pct = round((1 - alert_volume / max(dataset_size * 0.07, 1)) * 100, 1)

        result = {
            "simulation_id": f"SIM-{now.strftime('%Y%m%d%H%M%S')}",
            "model_id": model_id,
            "threshold": threshold,
            "dataset_size": dataset_size,
            "confusion_matrix": {"true_positives": tp, "false_positives": fp,
                                 "false_negatives": fn, "true_negatives": tn},
            "metrics": {"precision": precision, "recall": recall, "f1_score": f1,
                        "false_positive_rate": fpr, "alert_volume": alert_volume,
                        "alert_reduction_pct": alert_reduction_pct},
            "recommendation": "increase_threshold" if fpr > 0.03 else "optimal" if f1 > 0.85 else "decrease_threshold",
            "timestamp": now.isoformat(),
        }
        simulation_results.append(result)
        return result

    def get_simulation_history(self) -> dict:
        return {"simulations": simulation_results[-20:], "total_simulations": len(simulation_results)}

    # ═══════════════════ Scenarios ═══════════════════

    def run_alert_reduction_scenario(self) -> dict:
        """Scenario 1: ML-based Alert Reduction — reduce false positives by 40-60%."""
        now = datetime.utcnow()
        baseline_alerts = 10000
        baseline_fp = 6500  # 65% FP rate
        baseline_tp = 3500

        # After ML scoring & threshold tuning
        ml_scored_fp = int(baseline_fp * 0.42)  # 58% reduction
        ml_scored_tp = int(baseline_tp * 0.97)  # 97% recall maintained
        ml_total_alerts = ml_scored_tp + ml_scored_fp
        reduction_pct = round((1 - ml_total_alerts / baseline_alerts) * 100, 1)

        steps = [
            {"step": 1, "action": "baseline_measurement",
             "result": f"Baseline: {baseline_alerts} alerts, {baseline_fp} false positives ({baseline_fp/baseline_alerts*100:.0f}% FP rate)",
             "metrics": {"total_alerts": baseline_alerts, "false_positives": baseline_fp, "fp_rate": 0.65}},
            {"step": 2, "action": "ml_model_scoring",
             "result": "Applied AML Transaction Classifier (MDL-AML-001) + Fraud Detector (MDL-FRD-001) ensemble scoring",
             "metrics": {"models_applied": 2, "features_used": 98}},
            {"step": 3, "action": "behavioral_analytics",
             "result": "Behavioral Analytics Engine (MDL-BEH-001) applied — baseline deviation scoring per customer",
             "metrics": {"profiles_evaluated": 4500, "deviations_detected": 850}},
            {"step": 4, "action": "peer_group_filtering",
             "result": "Peer group analysis removed alerts for activity within normal peer range",
             "metrics": {"peer_groups_analyzed": 5, "alerts_within_peer_norm": 1800}},
            {"step": 5, "action": "threshold_optimization",
             "result": f"Optimized thresholds via simulation — FP reduced from {baseline_fp} to {ml_scored_fp}",
             "metrics": {"threshold_aml": 0.65, "threshold_fraud": 0.72}},
            {"step": 6, "action": "result_validation",
             "result": f"Final: {ml_total_alerts} alerts ({reduction_pct}% reduction), {ml_scored_tp} true positives retained (97% recall)",
             "metrics": {"final_alerts": ml_total_alerts, "final_fp": ml_scored_fp,
                         "final_tp": ml_scored_tp, "recall": 0.97, "reduction_pct": reduction_pct}},
        ]

        return {
            "scenario": "ML-based Alert Reduction",
            "scenario_id": f"SCEN-ALR-{now.strftime('%H%M%S')}",
            "baseline": {"total_alerts": baseline_alerts, "false_positives": baseline_fp,
                         "true_positives": baseline_tp, "fp_rate": 0.65},
            "after_ml": {"total_alerts": ml_total_alerts, "false_positives": ml_scored_fp,
                         "true_positives": ml_scored_tp, "fp_rate": round(ml_scored_fp / max(ml_total_alerts, 1), 4),
                         "recall": 0.97},
            "reduction_pct": reduction_pct,
            "reduction_target_met": 40 <= reduction_pct <= 60,
            "models_used": ["MDL-AML-001", "MDL-FRD-001", "MDL-BEH-001", "MDL-PGA-001"],
            "steps": steps,
        }

    def run_predictive_fraud_scenario(self) -> dict:
        """Scenario 2: Predictive Fraud Detection — identify suspicious behavior before transaction."""
        now = datetime.utcnow()

        steps = [
            {"step": 1, "action": "behavioral_baseline",
             "result": "Loaded 6-month behavioral profile for customer CUST-PRED-001 — 180 observations",
             "metrics": {"observations": 180, "profile_status": "established"}},
            {"step": 2, "action": "real_time_signal_detection",
             "result": "Detected 3 pre-transaction signals: unusual login time (3:42 AM), new device fingerprint, rapid session navigation",
             "metrics": {"signals_detected": 3, "signal_types": ["temporal", "device", "behavioral"]}},
            {"step": 3, "action": "predictive_scoring",
             "result": "MDL-FRD-001 pre-auth score: 0.82 (CRITICAL) — high probability of fraud before transaction attempt",
             "metrics": {"pre_auth_score": 0.82, "risk_level": "critical", "confidence": 0.91}},
            {"step": 4, "action": "peer_group_comparison",
             "result": "Activity pattern 4.2σ from retail_banking_individual peer norm",
             "metrics": {"peer_group": "retail_banking_individual", "z_score": 4.2}},
            {"step": 5, "action": "xai_explanation",
             "result": "SHAP analysis: device_trust (-0.28), login_hour (-0.22), navigation_speed (-0.18) are top risk drivers",
             "metrics": {"xai_method": "shap", "top_features": 3}},
            {"step": 6, "action": "preventive_action",
             "result": "Pre-transaction block triggered — step-up authentication required, account flagged for review",
             "metrics": {"action": "step_up_auth", "fraud_prevented": True, "estimated_loss_prevented": 45000}},
        ]

        return {
            "scenario": "Predictive Fraud Detection",
            "scenario_id": f"SCEN-PFD-{now.strftime('%H%M%S')}",
            "customer_id": "CUST-PRED-001",
            "pre_transaction_score": 0.82,
            "risk_level": "critical",
            "fraud_prevented": True,
            "estimated_loss_prevented": 45000,
            "signals": [
                {"signal": "unusual_login_time", "value": "03:42", "deviation": "outside typical 08:00-20:00"},
                {"signal": "new_device", "value": "unknown_device_fingerprint", "trust_score": 0.12},
                {"signal": "rapid_navigation", "value": "8 pages in 15 seconds", "deviation": "3.5x normal speed"},
            ],
            "models_used": ["MDL-FRD-001", "MDL-BEH-001", "MDL-PGA-001"],
            "steps": steps,
        }

    def run_risk_score_update_scenario(self) -> dict:
        """Scenario 3: Customer Risk Score Update — ML model recalculates risk on new data."""
        now = datetime.utcnow()
        customer_id = "CUST-RISK-UPDATE-001"

        steps = [
            {"step": 1, "action": "load_existing_score",
             "result": "Current risk score for CUST-RISK-UPDATE-001: 0.35 (MEDIUM)",
             "metrics": {"current_score": 0.35, "risk_level": "medium", "last_updated": (now - timedelta(days=30)).isoformat()}},
            {"step": 2, "action": "ingest_new_data",
             "result": "New data ingested: 3 large international wires, adverse media hit, new high-risk jurisdiction counterparty",
             "metrics": {"new_events": 3, "data_sources": ["transaction_feed", "adverse_media", "counterparty_screening"]}},
            {"step": 3, "action": "feature_recalculation",
             "result": "65 features recalculated — transaction_risk: 0.72 (was 0.25), behavioral_risk: 0.58 (was 0.20), external_risk: 0.65 (was 0.10)",
             "metrics": {"features_updated": 65, "significant_changes": 3}},
            {"step": 4, "action": "ml_model_inference",
             "result": "MDL-RSK-001 recalculated score: 0.35 → 0.71 (HIGH) — delta +0.36",
             "metrics": {"new_score": 0.71, "previous_score": 0.35, "delta": 0.36, "risk_level": "high"}},
            {"step": 5, "action": "xai_explanation",
             "result": "Top risk drivers: international_wire_volume (SHAP +0.18), adverse_media_hit (SHAP +0.14), new_jurisdiction (SHAP +0.11)",
             "metrics": {"xai_method": "shap", "top_drivers": ["international_wire_volume", "adverse_media_hit", "new_jurisdiction"]}},
            {"step": 6, "action": "downstream_actions",
             "result": "Risk level escalation: MEDIUM→HIGH. Triggered: enhanced monitoring, KYC review flag, alert to compliance team",
             "metrics": {"escalation": "medium_to_high", "actions_triggered": 3,
                         "actions": ["enhanced_monitoring", "kyc_review_flag", "compliance_alert"]}},
        ]

        # Record in history
        risk_score_history.setdefault(customer_id, []).append(
            {"score": 0.35, "risk_level": "medium", "timestamp": (now - timedelta(days=30)).isoformat()})
        risk_score_history[customer_id].append(
            {"score": 0.71, "risk_level": "high", "timestamp": now.isoformat()})

        return {
            "scenario": "Customer Risk Score Update",
            "scenario_id": f"SCEN-RSU-{now.strftime('%H%M%S')}",
            "customer_id": customer_id,
            "previous_score": 0.35,
            "new_score": 0.71,
            "delta": 0.36,
            "previous_risk_level": "medium",
            "new_risk_level": "high",
            "trigger": "new_data_ingestion",
            "new_data_events": [
                {"event": "large_international_wire", "amount": 125000, "jurisdiction": "high_risk"},
                {"event": "adverse_media_hit", "source": "global_media_scan", "severity": "high"},
                {"event": "new_counterparty", "jurisdiction": "Cayman Islands", "risk": "high"},
            ],
            "downstream_actions": ["enhanced_monitoring", "kyc_review_flag", "compliance_alert"],
            "models_used": ["MDL-RSK-001", "MDL-BEH-001", "MDL-ANM-001"],
            "steps": steps,
        }

    # ═══════════════════ Dashboard ═══════════════════

    def get_dashboard(self) -> dict:
        """AI/ML analytics dashboard with model performance and risk metrics."""
        now = datetime.utcnow()
        active_models = [m for m in model_registry if m["status"] == ModelStatus.active]
        avg_accuracy = sum(m["accuracy"] for m in active_models if m.get("accuracy")) / max(
            sum(1 for m in active_models if m.get("accuracy")), 1)
        avg_fpr = sum(m.get("false_positive_rate", 0) for m in active_models if m.get("false_positive_rate")) / max(
            sum(1 for m in active_models if m.get("false_positive_rate")), 1)

        return {
            "generated_at": now.isoformat(),
            "model_metrics": {
                "total_models": len(model_registry),
                "active_models": len(active_models),
                "avg_accuracy": round(avg_accuracy, 4),
                "avg_false_positive_rate": round(avg_fpr, 4),
                "total_features": sum(m["features"] for m in active_models),
                "total_training_samples": sum(m["training_samples"] for m in active_models),
            },
            "behavioral_analytics": {
                "profiles_tracked": len(behavioral_profiles),
                "baselines_established": sum(1 for p in behavioral_profiles.values() if p.get("baseline_established")),
            },
            "peer_groups": {
                "groups_defined": len(PEER_GROUP_DEFINITIONS),
                "groups": list(PEER_GROUP_DEFINITIONS.keys()),
            },
            "anomaly_detection": {
                "methods_available": len(ANOMALY_METHODS),
                "methods": list(ANOMALY_METHODS.keys()),
            },
            "ingestion_jobs": {
                "total_completed": len(ingestion_jobs),
                "last_job": ingestion_jobs[-1] if ingestion_jobs else None,
            },
            "simulations": {
                "total_run": len(simulation_results),
                "last_simulation": simulation_results[-1] if simulation_results else None,
            },
            "xai_methods": XAI_METHODS,
        }

    # ═══════════════════ Helpers ═══════════════════

    def _score_to_risk(self, score: float) -> str:
        if score >= 0.8:
            return "critical"
        if score >= 0.6:
            return "high"
        if score >= 0.3:
            return "medium"
        return "low"

    def _generate_xai(self, data: dict, score: float, model_type: str) -> dict:
        """Generate simplified XAI explanation for any prediction."""
        factors = []
        for key, val in data.items():
            if isinstance(val, (int, float)) and val > 0:
                impact = round((val if isinstance(val, float) and val <= 1 else val / 100000) * 0.15, 4)
                factors.append({"feature": key, "value": val,
                                "impact": impact, "direction": "increases_risk" if impact > 0.05 else "neutral"})
        factors.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return {
            "method": "shap_values",
            "top_risk_drivers": factors[:5],
            "model_type": model_type,
            "prediction_score": score,
        }


aiml_engine = AIMLEngine()
