"""Payments Fraud (PMF) — ACH, Wire, RTP/Zelle, Card-Not-Present, Check (image analysis)."""

import logging
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# 1. ACH Fraud Detector
# ═════════════════════════════════════════════════════════════════════════════
class ACHFraudDetector:
    """Detects fraudulent ACH originations: unauthorized debits, velocity spikes,
    account validation failures, NACHA return code analysis, payee manipulation."""

    RETURN_CODE_RISK = {
        "R01": 0.10,  # Insufficient funds
        "R02": 0.25,  # Account closed
        "R03": 0.30,  # No account / unable to locate
        "R05": 0.35,  # Unauthorized debit
        "R07": 0.40,  # Authorization revoked
        "R08": 0.45,  # Payment stopped
        "R10": 0.60,  # Customer advises not authorized
        "R11": 0.15,  # Check truncation entry return
        "R29": 0.50,  # Corporate customer advises not authorized
    }

    MAX_DAILY_ACH = 10
    LARGE_ACH_THRESHOLD = 25_000

    def __init__(self):
        self._customer_history: dict[str, list[dict]] = defaultdict(list)
        self._return_history: dict[str, list[str]] = defaultdict(list)

    def record_transaction(self, customer_id: str, txn: dict) -> None:
        self._customer_history[customer_id].append({"ts": datetime.utcnow(), **txn})
        self._customer_history[customer_id] = self._customer_history[customer_id][-200:]

    def record_return(self, customer_id: str, return_code: str) -> None:
        self._return_history[customer_id].append(return_code)
        self._return_history[customer_id] = self._return_history[customer_id][-50:]

    def assess(self, customer_id: str, transaction: dict) -> dict:
        flags = []
        score = 0.0
        now = datetime.utcnow()
        amount = transaction.get("amount", 0)
        direction = transaction.get("direction", "debit")  # debit or credit

        # ── Unauthorized debit pattern ──
        if direction == "debit" and transaction.get("authorization_missing", False):
            score += 0.40
            flags.append({"flag": "unauthorized_debit", "amount": amount})

        # ── Large transaction threshold ──
        if amount > self.LARGE_ACH_THRESHOLD:
            score += 0.15
            flags.append({"flag": "large_ach_amount", "amount": amount, "threshold": self.LARGE_ACH_THRESHOLD})

        # ── Velocity: too many ACH in 24h ──
        history = self._customer_history.get(customer_id, [])
        recent = [h for h in history if (now - h["ts"]).total_seconds() < 86400]
        if len(recent) > self.MAX_DAILY_ACH:
            score += 0.25
            flags.append({"flag": "ach_velocity_spike", "count_24h": len(recent), "limit": self.MAX_DAILY_ACH})

        # ── Return code history ──
        returns = self._return_history.get(customer_id, [])
        if returns:
            worst = max(returns[-5:], key=lambda rc: self.RETURN_CODE_RISK.get(rc, 0))
            risk_val = self.RETURN_CODE_RISK.get(worst, 0)
            if risk_val >= 0.25:
                score += risk_val * 0.5
                flags.append({"flag": "risky_return_history", "recent_returns": returns[-5:], "worst_code": worst})

        # ── New payee + large amount ──
        if transaction.get("new_payee", False) and amount > 5000:
            score += 0.20
            flags.append({"flag": "new_payee_large_amount", "amount": amount, "payee": transaction.get("payee_name", "")})

        # ── Same-day ACH with micro-deposit probe ──
        if transaction.get("same_day", False) and transaction.get("micro_deposit_probe", False):
            score += 0.30
            flags.append({"flag": "micro_deposit_probe_sameday"})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.70 else "high" if score >= 0.45 else "medium" if score >= 0.25 else "low"
        return {
            "customer_id": customer_id,
            "ach_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.40,
            "risk_level": risk,
            "flags": flags,
            "transaction_amount": amount,
            "direction": direction,
        }


