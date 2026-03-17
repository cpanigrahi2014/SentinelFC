"""Sanctions and watchlist screening engine with fuzzy, phonetic, and transliteration matching."""

import logging
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


# ═══════════════════ Phonetic Matching (Soundex + Double Metaphone) ═══════════════════

def soundex(name: str) -> str:
    """Compute American Soundex code for a name."""
    name = re.sub(r"[^A-Za-z]", "", name.upper())
    if not name:
        return "0000"
    first_letter = name[0]
    mapping = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6",
    }
    codes = [first_letter]
    prev_code = mapping.get(first_letter, "0")
    for ch in name[1:]:
        code = mapping.get(ch, "0")
        if code != "0" and code != prev_code:
            codes.append(code)
        prev_code = code if code != "0" else prev_code
    return "".join(codes)[:4].ljust(4, "0")


def double_metaphone(name: str) -> tuple[str, str]:
    """Simplified Double Metaphone — returns (primary, secondary) codes."""
    name = re.sub(r"[^A-Za-z]", "", name.upper())
    if not name:
        return ("", "")
    # Simplified phonetic reduction for common AML name patterns
    vowels = set("AEIOU")
    primary = []
    secondary = []
    i = 0
    while i < len(name):
        ch = name[i]
        nxt = name[i + 1] if i + 1 < len(name) else ""
        if ch in vowels:
            if i == 0:
                primary.append("A")
                secondary.append("A")
        elif ch == "C":
            if nxt in ("E", "I", "Y"):
                primary.append("S")
                secondary.append("S")
            else:
                primary.append("K")
                secondary.append("K")
        elif ch == "G":
            if nxt in ("E", "I", "Y"):
                primary.append("J")
                secondary.append("K")
            else:
                primary.append("K")
                secondary.append("K")
        elif ch == "P" and nxt == "H":
            primary.append("F")
            secondary.append("F")
            i += 1
        elif ch == "S" and nxt == "H":
            primary.append("X")
            secondary.append("X")
            i += 1
        elif ch == "T" and nxt == "H":
            primary.append("0")
            secondary.append("T")
            i += 1
        elif ch == "W" or ch == "H":
            pass  # silent
        elif ch == "X":
            primary.append("KS")
            secondary.append("KS")
        elif ch == "Q":
            primary.append("K")
            secondary.append("K")
        elif ch == "Z":
            primary.append("S")
            secondary.append("S")
        else:
            primary.append(ch)
            secondary.append(ch)
        i += 1
    return ("".join(primary)[:6], "".join(secondary)[:6])


def phonetic_match(name1: str, name2: str) -> tuple[bool, str]:
    """Check if two names match phonetically. Returns (is_match, method)."""
    # Soundex comparison (per-token)
    tokens1 = name1.upper().split()
    tokens2 = name2.upper().split()
    if len(tokens1) == len(tokens2) and len(tokens1) > 0:
        if all(soundex(t1) == soundex(t2) for t1, t2 in zip(tokens1, tokens2)):
            return (True, "soundex")
    # Double Metaphone comparison (full string)
    dm1 = double_metaphone(name1)
    dm2 = double_metaphone(name2)
    if dm1[0] and dm2[0] and (dm1[0] == dm2[0] or dm1[0] == dm2[1] or dm1[1] == dm2[0]):
        return (True, "double_metaphone")
    return (False, "none")


# ═══════════════════ Transliteration ═══════════════════

# Common transliteration mappings (Arabic, Cyrillic, etc. → Latin equivalents)
TRANSLIT_MAP = {
    # Cyrillic common patterns
    "Ш": "SH", "Щ": "SHCH", "Ч": "CH", "Ж": "ZH", "Ц": "TS", "Ю": "YU", "Я": "YA",
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "З": "Z",
    "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M", "Н": "N", "О": "O",
    "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U", "Ф": "F", "Х": "KH",
    "Э": "E", "Ъ": "", "Ь": "", "Ы": "Y",
    # Arabic common Latin equivalences
    "محمد": "MUHAMMAD", "أحمد": "AHMED", "علي": "ALI", "حسن": "HASSAN",
    # Common Latin-letter variations
    "Ä": "AE", "Ö": "OE", "Ü": "UE", "ß": "SS",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "À": "A", "Â": "A", "Ã": "A", "Å": "A",
    "Ñ": "N", "Ç": "C", "Ø": "O", "Ð": "D",
}

