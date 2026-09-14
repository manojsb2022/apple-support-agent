"""
escalation.py
Urgency, sentiment, and risk evaluation module for determining when
a customer support tweet must be handed off immediately to human Tier-2 / senior agents.
"""

import re
from typing import Dict, Any, List

HIGH_RISK_KEYWORDS = [
    "stolen", "hacked", "fraud", "unauthorized", "scam", "police", "legal",
    "blacklist", "bootloop", "boot loop", "bricked", "smoke", "burning", "explod",
    "urgent", "emergency", "lost phone", "identity theft"
]

FRUSTRATION_KEYWORDS = [
    "ridiculous", "terrible", "worst", "unacceptable", "lawsuit", "sue",
    "scam", "useless", "garbage", "trash", "furious", "angry", "fed up"
]

REPEAT_CONTACT_PATTERNS = [
    r'\b(second|third|4th|5th)\s+(time|attempt)\b',
    r'\bcalled\s+\d+\s+times\b',
    r'\bno\s+one\s+is\s+helping\b',
    r'\bwaiting\s+for\s+\d+\s+(days|weeks|hours)\b'
]


class EscalationEngine:
    def __init__(self):
        self.high_risk_kw = HIGH_RISK_KEYWORDS
        self.frustration_kw = FRUSTRATION_KEYWORDS
        self.repeat_regexes = [re.compile(p, re.IGNORECASE) for p in REPEAT_CONTACT_PATTERNS]

    def evaluate(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Evaluates risk, urgency, and customer sentiment to decide whether to escalate.
        Returns escalation decision, priority level, and triggering reasons.
        """
        text_lower = text.lower()
        reasons: List[str] = []
        urgency = "low"
        escalate = False

        # 1. High Risk / Security Check
        for kw in self.high_risk_kw:
            if kw in text_lower:
                reasons.append(f"Security or device hazard keyword detected: '{kw}'")
                escalate = True
                urgency = "high"
                break

        # 2. Account Security Intent is always prioritized
        if intent == "account_security":
            if "Account security inquiry requires human verification" not in reasons:
                reasons.append("Account security inquiry requires human verification")
            escalate = True
            urgency = "high"

        # 3. Frustration / Negative Sentiment Detection
        found_frustration = [w for w in self.frustration_kw if w in text_lower]
        if found_frustration:
            reasons.append(f"High customer frustration indicators: {', '.join(found_frustration)}")
            escalate = True
            if urgency != "high":
                urgency = "medium"

        # 4. Repeat Contact Detection
        for pattern in self.repeat_regexes:
            if pattern.search(text_lower):
                reasons.append("Repeated unresolved contact pattern identified")
                escalate = True
                if urgency != "high":
                    urgency = "medium"
                break

        # 5. Financial threshold detection (e.g. charges > $100)
        dollar_match = re.findall(r'\$(\d+(?:\.\d{2})?)', text)
        for amt_str in dollar_match:
            try:
                amt = float(amt_str)
                if amt >= 100.0:
                    reasons.append(f"High monetary value transaction (${amt:.2f})")
                    escalate = True
                    urgency = "high"
            except ValueError:
                pass

        return {
            "escalate": escalate,
            "urgency": urgency,
            "reasons": reasons
        }
