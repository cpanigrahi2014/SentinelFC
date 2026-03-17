"""Digital Banking Fraud (DBF) — Login anomaly, session hijacking, bot detection, social engineering."""

import logging
import math
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ─── Geo-IP distance approximation (Haversine) ─────────────────────────────
def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in km."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ═════════════════════════════════════════════════════════════════════════════
# 1. Login Anomaly Detection
# ═════════════════════════════════════════════════════════════════════════════
class LoginAnomalyDetector:
    """Detects unusual login patterns: impossible travel, unusual time, geo anomaly, credential stuffing."""

    IMPOSSIBLE_TRAVEL_SPEED_KPH = 900  # faster than commercial air

    def __init__(self):
        # customer_id → list of { ts, lat, lon, ip, device_id, country }
        self._login_history: dict[str, list[dict]] = defaultdict(list)
        # ip → list of { ts, customer_id, success }
        self._ip_attempts: dict[str, list[dict]] = defaultdict(list)
        # customer_id → set of typical hours (0-23)
        self._typical_hours: dict[str, set[int]] = defaultdict(set)

    def record_login(self, customer_id: str, login: dict) -> None:
        ts = datetime.utcnow()
        entry = {"ts": ts, **login}
        self._login_history[customer_id].append(entry)
        # keep last 100 entries
        self._login_history[customer_id] = self._login_history[customer_id][-100:]
        ip = login.get("ip", "")
        if ip:
            self._ip_attempts[ip].append({"ts": ts, "customer_id": customer_id, "success": login.get("success", True)})
            self._ip_attempts[ip] = self._ip_attempts[ip][-500:]
        if login.get("success", True):
            self._typical_hours[customer_id].add(ts.hour)

    def assess(self, customer_id: str, current_login: dict) -> dict:
        flags = []
        score = 0.0
        now = datetime.utcnow()
        history = self._login_history.get(customer_id, [])

        # ── Impossible Travel ──
        lat, lon = current_login.get("lat"), current_login.get("lon")
        if lat is not None and lon is not None and history:
            last = next((h for h in reversed(history) if h.get("lat") is not None), None)
            if last:
                dist = _haversine_km(last["lat"], last["lon"], lat, lon)
                dt_hours = max((now - last["ts"]).total_seconds() / 3600, 0.01)
                speed = dist / dt_hours
                if speed > self.IMPOSSIBLE_TRAVEL_SPEED_KPH and dist > 500:
                    score += 0.35
                    flags.append({"flag": "impossible_travel", "distance_km": round(dist, 1),
                                  "speed_kph": round(speed, 1), "hours_between": round(dt_hours, 2)})

        # ── Unusual Login Time ──
        typical = self._typical_hours.get(customer_id, set())
        if typical and now.hour not in typical and len(typical) >= 5:
            score += 0.15
            flags.append({"flag": "unusual_login_time", "hour": now.hour,
                          "typical_hours": sorted(typical)})

        # ── New Country / Geo Anomaly ──
        country = current_login.get("country", "")
        prev_countries = {h.get("country") for h in history if h.get("country")}
        if country and prev_countries and country not in prev_countries:
            score += 0.20
            flags.append({"flag": "new_country", "country": country,
                          "previous_countries": sorted(prev_countries)})

        # ── New Device ──
        device_id = current_login.get("device_id", "")
        prev_devices = {h.get("device_id") for h in history if h.get("device_id")}
        if device_id and prev_devices and device_id not in prev_devices:
            score += 0.10
            flags.append({"flag": "new_device", "device_id": device_id})

        # ── Credential Stuffing (high-velocity failed logins from single IP) ──
        ip = current_login.get("ip", "")
        stuffing_detail = self._check_credential_stuffing(ip)
        if stuffing_detail:
            score += 0.30
            flags.append(stuffing_detail)

        score = min(score, 1.0)
        risk = "critical" if score >= 0.75 else "high" if score >= 0.50 else "medium" if score >= 0.25 else "low"
        return {
            "customer_id": customer_id,
            "login_anomaly_score": round(score, 4),
            "is_anomalous": score >= 0.40,
            "risk_level": risk,
            "flags": flags,
            "login_history_size": len(history),
        }

    def _check_credential_stuffing(self, ip: str) -> dict | None:
        if not ip:
            return None
        attempts = self._ip_attempts.get(ip, [])
        window = datetime.utcnow() - timedelta(minutes=10)
        recent = [a for a in attempts if a["ts"] >= window]
        failed = [a for a in recent if not a.get("success", True)]
        unique_customers = len({a["customer_id"] for a in recent})
        if len(failed) >= 10 or unique_customers >= 5:
            return {"flag": "credential_stuffing", "failed_attempts_10min": len(failed),
                    "unique_accounts_targeted": unique_customers, "ip": ip}
        return None


