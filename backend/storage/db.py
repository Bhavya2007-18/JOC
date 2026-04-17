import sqlite3
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
from utils.paths import get_persistent_path
DB_PATH = get_persistent_path("snapshots.db", "storage")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            cpu_percent REAL,
            memory_percent REAL,
            process_count INTEGER,
            data TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            event_type TEXT,
            severity TEXT,
            message TEXT,
            metadata TEXT
        )
    """)

    conn.commit()
    conn.close()


def set_setting(key: str, value: str):
    """Save a setting value to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = None) -> str:
    """Retrieve a setting value from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def save_snapshot(snapshot):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO snapshots (timestamp, cpu_percent, memory_percent, process_count, data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        snapshot.timestamp,
        snapshot.cpu_percent,
        snapshot.memory_percent,
        snapshot.process_count,
        json.dumps(snapshot.__dict__, default=str)
    ))

    conn.commit()
    conn.close()


def load_recent_snapshots(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT data FROM snapshots
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [json.loads(row["data"]) for row in rows]


def log_timeline_event(event_type: str, severity: str, message: str, metadata: dict = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO timeline_events (timestamp, event_type, severity, message, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (
        time.time(),
        event_type,
        severity,
        message,
        json.dumps(metadata or {})
    ))
    conn.commit()
    conn.close()


def get_timeline_events(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, event_type, severity, message, metadata 
        FROM timeline_events 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "timestamp": row["timestamp"],
        "event_type": row["event_type"],
        "severity": row["severity"],
        "message": row["message"],
        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
    } for row in rows]