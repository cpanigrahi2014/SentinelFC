"""Customer risk scoring engine for KYC/CDD assessment."""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Country risk ratings
HIGH_RISK_COUNTRIES = {
    "AF", "IR", "KP", "SY", "YE", "MM", "LY", "SO", "SS", "CU", "VE", "NI", "ZW", "BY", "RU",
}
MEDIUM_RISK_COUNTRIES = {
    "CN", "PK", "NG", "LB", "IQ", "UA", "KZ", "UZ", "TJ", "KG",
}

# High-risk occupations/industries
HIGH_RISK_OCCUPATIONS = {
    "money_service_business", "casino_gambling", "cryptocurrency",
    "precious_metals", "arms_dealer", "real_estate_agent",
    "lawyer_notary", "accountant", "politically_exposed",
}


@dataclass
class RiskFactor:
    factor_name: str
    category: str
    score: float
    weight: float
    description: str


class CustomerRiskEngine:
    """
    Multi-factor customer risk scoring engine.
    Evaluates customers across geographic, demographic, behavioral, and product risk dimensions.
    """

    def calculate_risk_score(self, customer: dict) -> dict:
        """Calculate composite risk score for a customer."""
        factors = []

        factors.append(self._geographic_risk(customer))
        factors.append(self._occupation_risk(customer))
        factors.append(self._pep_risk(customer))
        factors.append(self._sanctions_risk(customer))
        factors.append(self._account_behavior_risk(customer))
        factors.append(self._product_risk(customer))
        factors.append(self._age_risk(customer))
        factors.append(self._income_risk(customer))

        # Weighted composite score
        total_weight = sum(f.weight for f in factors)
        composite_score = sum(f.score * f.weight for f in factors) / total_weight if total_weight > 0 else 0.0
        composite_score = min(1.0, composite_score)

        risk_level = self._score_to_level(composite_score)

        return {
            "customer_id": customer.get("customer_id"),
            "composite_score": round(composite_score, 4),
            "risk_level": risk_level,
            "factors": [
                {
                    "name": f.factor_name,
                    "category": f.category,
                    "score": round(f.score, 4),
                    "weight": f.weight,
                    "description": f.description,
                }
                for f in factors
            ],
            "cdd_level": self._determine_cdd_level(risk_level),
            "review_frequency": self._determine_review_frequency(risk_level),
        }

    def _geographic_risk(self, customer: dict) -> RiskFactor:
        country = customer.get("country_of_residence", "US")
        nationality = customer.get("nationality", "US")
        score = 0.0

        if country in HIGH_RISK_COUNTRIES or nationality in HIGH_RISK_COUNTRIES:
            score = 0.9
        elif country in MEDIUM_RISK_COUNTRIES or nationality in MEDIUM_RISK_COUNTRIES:
            score = 0.5

        return RiskFactor(
            factor_name="Geographic Risk",
            category="geographic",
            score=score,
            weight=2.0,
            description=f"Country: {country}, Nationality: {nationality}",
        )

    def _occupation_risk(self, customer: dict) -> RiskFactor:
        occupation = customer.get("occupation", "").lower().replace(" ", "_")
        score = 0.8 if occupation in HIGH_RISK_OCCUPATIONS else 0.1
        return RiskFactor(
            factor_name="Occupation Risk",
            category="demographic",
            score=score,
            weight=1.5,
            description=f"Occupation: {customer.get('occupation', 'unknown')}",
        )

    def _pep_risk(self, customer: dict) -> RiskFactor:
        is_pep = customer.get("pep_status", False)
        return RiskFactor(
            factor_name="PEP Status",
            category="regulatory",
            score=0.95 if is_pep else 0.0,
            weight=2.5,
            description="Politically Exposed Person" if is_pep else "Not a PEP",
        )

    def _sanctions_risk(self, customer: dict) -> RiskFactor:
        is_match = customer.get("sanctions_match", False)
        return RiskFactor(
            factor_name="Sanctions Match",
            category="regulatory",
            score=1.0 if is_match else 0.0,
            weight=3.0,
            description="Sanctions list match found" if is_match else "No sanctions match",
        )

    def _account_behavior_risk(self, customer: dict) -> RiskFactor:
        # In production, this would analyze actual transaction patterns
        txn_volume = customer.get("transaction_volume_30d", 0)
        avg_amount = customer.get("avg_transaction_amount_30d", 0)
        score = 0.0
        if txn_volume > 100 or avg_amount > 50000:
            score = 0.6
        elif txn_volume > 50 or avg_amount > 20000:
            score = 0.3
        return RiskFactor(
            factor_name="Account Behavior",
            category="behavioral",
            score=score,
            weight=1.5,
            description=f"30d volume: {txn_volume}, avg amount: {avg_amount}",
        )

    def _product_risk(self, customer: dict) -> RiskFactor:
        products = customer.get("products", [])
        high_risk_products = {"private_banking", "correspondent_banking", "wire_transfer", "trade_finance"}
        has_high_risk = bool(set(products) & high_risk_products)
        return RiskFactor(
            factor_name="Product Risk",
            category="product",
            score=0.6 if has_high_risk else 0.1,
            weight=1.0,
            description=f"Products: {', '.join(products) if products else 'none'}",
        )

    def _age_risk(self, customer: dict) -> RiskFactor:
        # Very young or very old account holders can be higher risk (mule accounts)
        age = customer.get("age", 30)
        score = 0.0
        if age < 20 or age > 85:
            score = 0.4
        return RiskFactor(
            factor_name="Age Risk",
            category="demographic",
            score=score,
            weight=0.5,
            description=f"Customer age: {age}",
        )

    def _income_risk(self, customer: dict) -> RiskFactor:
        income = float(customer.get("annual_income", 0))
        txn_volume = float(customer.get("total_transaction_volume_annual", 0))
        score = 0.0
        if income > 0 and txn_volume > income * 3:
            score = 0.7  # Transaction volume significantly exceeds income
        return RiskFactor(
            factor_name="Income Mismatch",
            category="behavioral",
            score=score,
            weight=1.5,
            description=f"Income: {income}, Annual txn volume: {txn_volume}",
        )

    @staticmethod
    def _score_to_level(score: float) -> str:
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.3:
            return "medium"
        return "low"

    @staticmethod
    def _determine_cdd_level(risk_level: str) -> str:
        return {
            "critical": "enhanced_due_diligence",
            "high": "enhanced_due_diligence",
            "medium": "standard_due_diligence",
            "low": "simplified_due_diligence",
        }.get(risk_level, "standard_due_diligence")

    @staticmethod
    def _determine_review_frequency(risk_level: str) -> str:
        return {
            "critical": "monthly",
            "high": "quarterly",
            "medium": "annually",
            "low": "every_3_years",
        }.get(risk_level, "annually")

    # ───────── Peer-group & segment comparison ─────────

    # Segment definitions: each maps to baseline thresholds derived from peer averages
    SEGMENT_DEFINITIONS = {
        "retail_individual": {
            "label": "Retail Individual",
            "avg_monthly_txns": 25,
            "avg_txn_amount": 800,
            "std_txn_amount": 1200,
            "max_expected_monthly_volume": 40000,
        },
        "retail_hnwi": {
            "label": "Retail HNWI",
            "avg_monthly_txns": 50,
            "avg_txn_amount": 15000,
            "std_txn_amount": 25000,
            "max_expected_monthly_volume": 1500000,
        },
        "commercial_smb": {
            "label": "Commercial SMB",
            "avg_monthly_txns": 120,
            "avg_txn_amount": 5000,
            "std_txn_amount": 8000,
            "max_expected_monthly_volume": 750000,
        },
        "commercial_corporate": {
            "label": "Commercial Corporate",
            "avg_monthly_txns": 500,
            "avg_txn_amount": 25000,
            "std_txn_amount": 50000,
            "max_expected_monthly_volume": 15000000,
        },
        "correspondent_banking": {
            "label": "Correspondent Banking",
            "avg_monthly_txns": 2000,
            "avg_txn_amount": 100000,
            "std_txn_amount": 200000,
            "max_expected_monthly_volume": 250000000,
        },
    }

    def classify_segment(self, customer: dict) -> str:
        """Classify a customer into a peer-group segment."""
        customer_type = customer.get("customer_type", "individual")
        annual_income = float(customer.get("annual_income", 0))
        products = set(customer.get("products", []))

        if "correspondent_banking" in products:
            return "correspondent_banking"
        if customer_type == "corporate":
            return "commercial_corporate"
        if customer_type == "business":
            return "commercial_smb"
        if annual_income >= 500000:
            return "retail_hnwi"
        return "retail_individual"

    def peer_group_comparison(self, customer: dict) -> dict:
        """Compare a customer's activity against their peer-group baselines."""
        segment = self.classify_segment(customer)
        baseline = self.SEGMENT_DEFINITIONS[segment]

        monthly_txns = customer.get("transaction_volume_30d", 0)
        avg_amount = float(customer.get("avg_transaction_amount_30d", 0))
        monthly_volume = monthly_txns * avg_amount

        txn_count_deviation = (
            (monthly_txns - baseline["avg_monthly_txns"]) / max(baseline["avg_monthly_txns"], 1)
        )
        amount_deviation = (
            (avg_amount - baseline["avg_txn_amount"]) / max(baseline["std_txn_amount"], 1)
        )
        volume_ratio = monthly_volume / max(baseline["max_expected_monthly_volume"], 1)

        deviations = {
            "txn_count_zscore": round(txn_count_deviation, 2),
            "amount_zscore": round(amount_deviation, 2),
            "volume_ratio": round(volume_ratio, 4),
        }

        anomaly_flags = []
        if txn_count_deviation > 2.0:
            anomaly_flags.append("excessive_transaction_frequency")
        if amount_deviation > 2.0:
            anomaly_flags.append("unusually_high_amounts")
        if volume_ratio > 1.0:
            anomaly_flags.append("volume_exceeds_peer_maximum")

        peer_risk_score = min(
            1.0,
            max(0.0, txn_count_deviation / 4) * 0.3
            + max(0.0, amount_deviation / 4) * 0.4
            + max(0.0, (volume_ratio - 0.5) * 2) * 0.3,
        )

        return {
            "segment": segment,
            "segment_label": baseline["label"],
            "baselines": baseline,
            "deviations": deviations,
            "anomaly_flags": anomaly_flags,
            "peer_risk_score": round(peer_risk_score, 4),
        }


risk_engine = CustomerRiskEngine()