# ═════════════════════════════════════════════════════════════════════════════
# 2. Session Hijacking Detection
# ═════════════════════════════════════════════════════════════════════════════
class SessionHijackingDetector:
    """Detects session token theft, concurrent sessions from different IPs, session replay."""

    def __init__(self):
        # session_id → { customer_id, ip, ua, created, last_seen, token_hash, requests: [dict] }
        self._sessions: dict[str, dict] = {}
        # customer_id → list of active session_ids
        self._customer_sessions: dict[str, list[str]] = defaultdict(list)

    def register_session(self, session_id: str, customer_id: str, ip: str, user_agent: str) -> dict:
        token_hash = hashlib.sha256(session_id.encode()).hexdigest()[:16]
        now = datetime.utcnow()
        self._sessions[session_id] = {
            "customer_id": customer_id, "ip": ip, "ua": user_agent,
            "created": now, "last_seen": now, "token_hash": token_hash,
            "requests": [{"ts": now, "ip": ip, "ua": user_agent}],
        }
        self._customer_sessions[customer_id].append(session_id)
        # keep last 20 sessions per customer
        self._customer_sessions[customer_id] = self._customer_sessions[customer_id][-20:]
        return {"session_id": session_id, "token_hash": token_hash, "registered": True}

    def assess(self, session_id: str, current_ip: str, current_ua: str) -> dict:
        flags = []
        score = 0.0
        session = self._sessions.get(session_id)
        if not session:
            return {"session_id": session_id, "hijack_score": 0.0, "is_hijacked": False,
                    "risk_level": "low", "flags": [{"flag": "unknown_session"}]}

        now = datetime.utcnow()
        session["requests"].append({"ts": now, "ip": current_ip, "ua": current_ua})
        session["requests"] = session["requests"][-200:]
        session["last_seen"] = now

        # ── IP Change mid-session ──
        if current_ip != session["ip"]:
            score += 0.35
            flags.append({"flag": "ip_changed_mid_session", "original_ip": session["ip"],
                          "current_ip": current_ip})

        # ── User-Agent Change ──
        if current_ua != session["ua"]:
            score += 0.30
            flags.append({"flag": "user_agent_changed", "original_ua": session["ua"][:60],
                          "current_ua": current_ua[:60]})

        # ── Concurrent sessions from different IPs ──
        customer_id = session["customer_id"]
        active = [sid for sid in self._customer_sessions.get(customer_id, [])
                  if sid in self._sessions and
                  (now - self._sessions[sid]["last_seen"]).total_seconds() < 1800]
        unique_ips = {self._sessions[sid]["ip"] for sid in active if sid in self._sessions}
        if len(unique_ips) >= 2:
            score += 0.25
            flags.append({"flag": "concurrent_sessions_different_ips",
                          "active_sessions": len(active), "unique_ips": list(unique_ips)})

        # ── Session Replay (rapid duplicate requests) ──
        recent = [r for r in session["requests"] if (now - r["ts"]).total_seconds() < 5]
        if len(recent) > 10:
            score += 0.25
            flags.append({"flag": "session_replay_suspected",
                          "requests_in_5s": len(recent)})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.70 else "high" if score >= 0.45 else "medium" if score >= 0.25 else "low"
        return {
            "session_id": session_id,
            "customer_id": customer_id,
            "hijack_score": round(score, 4),
            "is_hijacked": score >= 0.45,
            "risk_level": risk,
            "flags": flags,
        }


# ═════════════════════════════════════════════════════════════════════════════
# 3. Bot Detection
# ═════════════════════════════════════════════════════════════════════════════
BOT_UA_SIGNATURES = [
    "headless", "phantom", "selenium", "puppeteer", "playwright", "webdriver",
    "scrapy", "httpclient", "python-requests", "curl/", "wget/",
]

