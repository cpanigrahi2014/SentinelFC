"""
Fraud Detection Model Training Pipeline

Trains a binary classification model to detect fraudulent transactions.
Uses scikit-learn with synthetic data for demonstration.

Usage:
    python train_fraud_model.py --output models/fraud_model.pkl
"""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def generate_synthetic_data(n_samples: int = 50000, fraud_ratio: float = 0.02) -> pd.DataFrame:
    """Generate synthetic transaction data for model training."""
    np.random.seed(42)

    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud

    # Legitimate transactions
    legit = pd.DataFrame({
        "amount": np.random.lognormal(mean=5, sigma=1.5, size=n_legit).clip(1, 500000),
        "hour_of_day": np.random.choice(range(7, 22), size=n_legit),
        "day_of_week": np.random.choice(range(5), size=n_legit, p=[0.22, 0.22, 0.22, 0.22, 0.12]),
        "is_international": np.random.binomial(1, 0.05, size=n_legit),
        "is_cash": np.random.binomial(1, 0.15, size=n_legit),
        "is_online": np.random.binomial(1, 0.4, size=n_legit),
        "amount_zscore": np.random.normal(0, 0.5, size=n_legit),
        "txn_frequency_1h": np.random.poisson(0.5, size=n_legit),
        "txn_frequency_24h": np.random.poisson(3, size=n_legit),
        "avg_amount_30d": np.random.lognormal(mean=5, sigma=1, size=n_legit),
        "std_amount_30d": np.random.exponential(200, size=n_legit),
        "unique_destinations_7d": np.random.poisson(2, size=n_legit),
        "is_new_destination": np.random.binomial(1, 0.1, size=n_legit),
        "is_round_amount": np.random.binomial(1, 0.1, size=n_legit),
        "distance_from_home": np.random.exponential(50, size=n_legit),
        "is_fraud": 0,
    })

    # Fraudulent transactions (different distributions)
    fraud = pd.DataFrame({
        "amount": np.random.lognormal(mean=8, sigma=2, size=n_fraud).clip(100, 1000000),
        "hour_of_day": np.random.choice(range(0, 6), size=n_fraud),
        "day_of_week": np.random.choice(range(7), size=n_fraud),
        "is_international": np.random.binomial(1, 0.4, size=n_fraud),
        "is_cash": np.random.binomial(1, 0.3, size=n_fraud),
        "is_online": np.random.binomial(1, 0.7, size=n_fraud),
        "amount_zscore": np.random.normal(2, 1, size=n_fraud),
        "txn_frequency_1h": np.random.poisson(3, size=n_fraud),
        "txn_frequency_24h": np.random.poisson(8, size=n_fraud),
        "avg_amount_30d": np.random.lognormal(mean=4, sigma=1, size=n_fraud),
        "std_amount_30d": np.random.exponential(1000, size=n_fraud),
        "unique_destinations_7d": np.random.poisson(6, size=n_fraud),
        "is_new_destination": np.random.binomial(1, 0.6, size=n_fraud),
        "is_round_amount": np.random.binomial(1, 0.4, size=n_fraud),
        "distance_from_home": np.random.exponential(500, size=n_fraud),
        "is_fraud": 1,
    })

    data = pd.concat([legit, fraud], ignore_index=True).sample(frac=1, random_state=42)
    return data


def train_model(data: pd.DataFrame) -> dict:
    """Train and evaluate fraud detection models."""
    X = data[FEATURE_NAMES]
    y = data["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info("Training data: %d samples, %d fraud (%.2f%%)",
                len(X_train), y_train.sum(), y_train.mean() * 100)
    logger.info("Test data: %d samples, %d fraud (%.2f%%)",
                len(X_test), y_test.sum(), y_test.mean() * 100)

    # Define models to evaluate
    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000)),
        ]),
        "random_forest": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1
            )),
        ]),
        "gradient_boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", GradientBoostingClassifier(
                n_estimators=200, max_depth=5, min_samples_leaf=20, random_state=42
            )),
        ]),
    }

    results = {}
    best_model_name = None
    best_auc = 0

    for name, pipeline in models.items():
        logger.info("Training %s...", name)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, y_proba)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "auc_roc": auc,
        }
        results[name] = {
            "metrics": metrics,
            "pipeline": pipeline,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred),
        }

        logger.info(
            "%s - AUC: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f",
            name, auc, metrics["precision"], metrics["recall"], metrics["f1"],
        )

        if auc > best_auc:
            best_auc = auc
            best_model_name = name

        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc")
        results[name]["cv_auc_mean"] = cv_scores.mean()
        results[name]["cv_auc_std"] = cv_scores.std()
        logger.info("%s - CV AUC: %.4f (±%.4f)", name, cv_scores.mean(), cv_scores.std())

    return {
        "results": results,
        "best_model": best_model_name,
        "best_pipeline": results[best_model_name]["pipeline"],
    }


def save_model(pipeline, output_path: str, metadata: dict):
    """Save trained model and metadata."""
    import pickle

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        pickle.dump(pipeline, f)
    logger.info("Model saved to %s", output_path)

    meta_path = output_path.replace(".pkl", "_metadata.json")
    serializable_meta = {}
    for model_name, model_results in metadata.get("results", {}).items():
        serializable_meta[model_name] = {
            "metrics": model_results["metrics"],
            "confusion_matrix": model_results["confusion_matrix"],
            "cv_auc_mean": model_results.get("cv_auc_mean"),
            "cv_auc_std": model_results.get("cv_auc_std"),
        }
    serializable_meta["best_model"] = metadata["best_model"]
    serializable_meta["features"] = FEATURE_NAMES

    with open(meta_path, "w") as f:
        json.dump(serializable_meta, f, indent=2)
    logger.info("Metadata saved to %s", meta_path)


def main():
    parser = argparse.ArgumentParser(description="Train fraud detection model")
    parser.add_argument("--output", default="models/fraud_model.pkl", help="Output model path")
    parser.add_argument("--samples", type=int, default=50000, help="Number of training samples")
    parser.add_argument("--fraud-ratio", type=float, default=0.02, help="Fraud ratio in training data")
    args = parser.parse_args()

    logger.info("Generating synthetic training data...")
    data = generate_synthetic_data(n_samples=args.samples, fraud_ratio=args.fraud_ratio)

    logger.info("Training models...")
    training_results = train_model(data)

    logger.info("Best model: %s", training_results["best_model"])
    save_model(training_results["best_pipeline"], args.output, training_results)
    logger.info("Training complete!")


if __name__ == "__main__":
    main()