# ═════════════════════════════════════════════════════════════════════════════
# 2. Wire Fraud Detector
# ═════════════════════════════════════════════════════════════════════════════
class WireFraudDetector:
    """Detects wire transfer fraud: BEC patterns, unusual beneficiary countries,
    amount anomalies, urgency indicators, SWIFT code validation."""

    HIGH_RISK_COUNTRIES = {"AF", "IR", "KP", "SY", "YE", "MM", "LY", "SO", "SS", "VE", "CU"}
    BEC_SIGNALS = [
        "ceo_impersonation", "vendor_invoice_change", "urgency_language",
        "account_change_request", "reply_to_mismatch", "domain_typosquat",
    ]

    def __init__(self):
        self._customer_history: dict[str, list[dict]] = defaultdict(list)
        self._beneficiary_baseline: dict[str, set[str]] = defaultdict(set)

    def record_transfer(self, customer_id: str, transfer: dict) -> None:
        self._customer_history[customer_id].append({"ts": datetime.utcnow(), **transfer})
        self._customer_history[customer_id] = self._customer_history[customer_id][-100:]
        bene = transfer.get("beneficiary_account", "")
        if bene:
            self._beneficiary_baseline[customer_id].add(bene)

    def assess(self, customer_id: str, transfer: dict) -> dict:
        flags = []
        score = 0.0
        amount = transfer.get("amount", 0)
        country = transfer.get("beneficiary_country", "").upper()

        # ── High-risk destination country ──
        if country in self.HIGH_RISK_COUNTRIES:
            score += 0.35
            flags.append({"flag": "high_risk_country", "country": country})

        # ── BEC (Business Email Compromise) signals ──
        bec_present = [s for s in self.BEC_SIGNALS if s in transfer.get("signals", [])]
        if bec_present:
            bec_ratio = len(bec_present) / len(self.BEC_SIGNALS)
            bec_score = min(bec_ratio * 1.8, 1.0) if len(bec_present) >= 3 else bec_ratio * 0.7
            score += bec_score * 0.4
            flags.append({"flag": "bec_indicators", "matched_signals": bec_present, "bec_score": round(bec_score, 4)})

        # ── Amount anomaly: significantly larger than baseline ──
        history = self._customer_history.get(customer_id, [])
        if history:
            avg_amount = sum(h.get("amount", 0) for h in history) / len(history)
            if avg_amount > 0 and amount > avg_amount * 5:
                score += 0.25
                flags.append({"flag": "amount_anomaly", "amount": amount,
                              "avg_historical": round(avg_amount, 2), "multiplier": round(amount / avg_amount, 1)})

        # ── New beneficiary ──
        bene_account = transfer.get("beneficiary_account", "")
        known = self._beneficiary_baseline.get(customer_id, set())
        if bene_account and known and bene_account not in known:
            score += 0.15
            flags.append({"flag": "new_beneficiary", "beneficiary_account": bene_account})

        # ── Urgency / after-hours ──
        if transfer.get("urgency", False):
            score += 0.10
            flags.append({"flag": "urgency_indicator"})

        # ── Invalid / suspicious SWIFT code ──
        swift = transfer.get("swift_code", "")
        if swift and (len(swift) not in (8, 11) or not swift[:4].isalpha()):
            score += 0.20
            flags.append({"flag": "invalid_swift_code", "swift_code": swift})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.70 else "high" if score >= 0.45 else "medium" if score >= 0.25 else "low"
        return {
            "customer_id": customer_id,
            "wire_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.40,
            "risk_level": risk,
            "flags": flags,
            "transaction_amount": amount,
            "beneficiary_country": country,
        }


