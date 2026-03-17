"""AML Rule Engine - Configurable rules for transaction monitoring."""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


def _parse_naive(ts_str: str) -> datetime:
    """Parse an ISO-8601 string and return a timezone-naive datetime."""
    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    triggered: bool
    risk_score: float
    description: str
    details: dict


class AMLRuleEngine:
    """
    Rule engine for Anti-Money Laundering detection.
    Evaluates transactions against predefined AML rules and returns risk assessments.
    """

    def __init__(self, config):
        self.config = config
        self._transaction_cache: dict[str, list[dict]] = {}
        # Beneficiary-level cache for smurfing / fan-in detection
        self._beneficiary_cache: dict[str, list[dict]] = {}

    def evaluate(self, transaction: dict) -> list[RuleResult]:
        """Run all AML rules against a transaction and return triggered results."""
        results = []
        rules = [
            self._rule_large_cash_deposit,
            self._rule_structuring,
            self._rule_high_risk_country,
            self._rule_rapid_movement,
            self._rule_round_amount,
            self._rule_unusual_channel,
            self._rule_dormant_account,
            self._rule_ach_threshold,
            self._rule_swift_threshold,
            self._rule_card_atm_threshold,
            self._rule_cross_channel,
            self._rule_velocity_spike,
            self._rule_smurfing_fan_in,
        ]

        for rule_func in rules:
            result = rule_func(transaction)
            if result.triggered:
                results.append(result)
                logger.info(
                    f"Rule triggered: {result.rule_name} for customer={transaction.get('customer_id')}"
                )

        # Cache transaction for time-window rules
        customer_id = transaction.get("customer_id", "")
        if customer_id not in self._transaction_cache:
            self._transaction_cache[customer_id] = []
        self._transaction_cache[customer_id].append(transaction)
        # Keep only recent transactions
        cutoff = datetime.utcnow() - timedelta(hours=self.config.structuring_window_hours)
        self._transaction_cache[customer_id] = [
            t for t in self._transaction_cache[customer_id]
            if _parse_naive(t.get("timestamp", datetime.utcnow().isoformat())) > cutoff
        ]

        # Cache by beneficiary account for fan-in / smurfing detection
        beneficiary = transaction.get("beneficiary_account", "")
        if beneficiary:
            if beneficiary not in self._beneficiary_cache:
                self._beneficiary_cache[beneficiary] = []
            self._beneficiary_cache[beneficiary].append(transaction)
            self._beneficiary_cache[beneficiary] = [
                t for t in self._beneficiary_cache[beneficiary]
                if _parse_naive(t.get("timestamp", datetime.utcnow().isoformat())) > cutoff
            ]

        return results

    def calculate_composite_score(self, results: list[RuleResult]) -> float:
        """Calculate a composite risk score from all triggered rules."""
        if not results:
            return 0.0
        max_score = max(r.risk_score for r in results)
        avg_score = sum(r.risk_score for r in results) / len(results)
        # Weighted: 60% max + 40% average, capped at 1.0
        return min(1.0, 0.6 * max_score + 0.4 * avg_score)

    # --- Rule Implementations ---

    def _rule_large_cash_deposit(self, txn: dict) -> RuleResult:
        """Rule 1: Large cash deposits over threshold."""
        amount = Decimal(str(txn.get("amount", 0)))
        txn_type = txn.get("transaction_type", "")
        triggered = (
            amount > self.config.large_cash_threshold
            and txn_type == "cash_deposit"
        )
        return RuleResult(
            rule_id="AML-001",
            rule_name="Large Cash Deposit",
            triggered=triggered,
            risk_score=0.8 if triggered else 0.0,
            description=f"Cash deposit of {amount} exceeds threshold of {self.config.large_cash_threshold}",
            details={"amount": float(amount), "threshold": self.config.large_cash_threshold},
        )

    def _rule_structuring(self, txn: dict) -> RuleResult:
        """Rule 2: Structuring - multiple transactions below reporting limit within window."""
        customer_id = txn.get("customer_id", "")
        recent_txns = self._transaction_cache.get(customer_id, [])
        cash_txns = [
            t for t in recent_txns
            if t.get("transaction_type") in ("cash_deposit", "cash_withdrawal")
            and Decimal(str(t.get("amount", 0))) < self.config.structuring_threshold
        ]
        total = sum(Decimal(str(t.get("amount", 0))) for t in cash_txns)
        triggered = len(cash_txns) >= 3 and total > self.config.structuring_threshold
        return RuleResult(
            rule_id="AML-002",
            rule_name="Structuring Detection",
            triggered=triggered,
            risk_score=0.9 if triggered else 0.0,
            description=f"{len(cash_txns)} cash transactions totaling {total} within {self.config.structuring_window_hours}h",
            details={
                "transaction_count": len(cash_txns),
                "total_amount": float(total),
                "window_hours": self.config.structuring_window_hours,
            },
        )

    def _rule_high_risk_country(self, txn: dict) -> RuleResult:
        """Rule 3: Transfers to/from high-risk countries."""
        dest_country = txn.get("destination_country", "")
        src_country = txn.get("source_country", "")
        amount = Decimal(str(txn.get("amount", 0)))
        is_high_risk = (
            dest_country in self.config.high_risk_countries
            or src_country in self.config.high_risk_countries
        )
        triggered = is_high_risk and amount > 5000
        risk_country = dest_country if dest_country in self.config.high_risk_countries else src_country
        return RuleResult(
            rule_id="AML-003",
            rule_name="High-Risk Country Transfer",
            triggered=triggered,
            risk_score=0.85 if triggered else 0.0,
            description=f"Transfer of {amount} involving high-risk country {risk_country}",
            details={
                "amount": float(amount),
                "risk_country": risk_country,
                "destination": dest_country,
                "source": src_country,
            },
        )

    def _rule_rapid_movement(self, txn: dict) -> RuleResult:
        """Rule 4: Rapid fund movement - deposit followed by immediate transfer."""
        customer_id = txn.get("customer_id", "")
        recent_txns = self._transaction_cache.get(customer_id, [])
        txn_type = txn.get("transaction_type", "")

        has_recent_deposit = any(
            t.get("transaction_type") in ("cash_deposit", "check_deposit")
            for t in recent_txns[-5:]
        )
        is_transfer = txn_type in ("wire_transfer", "online_transfer", "ach_transfer")
        triggered = has_recent_deposit and is_transfer
        return RuleResult(
            rule_id="AML-004",
            rule_name="Rapid Fund Movement",
            triggered=triggered,
            risk_score=0.75 if triggered else 0.0,
            description="Deposit followed by immediate outbound transfer detected",
            details={
                "current_transaction_type": txn_type,
                "recent_deposit_detected": has_recent_deposit,
            },
        )

    def _rule_round_amount(self, txn: dict) -> RuleResult:
        """Rule 5: Unusually round amounts (potential indicator)."""
        amount = Decimal(str(txn.get("amount", 0)))
        is_round = amount > 1000 and amount % 1000 == 0
        is_large = amount >= 5000
        triggered = is_round and is_large
        return RuleResult(
            rule_id="AML-005",
            rule_name="Round Amount Transaction",
            triggered=triggered,
            risk_score=0.4 if triggered else 0.0,
            description=f"Large round amount transaction of {amount}",
            details={"amount": float(amount)},
        )

    def _rule_unusual_channel(self, txn: dict) -> RuleResult:
        """Rule 6: Transaction through unusual channel for the amount."""
        amount = Decimal(str(txn.get("amount", 0)))
        channel = txn.get("channel", "")
        triggered = amount > 50000 and channel in ("mobile", "online")
        return RuleResult(
            rule_id="AML-006",
            rule_name="Unusual Channel for Amount",
            triggered=triggered,
            risk_score=0.6 if triggered else 0.0,
            description=f"High-value transaction ({amount}) through {channel} channel",
            details={"amount": float(amount), "channel": channel},
        )

    def _rule_dormant_account(self, txn: dict) -> RuleResult:
        """Rule 7: Activity on previously dormant account (placeholder - needs account history)."""
        # In production, this would check account activity history from database
        is_dormant = txn.get("account_dormant", False)
        amount = Decimal(str(txn.get("amount", 0)))
        triggered = is_dormant and amount > 1000
        return RuleResult(
            rule_id="AML-007",
            rule_name="Dormant Account Activity",
            triggered=triggered,
            risk_score=0.7 if triggered else 0.0,
            description="Significant activity detected on previously dormant account",
            details={"amount": float(amount), "account_dormant": is_dormant},
        )

    # --- New rules: instrument-specific thresholds, cross-channel, velocity, smurfing ---

    def _rule_ach_threshold(self, txn: dict) -> RuleResult:
        """Rule 8: ACH transfer threshold – debits/credits exceeding $25,000."""
        amount = Decimal(str(txn.get("amount", 0)))
        txn_type = txn.get("transaction_type", "")
        triggered = txn_type == "ach_transfer" and amount > 25000
        return RuleResult(
            rule_id="AML-008",
            rule_name="ACH Transfer Threshold",
            triggered=triggered,
            risk_score=0.65 if triggered else 0.0,
            description=f"ACH transfer of {amount} exceeds $25,000 threshold",
            details={"amount": float(amount), "transaction_type": txn_type},
        )

    def _rule_swift_threshold(self, txn: dict) -> RuleResult:
        """Rule 9: SWIFT/wire transfer threshold – amounts exceeding $50,000."""
        amount = Decimal(str(txn.get("amount", 0)))
        txn_type = txn.get("transaction_type", "")
        channel = txn.get("channel", "")
        is_swift = txn_type in ("wire_transfer", "swift_transfer") or channel == "wire"
        triggered = is_swift and amount > 50000
        return RuleResult(
            rule_id="AML-009",
            rule_name="SWIFT/Wire Transfer Threshold",
            triggered=triggered,
            risk_score=0.7 if triggered else 0.0,
            description=f"SWIFT/wire of {amount} exceeds $50,000 MT103 threshold",
            details={"amount": float(amount), "transaction_type": txn_type, "channel": channel},
        )

    def _rule_card_atm_threshold(self, txn: dict) -> RuleResult:
        """Rule 10: Card/ATM threshold – POS or ATM transactions exceeding $5,000."""
        amount = Decimal(str(txn.get("amount", 0)))
        channel = txn.get("channel", "")
        txn_type = txn.get("transaction_type", "")
        is_card = channel in ("pos", "atm") or txn_type in ("card_purchase", "atm_withdrawal")
        triggered = is_card and amount > 5000
        return RuleResult(
            rule_id="AML-010",
            rule_name="Card/ATM Threshold",
            triggered=triggered,
            risk_score=0.55 if triggered else 0.0,
            description=f"Card/ATM transaction of {amount} exceeds $5,000 threshold",
            details={"amount": float(amount), "channel": channel, "transaction_type": txn_type},
        )

    def _rule_cross_channel(self, txn: dict) -> RuleResult:
        """Rule 11: Cross-channel anomaly – same customer uses 3+ distinct channels within window."""
        customer_id = txn.get("customer_id", "")
        recent_txns = self._transaction_cache.get(customer_id, [])
        channels_used = {t.get("channel", "") for t in recent_txns if t.get("channel")}
        channels_used.add(txn.get("channel", ""))
        channels_used.discard("")
        triggered = len(channels_used) >= 3
        return RuleResult(
            rule_id="AML-011",
            rule_name="Cross-Channel Anomaly",
            triggered=triggered,
            risk_score=0.5 if triggered else 0.0,
            description=f"Customer used {len(channels_used)} channels ({', '.join(sorted(channels_used))}) within {self.config.structuring_window_hours}h",
            details={"channels": sorted(channels_used), "count": len(channels_used)},
        )

    def _rule_velocity_spike(self, txn: dict) -> RuleResult:
        """Rule 12: Velocity spike – >10 transactions in 1 hour or >30 in 24 hours."""
        customer_id = txn.get("customer_id", "")
        recent_txns = self._transaction_cache.get(customer_id, [])
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        txns_1h = [
            t for t in recent_txns
            if _parse_naive(t.get("timestamp", now.isoformat())) > one_hour_ago
        ]
        txns_24h = recent_txns  # already filtered to window in evaluate()

        spike_1h = len(txns_1h) > 10
        spike_24h = len(txns_24h) > 30
        triggered = spike_1h or spike_24h
        score = 0.0
        if spike_1h:
            score = 0.8
        elif spike_24h:
            score = 0.55
        return RuleResult(
            rule_id="AML-012",
            rule_name="Velocity Spike",
            triggered=triggered,
            risk_score=score,
            description=f"Velocity: {len(txns_1h)} txns/1h, {len(txns_24h)} txns/24h",
            details={
                "txn_count_1h": len(txns_1h),
                "txn_count_24h": len(txns_24h),
                "threshold_1h": 10,
                "threshold_24h": 30,
            },
        )

    def _rule_smurfing_fan_in(self, txn: dict) -> RuleResult:
        """Rule 13: Smurfing / Fan-in – 3+ distinct senders depositing into same beneficiary within window."""
        beneficiary = txn.get("beneficiary_account", "")
        if not beneficiary:
            return RuleResult(
                rule_id="AML-013",
                rule_name="Smurfing / Fan-In Detection",
                triggered=False,
                risk_score=0.0,
                description="No beneficiary account in transaction",
                details={},
            )
        recent = self._beneficiary_cache.get(beneficiary, [])
        distinct_senders = {t.get("customer_id", "") for t in recent if t.get("customer_id")}
        distinct_senders.add(txn.get("customer_id", ""))
        distinct_senders.discard("")
        total_amount = sum(Decimal(str(t.get("amount", 0))) for t in recent)
        triggered = len(distinct_senders) >= 3
        return RuleResult(
            rule_id="AML-013",
            rule_name="Smurfing / Fan-In Detection",
            triggered=triggered,
            risk_score=0.85 if triggered else 0.0,
            description=f"{len(distinct_senders)} distinct senders to account {beneficiary}, total {total_amount}",
            details={
                "beneficiary_account": beneficiary,
                "distinct_senders": len(distinct_senders),
                "total_amount": float(total_amount),
            },
        )
