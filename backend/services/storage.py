"""Persistent storage backed by SQLite.

The public functions keep the old JSON-storage API stable for routes while
moving persistence to a multi-process-safe database file.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get(
    "REPO_HEALTH_DATA_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "data"),
))
DB_FILE = Path(os.environ.get("REPO_HEALTH_DB_FILE", str(DATA_DIR / "repo_health.db")))
DATA_FILE = DATA_DIR / "history.json"
VOTES_FILE = DATA_DIR / "votes.json"
VOTE_COOLDOWN = 60

_lock = threading.RLock()

# Backward-compatible names for older tests/tools. They are no longer the
# source of truth; use clear_all() in tests.
_entries: list[dict[str, Any]] = []
_votes: dict[str, int] = {}


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    _ensure_dir()
    conn = sqlite3.connect(DB_FILE, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db() -> None:
    with _lock, _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_url TEXT NOT NULL,
                health_score REAL NOT NULL,
                badge_level TEXT NOT NULL,
                badge_color TEXT NOT NULL,
                analyzed_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_repo_time ON history(repo_url, analyzed_at)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS votes (
                repo_url TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vote_cooldowns (
                voter_id TEXT PRIMARY KEY,
                repo_url TEXT NOT NULL,
                last_time REAL NOT NULL
            )
            """
        )
        _migrate_json_if_empty(conn)


