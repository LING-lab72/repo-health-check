"""Tests for aggregator."""
import asyncio
from pathlib import Path

from backend.analyzer.aggregator import aggregate, _get_badge_level, _compute_health_score

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_aggregate_on_own_project():
    """Run aggregator against our own project."""
    result = asyncio.run(aggregate(REPO_ROOT, "https://github.com/user/repo-health-check"))

    assert "repo_url" in result
    assert "health_score" in result
    assert "badge_level" in result
    assert "badge_color" in result
    assert "dimensions" in result
    assert "analyzed_at" in result
    assert len(result["dimensions"]) == 6
    assert 0 <= result["health_score"] <= 100


def test_aggregate_dimensions_have_required_fields():
    """Each dimension result must have dimension/score/details/issues."""
    result = asyncio.run(aggregate(REPO_ROOT, "https://github.com/user/test"))
    for dim in result["dimensions"]:
        assert "dimension" in dim
        assert "score" in dim
        assert "details" in dim
        assert "issues" in dim


def test_badge_level_a():
    badge = _get_badge_level(85)
    assert badge["level"] == "A"
    assert badge["color"] == "brightgreen"


def test_badge_level_b():
    badge = _get_badge_level(65)
    assert badge["level"] == "B"
    assert badge["color"] == "yellow"


def test_badge_level_c():
    badge = _get_badge_level(45)
    assert badge["level"] == "C"
    assert badge["color"] == "orange"


def test_badge_level_d():
    badge = _get_badge_level(25)
    assert badge["level"] == "D"
    assert badge["color"] == "red"


def test_compute_health_score():
    dims = [
        {"dimension": "code_quality", "score": 80},
        {"dimension": "test_coverage", "score": 70},
        {"dimension": "architecture", "score": 90},
        {"dimension": "documentation", "score": 60},
        {"dimension": "dependency_security", "score": 85},
        {"dimension": "engineering", "score": 75},
    ]
    score = _compute_health_score(dims)
    assert 0 <= score <= 100