# Common alternative romanisations (e.g., Mohammed = Muhammad = Mohamed)
ROMANISATION_EQUIVALENTS = [
    {"MUHAMMAD", "MOHAMMED", "MOHAMED", "MOHAMMAD", "MUHAMMED", "MOHAMAD"},
    {"AHMED", "AHMAD", "AHMET"},
    {"HASSAN", "HASAN", "HASEN"},
    {"HUSSEIN", "HUSEIN", "HUSAIN", "HUSSAIN"},
    {"ALI", "ALEE"},
    {"IVAN", "IWAN"},
    {"SERGEI", "SERGEY", "SERGIY"},
    {"VLADIMIR", "VOLODYMYR", "WLADIMIR"},
    {"ALEXANDER", "ALEKSANDR", "ALEXANDRE", "ALEKSANDER"},
    {"YOUSSEF", "YUSUF", "YOSEF", "JOSEPH", "YOUSUF"},
    {"JEAN", "JOHN", "JUAN", "JOHANN", "GIOVANNI", "IVAN"},
]


def transliterate(name: str) -> str:
    """Transliterate non-Latin characters to Latin equivalents."""
    result = name.upper()
    for src, dst in TRANSLIT_MAP.items():
        result = result.replace(src, dst)
    return result


def romanisation_match(name1: str, name2: str) -> bool:
    """Check if two name tokens are romanisation equivalents."""
    tokens1 = set(name1.upper().split())
    tokens2 = set(name2.upper().split())
    for equiv_set in ROMANISATION_EQUIVALENTS:
        if tokens1 & equiv_set and tokens2 & equiv_set:
            return True
    return False


# ═══════════════════ ML False-Positive Reduction ═══════════════════

class FalsePositiveMLModel:
    """
    Logistic regression model to score likelihood of a screening match being a true positive.
    Features: match_score, name_length_ratio, country_risk, list_severity,
    has_identifiers_overlap, token_overlap_ratio, phonetic_match_flag.
    """

    # Pre-trained weights (production: trained on analyst disposition data)
    _WEIGHTS = {
        "intercept": -2.5,
        "match_score": 4.0,
        "name_length_ratio": 0.8,
        "country_risk": 1.5,
        "list_severity": 1.2,
        "has_identifier_overlap": 2.0,
        "token_overlap_ratio": 1.8,
        "phonetic_match": 1.0,
    }

    HIGH_RISK_COUNTRIES = {"IR", "KP", "SY", "CU", "AF", "YE", "SO", "SD", "VE", "BY", "RU", "MM"}
    LIST_SEVERITY = {"OFAC-SDN": 1.0, "EU-SANCTIONS": 0.9, "UN-CONSOLIDATED": 0.9, "PEP-LIST": 0.6, "LOCAL": 0.5}

    @classmethod
    def score_match(cls, match_score: float, screened_name: str, entry_name: str,
                    entry_country: str, list_name: str, has_id_overlap: bool = False) -> dict:
        """Score a match for true-positive likelihood (0-1)."""
        # Feature extraction
        len_ratio = min(len(screened_name), len(entry_name)) / max(len(screened_name), len(entry_name), 1)
        country_risk = 1.0 if entry_country in cls.HIGH_RISK_COUNTRIES else 0.0
        list_sev = cls.LIST_SEVERITY.get(list_name, 0.5)

        screened_tokens = set(screened_name.upper().split())
        entry_tokens = set(entry_name.upper().split())
        token_overlap = len(screened_tokens & entry_tokens) / max(len(screened_tokens | entry_tokens), 1)

        is_phonetic, _ = phonetic_match(screened_name, entry_name)

        # Logistic regression
        z = cls._WEIGHTS["intercept"]
        z += cls._WEIGHTS["match_score"] * match_score
        z += cls._WEIGHTS["name_length_ratio"] * len_ratio
        z += cls._WEIGHTS["country_risk"] * country_risk
        z += cls._WEIGHTS["list_severity"] * list_sev
        z += cls._WEIGHTS["has_identifier_overlap"] * (1.0 if has_id_overlap else 0.0)
        z += cls._WEIGHTS["token_overlap_ratio"] * token_overlap
        z += cls._WEIGHTS["phonetic_match"] * (1.0 if is_phonetic else 0.0)

        tp_probability = 1.0 / (1.0 + math.exp(-z))

        if tp_probability >= 0.80:
            disposition = "likely_true_positive"
        elif tp_probability >= 0.50:
            disposition = "review_required"
        elif tp_probability >= 0.25:
            disposition = "likely_false_positive"
        else:
            disposition = "auto_dismiss"

        return {
            "tp_probability": round(tp_probability, 4),
            "disposition": disposition,
            "features": {
                "match_score": match_score,
                "name_length_ratio": round(len_ratio, 3),
                "country_risk": country_risk,
                "list_severity": list_sev,
                "has_identifier_overlap": has_id_overlap,
                "token_overlap_ratio": round(token_overlap, 3),
                "phonetic_match": is_phonetic,
            },
        }


