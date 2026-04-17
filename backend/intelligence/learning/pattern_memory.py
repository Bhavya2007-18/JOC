import sqlite3
import uuid
import time
from pathlib import Path
from typing import Optional

from utils.paths import get_persistent_path
DB_PATH = get_persistent_path("pattern_memory.db", "storage")

class PatternMemory:
    INTENSITY_TOLERANCE  = 0.20
    DERIVATIVE_TOLERANCE = 0.30

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=5)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id    TEXT PRIMARY KEY,
                pattern_type  TEXT NOT NULL,
                resource      TEXT NOT NULL,
                intensity     REAL DEFAULT 0.0,
                duration      REAL DEFAULT 0.0,
                derivative    REAL DEFAULT 0.0,
                response      TEXT,
                success_score REAL DEFAULT 0.5,
                executions    INTEGER DEFAULT 0,
                last_seen     REAL,
                created_at    REAL
            )
        """)
        self._conn.commit()

    def upsert(self, pattern: dict, response: str) -> str:
        """
        Insert new pattern OR update existing similar pattern.
        Returns the pattern_id.
        """
        ptype    = pattern["pattern_type"]
        resource = pattern["resource"]
        intensity = pattern.get("intensity", 0.0)
        derivative = pattern.get("derivative", 0.0)

        # 1. Find existing similar pattern
        cursor = self._conn.execute("""
            SELECT pattern_id, intensity, derivative FROM patterns
            WHERE pattern_type = ? AND resource = ?
        """, (ptype, resource))
        
        existing = cursor.fetchall()
        for row in existing:
            i_diff = abs(row["intensity"] - intensity)
            d_diff = abs(row["derivative"] - derivative)
            if i_diff <= self.INTENSITY_TOLERANCE and d_diff <= self.DERIVATIVE_TOLERANCE:
                # Cluster hit — update last_seen and executions, keep response
                self._conn.execute("""
                    UPDATE patterns
                    SET last_seen=?, executions=executions+1, response=?
                    WHERE pattern_id=?
                """, (time.time(), response, row["pattern_id"]))
                self._conn.commit()
                return row["pattern_id"]

        # 2. No match — insert new pattern
        pid = str(uuid.uuid4())
        self._conn.execute("""
            INSERT INTO patterns 
            (pattern_id, pattern_type, resource, intensity, duration, derivative,
             response, success_score, executions, last_seen, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0.5, 1, ?, ?)
        """, (
            pid, ptype, resource, intensity,
            pattern.get("duration", 0.0),
            derivative, response,
            time.time(), time.time()
        ))
        self._conn.commit()
        return pid

    def update_score(self, pattern_id: str, success: bool, impact: float) -> None:
        """
        Updates success_score using Exponential Moving Average.
        impact: 0.0–100.0 (percentage threat reduction)
        """
        cursor = self._conn.execute(
            "SELECT success_score, executions FROM patterns WHERE pattern_id=?", (pattern_id,)
        )
        row = cursor.fetchone()
        if not row: return

        current_score = row["success_score"]
        new_signal    = (impact / 100.0) if success else 0.0
        # EMA: new = 0.3 × signal + 0.7 × current
        new_score = (0.3 * new_signal) + (0.7 * current_score)
        new_score = max(0.0, min(1.0, new_score))   # clamp [0, 1]

        self._conn.execute(
            "UPDATE patterns SET success_score=?, last_seen=? WHERE pattern_id=?",
            (new_score, time.time(), pattern_id)
        )
        self._conn.commit()

    def find_similar(self, pattern: dict, top_n: int = 3) -> list:
        """Returns top-N similar patterns ordered by decayed success score."""
        cursor = self._conn.execute("""
            SELECT * FROM patterns
            WHERE pattern_type=? AND resource=?
            ORDER BY success_score DESC
            LIMIT ?
        """, (pattern["pattern_type"], pattern["resource"], top_n * 2))   

        now = time.time()
        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            # Apply time decay: score × 0.99^(hours_since_last_seen)
            hours_ago = (now - (row_dict["last_seen"] or now)) / 3600
            decayed   = row_dict["success_score"] * (0.99 ** hours_ago)
            row_dict["effective_score"] = round(decayed, 4)
            results.append(row_dict)

        results.sort(key=lambda r: r["effective_score"], reverse=True)
        return results[:top_n]

    def get_best_response(self, pattern: dict) -> Optional[str]:
        """Returns the recommended tweak name for this pattern type, or None if uncertain."""
        similar = self.find_similar(pattern, top_n=1)
        if not similar: return None
        top = similar[0]
        # Only trust it if: enough executions AND effective score > 0.55 (above prior)
        if top["executions"] >= 5 and top["effective_score"] >= 0.55:
            return top["response"]
        return None

    def get_all(self, limit: int = 100) -> list:
        cursor = self._conn.execute(
            "SELECT * FROM patterns ORDER BY last_seen DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

