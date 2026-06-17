"""Persistent storage using JSON file. Keeps history and votes of all analyses."""
from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "history.json"
VOTES_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "votes.json"
_lock = threading.Lock()
_entries: list[dict[str, Any]] = []
_votes: dict[str, int] = {}


def _ensure_dir() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def load() -> list[dict[str, Any]]:
    """Load all entries from JSON file."""
    global _entries, _votes
    _ensure_dir()
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            _entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _entries = []
    try:
        with open(VOTES_FILE, encoding="utf-8") as f:
            _votes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _votes = {}
    return _entries


def save_entry(entry: dict[str, Any]) -> None:
    """Append a new analysis entry, persist to file."""
    with _lock:
        _entries.append(entry)
        _write_file()


def get_all() -> list[dict[str, Any]]:
    """Get latest entry per repo_url, sorted by health_score descending."""
    latest: dict[str, dict[str, Any]] = {}
    for e in _entries:
        repo = e["repo_url"]
        if repo not in latest or e["analyzed_at"] > latest[repo]["analyzed_at"]:
            latest[repo] = e
    # Add trend: compare latest two scores per repo
    for repo_url, latest_entry in latest.items():
        repo_history = sorted(
            [e for e in _entries if e["repo_url"] == repo_url],
            key=lambda x: x.get("analyzed_at", ""),
        )
        if len(repo_history) >= 2:
            prev = repo_history[-2]["health_score"]
            curr = repo_history[-1]["health_score"]
            latest_entry["_trend"] = "up" if curr > prev else "down" if curr < prev else "same"
        else:
            latest_entry["_trend"] = "new"

    result = sorted(latest.values(), key=lambda x: x["health_score"], reverse=True)
    for r in result:
        r["_votes"] = _votes.get(r["repo_url"], 0)
    return result


def get_history(repo_url: str) -> list[dict[str, Any]]:
    """Get all historical entries for a repo, sorted by analyzed_at ascending."""
    matches = [e for e in _entries if e["repo_url"] == repo_url]
    return sorted(matches, key=lambda x: x.get("analyzed_at", ""))


_vote_cooldowns: dict[str, tuple[str, float]] = {}  # ip → (repo_url, timestamp)

VOTE_COOLDOWN = 60  # seconds


def cast_vote(repo_url: str, client_ip: str) -> int | None:
    """Increment vote count. Returns new count, or None if cooldown active."""
    now = time.time()
    with _lock:
        # Check cooldown
        if client_ip in _vote_cooldowns:
            last_repo, last_time = _vote_cooldowns[client_ip]
            if last_repo == repo_url and now - last_time < VOTE_COOLDOWN:
                return None
        _vote_cooldowns[client_ip] = (repo_url, now)
        _votes[repo_url] = _votes.get(repo_url, 0) + 1
        _write_votes()
    return _votes[repo_url]


def _write_file() -> None:
    _ensure_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(_entries, f, indent=2, ensure_ascii=False)


def _write_votes() -> None:
    _ensure_dir()
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(_votes, f, indent=2, ensure_ascii=False)


def get_by_url_hash(url_hash: str) -> dict[str, Any] | None:
    """Find the latest entry by URL hash (first 12 chars of sha256)."""
    latest: dict[str, dict[str, Any]] = {}
    for e in _entries:
        repo = e["repo_url"]
        h = hashlib.sha256(repo.encode()).hexdigest()[:12]
        if h == url_hash:
            if repo not in latest or e["analyzed_at"] > latest[repo]["analyzed_at"]:
                latest[repo] = e
    return list(latest.values())[0] if latest else None


# Load on import
load()