# ═════════════════════════════════════════════════════════════════════════════
# 3. RTP / Zelle Fraud Detector
# ═════════════════════════════════════════════════════════════════════════════
class RTPZelleFraudDetector:
    """Detects real-time payment fraud: push-payment scams, velocity abuse,
    new-recipient large amounts, P2P fan-out patterns, account age risk."""

    MAX_HOURLY_TRANSACTIONS = 15
    LARGE_RTP_THRESHOLD = 5_000

    def __init__(self):
        self._customer_history: dict[str, list[dict]] = defaultdict(list)
        self._recipients: dict[str, set[str]] = defaultdict(set)

    def record_payment(self, customer_id: str, payment: dict) -> None:
        self._customer_history[customer_id].append({"ts": datetime.utcnow(), **payment})
        self._customer_history[customer_id] = self._customer_history[customer_id][-200:]
        recipient = payment.get("recipient_id", "")
        if recipient:
            self._recipients[customer_id].add(recipient)

    def assess(self, customer_id: str, payment: dict) -> dict:
        flags = []
        score = 0.0
        now = datetime.utcnow()
        amount = payment.get("amount", 0)
        channel = payment.get("channel", "rtp")  # "rtp" or "zelle"

        # ── Push-payment scam signals ──
        scam_signals = payment.get("signals", [])
        push_scam_indicators = ["urgency", "impersonation", "too_good_to_be_true",
                                "emotional_manipulation", "prize_notification"]
        matched_scam = [s for s in push_scam_indicators if s in scam_signals]
        if matched_scam:
            score += min(len(matched_scam) * 0.15, 0.45)
            flags.append({"flag": "push_payment_scam", "matched_signals": matched_scam})

        # ── Velocity: too many in 1 hour ──
        history = self._customer_history.get(customer_id, [])
        recent_1h = [h for h in history if (now - h["ts"]).total_seconds() < 3600]
        if len(recent_1h) > self.MAX_HOURLY_TRANSACTIONS:
            score += 0.25
            flags.append({"flag": "rtp_velocity_spike", "count_1h": len(recent_1h),
                          "limit": self.MAX_HOURLY_TRANSACTIONS})

        # ── Large amount to new recipient ──
        recipient = payment.get("recipient_id", "")
        known = self._recipients.get(customer_id, set())
        if recipient and known and recipient not in known and amount > self.LARGE_RTP_THRESHOLD:
            score += 0.30
            flags.append({"flag": "new_recipient_large_amount", "amount": amount,
                          "recipient_id": recipient, "threshold": self.LARGE_RTP_THRESHOLD})
        elif recipient and known and recipient not in known:
            score += 0.10
            flags.append({"flag": "new_recipient", "recipient_id": recipient})

        # ── Fan-out pattern: many different recipients in short time ──
        recent_recipients = {h.get("recipient_id") for h in recent_1h if h.get("recipient_id")}
        if len(recent_recipients) >= 5:
            score += 0.25
            flags.append({"flag": "fan_out_pattern", "unique_recipients_1h": len(recent_recipients)})

        # ── Account age risk ──
        account_age_days = payment.get("account_age_days", 365)
        if account_age_days < 7:
            score += 0.20
            flags.append({"flag": "new_account_risk", "account_age_days": account_age_days})
        elif account_age_days < 30:
            score += 0.10
            flags.append({"flag": "young_account_risk", "account_age_days": account_age_days})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.70 else "high" if score >= 0.45 else "medium" if score >= 0.25 else "low"
        return {
            "customer_id": customer_id,
            "rtp_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.40,
            "risk_level": risk,
            "flags": flags,
            "transaction_amount": amount,
            "channel": channel,
        }


