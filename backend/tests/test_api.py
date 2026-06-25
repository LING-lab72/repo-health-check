"""Tests for API endpoints using TestClient."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app
from backend.services.cache import cache


try:
    from fastapi.testclient import TestClient
except RuntimeError:
    pytest.skip("httpx2 not installed, skipping API tests", allow_module_level=True)


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_analyze_invalid_url():
    """Invalid URL is accepted at the API level (HTTP 200),
    but clone will fail asynchronously and produce a cached error.
    The API returns code=1 (analyzing) since force_sync defaults to False."""
    client = TestClient(app)
    resp = client.post("/api/analyze", json={"repo_url": "not-a-valid-url"})
    assert resp.status_code == 200
    data = resp.json()
    # Async mode: code=1 means "analyzing" — clone failure happens later
    assert data["code"] == 1


def test_analyze_empty_url():
    """Empty URL is accepted at the API level (HTTP 200),
    but clone will fail asynchronously and produce a cached error.
    The API returns code=1 (analyzing) since force_sync defaults to False."""
    client = TestClient(app)
    resp = client.post("/api/analyze", json={"repo_url": ""})
    assert resp.status_code == 200
    data = resp.json()
    # Async mode: code=1 means "analyzing" — clone failure happens later
    assert data["code"] == 1


def test_analyze_missing_field():
    client = TestClient(app)
    resp = client.post("/api/analyze", json={})
    assert resp.status_code == 422


@patch("backend.routes.analyze.clone_repo")
@patch("backend.routes.analyze.aggregate", new_callable=AsyncMock)
def test_analyze_success_flow(mock_aggregate, mock_clone):
    """Test the full sync flow with mocked clone and aggregate.

    Uses force_sync=True to trigger the request/response path.
    """
    from pathlib import Path
    import tempfile

    tmpdir = Path(tempfile.mkdtemp())
    mock_clone.return_value = (tmpdir, "test-repo")
    mock_aggregate.return_value = {
        "repo_url": "https://github.com/test/repo",
        "health_score": 85.0,
        "badge_level": "A",
        "badge_color": "brightgreen",
        "badge_description": "健康",
        "dimensions": [
            {"dimension": "code_quality", "score": 90, "details": {}, "issues": []},
            {"dimension": "test_coverage", "score": 80, "details": {}, "issues": []},
            {"dimension": "architecture", "score": 85, "details": {}, "issues": []},
            {"dimension": "documentation", "score": 70, "details": {}, "issues": []},
            {"dimension": "dependency_security", "score": 95, "details": {}, "issues": []},
            {"dimension": "engineering", "score": 90, "details": {}, "issues": []},
        ],
        "ai_diagnosis": [],
        "analyzed_at": "2026-01-01T00:00:00+00:00",
    }

    client = TestClient(app)
    resp = client.post(
        "/api/analyze",
        json={"repo_url": "https://github.com/test/repo", "force_sync": True, "skip_ai": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["health_score"] == 85.0
    assert data["data"]["badge_level"] == "A"


def test_analyze_status_not_found():
    client = TestClient(app)
    resp = client.get("/api/analyze/status?task_id=nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["status"] == "not_found"


def test_badge_unknown():
    client = TestClient(app)
    resp = client.get("/api/badge/unknown123")
    assert resp.status_code == 200
    assert "image/svg+xml" in resp.headers.get("content-type", "")
    assert "unknown" in resp.text.lower()


def test_badge_cached_result():
    url = "https://github.com/test/repo"
    h = cache.url_hash(url)
    cache.set(url, {
        "repo_url": url,
        "health_score": 88,
        "badge_level": "A",
        "badge_color": "brightgreen",
        "dimensions": [],
        "analyzed_at": "2026-01-01T00:00:00Z",
    })

    client = TestClient(app)
    resp = client.get(f"/api/badge/{h}")
    assert resp.status_code == 200
    assert "A" in resp.text


@patch("backend.routes.analyze.ai_diagnose", new_callable=AsyncMock)
def test_analyze_enriches_cached_result_with_ai(mock_ai):
    url = "https://github.com/test/repo"
    mock_ai.return_value = [
        {
            "advice": "Improve tests",
            "severity": "medium",
            "estimated_hours": 2,
            "confidence": 80,
            "need_human_review": False,
        }
    ]
    cache.set(url, {
        "repo_url": url,
        "health_score": 80,
        "badge_level": "B",
        "badge_color": "yellow",
        "dimensions": [
            {"dimension": "test_coverage", "score": 55, "details": {}, "issues": []},
        ],
        "ai_diagnosis": [],
        "analyzed_at": "2026-01-01T00:00:00Z",
    })

    client = TestClient(app)
    resp = client.post(
        "/api/analyze",
        json={
            "repo_url": url,
            "force_sync": True,
            "skip_ai": False,
            "ai_api_key": "sk-user",
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "success (cached + ai)"
    assert data["data"]["ai_diagnosis"][0]["advice"] == "Improve tests"
    mock_ai.assert_awaited_once()
