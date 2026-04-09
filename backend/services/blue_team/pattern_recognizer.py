"""Attack pattern fingerprinting and recognition for Blue Team."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

from .defense_memory import DefenseMemory

logger = get_logger("blue_team.pattern_recognizer")


class PatternRecognizer:
    """Fingerprints anomaly patterns and matches them against known attacks.

    Each "fingerprint" is a hash of the anomaly signature (types + severity ordering).
    When a known fingerprint is re-encountered, the Blue Team can instantly classify
    the attack and apply the best known response — improving detection speed.
    """

    def __init__(self, memory: DefenseMemory) -> None:
        self.memory = memory

    def fingerprint(self, anomalies: List[Dict[str, Any]]) -> str:
        """Create a deterministic fingerprint from a set of anomalies.

        The fingerprint is based on anomaly types and severity distribution,
        NOT on timing or exact values — so the same attack pattern will
        produce the same fingerprint regardless of when it occurs.
        """
        if not anomalies:
            return "fp_empty"

        # Sort anomaly types for consistent ordering
        types = sorted(str(a.get("type", "unknown")) for a in anomalies)
        severities = sorted(str(a.get("severity", "medium")) for a in anomalies)

        # Include count of each type
        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1

        signature = f"{type_counts}|{severities}"
        fp_hash = hashlib.md5(signature.encode()).hexdigest()[:12]
        return f"fp_{fp_hash}"

    def match_known_pattern(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """Check if this fingerprint matches a known attack pattern."""
        return self.memory.get_pattern(fingerprint)

    def register_pattern(
        self,
        fingerprint: str,
        attack_type: str,
        blue_score: int,
        best_response: str,
    ) -> None:
        """Register or update a known pattern with its best response."""
        existing = self.memory.get_pattern(fingerprint)

        if existing:
            # Update if we found a better response
            if blue_score > existing.get("best_score", 0):
                existing["best_response"] = best_response
                existing["best_score"] = blue_score
            existing["encounter_count"] = existing.get("encounter_count", 0) + 1
            self.memory.register_pattern(fingerprint, existing)
        else:
            self.memory.register_pattern(fingerprint, {
                "attack_type": attack_type,
                "best_response": best_response,
                "best_score": blue_score,
                "encounter_count": 1,
            })

        logger.info(
            "Pattern registered: %s type=%s score=%d",
            fingerprint, attack_type, blue_score,
        )

    def get_recognition_stats(self) -> Dict[str, Any]:
        """Stats for frontend display."""
        patterns = self.memory.known_patterns
        return {
            "total_patterns": len(patterns),
            "patterns": [
                {
                    "fingerprint": fp,
                    "type": data.get("attack_type", "unknown"),
                    "encounters": data.get("encounter_count", 0),
                    "best_response": data.get("best_response", "unknown"),
                    "best_score": data.get("best_score", 0),
                }
                for fp, data in list(patterns.items())[:20]
            ],
        }