# ═════════════════════════════════════════════════════════════════════════════
# 4. Card-Not-Present (CNP) Fraud Detector
# ═════════════════════════════════════════════════════════════════════════════
class CNPFraudDetector:
    """Detects card-not-present fraud: AVS/CVV mismatches, velocity testing,
    device/IP anomaly, BIN attack, geo mismatch, 3-D Secure bypass."""

    def __init__(self):
        self._card_history: dict[str, list[dict]] = defaultdict(list)
        self._bin_attempts: dict[str, list[dict]] = defaultdict(list)

    def record_transaction(self, card_hash: str, txn: dict) -> None:
        self._card_history[card_hash].append({"ts": datetime.utcnow(), **txn})
        self._card_history[card_hash] = self._card_history[card_hash][-200:]
        bin_prefix = txn.get("bin_prefix", "")
        if bin_prefix:
            self._bin_attempts[bin_prefix].append({"ts": datetime.utcnow(), "card_hash": card_hash})
            self._bin_attempts[bin_prefix] = self._bin_attempts[bin_prefix][-500:]

    def assess(self, card_hash: str, transaction: dict) -> dict:
        flags = []
        score = 0.0
        now = datetime.utcnow()

        # ── AVS mismatch ──
        avs_code = transaction.get("avs_code", "Y")
        if avs_code in ("N", "A", "Z"):
            level = 0.25 if avs_code == "N" else 0.15
            score += level
            flags.append({"flag": "avs_mismatch", "avs_code": avs_code})

        # ── CVV mismatch ──
        if transaction.get("cvv_mismatch", False):
            score += 0.30
            flags.append({"flag": "cvv_mismatch"})

        # ── Velocity testing: many small authorizations ──
        history = self._card_history.get(card_hash, [])
        recent_10min = [h for h in history if (now - h["ts"]).total_seconds() < 600]
        small_auths = [h for h in recent_10min if h.get("amount", 0) < 5]
        if len(small_auths) >= 3:
            score += 0.35
            flags.append({"flag": "velocity_testing", "small_auth_count_10min": len(small_auths)})

        # ── Device / IP anomaly ──
        if transaction.get("new_device", False) and transaction.get("new_ip", False):
            score += 0.20
            flags.append({"flag": "device_ip_anomaly", "device_id": transaction.get("device_id", ""),
                          "ip": transaction.get("ip", "")})

        # ── BIN attack: many unique cards from same BIN in short window ──
        bin_prefix = transaction.get("bin_prefix", "")
        if bin_prefix:
            bin_recent = [a for a in self._bin_attempts.get(bin_prefix, [])
                          if (now - a["ts"]).total_seconds() < 600]
            unique_cards = len({a["card_hash"] for a in bin_recent})
            if unique_cards >= 5:
                score += 0.40
                flags.append({"flag": "bin_attack", "bin_prefix": bin_prefix,
                              "unique_cards_10min": unique_cards})

        # ── Billing / shipping geo mismatch ──
        if transaction.get("billing_country") and transaction.get("shipping_country"):
            if transaction["billing_country"] != transaction["shipping_country"]:
                score += 0.15
                flags.append({"flag": "geo_mismatch",
                              "billing_country": transaction["billing_country"],
                              "shipping_country": transaction["shipping_country"]})

        # ── 3-D Secure bypass ──
        if transaction.get("three_ds_attempted", False) and not transaction.get("three_ds_authenticated", True):
            score += 0.25
            flags.append({"flag": "three_ds_bypass"})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.70 else "high" if score >= 0.45 else "medium" if score >= 0.25 else "low"
        return {
            "card_hash": card_hash,
            "cnp_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.40,
            "risk_level": risk,
            "flags": flags,
            "transaction_amount": transaction.get("amount", 0),
        }


# ═════════════════════════════════════════════════════════════════════════════
# 5. Check Fraud Detector (Image Analysis)
# ═════════════════════════════════════════════════════════════════════════════
class CheckFraudDetector:
    """Detects check fraud via image analysis heuristics: MICR tampering,
    payee alteration, amount mismatch, duplicate detection, wash patterns,
    signature anomaly, counterfeit stock detection."""

    def __init__(self):
        self._check_hashes: dict[str, dict] = {}  # check_hash → metadata
        self._account_checks: dict[str, list[dict]] = defaultdict(list)

    def _compute_hash(self, check_image_data: str) -> str:
        """Simulate perceptual hash of check image."""
        return hashlib.sha256(check_image_data.encode()).hexdigest()[:16]

    def record_check(self, account_id: str, check: dict) -> None:
        img = check.get("image_data", "")
        if img:
            h = self._compute_hash(img)
            self._check_hashes[h] = {"account_id": account_id, "ts": datetime.utcnow(), **check}
        self._account_checks[account_id].append({"ts": datetime.utcnow(), **check})
        self._account_checks[account_id] = self._account_checks[account_id][-100:]

    def assess(self, account_id: str, check: dict) -> dict:
        flags = []
        score = 0.0

        # ── MICR line tampering ──
        micr = check.get("micr_data", {})
        if micr.get("routing_mismatch", False):
            score += 0.35
            flags.append({"flag": "micr_routing_mismatch",
                          "expected_routing": micr.get("expected", ""),
                          "actual_routing": micr.get("actual", "")})
        if micr.get("account_mismatch", False):
            score += 0.30
            flags.append({"flag": "micr_account_mismatch"})

        # ── Payee name alteration ──
        if check.get("payee_alteration_detected", False):
            score += 0.35
            flags.append({"flag": "payee_alteration", "confidence": check.get("alteration_confidence", 0)})

        # ── CAR / LAR amount mismatch (Courtesy Amount vs Legal Amount) ──
        car = check.get("car_amount")  # machine-read numeric
        lar = check.get("lar_amount")  # handwritten legal
        if car is not None and lar is not None and abs(car - lar) > 0.01:
            score += 0.40
            flags.append({"flag": "amount_mismatch", "car_amount": car, "lar_amount": lar})

        # ── Duplicate check detection ──
        img = check.get("image_data", "")
        if img:
            h = self._compute_hash(img)
            existing = self._check_hashes.get(h)
            if existing and existing.get("account_id") != account_id:
                score += 0.50
                flags.append({"flag": "duplicate_check_different_account",
                              "original_account": existing["account_id"]})
            elif existing:
                score += 0.30
                flags.append({"flag": "duplicate_check_same_account"})

        # ── Chemical wash indicators ──
        if check.get("wash_indicators", False):
            score += 0.40
            flags.append({"flag": "chemical_wash_detected",
                          "indicators": check.get("wash_details", ["ink_inconsistency", "fiber_damage"])})

        # ── Signature anomaly ──
        sig = check.get("signature_analysis", {})
        if sig.get("missing", False):
            score += 0.25
            flags.append({"flag": "signature_missing"})
        elif sig.get("mismatch", False):
            score += 0.30
            flags.append({"flag": "signature_mismatch", "confidence": sig.get("confidence", 0)})

        # ── Counterfeit stock detection ──
        if check.get("counterfeit_stock", False):
            score += 0.45
            flags.append({"flag": "counterfeit_stock",
                          "details": check.get("stock_details", ["missing_watermark", "wrong_weight"])})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.70 else "high" if score >= 0.45 else "medium" if score >= 0.25 else "low"
        return {
            "account_id": account_id,
            "check_fraud_score": round(score, 4),
            "is_suspicious": score >= 0.40,
            "risk_level": risk,
            "flags": flags,
            "check_amount": check.get("amount", check.get("car_amount", 0)),
        }


