"""Tests for leaderboard API with JSON storage and votes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app
from backend.services import storage

try:
    from fastapi.testclient import TestClient
except RuntimeError:
    pytest.skip("httpx2 not installed", allow_module_level=True)


@pytest.fixture(autouse=True)
def clear_storage():
    storage._entries.clear()
    storage._votes.clear()
    yield
    storage._entries.clear()
    storage._votes.clear()


def test_leaderboard_empty():
    client = TestClient(app)
    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


def test_vote_cooldown():
    storage.save_entry({
        "repo_url": "https://github.com/a/repo1",
        "health_score": 95,
        "badge_level": "A",
        "badge_color": "brightgreen",
        "analyzed_at": "2026-01-01T00:00:00Z",
    })
    c1 = storage.cast_vote("https://github.com/a/repo1", "1.2.3.4")
    assert c1 == 1
    c2 = storage.cast_vote("https://github.com/a/repo1", "1.2.3.4")
    assert c2 is None  # cooldown


def test_leaderboard_with_votes():
    storage.save_entry({
        "repo_url": "https://github.com/a/repo1",
        "health_score": 95,
        "badge_level": "A",
        "badge_color": "brightgreen",
        "analyzed_at": "2026-01-01T00:00:00Z",
    })
    storage.cast_vote("https://github.com/a/repo1", "10.0.0.1")

    client = TestClient(app)
    resp = client.get("/api/leaderboard")
    data = resp.json()["data"]
    assert data[0]["_votes"] == 1


def test_save_entry_updates_existing():
    storage.save_entry({
        "repo_url": "https://github.com/test/x",
        "health_score": 80,
        "badge_level": "A",
        "badge_color": "brightgreen",
        "analyzed_at": "2026-01-01T00:00:00Z",
    })
    storage.save_entry({
        "repo_url": "https://github.com/test/x",
        "health_score": 65,
        "badge_level": "B",
        "badge_color": "yellow",
        "analyzed_at": "2026-01-02T00:00:00Z",
    })

    data = storage.get_all()
    assert len(data) == 1
    assert data[0]["health_score"] == 65


def test_vote_endpoint():
    storage.save_entry({
        "repo_url": "https://github.com/a/repo1",
        "health_score": 95,
        "badge_level": "A",
        "badge_color": "brightgreen",
        "analyzed_at": "2026-01-01T00:00:00Z",
    })

    client = TestClient(app)
    resp = client.post("/api/vote", json={"repo_url": "https://github.com/a/repo1"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["votes"] == 1
    assert "current_leader" in data
