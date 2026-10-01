"""Append-only log of WordPress writes the Sync agent makes.

Nothing in the pipeline persisted this before: `create_wp_post`/
`update_wp_post` just ran and returned, visible only transiently as SSE
`tool_call`/`tool_result` events while a run was streaming, and gone
once that run ended (or the backend restarted). This gives the
frontend's Sync Activity view something durable to read back, by
appending one JSON line per write to `data/sync-log.jsonl` — kept
outside `sandbox/`, which is the agents' own TTL workspace, since this
is app-level audit data rather than agent-authored content.
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_LOG_PATH = Path("data") / "sync-log.jsonl"


@dataclass
class SyncLogEntry:
    timestamp: float
    tool_name: str
    args: dict[str, Any]
    result: dict[str, Any]
    success: bool


def append_entry(entry: SyncLogEntry) -> None:
    """Append one entry to the log, creating `data/` if needed."""
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOG_PATH.open("a") as f:
        f.write(json.dumps(asdict(entry), default=str) + "\n")


def read_entries(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """Read logged entries, newest first.

    Parameters
    ----------
    limit : int
        Maximum number of entries to return.
    offset : int
        Number of newest entries to skip (for pagination).

    Returns
    -------
    list[dict]
        Up to `limit` entries, newest first. Empty if nothing has been
        logged yet.

    """
    if not _LOG_PATH.exists():
        return []
    lines = _LOG_PATH.read_text().splitlines()
    lines.reverse()
    return [json.loads(line) for line in lines[offset : offset + limit] if line]