# ═════════════════════════════════════════════════════════════════════════════
# PMF Orchestrator
# ═════════════════════════════════════════════════════════════════════════════
class PMFOrchestrator:
    """Orchestrates all Payments Fraud detection engines."""

    def __init__(self):
        self.ach = ACHFraudDetector()
        self.wire = WireFraudDetector()
        self.rtp_zelle = RTPZelleFraudDetector()
        self.cnp = CNPFraudDetector()
        self.check = CheckFraudDetector()
        logger.info("PMFOrchestrator initialized — 5 engines (ACH, Wire, RTP/Zelle, CNP, Check)")

    def full_assessment(self, customer_id: str, context: dict) -> dict:
        """Run all applicable PMF engines and produce a composite score."""
        results = {}
        weights = {"ach": 0.20, "wire": 0.25, "rtp_zelle": 0.20, "cnp": 0.20, "check": 0.15}
        composite = 0.0

        if context.get("ach_transaction"):
            res = self.ach.assess(customer_id, context["ach_transaction"])
            results["ach"] = res
            composite += res["ach_fraud_score"] * weights["ach"]

        if context.get("wire_transfer"):
            res = self.wire.assess(customer_id, context["wire_transfer"])
            results["wire"] = res
            composite += res["wire_fraud_score"] * weights["wire"]

        if context.get("rtp_payment"):
            res = self.rtp_zelle.assess(customer_id, context["rtp_payment"])
            results["rtp_zelle"] = res
            composite += res["rtp_fraud_score"] * weights["rtp_zelle"]

        if context.get("cnp_transaction"):
            res = self.cnp.assess(context.get("card_hash", customer_id), context["cnp_transaction"])
            results["cnp"] = res
            composite += res["cnp_fraud_score"] * weights["cnp"]

        if context.get("check"):
            res = self.check.assess(customer_id, context["check"])
            results["check"] = res
            composite += res["check_fraud_score"] * weights["check"]

        composite = min(composite, 1.0)
        risk = "critical" if composite >= 0.70 else "high" if composite >= 0.45 else "medium" if composite >= 0.25 else "low"

        return {
            "customer_id": customer_id,
            "pmf_composite_score": round(composite, 4),
            "risk_level": risk,
            "engines_run": list(results.keys()),
            "engine_results": results,
        }