class BotDetector:
    """Detects automated scripts, headless browsers, abnormal interaction patterns."""

    def __init__(self):
        # session_id → interaction events
        self._interactions: dict[str, list[dict]] = defaultdict(list)

    def assess(self, session: dict) -> dict:
        flags = []
        score = 0.0

        ua = session.get("user_agent", "").lower()
        # ── UA-based bot detection ──
        for sig in BOT_UA_SIGNATURES:
            if sig in ua:
                score += 0.30
                flags.append({"flag": "bot_user_agent", "matched_signature": sig})
                break

        # ── Missing browser signals ──
        if not session.get("has_javascript", True):
            score += 0.20
            flags.append({"flag": "javascript_disabled"})
        if not session.get("has_cookies", True):
            score += 0.15
            flags.append({"flag": "cookies_disabled"})
        if session.get("webdriver_flag", False):
            score += 0.30
            flags.append({"flag": "webdriver_detected"})

        # ── Abnormal click/interaction patterns ──
        click_interval_ms = session.get("avg_click_interval_ms")
        if click_interval_ms is not None and click_interval_ms < 50:
            score += 0.25
            flags.append({"flag": "superhuman_click_speed", "avg_click_interval_ms": click_interval_ms})

        mouse_movements = session.get("mouse_movement_count", -1)
        if mouse_movements == 0:
            score += 0.20
            flags.append({"flag": "zero_mouse_movements"})

        # ── CAPTCHA bypass indicators ──
        captcha_time_ms = session.get("captcha_solve_time_ms")
        if captcha_time_ms is not None:
            if captcha_time_ms < 500:
                score += 0.30
                flags.append({"flag": "captcha_solved_too_fast", "solve_time_ms": captcha_time_ms})
            elif captcha_time_ms < 1500:
                score += 0.10
                flags.append({"flag": "captcha_solved_suspiciously_fast", "solve_time_ms": captcha_time_ms})

        # ── Request rate spike ──
        req_per_minute = session.get("requests_per_minute", 0)
        if req_per_minute > 60:
            score += 0.25
            flags.append({"flag": "high_request_rate", "requests_per_minute": req_per_minute})

        # ── Canvas / WebGL fingerprint mismatch ──
        if session.get("canvas_fingerprint_mismatch", False):
            score += 0.15
            flags.append({"flag": "canvas_fingerprint_mismatch"})

        # ── Timezone / language mismatch ──
        if session.get("timezone_mismatch", False):
            score += 0.10
            flags.append({"flag": "timezone_language_mismatch"})

        score = min(score, 1.0)
        risk = "critical" if score >= 0.75 else "high" if score >= 0.50 else "medium" if score >= 0.25 else "low"
        return {
            "session_id": session.get("session_id", ""),
            "bot_score": round(score, 4),
            "is_bot": score >= 0.45,
            "risk_level": risk,
            "flags": flags,
        }


# ═════════════════════════════════════════════════════════════════════════════
# 4. Social Engineering / Scam Detection
# ═════════════════════════════════════════════════════════════════════════════
SCAM_TYPE_WEIGHTS = {
    "app_fraud": 0.35,       # Authorized Push Payment fraud
    "romance_scam": 0.25,
    "tech_support": 0.20,
    "impersonation": 0.20,
}

