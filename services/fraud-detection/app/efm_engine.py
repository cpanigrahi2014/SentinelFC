"""Enterprise Fraud Management (EFM) — Comprehensive fraud detection engines."""

import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ─── MCC Risk Table ─────────────────────────────────────────────────────────
HIGH_RISK_MCC = {
    "5967": "Direct Marketing – Inbound Telemarketing",
    "5966": "Direct Marketing – Outbound Telemarketing",
    "7995": "Gambling / Betting",
    "5912": "Drug Stores / Pharmacies",
    "5944": "Jewelry / Watch / Clock Stores",
    "5094": "Precious Stones / Metals",
    "4829": "Money Transfer / Wire Transfer",
    "6051": "Quasi-Cash – Cryptocurrency",
    "6012": "Financial Institutions – Merchandise / Services",
    "6211": "Securities – Brokers / Dealers",
    "7801": "Online Gambling",
    "7802": "Horse/Dog Racing (government-licensed)",
}

FOREIGN_HIGH_RISK_COUNTRIES = {"RU", "NG", "PH", "RO", "BR", "UA", "VN", "CN", "KP", "IR", "SY"}


class DeviceFingerprintEngine:
    """Device fingerprinting and trust scoring."""

    def __init__(self):
        # customer_id -> list of known device records
        self._device_registry: dict[str, list[dict]] = defaultdict(list)

    def register_device(self, customer_id: str, device: dict) -> dict:
        """Register/update a device for a customer, return trust assessment."""
        known = self._device_registry.get(customer_id, [])
        fp = device.get("fingerprint_hash", device.get("device_id", ""))
        existing = next((d for d in known if d["fingerprint_hash"] == fp), None)

        if existing:
            existing["last_seen"] = datetime.utcnow().isoformat()
            existing["session_count"] = existing.get("session_count", 1) + 1
            return {
                "device_id": device.get("device_id"),
                "is_known": True,
                "trust_score": min(1.0, 0.5 + existing["session_count"] * 0.05),
                "device_age_days": (datetime.utcnow() - datetime.fromisoformat(existing["first_seen"])).days,
                "risk_flags": self._assess_device_risk(device),
            }

        new_record = {
            "fingerprint_hash": fp,
            "device_id": device.get("device_id", ""),
            "browser_ua": device.get("browser_ua", ""),
            "ip_address": device.get("ip_address", ""),
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "session_count": 1,
        }
        self._device_registry[customer_id].append(new_record)

        return {
            "device_id": device.get("device_id"),
            "is_known": False,
            "trust_score": 0.15,
            "device_age_days": 0,
            "risk_flags": ["new_device"] + self._assess_device_risk(device),
        }

    def _assess_device_risk(self, device: dict) -> list[str]:
        flags = []
        if device.get("vpn_flag") or device.get("is_vpn"):
            flags.append("vpn_detected")
        if device.get("is_tor"):
            flags.append("tor_detected")
        if device.get("is_proxy"):
            flags.append("proxy_detected")
        if device.get("is_emulator"):
            flags.append("emulator_detected")
        ua = device.get("browser_ua", "").lower()
        if "headless" in ua or "phantom" in ua:
            flags.append("headless_browser")
        return flags

    def get_customer_devices(self, customer_id: str) -> list[dict]:
        return self._device_registry.get(customer_id, [])

    def score_device(self, customer_id: str, device: dict) -> float:
        """Return 0-1 risk score for a device (1 = highest risk)."""
        result = self.register_device(customer_id, device)
        risk = 1.0 - result["trust_score"]
        risk += len(result["risk_flags"]) * 0.1
        return min(risk, 1.0)