def _migrate_json_if_empty(conn: sqlite3.Connection) -> None:
    history_count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    if history_count == 0 and DATA_FILE.exists():
        try:
            entries = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            entries = []
        for entry in entries if isinstance(entries, list) else []:
            if isinstance(entry, dict):
                _insert_entry(conn, entry)

    vote_count = conn.execute("SELECT COUNT(*) FROM votes").fetchone()[0]
    if vote_count == 0 and VOTES_FILE.exists():
        try:
            votes = json.loads(VOTES_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            votes = {}
        for repo_url, count in votes.items() if isinstance(votes, dict) else []:
            try:
                safe_count = max(0, int(count))
            except (TypeError, ValueError):
                safe_count = 0
            conn.execute(
                "INSERT OR REPLACE INTO votes(repo_url, count) VALUES (?, ?)",
                (str(repo_url), safe_count),
            )


def _insert_entry(conn: sqlite3.Connection, entry: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO history(repo_url, health_score, badge_level, badge_color, analyzed_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(entry.get("repo_url", "")),
            float(entry.get("health_score", 0)),
            str(entry.get("badge_level", "?")),
            str(entry.get("badge_color", "lightgrey")),
            str(entry.get("analyzed_at", "")),
        ),
    )


def _row_to_entry(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "repo_url": row["repo_url"],
        "health_score": row["health_score"],
        "badge_level": row["badge_level"],
        "badge_color": row["badge_color"],
        "analyzed_at": row["analyzed_at"],
    }


def load() -> list[dict[str, Any]]:
    """Load all history entries from SQLite."""
    with _lock, _connect() as conn:
        rows = conn.execute(
            """
            SELECT repo_url, health_score, badge_level, badge_color, analyzed_at
            FROM history
            ORDER BY analyzed_at ASC, id ASC
            """
        ).fetchall()
    return [_row_to_entry(row) for row in rows]


def save_entry(entry: dict[str, Any]) -> None:
    """Append a new analysis entry."""
    with _lock, _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        _insert_entry(conn, entry)
        conn.commit()


def _trend(current: float, previous: float | None) -> str:
    if previous is None:
        return "new"
    return "up" if current > previous else "down" if current < previous else "same"


def get_total_count() -> int:
    """Count repositories represented in the leaderboard."""
    with _lock, _connect() as conn:
        row = conn.execute("SELECT COUNT(DISTINCT repo_url) AS total FROM history").fetchone()
    return int(row["total"] if row else 0)


def get_all(limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
    """Get latest entry per repo_url, sorted by health_score descending."""
    params: list[Any] = []
    page_clause = ""
    if limit is not None:
        safe_limit = max(1, int(limit))
        safe_offset = max(0, int(offset))
        page_clause = "LIMIT ? OFFSET ?"
        params.extend([safe_limit, safe_offset])

    with _lock, _connect() as conn:
        rows = conn.execute(
            f"""
            WITH ranked AS (
                SELECT
                    repo_url,
                    health_score,
                    badge_level,
                    badge_color,
                    analyzed_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY repo_url
                        ORDER BY analyzed_at DESC, id DESC
                    ) AS rn,
                    LEAD(health_score) OVER (
                        PARTITION BY repo_url
                        ORDER BY analyzed_at DESC, id DESC
                    ) AS previous_score
                FROM history
            )
            SELECT
                ranked.repo_url,
                ranked.health_score,
                ranked.badge_level,
                ranked.badge_color,
                ranked.analyzed_at,
                ranked.previous_score,
                COALESCE(votes.count, 0) AS votes
            FROM ranked
            LEFT JOIN votes ON votes.repo_url = ranked.repo_url
            WHERE ranked.rn = 1
            ORDER BY ranked.health_score DESC, ranked.analyzed_at DESC
            {page_clause}
            """,
            params,
        ).fetchall()

    items: list[dict[str, Any]] = []
    for row in rows:
        item = _row_to_entry(row)
        previous = row["previous_score"]
        item["_trend"] = _trend(float(item["health_score"]), float(previous) if previous is not None else None)
        item["_votes"] = int(row["votes"])
        items.append(item)
    return items


def get_history(repo_url: str) -> list[dict[str, Any]]:
    """Get all historical entries for a repo, sorted by analyzed_at ascending."""
    with _lock, _connect() as conn:
        rows = conn.execute(
            """
            SELECT repo_url, health_score, badge_level, badge_color, analyzed_at
            FROM history
            WHERE repo_url = ?
            ORDER BY analyzed_at ASC, id ASC
            """,
            (repo_url,),
        ).fetchall()
    return [_row_to_entry(row) for row in rows]


def cast_vote(repo_url: str, voter_id: str) -> int | None:
    """Increment vote count. Returns new count, or None if cooldown active."""
    now = time.time()
    with _lock, _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        cooldown = conn.execute(
            "SELECT repo_url, last_time FROM vote_cooldowns WHERE voter_id = ?",
            (voter_id,),
        ).fetchone()
        if cooldown and cooldown["repo_url"] == repo_url and now - cooldown["last_time"] < VOTE_COOLDOWN:
            conn.rollback()
            return None

        conn.execute(
            """
            INSERT INTO vote_cooldowns(voter_id, repo_url, last_time)
            VALUES (?, ?, ?)
            ON CONFLICT(voter_id) DO UPDATE SET
                repo_url = excluded.repo_url,
                last_time = excluded.last_time
            """,
            (voter_id, repo_url, now),
        )
        conn.execute(
            """
            INSERT INTO votes(repo_url, count) VALUES (?, 1)
            ON CONFLICT(repo_url) DO UPDATE SET count = count + 1
            """,
            (repo_url,),
        )
        count = conn.execute("SELECT count FROM votes WHERE repo_url = ?", (repo_url,)).fetchone()[
            "count"
        ]
        conn.commit()
    return int(count)


def get_by_url_hash(url_hash: str) -> dict[str, Any] | None:
    """Find the latest entry by URL hash (first 12 chars of sha256)."""
    latest: dict[str, dict[str, Any]] = {}
    for entry in load():
        repo = entry["repo_url"]
        if hashlib.sha256(repo.encode()).hexdigest()[:12] == url_hash:
            if repo not in latest or entry["analyzed_at"] > latest[repo]["analyzed_at"]:
                latest[repo] = entry
    return list(latest.values())[0] if latest else None


def clear_all() -> None:
    """Clear SQLite storage. Intended for tests and local maintenance."""
    with _lock, _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM vote_cooldowns")
        conn.execute("DELETE FROM votes")
        conn.execute("DELETE FROM history")
        conn.commit()


_init_db()