class SocialEngineeringDetector:
    """Detects APP fraud, romance scams, tech support scams, impersonation."""

    # Behavioral red flags per scam type
    APP_FRAUD_SIGNALS = [
        "first_time_payee", "large_amount", "urgency_language", "coached_call",
        "unusual_payment_method", "new_beneficiary_country",
    ]
    ROMANCE_SIGNALS = [
        "new_relationship_payee", "escalating_amounts", "emotional_language",
        "cryptocurrency_destination", "overseas_recipient", "repeated_small_then_large",
    ]
    TECH_SUPPORT_SIGNALS = [
        "remote_access_active", "screen_sharing", "gift_card_purchase",
        "refund_overpayment_pattern", "unusual_software_download",
    ]
    IMPERSONATION_SIGNALS = [
        "claims_bank_official", "urgency_to_move_funds", "safe_account_narrative",
        "phone_call_during_transaction", "requests_credentials",
    ]

    def __init__(self):
        # customer_id → list of scam-related events
        self._events: dict[str, list[dict]] = defaultdict(list)

    def record_event(self, customer_id: str, event: dict) -> None:
        self._events[customer_id].append({"ts": datetime.utcnow(), **event})
        self._events[customer_id] = self._events[customer_id][-100:]

    def assess(self, customer_id: str, transaction: dict) -> dict:
        # Score each scam type
        scam_results = {}
        combined_score = 0.0

        for scam_type, weight in SCAM_TYPE_WEIGHTS.items():
            sub_score, sub_flags = self._score_scam_type(customer_id, transaction, scam_type)
            scam_results[scam_type] = {
                "score": round(sub_score, 4),
                "flags": sub_flags,
                "weight": weight,
            }
            combined_score += sub_score * weight

        combined_score = min(combined_score, 1.0)
        primary_type = max(scam_results, key=lambda k: scam_results[k]["score"])
        risk = "critical" if combined_score >= 0.70 else "high" if combined_score >= 0.45 else "medium" if combined_score >= 0.25 else "low"

        return {
            "customer_id": customer_id,
            "social_engineering_score": round(combined_score, 4),
            "is_suspicious": combined_score >= 0.40,
            "primary_scam_type": primary_type,
            "risk_level": risk,
            "scam_assessments": scam_results,
            "transaction_amount": transaction.get("amount", 0),
        }

    def _score_scam_type(self, customer_id: str, txn: dict, scam_type: str) -> tuple[float, list[str]]:
        signals_map = {
            "app_fraud": self.APP_FRAUD_SIGNALS,
            "romance_scam": self.ROMANCE_SIGNALS,
            "tech_support": self.TECH_SUPPORT_SIGNALS,
            "impersonation": self.IMPERSONATION_SIGNALS,
        }
        signal_list = signals_map.get(scam_type, [])
        present = txn.get("signals", [])  # signals attached to the transaction
        matched = [s for s in signal_list if s in present]
        if not matched:
            return (0.0, [])
        ratio = len(matched) / len(signal_list)
        # Non-linear: matching 3+ signals escalates quickly
        score = min(ratio * 1.5, 1.0) if len(matched) >= 3 else ratio * 0.8
        return (score, matched)


# ═════════════════════════════════════════════════════════════════════════════
# DBF Orchestrator
# ═════════════════════════════════════════════════════════════════════════════
class DBFOrchestrator:
    """Orchestrates all Digital Banking Fraud detection engines."""

    def __init__(self):
        self.login_anomaly = LoginAnomalyDetector()
        self.session_hijack = SessionHijackingDetector()
        self.bot_detector = BotDetector()
        self.social_engineering = SocialEngineeringDetector()
        logger.info("DBFOrchestrator initialized — 4 engines (Login Anomaly, Session Hijacking, Bot Detection, Social Engineering)")

    def full_assessment(self, customer_id: str, context: dict) -> dict:
        """Run all applicable DBF engines and produce a composite score."""
        results = {}
        weights = {"login_anomaly": 0.30, "session_hijack": 0.25, "bot": 0.25, "social_engineering": 0.20}
        composite = 0.0

        # Login anomaly
        if context.get("login"):
            res = self.login_anomaly.assess(customer_id, context["login"])
            results["login_anomaly"] = res
            composite += res["login_anomaly_score"] * weights["login_anomaly"]

        # Session hijacking
        if context.get("session_id"):
            res = self.session_hijack.assess(
                context["session_id"], context.get("ip", ""), context.get("user_agent", ""))
            results["session_hijack"] = res
            composite += res["hijack_score"] * weights["session_hijack"]

        # Bot detection
        if context.get("session"):
            res = self.bot_detector.assess(context["session"])
            results["bot"] = res
            composite += res["bot_score"] * weights["bot"]

        # Social engineering
        if context.get("transaction"):
            res = self.social_engineering.assess(customer_id, context["transaction"])
            results["social_engineering"] = res
            composite += res["social_engineering_score"] * weights["social_engineering"]

        composite = min(composite, 1.0)
        risk = "critical" if composite >= 0.70 else "high" if composite >= 0.45 else "medium" if composite >= 0.25 else "low"

        return {
            "customer_id": customer_id,
            "dbf_composite_score": round(composite, 4),
            "risk_level": risk,
            "engines_run": list(results.keys()),
            "engine_results": results,
        }