class BehavioralBiometricsEngine:
    """Behavioral biometrics risk scoring based on session telemetry."""

    def __init__(self):
        # customer_id -> list of baseline session profiles
        self._baselines: dict[str, list[dict]] = defaultdict(list)

    def build_baseline(self, customer_id: str, session: dict):
        """Add a session profile to the customer's baseline."""
        profile = {
            "typing_speed_wpm": session.get("typing_speed_wpm", 0),
            "avg_keystroke_interval_ms": session.get("avg_keystroke_interval_ms", 0),
            "mouse_movement_entropy": session.get("mouse_movement_entropy", 0),
            "scroll_pattern_score": session.get("scroll_pattern_score", 0),
            "swipe_velocity_avg": session.get("swipe_velocity_avg", 0),
            "session_duration_s": session.get("session_duration_s", 0),
            "navigation_pattern_hash": session.get("navigation_pattern_hash", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }
        baseline = self._baselines[customer_id]
        baseline.append(profile)
        if len(baseline) > 50:
            self._baselines[customer_id] = baseline[-50:]

    def score_session(self, customer_id: str, session: dict) -> dict:
        """Score a session against the customer baseline. Returns anomaly score 0-1."""
        baseline = self._baselines.get(customer_id, [])
        if len(baseline) < 3:
            return {
                "anomaly_score": 0.3,
                "confidence": 0.2,
                "deviations": [],
                "baseline_sessions": len(baseline),
                "verdict": "insufficient_baseline",
            }

        deviations = []
        metrics = {
            "typing_speed_wpm": session.get("typing_speed_wpm", 0),
            "avg_keystroke_interval_ms": session.get("avg_keystroke_interval_ms", 0),
            "mouse_movement_entropy": session.get("mouse_movement_entropy", 0),
            "swipe_velocity_avg": session.get("swipe_velocity_avg", 0),
        }

        anomaly = 0.0
        for key, val in metrics.items():
            bl_vals = [b[key] for b in baseline if b.get(key, 0) > 0]
            if not bl_vals:
                continue
            mean = sum(bl_vals) / len(bl_vals)
            std = (sum((v - mean) ** 2 for v in bl_vals) / len(bl_vals)) ** 0.5
            if std > 0 and val > 0:
                z = abs(val - mean) / std
                if z > 2.5:
                    deviations.append({"metric": key, "z_score": round(z, 2), "current": val, "baseline_mean": round(mean, 2)})
                    anomaly += min(z / 5.0, 0.3)

        anomaly = min(anomaly, 1.0)
        return {
            "anomaly_score": round(anomaly, 4),
            "confidence": min(len(baseline) / 20.0, 1.0),
            "deviations": deviations,
            "baseline_sessions": len(baseline),
            "verdict": "anomalous" if anomaly >= 0.6 else "normal" if anomaly < 0.3 else "borderline",
        }


class AccountTakeoverDetector:
    """Detects account takeover patterns: new device + password reset + high-value transfer."""

    def __init__(self):
        # customer_id -> list of recent security events
        self._events: dict[str, list[dict]] = defaultdict(list)

    def record_event(self, customer_id: str, event_type: str, metadata: dict = None):
        """Record a security event. event_type: login, password_reset, device_change, mfa_change, high_value_transfer."""
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        events = self._events[customer_id]
        events.append(event)
        # Keep last 100 events
        if len(events) > 100:
            self._events[customer_id] = events[-100:]

    def assess(self, customer_id: str, window_hours: int = 24) -> dict:
        """Assess ATO risk for a customer based on recent event patterns."""
        events = self._events.get(customer_id, [])
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent = [e for e in events if datetime.fromisoformat(e["timestamp"]) > cutoff]

        types = [e["type"] for e in recent]
        signals = {
            "new_device_login": "device_change" in types or "login" in types,
            "password_reset": "password_reset" in types,
            "mfa_change": "mfa_change" in types,
            "high_value_transfer": "high_value_transfer" in types,
            "multiple_failed_logins": sum(1 for e in recent if e["type"] == "failed_login") >= 3,
        }

        score = 0.0
        triggered = []
        if signals["new_device_login"] and signals["password_reset"]:
            score += 0.4
            triggered.append("new_device_plus_password_reset")
        if signals["new_device_login"] and signals["high_value_transfer"]:
            score += 0.35
            triggered.append("new_device_plus_high_value_transfer")
        if signals["password_reset"] and signals["high_value_transfer"]:
            score += 0.25
            triggered.append("password_reset_plus_transfer")
        if signals["mfa_change"]:
            score += 0.2
            triggered.append("mfa_change")
        if signals["multiple_failed_logins"]:
            score += 0.15
            triggered.append("multiple_failed_logins")

        # Full ATO chain: all 3 key signals
        if signals["new_device_login"] and signals["password_reset"] and signals["high_value_transfer"]:
            score = max(score, 0.95)
            triggered.append("FULL_ATO_CHAIN")

        score = min(score, 1.0)
        return {
            "ato_score": round(score, 4),
            "is_ato": score >= 0.7,
            "signals": signals,
            "triggered_patterns": triggered,
            "recent_events": len(recent),
            "risk_level": "critical" if score >= 0.85 else "high" if score >= 0.65 else "medium" if score >= 0.35 else "low",
        }


class MuleAccountDetector:
    """Detects mule account patterns: multiple incoming P2P → immediate withdrawals."""

    def __init__(self):
        # customer_id -> list of transaction events
        self._txn_cache: dict[str, list[dict]] = defaultdict(list)

    def add_transaction(self, customer_id: str, txn: dict):
        """Add a transaction to the mule detection cache."""
        entry = {
            "amount": float(txn.get("amount", 0)),
            "type": txn.get("transaction_type", ""),
            "direction": txn.get("direction", "inbound" if txn.get("transaction_type", "").startswith("p2p_receive") else "outbound"),
            "channel": txn.get("channel", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "source": txn.get("source_account", ""),
        }
        cache = self._txn_cache[customer_id]
        cache.append(entry)
        if len(cache) > 200:
            self._txn_cache[customer_id] = cache[-200:]

    def assess(self, customer_id: str, window_hours: int = 48) -> dict:
        """Assess mule account risk based on transaction patterns."""
        cache = self._txn_cache.get(customer_id, [])
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent = [t for t in cache if datetime.fromisoformat(t["timestamp"]) > cutoff]

        inbound = [t for t in recent if t["direction"] == "inbound"]
        outbound = [t for t in recent if t["direction"] == "outbound"]

        total_in = sum(t["amount"] for t in inbound)
        total_out = sum(t["amount"] for t in outbound)
        unique_senders = len(set(t["source"] for t in inbound if t["source"]))

        patterns = []
        score = 0.0

        # Pattern 1: Multiple distinct senders (fan-in)
        if unique_senders >= 3:
            score += 0.3
            patterns.append({"pattern": "fan_in_multiple_senders", "detail": f"{unique_senders} unique senders"})

        # Pattern 2: Rapid drain — high outbound ratio within short window
        if total_in > 0 and total_out / max(total_in, 1) > 0.8 and len(outbound) > 0:
            score += 0.35
            patterns.append({"pattern": "rapid_drain", "detail": f"Out/In ratio: {total_out/total_in:.1%}"})

        # Pattern 3: High volume with rapid cycling
        if total_in > 5000 and len(inbound) >= 3 and len(outbound) >= 2:
            score += 0.2
            patterns.append({"pattern": "high_volume_cycling", "detail": f"${total_in:,.0f} in, ${total_out:,.0f} out"})

        # Pattern 4: Cash withdrawal after electronic deposits
        cash_out = [t for t in outbound if "cash" in t.get("type", "") or "atm" in t.get("channel", "")]
        electronic_in = [t for t in inbound if t.get("channel", "") in ("online", "mobile")]
        if cash_out and electronic_in and len(electronic_in) >= 2:
            score += 0.25
            patterns.append({"pattern": "electronic_in_cash_out", "detail": f"{len(electronic_in)} e-deposits → {len(cash_out)} cash withdrawals"})

        # Pattern 5: Account age indicator (young account with high activity = suspicious)
        if len(recent) > 10:
            score += 0.1
            patterns.append({"pattern": "high_frequency_new_pattern", "detail": f"{len(recent)} txns in {window_hours}h"})

        score = min(score, 1.0)
        return {
            "mule_score": round(score, 4),
            "is_mule": score >= 0.6,
            "patterns": patterns,
            "stats": {
                "total_inbound": round(total_in, 2),
                "total_outbound": round(total_out, 2),
                "unique_senders": unique_senders,
                "inbound_count": len(inbound),
                "outbound_count": len(outbound),
            },
            "risk_level": "critical" if score >= 0.85 else "high" if score >= 0.60 else "medium" if score >= 0.35 else "low",
        }


class PaymentFraudDetector:
    """Detects payment-specific fraud across ACH, Zelle, RTP, SWIFT channels."""

    PAYMENT_LIMITS = {
        "zelle": {"daily": 2500, "per_txn": 1000},
        "rtp": {"daily": 100000, "per_txn": 25000},
        "ach": {"daily": 50000, "per_txn": 25000},
        "swift": {"daily": 500000, "per_txn": 100000},
    }

    def __init__(self):
        self._txn_cache: dict[str, list[dict]] = defaultdict(list)

    def assess_payment(self, customer_id: str, payment: dict) -> dict:
        """Assess fraud risk for a specific payment."""
        amount = float(payment.get("amount", 0))
        rail = payment.get("payment_rail", payment.get("payment_type", "")).lower()
        dest_country = payment.get("destination_country", "US")

        # Cache for daily aggregation
        cache = self._txn_cache[customer_id]
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = [t for t in cache if datetime.fromisoformat(t["timestamp"]) > cutoff]
        daily_total = sum(t["amount"] for t in recent if t["rail"] == rail)

        cache.append({"amount": amount, "rail": rail, "timestamp": datetime.utcnow().isoformat()})
        if len(cache) > 200:
            self._txn_cache[customer_id] = cache[-200:]

        flags = []
        score = 0.0
        limits = self.PAYMENT_LIMITS.get(rail, {})

        # Per-transaction limit check
        if limits.get("per_txn") and amount > limits["per_txn"]:
            score += 0.3
            flags.append(f"{rail}_per_txn_limit_exceeded")

        # Daily aggregate limit check
        if limits.get("daily") and (daily_total + amount) > limits["daily"]:
            score += 0.25
            flags.append(f"{rail}_daily_limit_exceeded")

        # High-risk destination
        if dest_country in FOREIGN_HIGH_RISK_COUNTRIES:
            score += 0.2
            flags.append("high_risk_destination")

        # Rapid succession (multiple same-rail payments in short window)
        last_hour = [t for t in recent if t["rail"] == rail and datetime.fromisoformat(t["timestamp"]) > datetime.utcnow() - timedelta(hours=1)]
        if len(last_hour) >= 3:
            score += 0.2
            flags.append(f"{rail}_rapid_succession")

        # First-time rail usage with high amount
        all_rail_txns = [t for t in self._txn_cache[customer_id] if t["rail"] == rail]
        if len(all_rail_txns) <= 1 and amount > 1000:
            score += 0.15
            flags.append(f"first_time_{rail}_high_amount")

        score = min(score, 1.0)
        return {
            "payment_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.5,
            "payment_rail": rail,
            "amount": amount,
            "flags": flags,
            "daily_total": round(daily_total + amount, 2),
            "daily_limit": limits.get("daily"),
            "risk_level": "critical" if score >= 0.80 else "high" if score >= 0.55 else "medium" if score >= 0.30 else "low",
        }


class CardFraudDetector:
    """Detects card fraud: unusual MCC + foreign location patterns."""

    def __init__(self):
        self._customer_home: dict[str, str] = {}
        self._customer_mcc_history: dict[str, list[str]] = defaultdict(list)

    def set_home_country(self, customer_id: str, country: str):
        self._customer_home[customer_id] = country

    def assess_card_transaction(self, customer_id: str, txn: dict) -> dict:
        """Assess card fraud risk for a transaction."""
        mcc = str(txn.get("merchant_category", txn.get("mcc", "")))
        merchant_country = txn.get("merchant_country", txn.get("destination_country", "US"))
        amount = float(txn.get("amount", 0))
        home_country = self._customer_home.get(customer_id, "US")

        # Track MCC history
        history = self._customer_mcc_history[customer_id]
        history.append(mcc)
        if len(history) > 100:
            self._customer_mcc_history[customer_id] = history[-100:]

        flags = []
        score = 0.0

        # High-risk MCC
        if mcc in HIGH_RISK_MCC:
            score += 0.25
            flags.append(f"high_risk_mcc_{mcc}:{HIGH_RISK_MCC[mcc]}")

        # Foreign location
        is_foreign = merchant_country != home_country
        if is_foreign:
            score += 0.15
            flags.append(f"foreign_merchant_country_{merchant_country}")

        # High-risk foreign country
        if is_foreign and merchant_country in FOREIGN_HIGH_RISK_COUNTRIES:
            score += 0.2
            flags.append("high_risk_foreign_country")

        # MCC + foreign combination (card fraud scenario)
        if mcc in HIGH_RISK_MCC and is_foreign:
            score += 0.25
            flags.append("high_risk_mcc_plus_foreign_location")

        # Unusual MCC (not in customer history)
        if mcc and mcc not in history[:-1]:
            score += 0.1
            flags.append("new_mcc_for_customer")

        # High amount at unusual merchant
        if mcc in HIGH_RISK_MCC and amount > 5000:
            score += 0.15
            flags.append("high_amount_at_risky_merchant")

        score = min(score, 1.0)
        return {
            "card_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.5,
            "mcc": mcc,
            "mcc_description": HIGH_RISK_MCC.get(mcc, "Standard"),
            "merchant_country": merchant_country,
            "home_country": home_country,
            "is_foreign": is_foreign,
            "flags": flags,
            "risk_level": "critical" if score >= 0.80 else "high" if score >= 0.55 else "medium" if score >= 0.30 else "low",
        }


class CrossChannelFraudCorrelator:
    """Temporal cross-channel fraud correlation: login → password change → transfer within time window."""

    def __init__(self):
        self._event_sequences: dict[str, list[dict]] = defaultdict(list)

    def record_channel_event(self, customer_id: str, event: dict):
        """Record a channel event: channel, event_type, amount, timestamp."""
        entry = {
            "channel": event.get("channel", ""),
            "event_type": event.get("event_type", ""),
            "amount": float(event.get("amount", 0)),
            "timestamp": datetime.utcnow().isoformat(),
        }
        seq = self._event_sequences[customer_id]
        seq.append(entry)
        if len(seq) > 200:
            self._event_sequences[customer_id] = seq[-200:]

    def assess(self, customer_id: str, window_hours: int = 4) -> dict:
        """Assess cross-channel fraud correlation patterns."""
        seq = self._event_sequences.get(customer_id, [])
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent = [e for e in seq if datetime.fromisoformat(e["timestamp"]) > cutoff]

        channels_used = list(set(e["channel"] for e in recent if e["channel"]))
        event_types = [e["event_type"] for e in recent]

        patterns = []
        score = 0.0

        # Pattern 1: Multi-channel activity (3+ channels quickly)
        if len(channels_used) >= 3:
            score += 0.25
            patterns.append({"pattern": "multi_channel_burst", "detail": f"{len(channels_used)} channels in {window_hours}h", "channels": channels_used})

        # Pattern 2: Login on mobile + password change on web + transfer from branch
        login_channels = [e["channel"] for e in recent if e["event_type"] in ("login", "session_start")]
        change_channels = [e["channel"] for e in recent if e["event_type"] in ("password_change", "password_reset", "mfa_change")]
        transfer_channels = [e["channel"] for e in recent if e["event_type"] in ("transfer", "wire", "payment") and e["amount"] > 0]

        if login_channels and change_channels and transfer_channels:
            if len(set(login_channels + change_channels + transfer_channels)) >= 2:
                score += 0.4
                patterns.append({"pattern": "login_change_transfer_sequence", "detail": "login → credential change → transfer across channels"})

        # Pattern 3: High-value transfer shortly after credential change
        if change_channels and transfer_channels:
            score += 0.25
            patterns.append({"pattern": "credential_change_then_transfer", "detail": "Credential change followed by transfer"})

        # Pattern 4: Unusual channel for high-value transaction
        high_val = [e for e in recent if e["amount"] > 10000 and e["channel"] in ("mobile", "online")]
        if high_val:
            score += 0.15
            patterns.append({"pattern": "high_value_digital", "detail": f"{len(high_val)} high-value digital txn(s)"})

        score = min(score, 1.0)
        return {
            "correlation_score": round(score, 4),
            "is_suspicious": score >= 0.5,
            "channels_used": channels_used,
            "event_count": len(recent),
            "patterns": patterns,
            "risk_level": "critical" if score >= 0.80 else "high" if score >= 0.55 else "medium" if score >= 0.35 else "low",
        }


class EFMOrchestrator:
    """Master orchestrator that runs all EFM engines and produces a unified fraud assessment."""

    def __init__(self):
        self.device_engine = DeviceFingerprintEngine()
        self.biometrics_engine = BehavioralBiometricsEngine()
        self.ato_detector = AccountTakeoverDetector()
        self.mule_detector = MuleAccountDetector()
        self.payment_fraud = PaymentFraudDetector()
        self.card_fraud = CardFraudDetector()
        self.cross_channel = CrossChannelFraudCorrelator()

    def full_assessment(self, customer_id: str, context: dict) -> dict:
        """Run all applicable EFM engines and produce a unified score."""
        results = {}
        sub_scores = []

        # Device assessment
        if context.get("device"):
            dr = self.device_engine.register_device(customer_id, context["device"])
            results["device"] = dr
            sub_scores.append(("device", 1.0 - dr["trust_score"], 0.20))

        # Biometrics assessment
        if context.get("session"):
            br = self.biometrics_engine.score_session(customer_id, context["session"])
            results["biometrics"] = br
            sub_scores.append(("biometrics", br["anomaly_score"], 0.15))

        # ATO assessment
        ato = self.ato_detector.assess(customer_id)
        results["ato"] = ato
        sub_scores.append(("ato", ato["ato_score"], 0.25))

        # Mule assessment
        mule = self.mule_detector.assess(customer_id)
        results["mule"] = mule
        sub_scores.append(("mule", mule["mule_score"], 0.20))

        # Payment fraud
        if context.get("payment"):
            pf = self.payment_fraud.assess_payment(customer_id, context["payment"])
            results["payment_fraud"] = pf
            sub_scores.append(("payment_fraud", pf["payment_fraud_score"], 0.10))

        # Card fraud
        if context.get("card_txn"):
            cf = self.card_fraud.assess_card_transaction(customer_id, context["card_txn"])
            results["card_fraud"] = cf
            sub_scores.append(("card_fraud", cf["card_fraud_score"], 0.10))

        # Cross-channel
        xc = self.cross_channel.assess(customer_id)
        results["cross_channel"] = xc
        sub_scores.append(("cross_channel", xc["correlation_score"], 0.10))

        # Weighted composite
        if sub_scores:
            total_weight = sum(w for _, _, w in sub_scores)
            composite = sum(s * w for _, s, w in sub_scores) / total_weight if total_weight > 0 else 0.0
        else:
            composite = 0.0

        return {
            "customer_id": customer_id,
            "composite_fraud_score": round(composite, 4),
            "risk_level": "critical" if composite >= 0.80 else "high" if composite >= 0.55 else "medium" if composite >= 0.30 else "low",
            "engines_run": [name for name, _, _ in sub_scores],
            "sub_scores": {name: round(s, 4) for name, s, _ in sub_scores},
            "details": results,
        }
