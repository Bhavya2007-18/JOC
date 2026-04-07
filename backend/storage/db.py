import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "snapshots.db"


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

    conn.commit()
    conn.close()


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