@dataclass
class WatchlistEntry:
    entry_id: str
    list_name: str
    entity_name: str
    aliases: list[str] = field(default_factory=list)
    entity_type: str = "individual"  # individual, organization
    country: Optional[str] = None
    date_added: Optional[str] = None
    identifiers: dict = field(default_factory=dict)  # passport, national_id, etc.


@dataclass
class ScreeningMatch:
    entry: WatchlistEntry
    match_score: float
    match_type: str  # exact, fuzzy, alias, partial
    matched_field: str
    matched_value: str


class SanctionsEngine:
    """
    Sanctions screening engine with fuzzy name matching.
    Supports OFAC, EU, UN, and other sanctions/PEP lists.
    """

    def __init__(self, fuzzy_threshold: float = 0.85):
        self.fuzzy_threshold = fuzzy_threshold
        self._watchlists: dict[str, list[WatchlistEntry]] = {}
        self._all_entries: list[WatchlistEntry] = []

    def load_default_lists(self):
        """Load sample sanctions list entries for demonstration."""
        # In production, these would be loaded from external data feeds
        sample_entries = [
            WatchlistEntry("OFAC-001", "OFAC-SDN", "JOHN DOE", ["J. DOE"], "individual", "IR"),
            WatchlistEntry("OFAC-002", "OFAC-SDN", "ACME TRADING CO", ["ACME TRADE"], "organization", "SY"),
            WatchlistEntry("OFAC-003", "OFAC-SDN", "IVAN PETROV", ["I. PETROV", "IVAN PETROFF"], "individual", "RU"),
            WatchlistEntry("EU-001", "EU-SANCTIONS", "GLOBAL SHELL LTD", [], "organization", "CY"),
            WatchlistEntry("EU-002", "EU-SANCTIONS", "MARIA GARCIA", ["M. GARCIA"], "individual", "VE"),
            WatchlistEntry("UN-001", "UN-CONSOLIDATED", "WEAPONS CORP", ["WEAPONS CORPORATION"], "organization", "KP"),
            WatchlistEntry("UN-002", "UN-CONSOLIDATED", "ALI HASSAN", ["A. HASSAN"], "individual", "AF"),
            WatchlistEntry("PEP-001", "PEP-LIST", "CARLOS MENDEZ", [], "individual", "NI"),
            WatchlistEntry("PEP-002", "PEP-LIST", "OLGA IVANOVA", ["O. IVANOVA"], "individual", "BY"),
        ]

        for entry in sample_entries:
            list_name = entry.list_name
            if list_name not in self._watchlists:
                self._watchlists[list_name] = []
            self._watchlists[list_name].append(entry)
            self._all_entries.append(entry)

        logger.info("Loaded %d sanctions entries across %d lists", len(self._all_entries), len(self._watchlists))

    def add_entries(self, list_name: str, entries: list[WatchlistEntry]):
        """Add entries to a specific watchlist."""
        if list_name not in self._watchlists:
            self._watchlists[list_name] = []
        self._watchlists[list_name].extend(entries)
        self._all_entries.extend(entries)

    def screen_name(
        self,
        name: str,
        lists: Optional[list[str]] = None,
    ) -> list[ScreeningMatch]:
        """Screen a name against sanctions lists using fuzzy, phonetic, and transliteration matching."""
        matches = []
        normalized_name = self._normalize_name(name)
        transliterated_name = self._normalize_name(transliterate(name))
        entries = self._get_entries(lists)

        for entry in entries:
            entry_normalized = self._normalize_name(entry.entity_name)

            # 1. Exact match
            if normalized_name == entry_normalized:
                matches.append(ScreeningMatch(
                    entry=entry, match_score=1.0,
                    match_type="exact", matched_field="entity_name",
                    matched_value=entry.entity_name,
                ))
                continue

            # 2. Fuzzy match on primary name
            similarity = self._fuzzy_match(normalized_name, entry_normalized)
            if similarity >= self.fuzzy_threshold:
                matches.append(ScreeningMatch(
                    entry=entry, match_score=similarity,
                    match_type="fuzzy", matched_field="entity_name",
                    matched_value=entry.entity_name,
                ))
                continue

            # 3. Phonetic match (Soundex / Double Metaphone)
            is_phonetic, phonetic_method = phonetic_match(normalized_name, entry_normalized)
            if is_phonetic:
                matches.append(ScreeningMatch(
                    entry=entry, match_score=0.88,
                    match_type=f"phonetic_{phonetic_method}", matched_field="entity_name",
                    matched_value=entry.entity_name,
                ))
                continue

            # 4. Transliteration match
            translit_entry = self._normalize_name(transliterate(entry.entity_name))
            if transliterated_name == translit_entry and transliterated_name != normalized_name:
                matches.append(ScreeningMatch(
                    entry=entry, match_score=0.90,
                    match_type="transliteration", matched_field="entity_name",
                    matched_value=entry.entity_name,
                ))
                continue

            # 5. Romanisation equivalence
            if romanisation_match(normalized_name, entry_normalized):
                matches.append(ScreeningMatch(
                    entry=entry, match_score=0.87,
                    match_type="romanisation", matched_field="entity_name",
                    matched_value=entry.entity_name,
                ))
                continue

            # 6. Check aliases (fuzzy + phonetic)
            for alias in entry.aliases:
                alias_normalized = self._normalize_name(alias)
                if normalized_name == alias_normalized:
                    matches.append(ScreeningMatch(
                        entry=entry, match_score=0.95,
                        match_type="alias", matched_field="alias",
                        matched_value=alias,
                    ))
                    break
                alias_similarity = self._fuzzy_match(normalized_name, alias_normalized)
                if alias_similarity >= self.fuzzy_threshold:
                    matches.append(ScreeningMatch(
                        entry=entry, match_score=alias_similarity,
                        match_type="fuzzy_alias", matched_field="alias",
                        matched_value=alias,
                    ))
                    break
                is_alias_phonetic, alias_ph_method = phonetic_match(normalized_name, alias_normalized)
                if is_alias_phonetic:
                    matches.append(ScreeningMatch(
                        entry=entry, match_score=0.86,
                        match_type=f"phonetic_alias_{alias_ph_method}", matched_field="alias",
                        matched_value=alias,
                    ))
                    break

        # Sort by match score descending
        matches.sort(key=lambda m: m.match_score, reverse=True)
        return matches

    def screen_customer(self, customer: dict) -> dict:
        """Full screening of a customer profile."""
        results = {
            "customer_id": customer.get("customer_id"),
            "matches": [],
            "highest_score": 0.0,
            "is_match": False,
            "lists_screened": list(self._watchlists.keys()),
        }

        # Screen by name
        full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
        if full_name:
            name_matches = self.screen_name(full_name)
            for match in name_matches:
                results["matches"].append({
                    "entry_id": match.entry.entry_id,
                    "list_name": match.entry.list_name,
                    "matched_name": match.entry.entity_name,
                    "match_score": match.match_score,
                    "match_type": match.match_type,
                    "entity_type": match.entry.entity_type,
                    "country": match.entry.country,
                })

        if results["matches"]:
            results["highest_score"] = max(m["match_score"] for m in results["matches"])
            results["is_match"] = results["highest_score"] >= self.fuzzy_threshold

        return results

    def _get_entries(self, lists: Optional[list[str]] = None) -> list[WatchlistEntry]:
        if lists:
            entries = []
            for lst in lists:
                entries.extend(self._watchlists.get(lst, []))
            return entries
        return self._all_entries

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a name for comparison."""
        name = name.upper().strip()
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", " ", name)
        return name

    @staticmethod
    def _fuzzy_match(name1: str, name2: str) -> float:
        """Compute fuzzy similarity between two normalized names."""
        return SequenceMatcher(None, name1, name2).ratio()

    # ── Real-time Payment Screening ──

    def screen_payment(self, payment: dict) -> dict:
        """
        Real-time screening of a payment against all watchlists.
        Returns block/release decision with match details.
        """
        now = datetime.utcnow()
        beneficiary_name = payment.get("beneficiary_name", "")
        originator_name = payment.get("originator_name", "")
        beneficiary_country = payment.get("beneficiary_country", "")
        amount = payment.get("amount", 0)
        currency = payment.get("currency", "USD")
        payment_type = payment.get("payment_type", "wire")

        ben_matches = self.screen_name(beneficiary_name) if beneficiary_name else []
        orig_matches = self.screen_name(originator_name) if originator_name else []

        all_matches = []
        for m in ben_matches:
            ml_result = FalsePositiveMLModel.score_match(
                m.match_score, beneficiary_name, m.entry.entity_name,
                m.entry.country or "", m.entry.list_name,
            )
            all_matches.append({
                "direction": "beneficiary",
                "entry_id": m.entry.entry_id,
                "list_name": m.entry.list_name,
                "entity_name": m.entry.entity_name,
                "match_score": m.match_score,
                "match_type": m.match_type,
                "country": m.entry.country,
                "tp_probability": ml_result["tp_probability"],
                "ml_disposition": ml_result["disposition"],
            })
        for m in orig_matches:
            ml_result = FalsePositiveMLModel.score_match(
                m.match_score, originator_name, m.entry.entity_name,
                m.entry.country or "", m.entry.list_name,
            )
            all_matches.append({
                "direction": "originator",
                "entry_id": m.entry.entry_id,
                "list_name": m.entry.list_name,
                "entity_name": m.entry.entity_name,
                "match_score": m.match_score,
                "match_type": m.match_type,
                "country": m.entry.country,
                "tp_probability": ml_result["tp_probability"],
                "ml_disposition": ml_result["disposition"],
            })

        # Decision logic
        has_true_positive = any(m["ml_disposition"] == "likely_true_positive" for m in all_matches)
        has_review = any(m["ml_disposition"] == "review_required" for m in all_matches)
        has_sanctions = any(m["list_name"] in ("OFAC-SDN", "EU-SANCTIONS", "UN-CONSOLIDATED") for m in all_matches)

        if has_true_positive and has_sanctions:
            decision = "BLOCK"
            reason = "High-confidence match against sanctions list"
        elif has_true_positive:
            decision = "HOLD"
            reason = "High-confidence match requires manual review"
        elif has_review:
            decision = "HOLD"
            reason = "Potential match requires analyst review"
        else:
            decision = "RELEASE"
            reason = "No actionable matches" if not all_matches else "Matches auto-dismissed by ML model"

        return {
            "payment_id": payment.get("payment_id", str(uuid4())),
            "screened_at": now.isoformat(),
            "decision": decision,
            "reason": reason,
            "beneficiary_name": beneficiary_name,
            "originator_name": originator_name,
            "amount": amount,
            "currency": currency,
            "payment_type": payment_type,
            "beneficiary_country": beneficiary_country,
            "total_matches": len(all_matches),
            "matches": all_matches,
            "latency_ms": int((datetime.utcnow() - now).total_seconds() * 1000),
        }

    # ── Batch Screening ──

    def screen_batch(self, customers: list[dict]) -> dict:
        """
        Batch screening of a customer list. Each customer dict has:
        customer_id, first_name, last_name, [nationality, date_of_birth].
        """
        now = datetime.utcnow()
        results = []
        total_matches = 0
        blocked_count = 0

        for cust in customers:
            cust_result = self.screen_customer(cust)
            # Add ML scoring to each match
            full_name = f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip()
            for m in cust_result["matches"]:
                ml_score = FalsePositiveMLModel.score_match(
                    m["match_score"], full_name, m["matched_name"],
                    m.get("country", ""), m["list_name"],
                )
                m["tp_probability"] = ml_score["tp_probability"]
                m["ml_disposition"] = ml_score["disposition"]

            # Filter out auto-dismissed
            actionable = [m for m in cust_result["matches"] if m.get("ml_disposition") != "auto_dismiss"]
            cust_result["actionable_matches"] = actionable
            cust_result["auto_dismissed"] = len(cust_result["matches"]) - len(actionable)
            total_matches += len(actionable)
            if actionable:
                blocked_count += 1
            results.append(cust_result)

        elapsed = (datetime.utcnow() - now).total_seconds()
        return {
            "batch_id": str(uuid4()),
            "screened_at": now.isoformat(),
            "total_customers": len(customers),
            "customers_with_matches": blocked_count,
            "total_actionable_matches": total_matches,
            "total_auto_dismissed": sum(r.get("auto_dismissed", 0) for r in results),
            "processing_time_seconds": round(elapsed, 3),
            "lists_screened": list(self._watchlists.keys()),
            "results": results,
        }


# ═══════════════════ Alert Grouping & Prioritization ═══════════════════

class WLFAlertManager:
    """
    Groups screening alerts by entity/list, assigns priority scores,
    and provides consolidated alert views.
    """

    PRIORITY_WEIGHTS = {
        "match_score": 3.0,
        "list_severity": 2.5,
        "tp_probability": 2.0,
        "is_sanctions": 2.0,
        "is_pep": 1.5,
        "match_count": 1.0,
    }
    LIST_SEVERITY = {"OFAC-SDN": 1.0, "EU-SANCTIONS": 0.9, "UN-CONSOLIDATED": 0.9, "PEP-LIST": 0.6}

    def __init__(self):
        self._alerts: list[dict] = []
        self._groups: dict[str, dict] = {}  # group_key → group

    def create_alert(self, screening_result: dict, source: str = "manual") -> dict:
        """Create a WLF alert from a screening result."""
        alert_id = f"WLF-{str(uuid4())[:8].upper()}"
        now = datetime.utcnow()

        matches = screening_result.get("matches", [])
        if not matches:
            return None

        # Use highest-scoring match for primary info
        top_match = max(matches, key=lambda m: m.get("match_score", 0))
        is_sanctions = top_match.get("list_name", "") in ("OFAC-SDN", "EU-SANCTIONS", "UN-CONSOLIDATED")
        is_pep = top_match.get("list_name", "") == "PEP-LIST"
        tp_prob = top_match.get("tp_probability", 0.5)

        # Compute priority score
        z = 0
        z += self.PRIORITY_WEIGHTS["match_score"] * top_match.get("match_score", 0)
        z += self.PRIORITY_WEIGHTS["list_severity"] * self.LIST_SEVERITY.get(top_match.get("list_name", ""), 0.5)
        z += self.PRIORITY_WEIGHTS["tp_probability"] * tp_prob
        z += self.PRIORITY_WEIGHTS["is_sanctions"] * (1.0 if is_sanctions else 0.0)
        z += self.PRIORITY_WEIGHTS["is_pep"] * (1.0 if is_pep else 0.0)
        z += self.PRIORITY_WEIGHTS["match_count"] * min(len(matches) / 5.0, 1.0)
        priority_score = round(min(z / 12.0, 1.0), 4)  # normalize to 0-1

        if priority_score >= 0.80:
            priority = "critical"
        elif priority_score >= 0.60:
            priority = "high"
        elif priority_score >= 0.35:
            priority = "medium"
        else:
            priority = "low"

        alert = {
            "alert_id": alert_id,
            "source": source,
            "status": "open",
            "priority": priority,
            "priority_score": priority_score,
            "screened_entity": screening_result.get("name_screened") or screening_result.get("customer_id", ""),
            "total_matches": len(matches),
            "top_match": top_match,
            "all_matches": matches,
            "is_sanctions_hit": is_sanctions,
            "is_pep_hit": is_pep,
            "tp_probability": tp_prob,
            "created_at": now.isoformat(),
            "group_key": None,
        }

        # Group by matched entity + list
        group_key = f"{top_match.get('entity_name', 'UNKNOWN')}|{top_match.get('list_name', 'UNKNOWN')}"
        alert["group_key"] = group_key

        if group_key not in self._groups:
            self._groups[group_key] = {
                "group_key": group_key,
                "entity_name": top_match.get("entity_name", ""),
                "list_name": top_match.get("list_name", ""),
                "alert_ids": [],
                "highest_priority": priority,
                "highest_score": priority_score,
                "total_alerts": 0,
                "created_at": now.isoformat(),
            }
        grp = self._groups[group_key]
        grp["alert_ids"].append(alert_id)
        grp["total_alerts"] += 1
        if priority_score > grp["highest_score"]:
            grp["highest_priority"] = priority
            grp["highest_score"] = priority_score

        self._alerts.append(alert)
        return alert

    def get_alerts(self, status: str = None, priority: str = None) -> list[dict]:
        alerts = self._alerts
        if status:
            alerts = [a for a in alerts if a["status"] == status]
        if priority:
            alerts = [a for a in alerts if a["priority"] == priority]
        return sorted(alerts, key=lambda a: a["priority_score"], reverse=True)

    def get_groups(self) -> list[dict]:
        return sorted(self._groups.values(), key=lambda g: g["highest_score"], reverse=True)

    @property
    def stats(self) -> dict:
        by_priority = defaultdict(int)
        by_status = defaultdict(int)
        for a in self._alerts:
            by_priority[a["priority"]] += 1
            by_status[a["status"]] += 1
        return {
            "total_alerts": len(self._alerts),
            "total_groups": len(self._groups),
            "by_priority": dict(by_priority),
            "by_status": dict(by_status),
        }


# ═══════════════════ PEP Screening Engine ═══════════════════

@dataclass
class PEPEntry:
    pep_id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    country: str = ""
    pep_level: str = "domestic"  # domestic, foreign, international_org
    position: str = ""
    status: str = "active"  # active, former
    relatives_and_associates: list[dict] = field(default_factory=list)  # [{name, relationship}]
    date_of_birth: Optional[str] = None


class PEPScreeningEngine:
    """
    Specialized PEP screening with Relative/Close Associate (RCA) detection,
    PEP level classification, and family/associate matching.
    """

    def __init__(self, fuzzy_threshold: float = 0.85):
        self.fuzzy_threshold = fuzzy_threshold
        self._pep_entries: list[PEPEntry] = []

    def load_defaults(self):
        """Load sample PEP entries for demonstration."""
        self._pep_entries = [
            PEPEntry("PEP-D001", "CARLOS MENDEZ", ["C. MENDEZ"], "NI", "domestic",
                     "Former Minister of Finance", "former",
                     [{"name": "MARIA MENDEZ", "relationship": "spouse"},
                      {"name": "JORGE MENDEZ", "relationship": "son"}]),
            PEPEntry("PEP-D002", "OLGA IVANOVA", ["O. IVANOVA"], "BY", "foreign",
                     "Deputy Governor Central Bank", "active",
                     [{"name": "DMITRI IVANOV", "relationship": "spouse"}]),
            PEPEntry("PEP-D003", "AHMED AL-RASHID", ["A. AL-RASHID"], "AE", "domestic",
                     "Member of Parliament", "active",
                     [{"name": "FATIMA AL-RASHID", "relationship": "spouse"},
                      {"name": "OMAR AL-RASHID", "relationship": "brother"},
                      {"name": "HASSAN TRADING LLC", "relationship": "business_associate"}]),
            PEPEntry("PEP-D004", "JEAN-CLAUDE DUBOIS", ["JC DUBOIS"], "FR", "foreign",
                     "Ambassador to United Nations", "active",
                     [{"name": "CLAIRE DUBOIS", "relationship": "spouse"}]),
            PEPEntry("PEP-D005", "WANG LEI", ["WANG L."], "CN", "foreign",
                     "Provincial Party Secretary", "active",
                     [{"name": "CHEN MEI", "relationship": "spouse"},
                      {"name": "WANG INDUSTRIES", "relationship": "business_associate"}]),
        ]

    def screen_pep(self, name: str, include_rca: bool = True) -> dict:
        """Screen a name against PEP list including relatives/associates."""
        normalized = SanctionsEngine._normalize_name(name)
        results = {
            "screened_name": name,
            "pep_matches": [],
            "rca_matches": [],
            "is_pep": False,
            "is_rca": False,
            "highest_pep_score": 0.0,
            "highest_rca_score": 0.0,
        }

        for entry in self._pep_entries:
            # Check primary name
            entry_norm = SanctionsEngine._normalize_name(entry.name)
            score = SequenceMatcher(None, normalized, entry_norm).ratio()
            if score >= self.fuzzy_threshold:
                results["pep_matches"].append({
                    "pep_id": entry.pep_id,
                    "matched_name": entry.name,
                    "match_score": score,
                    "pep_level": entry.pep_level,
                    "position": entry.position,
                    "status": entry.status,
                    "country": entry.country,
                    "match_type": "direct",
                })
                continue

            # Check aliases
            for alias in entry.aliases:
                alias_norm = SanctionsEngine._normalize_name(alias)
                alias_score = SequenceMatcher(None, normalized, alias_norm).ratio()
                if alias_score >= self.fuzzy_threshold:
                    results["pep_matches"].append({
                        "pep_id": entry.pep_id,
                        "matched_name": entry.name,
                        "matched_alias": alias,
                        "match_score": alias_score,
                        "pep_level": entry.pep_level,
                        "position": entry.position,
                        "status": entry.status,
                        "country": entry.country,
                        "match_type": "alias",
                    })
                    break

            # Check relatives and close associates (RCA)
            if include_rca:
                for rca in entry.relatives_and_associates:
                    rca_norm = SanctionsEngine._normalize_name(rca["name"])
                    rca_score = SequenceMatcher(None, normalized, rca_norm).ratio()
                    if rca_score >= self.fuzzy_threshold:
                        results["rca_matches"].append({
                            "pep_id": entry.pep_id,
                            "pep_name": entry.name,
                            "rca_name": rca["name"],
                            "relationship": rca["relationship"],
                            "match_score": rca_score,
                            "pep_level": entry.pep_level,
                            "pep_position": entry.position,
                            "country": entry.country,
                            "match_type": "rca",
                        })

        results["is_pep"] = len(results["pep_matches"]) > 0
        results["is_rca"] = len(results["rca_matches"]) > 0
        if results["pep_matches"]:
            results["highest_pep_score"] = max(m["match_score"] for m in results["pep_matches"])
        if results["rca_matches"]:
            results["highest_rca_score"] = max(m["match_score"] for m in results["rca_matches"])

        return results

    @property
    def stats(self) -> dict:
        return {
            "total_pep_entries": len(self._pep_entries),
            "total_rca_entries": sum(len(e.relatives_and_associates) for e in self._pep_entries),
            "active_peps": sum(1 for e in self._pep_entries if e.status == "active"),
            "former_peps": sum(1 for e in self._pep_entries if e.status == "former"),
        }


# ═══════════════════ Adverse Media Screening ═══════════════════

@dataclass
class AdverseMediaEntry:
    media_id: str
    entity_name: str
    aliases: list[str] = field(default_factory=list)
    category: str = ""  # fraud, money_laundering, corruption, terrorism_financing, tax_evasion, sanctions_evasion
    severity: str = "medium"  # low, medium, high, critical
    source: str = ""
    headline: str = ""
    published_date: Optional[str] = None
    country: str = ""


class AdverseMediaEngine:
    """Screen names against adverse media records."""

    def __init__(self, fuzzy_threshold: float = 0.85):
        self.fuzzy_threshold = fuzzy_threshold
        self._entries: list[AdverseMediaEntry] = []

    def load_defaults(self):
        """Load sample adverse media entries."""
        self._entries = [
            AdverseMediaEntry("AM-001", "GLOBAL SHELL LTD", [], "money_laundering", "high",
                              "Reuters", "Shell company linked to $50M laundering scheme", "2024-01-15", "CY"),
            AdverseMediaEntry("AM-002", "IVAN PETROV", ["I. PETROV"], "sanctions_evasion", "critical",
                              "BBC News", "Russian businessman evading EU sanctions via crypto", "2024-03-20", "RU"),
            AdverseMediaEntry("AM-003", "ACME TRADING CO", ["ACME TRADE"], "terrorism_financing", "critical",
                              "US Treasury", "Designated for financing designated entities", "2024-02-01", "SY"),
            AdverseMediaEntry("AM-004", "CARLOS MENDEZ", [], "corruption", "high",
                              "Transparency International", "Former minister investigated for embezzlement", "2023-11-10", "NI"),
            AdverseMediaEntry("AM-005", "WANG INDUSTRIES", [], "tax_evasion", "medium",
                              "Financial Times", "Investigation into offshore tax structures", "2024-04-05", "CN"),
        ]

    def screen(self, name: str) -> dict:
        """Screen a name for adverse media mentions."""
        normalized = SanctionsEngine._normalize_name(name)
        results = {
            "screened_name": name,
            "matches": [],
            "has_adverse_media": False,
            "highest_severity": None,
            "categories_found": [],
        }

        for entry in self._entries:
            entry_norm = SanctionsEngine._normalize_name(entry.entity_name)
            score = SequenceMatcher(None, normalized, entry_norm).ratio()
            if score >= self.fuzzy_threshold:
                results["matches"].append({
                    "media_id": entry.media_id,
                    "entity_name": entry.entity_name,
                    "match_score": score,
                    "category": entry.category,
                    "severity": entry.severity,
                    "source": entry.source,
                    "headline": entry.headline,
                    "published_date": entry.published_date,
                    "country": entry.country,
                })
                continue

            # Check aliases
            for alias in entry.aliases:
                alias_norm = SanctionsEngine._normalize_name(alias)
                alias_score = SequenceMatcher(None, normalized, alias_norm).ratio()
                if alias_score >= self.fuzzy_threshold:
                    results["matches"].append({
                        "media_id": entry.media_id,
                        "entity_name": entry.entity_name,
                        "matched_alias": alias,
                        "match_score": alias_score,
                        "category": entry.category,
                        "severity": entry.severity,
                        "source": entry.source,
                        "headline": entry.headline,
                        "published_date": entry.published_date,
                        "country": entry.country,
                    })
                    break

        if results["matches"]:
            results["has_adverse_media"] = True
            severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            results["highest_severity"] = max(
                results["matches"], key=lambda m: severity_order.get(m["severity"], 0)
            )["severity"]
            results["categories_found"] = list(set(m["category"] for m in results["matches"]))

        return results

    @property
    def stats(self) -> dict:
        return {
            "total_entries": len(self._entries),
            "by_category": {},
            "by_severity": {},
        }
