"""The `mapping_rules` table: durable, content-addressed memory for every
resolution Mapping ever makes — including "no match found."

This is deliberately plain `sqlite3`, not LangGraph's checkpointer, even
though (see config.py) it lives in the same physical .db file as the
checkpointer's tables. The two are answering different questions:

- mapping_rules is keyed by WHAT was resolved: (source_system,
  source_content_type, source_ref). Looking it up answers "have we ever
  figured out what this field/value/mention corresponds to?" — a question
  that makes sense to ask before the graph even starts, on a totally fresh
  thread, possibly days later.
- LangGraph's checkpoints are keyed by WHICH RUN: a thread_id plus a step
  number. Looking one up answers "what state was this particular execution
  in when it last paused?" — a question that only makes sense within the
  lifetime of one thread.

See README.md for the fuller argument; this module is the concrete half of
it.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS mapping_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_system TEXT NOT NULL,
    source_content_type TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    evidence TEXT,
    target_system TEXT,
    target_content_type TEXT,
    target_ref TEXT,
    confidence REAL,
    method TEXT NOT NULL,
    resolved_at TEXT NOT NULL,
    UNIQUE(source_system, source_content_type, source_ref)
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def lookup(conn: sqlite3.Connection, source_system: str, source_content_type: str, source_ref: str) -> dict | None:
    row = conn.execute(
        """
        SELECT id, source_system, source_content_type, source_ref, evidence,
               target_system, target_content_type, target_ref, confidence,
               method, resolved_at
        FROM mapping_rules
        WHERE source_system = ? AND source_content_type = ? AND source_ref = ?
        """,
        (source_system, source_content_type, source_ref),
    ).fetchone()
    if row is None:
        return None
    cols = [
        "id", "source_system", "source_content_type", "source_ref", "evidence",
        "target_system", "target_content_type", "target_ref", "confidence",
        "method", "resolved_at",
    ]
    return dict(zip(cols, row))


def record(
    conn: sqlite3.Connection,
    *,
    source_system: str,
    source_content_type: str,
    source_ref: str,
    evidence: str,
    target_system: str | None,
    target_content_type: str | None,
    target_ref: str | None,
    confidence: float | None,
    method: str,
) -> dict:
    """Insert-or-replace a resolution row and return it as a dict.

    Idempotent by design (ON CONFLICT REPLACE on the natural key) so that
    re-running the same task twice — the exact scenario run.py exercises —
    never produces duplicate rows.
    """
    resolved_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO mapping_rules (
            source_system, source_content_type, source_ref, evidence,
            target_system, target_content_type, target_ref, confidence,
            method, resolved_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_system, source_content_type, source_ref)
        DO UPDATE SET
            evidence=excluded.evidence,
            target_system=excluded.target_system,
            target_content_type=excluded.target_content_type,
            target_ref=excluded.target_ref,
            confidence=excluded.confidence,
            method=excluded.method,
            resolved_at=excluded.resolved_at
        """,
        (
            source_system, source_content_type, source_ref, evidence,
            target_system, target_content_type, target_ref, confidence,
            method, resolved_at,
        ),
    )
    conn.commit()
    return lookup(conn, source_system, source_content_type, source_ref)


def all_rules(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT source_system, source_content_type, source_ref, target_system, "
        "target_content_type, target_ref, confidence, method, resolved_at "
        "FROM mapping_rules ORDER BY id"
    ).fetchall()
    cols = [
        "source_system", "source_content_type", "source_ref", "target_system",
        "target_content_type", "target_ref", "confidence", "method", "resolved_at",
    ]
    return [dict(zip(cols, r)) for r in rows]
